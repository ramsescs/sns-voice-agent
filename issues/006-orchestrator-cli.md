# 006 — Orchestrator + CLI (end-to-end triage flow)

**Type:** HITL — automated integration is AFK; the final acceptance is a manual
live smoke test that needs a human and a real `GEMINI_API_KEY`.

## Source plan

`MVP_PLAN.md`

## What to build

The deterministic control loop that ties the core together, plus the text CLI
entrypoint — the first runnable end-to-end triage flow. This is where the
**genuine red-flag bypass** lives: control flow and level assignment are
deterministic Python; only findings extraction is LLM-mediated.

- `src/triage/orchestrator.py` implementing the plan's loop:
  1. Emit an **AI-disclosure greeting** at call start (AI Act Art. 50).
  2. Each turn: read user text → `dialogue` updates findings →
     **`redflag.check` runs on the updated findings; a hit immediately escalates
     and ends the call** (genuine bypass).
  3. On `finalize()`: run `set_engine.classify` → level + channel + rationale.
  4. Emit the outcome as text; write the audit record via `audit.py`.
- `src/triage/cli.py` — text chat entrypoint (`python -m triage.cli`) wrapping the
  orchestrator with `input()`/`print()` (the seam voice/STT-TTS replaces later).

## Acceptance criteria

- [ ] Orchestrator emits the AI-disclosure greeting before the first question.
- [ ] After each findings update, `redflag.check` runs; a hit escalates to 112 and
      **ends the call immediately**, before any further questions or `finalize`.
- [ ] On `finalize()` with no red flag, `set_engine.classify` produces the level,
      care channel, and rationale, emitted as text.
- [ ] Every interaction writes an audit JSON (via slice 004) recording transcript,
      findings updates, red-flag result, final outcome, model id, and rules version.
- [ ] `python -m triage.cli` runs an interactive text session end to end.
- [ ] Automated integration test passes with a **mocked dialogue** (deterministic):
      a red-flag path ends the call with escalation; a non-red-flag path reaches a
      SET classification; an audit file is written in both cases.

## How to test independently

Automated (AFK, no API key):

```
pytest tests/test_orchestrator.py
```

Drives findings through the loop with a mocked dialogue and asserts: red-flag
bypass fires and ends the call, non-red-flag path reaches a SET level, and an
audit JSON is written each time.

Manual live smoke test (HITL, needs `GEMINI_API_KEY`):

```
python -m triage.cli
```

- "chest pain radiating to my left arm" → **immediate escalation to 112** with
  rationale (bypass fired);
- "mild sore throat, no fever" → **primary-care / self-care** recommendation;
- confirm an **audit JSON** was written for each call.

## Blocked by

- Blocked by `issues/002-redflag-detector.md`
- Blocked by `issues/003-set-engine.md`
- Blocked by `issues/004-audit-log.md`
- Blocked by `issues/005-dialogue-manager.md`

(Transitively requires `issues/001-scaffold-and-findings.md`.)

## Plan sections covered

- "Key components → 5. `orchestrator.py` — deterministic control loop"
- "Approach → Proposed structure" (`cli.py`)
- "Verification → Manual smoke test"
- "Out of scope" → orchestrator/CLI are the seams for voice (STT/TTS) and the
  follow-up module
