#!/usr/bin/env python3
"""Propose prep around supplied availability and coursework; no network or writes."""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta
import json
import math
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_BYTES = 1_000_000
AREAS = ("introduction", "behavioral", "role_practice", "company_research", "mock")


class InputError(ValueError):
    pass


def finite(value, label, low=0, high=100000):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
        raise InputError(f"{label} must be a finite number between {low} and {high}")
    return value


def timestamp(value):
    if not isinstance(value, str):
        raise InputError("timestamps must be ISO strings with UTC offsets")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InputError("invalid ISO timestamp") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise InputError("timestamps need explicit UTC offsets")
    return result


def windows(values, now, interview, buffer=0):
    if not isinstance(values, list) or len(values) > 500:
        raise InputError("windows must be lists of at most 500 items")
    result = []
    for item in values:
        if not isinstance(item, dict):
            raise InputError("window must contain start and end")
        start, end = timestamp(item.get("start")), timestamp(item.get("end"))
        if end <= start:
            raise InputError("window end must follow start")
        start = max(now, start - timedelta(minutes=buffer))
        end = min(interview, end + timedelta(minutes=buffer))
        if start < end:
            result.append((start, end))
    merged = []
    for start, end in sorted(result):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def subtract(free, busy):
    for left, right in busy:
        remainder = []
        for start, end in free:
            if right <= start or left >= end:
                remainder.append((start, end))
            else:
                if start < left:
                    remainder.append((start, left))
                if right < end:
                    remainder.append((right, end))
        free = remainder
    return free


def block(kind, start, end, reason):
    return {"type": kind, "start": start.isoformat(), "end": end.isoformat(),
            "length_minutes": round((end - start).total_seconds() / 60, 2), "reason": reason}


def bounded(result):
    """Keep Cubbie's full proposal and review status inside its output read limit."""
    fields = ("coursework_reservations", "unresolved", "warnings")
    result["detail_counts"] = {key: len(result[key]) for key in fields}
    result["details_truncated"] = False
    for key in fields:
        if len(result[key]) > 8:
            result[key] = result[key][:8]
            result["details_truncated"] = True
    while len(json.dumps(result, ensure_ascii=False, separators=(",", ":"))) > 7500:
        choices = [key for key in fields if len(result[key]) > 1]
        if not choices:
            break
        largest = max(choices, key=lambda key: len(json.dumps(result[key], ensure_ascii=False)))
        result[largest].pop()
        result["details_truncated"] = True
    return result


def plan(data):
    if not isinstance(data, dict):
        raise InputError("input must be a JSON object")
    now, interview = timestamp(data.get("now")), timestamp(data.get("interview"))
    if interview <= now or interview - now > timedelta(days=60):
        raise InputError("interview must be in the next 60 days")
    if data.get("weakest_area", "behavioral") not in AREAS:
        raise InputError("weakest_area must be introduction, behavioral, role_practice, company_research or mock")
    limit = data.get("max_blocks", 6)
    if type(limit) is not int or not 1 <= limit <= 10:
        raise InputError("max_blocks must be an integer from 1 to 10")
    buffer = finite(data.get("buffer_minutes", 10), "buffer_minutes", 0, 60)
    free = windows(data.get("free_windows", []), now, interview)
    busy = windows(data.get("busy", []), now, interview, buffer)
    protected = windows(data.get("coursework_windows", []), now, interview)
    free = subtract(free, busy + protected)
    warnings, unresolved, reservations = [], [], []
    deadlines = data.get("deadlines", [])
    if not isinstance(deadlines, list) or len(deadlines) > 100:
        raise InputError("deadlines must be a list of at most 100 items")
    ranked = []
    for item in deadlines:
        if not isinstance(item, dict) or not isinstance(item.get("title"), str) or not 1 <= len(item["title"]) <= 200:
            raise InputError("each deadline needs a title of 1 to 200 characters")
        due = item.get("due")
        date_only = isinstance(due, str) and len(due) == 10
        if date_only:
            try:
                day = date.fromisoformat(due)
            except ValueError as exc:
                raise InputError("invalid date-only deadline") from exc
            if not isinstance(data.get("timezone"), str):
                unresolved.append({"title": item["title"], "reason": "date-only deadline needs a named local timezone or confirmed due time"})
                continue
            try:
                local_zone = ZoneInfo(data["timezone"])
            except (ZoneInfoNotFoundError, ValueError) as exc:
                raise InputError("named timezone unavailable; supply confirmed due timestamps instead") from exc
            # Conservative planning boundary, explicitly NOT an invented due time.
            cutoff = datetime.combine(day, time.min, tzinfo=local_zone)
            warnings.append(f"{item['title']}: date-only due {due}; reserve before that day, not an assumed due time.")
        else:
            cutoff = timestamp(due)
        minutes = item.get("remaining_minutes")
        if minutes is None:
            if cutoff <= interview:
                unresolved.append({"title": item["title"], "reason": "remaining coursework effort unknown"})
            continue
        finite(minutes, "remaining_minutes", 0, 6000)
        if minutes == 0:
            continue
        if cutoff > interview:
            warnings.append(f"{item['title']}: due after interview; include any earlier work in coursework_windows.")
            continue
        weight = finite(item.get("weight", 1), "weight", 0.01, 100)
        if item.get("points") is not None:
            finite(item["points"], "points")
        urgency = weight / max((cutoff - now).total_seconds() / 3600, 1)
        ranked.append((-urgency, cutoff, item["title"], minutes))
    for _, cutoff, title, minutes in sorted(ranked):
        remaining = minutes
        for start, end in reversed(free[:]):
            end = min(end, cutoff)
            if end <= start:
                continue
            length = min(remaining, (end - start).total_seconds() / 60)
            reserved_start = end - timedelta(minutes=length)
            reservations.append(block("coursework", reserved_start, end, f"Protect {title} before prep; estimated effort supplied by student."))
            free = subtract(free, [(reserved_start, end)])
            remaining -= length
            if remaining <= 0.00001:
                break
        if remaining > 0.00001:
            unresolved.append({"title": title, "reason": "insufficient free time before planning boundary", "unallocated_minutes": round(remaining, 2)})
    result = {"schema_version": 1, "proposals_only": True, "status": "proposed", "blocks": [],
              "coursework_reservations": sorted(reservations, key=lambda item: timestamp(item["start"])),
              "unresolved": unresolved, "warnings": warnings,
              "note": "Review all proposals; explicit approval and fresh conflict/duplicate checks precede any calendar change."}
    if unresolved:
        result["status"] = "coursework_needs_review"
        return bounded(result)
    weakest = data.get("weakest_area", "behavioral")
    sequence = [weakest, "introduction", "company_research", weakest, "role_practice", "mock"]
    durations = {"introduction": 15, "behavioral": 20, "company_research": 15, "role_practice": 25, "mock": 30}
    for kind in (sequence * 2)[:limit]:
        minutes = durations[kind]
        for start, end in free:
            finish = start + timedelta(minutes=minutes)
            if finish <= end:
                result["blocks"].append(block(kind, start, finish, "Extra practice for stated weakest area." if kind == weakest else "Cover a complementary interview preparation task."))
                free = subtract(free, [(start, finish + timedelta(minutes=buffer))])
                break
    if not result["blocks"]:
        result["status"] = "no_prep_space"
    return bounded(result)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="JSON file, or - for stdin")
    source.add_argument("--sample", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.sample:
            path = Path(__file__).resolve().parent.parent / "assets" / "sample_busy.json"
            with path.open("rb") as handle:
                raw = handle.read(MAX_BYTES + 1)
        elif args.input == "-":
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        else:
            with Path(args.input).open("rb") as handle:
                raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise InputError("input exceeds 1 MB")
        data = json.loads(raw.decode("utf-8"))
        result = plan(data)
        result["sample"] = args.sample
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
        return 5 if result["status"] == "coursework_needs_review" else 4 if result["status"] == "no_prep_space" else 0
    except (InputError, ValueError, OSError, OverflowError) as exc:
        print(f"invalid planning input: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
