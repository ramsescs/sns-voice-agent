# 003 — SET engine (deterministic level mapping)

**Type:** AFK

## Source plan

`MVP_PLAN.md`

## What to build

The deterministic classifier that maps structured findings onto a SET level —
the component the thesis is really about. Pure function
`classify(findings) -> TriageResult`, driven by an open, versioned
`rules/set_mapping.yaml`, with the conservative over-triage default baked in.

- `src/triage/set_engine.py` — `classify(findings: ClinicalFindings) -> TriageResult`
  where `TriageResult` carries: level (1–5), care channel
  ∈ {self-care, primary-care appointment, urgent care, emergency/112},
  rationale, and an uncertainty flag. Rules loaded from YAML.
- `src/triage/rules/set_mapping.yaml` — discriminator→level mapping for 3–5
  presenting complaints (e.g. chest pain, breathing difficulty, fever,
  abdominal pain, wound). Versioned.
- `src/triage/rules/MAPPING.md` — one-page human-readable spec **clearly labeling
  the mapping as a placeholder pending real SET sourcing** (thesis O1), with the
  SET provenance note. This labeling is part of acceptance, not optional.
- `tests/vignettes.yaml` — findings → expected SET level (seeds the thesis's
  stratified under-triage benchmark; not throwaway).
- `tests/test_set_engine.py` — table-driven over the mapping and vignettes.

**Conservative default:** under uncertainty or missing data, route **upward**
(over-triage) — under-triage is the dangerous error.

## Acceptance criteria

- [ ] `classify()` is a pure function over `ClinicalFindings` (no I/O, no LLM).
- [ ] Mapping lives in `rules/set_mapping.yaml`, not in Python; file is versioned.
- [ ] `TriageResult` includes level, care channel, rationale, and uncertainty flag.
- [ ] Every vignette in `tests/vignettes.yaml` classifies to its expected level.
- [ ] Missing/ambiguous findings produce an **upward** (more urgent) level and set
      the uncertainty flag — verified by a dedicated test.
- [ ] `rules/MAPPING.md` exists and **explicitly labels the mapping a placeholder**
      pending real SET sourcing, with a provenance note.

## How to test independently

```
pytest tests/test_set_engine.py
```

Asserts vignette classifications match expected SET levels and that
missing-data cases over-triage. Runs with no API key and depends only on
slice 001's findings schema.

## Blocked by

- Blocked by `issues/001-scaffold-and-findings.md` (needs `ClinicalFindings`).

## Plan sections covered

- "Key components → 3. `set_engine.py` — deterministic SET mapping" (incl. the
  SET sourcing flag / placeholder labeling)
- "Open, versioned rules (commitment #2 from day one)" (`rules/set_mapping.yaml`,
  `MAPPING.md`)
- "Verification → Vignette set" (`vignettes.yaml`)
