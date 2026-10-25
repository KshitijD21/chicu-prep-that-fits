# Interview Sprint

Prepare for any company and role without letting coursework slip. Tell Cubbie your interview
date, fit prep around your commitments, then practise your own answers with measured transcript
feedback and one useful next step.

A [Cubbie Hackathon](https://hackathon.cubbie.ai) Track 1 Skill that runs inside Cubbie.
[Amazon SWE behavioral practice](references/demo_amazon.md) is an optional public-source sample;
the workflow supports other employers, roles and interview formats.

## What it does

- Proposes short prep blocks around Calendar commitments and Canvas coursework.
- Counts transcript words and filler occurrences, separates context-sensitive terms, and compares takes.
- Uses real duration for optional pace feedback and actual timestamped segments for gap observations.
- Coaches answer structure and real experience with transcript evidence, without hiring predictions.

## Install and use

Text Cubbie the GitHub link to this Skill's folder and approve the installation when prompted.
Then try "I have an interview next week" or "Can I practise my introduction?"
To update, text the branch link again; a pinned commit link stays on one version.

Connect your own Canvas and Google Calendar accounts for schedule-aware planning.
You can also paste free windows and deadlines for a tentative plan. A resume is optional.
Audio timing and saved settings depend on capabilities available in your Cubbie environment;
text practice works without them. See [capability checks](references/capability-checks.md).

## Approval and privacy

Review exact calendar changes before approving them. Reminders, recurring check-ins and calls
require separate approval. Conditional calls stay disabled until their capability checks pass;
verification does not authorize future calls. Calls are one-way reminders, with replies by text.

Resume extractions are shown for confirmation before saving. Retain only agreed preferences,
story summaries and comparison metrics; ask Cubbie to show or delete your saved Interview Sprint data.
Keep saved data outside the installed Skill folder so updates do not replace it.
Removing the Skill may leave saved files and scheduled tasks, which need separate cleanup.
Conversation history and platform backups are not guaranteed to be erased by that cleanup.

Scripts do not send interview data to other services. Cubbie uses its own media and connected-account
abilities; this is not a promise of device-only processing or fully confidential conversations.
The Skill does not complete graded work, alter Canvas submissions or apply for jobs.

## Offline examples

Python 3.9+ and the standard library are sufficient; no packages, keys or network are needed
by the scripts. Run from this folder:

```bash
python3 scripts/analyze_take.py --sample --json
python3 scripts/plan_blocks.py --sample
python3 scripts/analyze_take.py answer.txt --json
python3 scripts/analyze_take.py take-two.txt --previous take-one.json --json
```

Sample data is synthetic and never mixed with saved student data. Scripts read the specified
inputs and print results; Cubbie retrieves Calendar/Canvas data and performs approved actions.
See [measurement details](references/metrics.md), [planner inputs](references/planning.md) and
[call procedures](references/calls.md) for the relevant limits and fallbacks.
