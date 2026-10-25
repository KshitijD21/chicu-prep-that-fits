# Transcript measurements

Run `python3 scripts/analyze_take.py [UTF-8-file|-] [--duration-seconds N] [--segments-file segments.json] [--previous prior.json] [--json]` from the Skill folder. Omit the file to read stdin. `--json` emits a single compact JSON object suitable for a prior-take file; otherwise the second output line is a human summary. Do not feed that two-line format to `--previous`.

`--sample` reads only the bundled synthetic take, never saved settings. It cannot read previous/student segment files. A duration supplied in sample mode is marked synthetic. Scripts never save state, recordings or transcripts; the caller chooses any working files explicitly. File/stdin inputs are capped at 1 MB; timing inputs at 2,000 segments. Output limits lists to three hot zones, five repeated openings and five pause gaps.

## Counting contract

Words are Unicode letters (with internal straight/curly apostrophes) or numbers, including decimal/thousands punctuation. Hyphens separate words. Case is ignored for matching. This is a reproducible tokenizer, not a claim about linguistic word boundaries in every language. Automatic coaching lists are English-only; for other languages report that limitation and use a qualitative rubric or an explicitly agreed language-specific extension.

`filler_counts` uses exact whole-word occurrences of: **um, uh, er, ah, mm, hmm**. `filler_count` is their sum; `fillers_per_100_words = 100 × filler_count / word_count`. These are transcript occurrences, not validated acoustic disfluencies. Transcription can omit fillers, so changes between transcripts can reflect transcription differences.

`candidate_counts` separately lists: **you know, I mean, kind of, sort of, like, so, basically, actually, literally, right, okay, well**. Whole-token phrases use whitespace between words and never bridge sentence punctuation. Longer phrases win. These counts are excluded from filler totals; ordinary meanings must not be penalized. The list is a transparent heuristic vocabulary, not a universal judgment of speaking quality.

Repeated openings are the same first two tokens in at least two punctuation/newline-delimited sentences. They are review cues, not automatic mistakes. Proper nouns and abbreviations can affect sentence splitting.

Hot zones are nonoverlapping 20-word windows with at least three strong-list filler occurrences. The final shorter window uses its actual length as denominator. Report word ranges, not seconds. Rank by density, then earliest position. No severity or confidence score is inferred from density.

## Timing

WPM is total transcript words divided by supplied **whole recording seconds**, times 60; it includes silence. Do not call this articulation rate or compare it directly to a rate that excludes pauses. Bands are below 100, 100–under 130, 130–160, over 160–180, over 180. They are editable practice suggestions; accent, disability, language, question complexity and speaking style matter. Do not claim an ideal pace ensures comprehension or hiring success.

Optional segment JSON is an array of `{ "start": 0, "end": 5.5, "text": "..." }` with seconds from the actual recording. It must be ordered, nonoverlapping and cover the same transcript, with positive segment durations. Reject timestamps beyond supplied recording duration. Only a verified single-speaker take is supported. Segment boundaries are not word timestamps and may not align with acoustic silence.

The script reports gaps ≥3 seconds, labeled `sentence_boundary` or `within_sentence` from punctuation. These are timestamp gaps, not classifications of deliberate emphasis, anxiety or hesitation. If Cubbie cannot provide actual timings, omit them. Do not reconstruct them by spreading words evenly over an audio duration.

## Comparing

Save the first take's `--json` output only when the student agreed to retaining it. Run the same-question second take with `--previous`. Deltas are **current minus previous**. Rates accompany counts to avoid rewarding shorter answers automatically. WPM deltas require durations in both takes; keep actual and self-reported timing provenance explicit. Sample output cannot be a previous student take. No content quality score is computed.

Exit 0: measurement printed. Exit 2: malformed/missing/unreadable inputs, unsupported prior schema or invalid timing. Exit 3: no transcript words. Errors go to stderr as one line and do not include the transcript. `transcript_sha256` identifies the exact input for comparison; it is not anonymization or secure storage.
