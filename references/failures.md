# Failure replies and recovery

Read only the relevant case. Give one short actionable reply, then use the available fallback.
Never invent a count, source, date, successful write or scheduled action to cover a failure.

## Accounts and sources

- Google unavailable: "I can't read your calendar here. Send your free windows, or reconnect
  Google; I'll keep the plan tentative."
- Canvas missing, stale or partial: "Based on your latest Canvas sync, I may be missing work.
  Send any heavy deadlines before we place prep blocks."
- No assignments returned: "No assignments showed up for that range. Does that match your week?"
  Do not interpret an empty response as proof of no coursework.
- Resume unreadable: "I couldn't read that resume. Paste one project and your role; we can practise."
- No public process information: "I couldn't confirm that format publicly. I'll use general
  practice for your role."

## Measurements and script exits

- No duration or timestamps: "I can count words and fillers in this transcript. Pace and pauses
  need timing data I don't have." Use counts-only feedback; timing is unavailable, not zero.
- Exit 2, either script: invalid arguments, unreadable file or malformed input. Read the short
  stderr error and correct once if source data supports it; otherwise ask for the missing input.
- Analyzer exit 3: empty transcript. Ask for a pasted answer or another voice note.
- Planner exit 4: no prep space. Offer a shorter drill or another day without moving commitments.
- Planner exit 5: unresolved coursework/effort. Show the conflict or missing estimate before prep.
- Unexpected failure: "The measurement didn't run. I can still review your answer, but I won't
  claim counts until it works."

## Calendar and schedules

On partial calendar failure, read back existing events before retrying. Refresh conflicts and
check duplicates; a changed proposal requires fresh approval. If durable event IDs are unavailable,
re-query Calendar rather than assuming nothing was added.

For an unanswered call, take no additional action unless an approved check-in explicitly permits
it. A permitted follow-up can say "The call wasn't answered. Reply by text when you're ready."
Use calls.md for cancellation and unsupported-call fallbacks.
