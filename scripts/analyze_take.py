#!/usr/bin/env python3
"""Offline transcript measurements. Python 3.9+, standard library only; no writes."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys

VERSION = 1
MAX_BYTES = 1_000_000
# Text occurrences, not a diagnosis of disfluency or confidence.
FILLERS = ("um", "uh", "er", "ah", "mm", "hmm")
CANDIDATES = (
    "you know", "i mean", "kind of", "sort of", "like", "so", "basically",
    "actually", "literally", "right", "okay", "well",
)
TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*|\d+(?:[.,]\d+)*", re.UNICODE)


class InputError(ValueError):
    pass


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{label} must be a finite number")
    return value


def read_text(path):
    try:
        with Path(path).open("rb") as handle:
            data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise InputError("input exceeds 1 MB")
        return data.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise InputError("input file must be readable UTF-8") from exc


def load_json(path):
    try:
        return json.loads(read_text(path), parse_constant=lambda value: (_ for _ in ()).throw(InputError("non-finite JSON number")))
    except json.JSONDecodeError as exc:
        raise InputError("invalid JSON input") from exc


def occurrences(text, tokens, phrases):
    """Longest whole-token phrase first; never bridge sentence punctuation."""
    counts = Counter()
    spans = []
    choices = sorted((phrase.split() for phrase in phrases), key=lambda parts: (-len(parts), parts))
    index = 0
    while index < len(tokens):
        for parts in choices:
            selected = tokens[index:index + len(parts)]
            if len(selected) != len(parts):
                continue
            if [m.group().casefold() for m in selected] != parts:
                continue
            if any(not text[a.end():b.start()].isspace() for a, b in zip(selected, selected[1:])):
                continue
            phrase = " ".join(parts)
            counts[phrase] += 1
            spans.append({"term": phrase, "start_word": index + 1, "end_word": index + len(parts)})
            index += len(parts)
            break
        else:
            index += 1
    return dict(sorted(counts.items())), spans


def pace_band(wpm):
    if wpm < 100:
        return "below_100"
    if wpm < 130:
        return "100_to_under_130"
    if wpm <= 160:
        return "130_to_160"
    if wpm <= 180:
        return "over_160_to_180"
    return "over_180"


def pause_metrics(segments, text, duration):
    if not isinstance(segments, list) or not segments or len(segments) > 2000:
        raise InputError("segments must be a nonempty list of at most 2000 items")
    validated = []
    for segment in segments:
        if not isinstance(segment, dict) or not isinstance(segment.get("text"), str):
            raise InputError("each segment needs start, end and text")
        start = number(segment.get("start"), "segment start")
        end = number(segment.get("end"), "segment end")
        if start < 0 or end <= start:
            raise InputError("segments need 0 <= start < end")
        if validated and start < validated[-1]["end"]:
            raise InputError("segments must be ordered and nonoverlapping")
        if duration is not None and end > duration:
            raise InputError("segment extends beyond the supplied duration")
        validated.append({"start": start, "end": end, "text": segment["text"]})
    normalize = lambda value: [m.group().casefold() for m in TOKEN.finditer(value)]
    if normalize(" ".join(s["text"] for s in validated)) != normalize(text):
        raise InputError("segments must cover the same transcript in order")
    gaps = []
    for before, after in zip(validated, validated[1:]):
        gap = after["start"] - before["end"]
        if gap >= 3:
            gaps.append({
                "start_seconds": before["end"], "duration_seconds": round(gap, 3),
                "context": "sentence_boundary" if before["text"].rstrip().endswith((".", "!", "?")) else "within_sentence",
            })
    return {"status": "available", "gap_threshold_seconds": 3, "gap_count": len(gaps), "gaps": gaps[:5], "truncated": len(gaps) > 5,
            "limitation": "Segment gaps only; punctuation cannot establish intent, emotion or confidence."}


def analyze(text, duration=None, segments=None):
    tokens = list(TOKEN.finditer(text))
    if not tokens:
        raise InputError("transcript contains no words")
    if duration is not None:
        number(duration, "duration")
        if duration <= 0:
            raise InputError("duration must be positive")
    fillers, spans = occurrences(text, tokens, FILLERS)
    candidates, _ = occurrences(text, tokens, CANDIDATES)
    total = len(tokens)
    filler_total = sum(fillers.values())
    openings = Counter()
    for sentence in re.split(r"[.!?\n]+", text):
        words = [m.group().casefold() for m in TOKEN.finditer(sentence)]
        if len(words) >= 2:
            openings[" ".join(words[:2])] += 1
    # Fixed, nonoverlapping word windows keep density denominators exact.
    zones = []
    for start in range(1, total + 1, 20):
        end = min(start + 19, total)
        count = sum(start <= span["start_word"] <= end for span in spans)
        if count >= 3:
            zones.append({"start_word": start, "end_word": end, "filler_count": count,
                          "fillers_per_100_words": round(100 * count / (end - start + 1), 2)})
    zones.sort(key=lambda zone: (-zone["fillers_per_100_words"], zone["start_word"]))
    wpm = total * 60 / duration if duration is not None else None
    if wpm is not None:
        number(wpm, "computed WPM; check duration")
    return {
        "schema_version": VERSION,
        "transcript_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "word_count": total, "filler_counts": fillers, "filler_count": filler_total,
        "fillers_per_100_words": round(100 * filler_total / total, 2),
        "candidate_counts": candidates, "candidate_count": sum(candidates.values()),
        "candidate_note": "Context-sensitive terms; excluded from filler_count. Review before coaching.",
        "repeated_openings": [{"opening": opening, "count": count} for opening, count in sorted(openings.items(), key=lambda item: (-item[1], item[0])) if count >= 2][:5],
        "hot_zones": zones[:3],
        "pace": {"status": "available" if wpm is not None else "unavailable", "duration_seconds": duration,
                 "words_per_minute": round(wpm, 2) if wpm is not None else None,
                 "band": pace_band(wpm) if wpm is not None else None,
                 "basis": "whole_recording_including_pauses", "guidance_only": True},
        "pauses": pause_metrics(segments, text, duration) if segments is not None else {"status": "unavailable", "reason": "no_verified_segments"},
    }


def compare(result, previous):
    if not isinstance(previous, dict) or type(previous.get("schema_version")) is not int or previous["schema_version"] != VERSION:
        raise InputError("previous take needs matching schema_version")
    for key in ("word_count", "filler_count", "fillers_per_100_words", "candidate_count"):
        value = number(previous.get(key), f"previous {key}")
        if value < 0 or (key != "fillers_per_100_words" and type(value) is not int):
            raise InputError("previous counts must be nonnegative integers")
    if previous["word_count"] <= 0 or previous["filler_count"] > previous["word_count"]:
        raise InputError("previous word/filler counts are inconsistent")
    expected = round(100 * previous["filler_count"] / previous["word_count"], 2)
    if abs(previous["fillers_per_100_words"] - expected) > 0.011:
        raise InputError("previous filler rate is inconsistent")
    delta = {key: round(result[key] - previous[key], 2) for key in ("word_count", "filler_count", "fillers_per_100_words", "candidate_count")}
    pace = previous.get("pace")
    if not isinstance(pace, dict):
        raise InputError("previous pace must be an object")
    delta["words_per_minute"] = None
    if pace.get("status") == "available":
        old_duration = number(pace.get("duration_seconds"), "previous duration")
        old_wpm = number(pace.get("words_per_minute"), "previous WPM")
        if old_duration <= 0 or abs(old_wpm - previous["word_count"] * 60 / old_duration) > 0.011:
            raise InputError("previous pace is inconsistent")
        if result["pace"]["status"] == "available":
            delta["words_per_minute"] = round(result["pace"]["words_per_minute"] - old_wpm, 2)
    elif pace.get("status") != "unavailable":
        raise InputError("previous pace status is invalid")
    return {"direction": "current_minus_previous", "deltas": delta,
            "note": "Compare the same question; fewer words or fillers alone does not establish a better answer."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("transcript", nargs="?", help="UTF-8 file; omit or use - for stdin")
    source.add_argument("--sample", action="store_true")
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--segments-file", help="JSON [{start,end,text}]; verified single-speaker timings only")
    parser.add_argument("--previous", help="JSON-only output of a previous take")
    parser.add_argument("--json", action="store_true", help="JSON only; default also prints one human line")
    args = parser.parse_args(argv)
    try:
        if args.sample and (args.previous or args.segments_file):
            raise InputError("--sample cannot read previous/student segment files")
        if args.sample:
            text = read_text(Path(__file__).resolve().parent.parent / "assets" / "sample_take.txt")
        elif args.transcript and args.transcript != "-":
            text = read_text(args.transcript)
        else:
            if sys.stdin.isatty():
                raise InputError("provide a transcript file, stdin, or --sample")
            text = sys.stdin.buffer.read(MAX_BYTES + 1).decode("utf-8")
            if len(text.encode("utf-8")) > MAX_BYTES:
                raise InputError("input exceeds 1 MB")
        if not TOKEN.search(text):
            print("empty transcript: send or paste an answer", file=sys.stderr)
            return 3
        result = analyze(text, args.duration_seconds, load_json(args.segments_file) if args.segments_file else None)
        result["sample"] = args.sample
        if args.sample and args.duration_seconds is not None:
            result["pace"]["basis"] = "synthetic_demo_duration"
        if args.previous:
            previous = load_json(args.previous)
            if isinstance(previous, dict) and previous.get("sample"):
                raise InputError("sample takes cannot be compared with student takes")
            result["comparison"] = compare(result, previous)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
        if not args.json:
            pace = result["pace"]
            print(f"{result['word_count']} words; {result['filler_count']} filler occurrences; {result['candidate_count']} terms to review; " +
                  (f"{pace['words_per_minute']} WPM (guidance only)." if pace["status"] == "available" else "pace unavailable without duration."))
        return 0
    except (InputError, UnicodeError, OverflowError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
