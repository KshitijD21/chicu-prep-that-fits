# Chicu - Prep That Fits

**Interview prep that fits around your classes, not on top of them.**

*CHICU = College Helper for Intelligent Career Uplift.* It is a Cubbie Skill that helps students prepare for interviews without letting coursework slip. Technical id: `interview-sprint`.

A [Cubbie Hackathon](https://hackathon.cubbie.ai/) Track 1 Skill that runs inside Cubbie on iMessage.

## The problem

Interview prep competes with assignments and exams. Most students don't know what to practise, can't fit it around classes, and rehearse alone with vague feedback.

## What Chicu does

- **Plans around your real week.** Tell Cubbie your interview date. It proposes short prep blocks around your Calendar and Canvas deadlines, and protects your coursework.
- **Coaches your own answers.** Send a voice note or paste an answer. You get one strength, one fix and real counts from your transcript (words and filler words), then a second take and a comparison.
- **Uses your evidence.** An optional resume helps match likely questions to your real projects. Gaps are named honestly, and nothing is invented.
- **Works for any company and role.** Process research uses public sources and cites them. Practice questions are labelled as practice, never as real employer questions.

## Try it

1. Text Cubbie [this Skill link](https://github.com/KshitijD21/chicu-prep-that-fits/tree/test-1) and approve the install when prompted.
2. Text: "I have an interview next week" or "Can I practise my introduction?"
3. Answer up to three quick questions, review the proposed plan, and approve only what you want added to your calendar.

To update, text the link again.

## Requirements

- A Cubbie account.
- Optional: connect your own Canvas and Google Calendar for schedule-aware planning. Without them you can paste your free windows and deadlines for a tentative plan.
- Optional: a resume.
- Voice-note timing (pace) and saved settings depend on capabilities in your Cubbie environment. Text practice works without them.

## Approval and privacy

- Calendar changes are shown first and added only after you approve.
- Reminders, recurring check-ins and calls need separate approval. Conditional calls are off until their capability checks pass. Calls are one-way spoken reminders, with replies by text.
- Resume extractions are shown for confirmation before saving. Only agreed preferences, story summaries and comparison numbers are kept, and you can ask Cubbie to show or delete your saved Interview Sprint data.
- The scripts make no network calls and need no keys. Cubbie's own abilities handle media and connected accounts, so this is not a promise of device-only processing or full confidentiality.
- Chicu does not do graded work, change Canvas submissions or apply for jobs.

## What is measured, and what is not

Counts come from the transcript: words, filler words, repeated openings, and the change between takes. Words per minute need a real recording duration, and pauses need real timestamps; otherwise they are left out. Chicu does not judge tone, emotion or confidence, and it makes no hiring predictions. Pace bands are suggestions only.

## Repository layout

- `SKILL.md`: the instructions Cubbie follows.
- `scripts/`: `analyze_take.py` (transcript counts) and `plan_blocks.py` (proposed prep blocks). Standard library only.
- `references/`: detail Cubbie opens only when needed ([metrics](references/metrics.md), [planning](references/planning.md), [calls](references/calls.md), [capability checks](references/capability-checks.md), [demo sample](references/demo_amazon.md)).
- `assets/`: synthetic sample data.

## Run the scripts locally


Python 3.9+ and the standard library are enough.

```bash
python3 scripts/analyze_take.py --sample --json
python3 scripts/plan_blocks.py --sample
python3 scripts/analyze_take.py answer.txt --json
python3 scripts/analyze_take.py take-two.txt --previous take-one.json --json
```

Sample data is synthetic and never mixed with a student's data.

## Sample

An optional public-source sample for Amazon software engineering behavioral practice is in [references/demo_amazon.md](references/demo_amazon.md). The workflow supports other employers, roles and interview formats.
