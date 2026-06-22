# 001 — Project scaffold + findings contract

**Type:** AFK

## Source plan

`MVP_PLAN.md`

## What to build

Bootstrap the Python package and ship the `ClinicalFindings` contract that every
other slice depends on. This is the foundation: after this slice the project
installs, runs `pytest`, and exposes the single Pydantic model the LLM fills in
and the deterministic engines consume.

- `pyproject.toml` declaring the `triage` package and the pinned dependencies
  (`google-genai`, `pydantic`, `pyyaml`, `pytest`) — nothing else.
- `src/triage/` package skeleton (`__init__.py`, empty module stubs are fine as
  long as they don't break import).
- `src/triage/findings.py` — the minimal `ClinicalFindings` Pydantic model
  exactly as enumerated in the plan: `presenting_complaint` (enum of 3–5),
  `pain_score` (0–10), `bleeding`, `consciousness`, `breathing_difficulty`,
  `chest_pain` + `chest_pain_radiating`, `stroke_signs_fast`,
  `allergic_reaction_severe`, `suicidal_ideation`, `onset` (free text).
- `GEMINI_API_KEY` / `GOOGLE_API_KEY` env handling documented in `README.md`
  (no key needed to install or run this slice's tests).

**Critical invariant:** the schema has **no triage-level field**. The LLM emits
only these findings; it never expresses a level.

## Acceptance criteria

- [ ] `pip install -e .` succeeds in a clean environment.
- [ ] `import triage` and `from triage.findings import ClinicalFindings` work.
- [ ] `ClinicalFindings` accepts a fully-specified valid set of findings.
- [ ] Invalid input is rejected: out-of-range `pain_score`, unknown
      `presenting_complaint`, wrong enum values for bleeding/consciousness/breathing.
- [ ] The model exposes **no** triage-level / SET-level field (asserted in a test).
- [ ] Fields that the LLM may not yet know are optional/defaultable so a
      partial interview is representable.
- [ ] `README.md` documents the env var(s) and how to install + run tests.

## How to test independently

```
pip install -e .
pytest tests/test_findings.py
```

The test suite validates good input round-trips, bad input raises
`ValidationError`, and that there is no level field on the model. No API key and
no other slice are required.

## Blocked by

None — can start immediately.

## Plan sections covered

- "Approach → Proposed structure" (`pyproject.toml`, `src/triage/` skeleton)
- "Key components → 1. `findings.py` — the contract"
- "Reuse / dependencies" (dependency set, `GEMINI_API_KEY`/`GOOGLE_API_KEY` env)
