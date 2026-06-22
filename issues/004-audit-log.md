# 004 — Audit log (auditable rationale)

**Type:** AFK

## Source plan

`MVP_PLAN.md`

## What to build

A small, reusable audit writer: one JSON file per interaction capturing
everything needed to fully reconstruct a decision (thesis O5 / open-reproducible
safety spec). It accepts structured records and is testable on its own with
synthetic data — it does not need the engines or the LLM to exist.

- `src/triage/audit.py` — a function/class that takes a completed interaction
  record and writes one JSON file. Record fields (per the plan): timestamp, full
  transcript, every findings update, the red-flag result, the final
  level/channel/rationale, **and the model id + rules-file version(s)**.
- The writer accepts generic structured input (dicts / serialisable objects) so
  it can be built and tested before slices 002/003 exist; the orchestrator
  (slice 006) wires in the real `RedFlagResult` / `TriageResult`.

## Acceptance criteria

- [ ] Writing an interaction produces exactly one JSON file per interaction.
- [ ] The JSON contains: timestamp, full transcript, all findings updates,
      red-flag result, final level + care channel + rationale.
- [ ] The JSON records the **model id** and the **rules-file version(s)** so a
      decision is reconstructable.
- [ ] The file round-trips: it can be re-read and parsed back into the same data.
- [ ] No personally identifiable data assumptions — works with synthetic
      vignette content only.

## How to test independently

```
pytest tests/test_audit.py
```

Build a synthetic interaction record, write it, then assert the resulting JSON
file exists and contains every required field (including model id + rules
version) and reloads cleanly. No API key, no other slice beyond 001 required.

## Blocked by

- Blocked by `issues/001-scaffold-and-findings.md` (package scaffold).

## Plan sections covered

- "Key components → 6. `audit.py` — auditable rationale"
- "Out of scope" → audit log is a reuse seam for the deferred follow-up module
