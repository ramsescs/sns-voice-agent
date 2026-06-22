# 005 — Dialogue manager (Gemini conversation layer)

**Type:** AFK

## Source plan

`MVP_PLAN.md`

## What to build

The thin LLM layer that conducts the interview and extracts structured findings —
**never a level**. Uses the `google-genai` SDK with function calling. Built so it
is unit-testable with a mocked client (no live API key needed to verify the
wiring); live-model behaviour is validated in slice 006's smoke test.

- `src/triage/dialogue.py` — wraps a `google-genai` client with:
  - a system prompt constraining the model to ask short discriminator questions,
    refuse diagnosis/prescription/out-of-scope, and stay in scope;
  - two tools the model can call: `update_findings(...)` (whenever it learns
    something) and `finalize()` (when the interview is complete);
  - translation of a model `update_findings` tool call into a validated
    `ClinicalFindings` update, and recognition of `finalize()`.
- Default model `gemini-2.5-flash` (swappable to `gemini-2.5-pro`); **confirm
  current model IDs from Gemini docs** before finalising.
- The model is **never** asked for, and the layer never emits, a triage level.

## Acceptance criteria

- [ ] `dialogue.py` exposes the conversation step(s) the orchestrator will drive.
- [ ] System prompt constrains the model to discriminator questions and refuses
      diagnosis / prescription / out-of-scope requests.
- [ ] `update_findings` and `finalize` are registered as function-calling tools.
- [ ] A mocked-client test: an `update_findings` tool call is parsed into a valid
      `ClinicalFindings` update; an invalid payload is rejected.
- [ ] A mocked-client test confirms `finalize()` is detected and surfaced to the
      caller.
- [ ] No code path produces a triage level from the LLM (asserted in a test).
- [ ] The model id in use is exposed so the audit log (slice 004) can record it.

## How to test independently

```
pytest tests/test_dialogue.py
```

Uses a **mocked `google-genai` client** so no API key is needed: assert that a
simulated tool call becomes a `ClinicalFindings` update, that `finalize()` is
recognised, and that no level is ever emitted. Depends only on slice 001.

## Blocked by

- Blocked by `issues/001-scaffold-and-findings.md` (needs `ClinicalFindings`).

## Plan sections covered

- "Key components → 4. `dialogue.py` — Gemini conversation layer"
- "Reuse / dependencies" (`google-genai`, model IDs)
