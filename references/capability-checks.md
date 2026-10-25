# Check optional capabilities when needed

Check capabilities in the student's own Cubbie environment before relying on them.
Use observed results rather than a statement that a feature should work.
Present one check at a time and continue with the available fallback.

## Connected accounts

Check whether Canvas and Google are linked before reading them. Confirm the relevant calendar
range and available coursework data; a connection does not guarantee a complete or current sync.
If missing, ask for free windows and deadlines and label the resulting plan tentative.

## Audio metadata

For the student's own short voice note, ask for its actual recording duration and whether real
word or segment timestamps are available. Request metadata or a small example, not an estimate.
A readable audio file alone does not prove timing metadata is available.

Before passing timing to the analyzer, read metrics.md. Verify that supplied segments cover
the same transcript in order and fit within the recording. A duration supplied directly by
Cubbie's media ability can be passed as a scalar even if the audio file is inaccessible.
If timing is unavailable, report transcript counts without pace or pause measurements.

## Saved settings

Before depending on a saved preference or file in a later conversation, confirm that it can
actually be recovered there. Same-chat readback does not establish cross-conversation durability.
Follow saved-data.md; if unavailable, use conversation-local information or ask again.

## Calls

Follow calls.md before offering a call. Conditional calls remain disabled until a real test
verifies condition lookup, execution, completion suppression and cancellation.
A capability test never grants permission for later reminders or calls.
