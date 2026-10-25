# Deterministic planning contract

`python3 scripts/plan_blocks.py --input plan-input.json` (or `--input -` for stdin) proposes blocks only. `--sample` reads the bundled synthetic scenario. It performs no API calls, calendar writes or persistence. Inputs are capped at 1 MB, 500 intervals per interval list, 100 deadlines and a 60-day horizon. Output is bounded to ten prep blocks; put only relevant coursework in the input.

Input example:

```json
{
  "now": "2026-10-26T09:00:00-07:00",
  "interview": "2026-10-30T10:00:00-07:00",
  "timezone": "America/Phoenix",
  "weakest_area": "behavioral",
  "max_blocks": 6,
  "buffer_minutes": 10,
  "free_windows": [{"start": "2026-10-26T14:00:00-07:00", "end": "2026-10-26T18:00:00-07:00"}],
  "busy": [{"start": "2026-10-26T15:00:00-07:00", "end": "2026-10-26T16:00:00-07:00"}],
  "coursework_windows": [],
  "deadlines": [{"title": "Project", "due": "2026-10-28T18:00:00-07:00", "points": 100, "weight": 3, "remaining_minutes": 60}]
}
```

`now` and `interview` are supplied by Cubbie with explicit UTC offsets, never inferred from the machine clock. Resolve the interview time before using the planner. Free windows are student-approved waking/prep availability, not the entire day merely because Calendar is empty. Supply each interval's real offset, including daylight-saving changes. All timestamps must be aware and ends later than starts. Overlapping free windows merge; busy windows with buffers and protected coursework are subtracted. Adjacent endpoints are not overlaps.

`coursework_windows` protects study time already agreed. `remaining_minutes` is additional estimated work to reserve, **excluding** work already covered by those protected windows; zero means no further reservation is needed. Estimates come from the student, not Canvas point counts. Missing effort for a deadline in the horizon blocks prep proposals until reviewed. Include future-deadline work that must happen before the interview in `coursework_windows` too.

`weight` is explicit relative planning importance (0.01–100), default 1, not a predicted grade impact. Cubbie should use known course grade weights and user priorities to propose it; raw assignment points remain context and are not compared across courses. Reserve coursework first, ranked by `weight / hours until planning boundary` (minimum one hour), then due boundary and title. Allocate its estimated time into the latest available gaps before that boundary. This is a transparent greedy heuristic; a failure can mean the heuristic needs a different allocation, not that no feasible plan exists. Show alternatives rather than moving work.

Date-only `due` values stay date-only in the source data. When a named local `timezone` is supplied (for example `America/Phoenix`), the planner can conservatively reserve work **before the beginning of that date**, explicitly labeled as a planning boundary rather than the actual due time. Without the time zone, request review. If that boundary is already past and work remains, ask the student about the actual due time; do not invent midnight or treat the task as late.

Prep kinds: `introduction` (15 min), `behavioral` (20), `company_research` (15), `role_practice` (25), `mock` (30). Weakest-area practice gets extra slots. Role practice is interpreted by Cubbie for the student's field. Blocks use the earliest fitting remaining windows with transition buffers. The bounded list is a starter plan, not a complete curriculum or optimization guarantee.

Output includes prep `blocks`, protective `coursework_reservations`, warnings and unresolved items. All are proposals. Detail lists are bounded to fit Cubbie's 8,000-character output read limit; `detail_counts` and `details_truncated` reveal omitted details. Review the original input or a document for the full coursework picture, especially when truncated; do not treat a partial list as complete. All prep proposals remain in the output. Do not automatically add coursework reservations as events. Before approved prep calendar writes, Cubbie refreshes conflicts and checks duplicates. Missing data is not authorization to overwrite commitments.

Exit 0: proposed prep blocks. Exit 2: invalid input. Exit 4: no block fits. Exit 5: unresolved coursework or effort; no prep blocks are proposed. A failed attempt may print partial protective reservations for review; they have not been booked. All scripts are independent of company and role names.
