# 002 — Red-flag detector (deterministic bypass)

**Type:** AFK

## Source plan

`MVP_PLAN.md`

## What to build

The deterministic safety bypass: a pure function `check(findings) -> RedFlagResult`
driven by an open, versioned `rules/red_flags.yaml`. A hit returns an unambiguous
"escalate to 112/emergency" with a human-readable rationale. This is the thesis's
headline safety guarantee and must be fully testable without the LLM.

- `src/triage/redflag.py` — `check(findings: ClinicalFindings) -> RedFlagResult`,
  rules loaded from YAML (not hardcoded in Python).
- `src/triage/rules/red_flags.yaml` — ~5 rules to start: chest pain radiating to
  arm/jaw; FAST stroke signs; severe breathing difficulty; severe allergic
  reaction (anaphylaxis); suicidal ideation. The file is versioned (carries a
  version/identifier the audit log can record).
- `tests/red_flag_suite.yaml` — red-flag scenarios (findings → must-escalate).
- `tests/test_redflag.py` — table-driven over both YAMLs.

`RedFlagResult` should carry at least: whether it fired, which rule, and the
rationale string.

## Acceptance criteria

- [ ] `check()` is a pure function over `ClinicalFindings` (no I/O, no LLM).
- [ ] All ~5 rules live in `rules/red_flags.yaml`, not in Python.
- [ ] Each rule has a unit test asserting it fires on a matching findings set
      and does not fire on a clearly non-matching one.
- [ ] Every scenario in `tests/red_flag_suite.yaml` escalates — **100% recall**.
- [ ] A red-flag hit returns an unambiguous emergency/112 outcome plus a
      human-readable rationale.
- [ ] `red_flags.yaml` carries a version identifier (so the audit log, slice 004,
      can record which rules version produced a decision).

## How to test independently

```
pytest tests/test_redflag.py
```

Table-driven from `rules/red_flags.yaml` and `tests/red_flag_suite.yaml`; the
suite must pass with **100% recall** on red-flag scenarios. Runs with no API key
and depends only on slice 001's findings schema.

## Blocked by

- Blocked by `issues/001-scaffold-and-findings.md` (needs `ClinicalFindings`).

## Plan sections covered

- "Key components → 2. `redflag.py` — deterministic bypass"
- "Open, versioned rules (commitment #2 from day one)" (`rules/red_flags.yaml`)
- "Verification → Red-flag suite" (`red_flag_suite.yaml`, target 100% recall)
