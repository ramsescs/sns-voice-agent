# MVP Plan — SNS Triage Voice Agent (text-first core)

## Context

The repo currently holds only thesis proposals (`thesis-proposals/`), no code. We want a **small, simple MVP** that proves the project's central architectural claim and gives us something to iterate on.

The thesis's non-negotiable invariant (`core-proposal.md` §4.1) is: **the LLM never assigns the triage level.** The LLM conducts the conversation and extracts structured clinical findings; a separate **deterministic engine** maps those findings onto a SET level, and a **red-flag detector** can force emergency escalation at any time. The methodology in both proposals explicitly says to build the **SET engine and safety tools first**.

Two decisions shape this MVP:

- **Text-first, not voice.** This is the *constraint-respecting* choice, not just the easy one: `platform-decision.md` says not to lock in a platform until the decision is recorded, and the ElevenLabs credit grant is still pending. Adding STT/TTS now would force a premature vendor choice. Text-first keeps the MVP on the part the project owns regardless of platform — the SET engine, red-flag detector, and dialogue manager. Voice becomes a thin layer added later.
- **Google Gemini** drives the dialogue manager (user's choice).

**In scope:** the triage flow only. **Explicitly deferred:** the follow-up module, co-official languages, atypical/older-adult speech accessibility, and voice (STT/TTS). The architecture leaves clean seams for all of these.

## Approach

A small Python package with a **deterministic core** (the part the thesis is really about) and a **thin Gemini-driven conversation layer** around it. Control flow is owned by deterministic Python (server-orchestrated), which gives us a *genuine* red-flag bypass — stronger than the called-tool pattern in the ElevenLabs variant. Honest framing for the thesis: control flow and level assignment are deterministic; **findings extraction is still LLM-mediated** — we don't oversell the bypass as more than that.

### Proposed structure

```
sns-voice-agent/
  pyproject.toml
  src/triage/
    findings.py        # Pydantic ClinicalFindings schema — the LLM↔engine contract
    redflag.py         # deterministic red-flag detector over findings
    set_engine.py      # deterministic SET mapping → level + care channel + rationale
    dialogue.py        # Gemini dialogue manager: asks questions, extracts findings (never a level)
    orchestrator.py    # deterministic control loop: red-flag bypass → SET classify → audit
    audit.py           # per-interaction JSON audit log
    cli.py             # text chat entrypoint
    rules/
      red_flags.yaml   # open, versioned red-flag rules
      set_mapping.yaml # open, versioned discriminator→level mapping (LABELED PLACEHOLDER)
      MAPPING.md       # one-page human-readable spec + SET sourcing/provenance note
  tests/
    test_redflag.py
    test_set_engine.py
    test_vignettes.py
    vignettes.yaml         # findings → expected SET level
    red_flag_suite.yaml    # red-flag scenarios → must escalate
  README.md
```

### Key components

**1. `findings.py` — the contract.** A small Pydantic model the LLM fills in. Keep it minimal: `presenting_complaint` (enum of 3–5 complaints), `pain_score` (0–10), `bleeding` (none/minor/severe), `consciousness` (alert/drowsy/unresponsive), `breathing_difficulty` (none/mild/severe), `chest_pain` + `chest_pain_radiating` (bool), `stroke_signs_fast` (bool), `allergic_reaction_severe` (bool), `suicidal_ideation` (bool), `onset` (free text). The LLM emits **only** these fields — never a level.

**2. `redflag.py` — deterministic bypass.** Pure function `check(findings) -> RedFlagResult` driven by `rules/red_flags.yaml`. ~5 rules to start: chest pain radiating to arm/jaw; FAST stroke signs; severe breathing difficulty; severe allergic reaction (anaphylaxis); suicidal ideation. A hit returns an unambiguous "escalate to 112/emergency" with a human-readable rationale.

**3. `set_engine.py` — deterministic SET mapping.** Pure function `classify(findings) -> TriageResult` (level 1–5, care channel ∈ {self-care, primary-care appointment, urgent care, emergency/112}, rationale, uncertainty flag), driven by `rules/set_mapping.yaml`. 3–5 presenting complaints only (e.g. chest pain, breathing difficulty, fever, abdominal pain, wound). **Conservative default: under uncertainty or missing data, over-triage (route upward)** — under-triage is the dangerous error.

> **SET sourcing flag:** SET discriminator tables are an accredited (and possibly proprietary) standard and may not be freely available. For the MVP the `set_mapping.yaml` is a deliberately simplified mapping **clearly labeled as a placeholder pending real SET sourcing** in `MAPPING.md`. This does not block the MVP — but it must be labeled, not silently passed off as "SET-grounded." Sourcing the real tables is a follow-up task (thesis O1).

**4. `dialogue.py` — Gemini conversation layer.** Uses the `google-genai` SDK with function calling. Default model `gemini-2.5-flash` for cheap iteration (swap to `gemini-2.5-pro` for quality); confirm current model IDs from Gemini docs. The model is given a system prompt that constrains it to: ask short discriminator questions, refuse diagnosis/prescription/out-of-scope, and call `update_findings(...)` whenever it learns something and `finalize()` when the interview is complete. The model is **never** asked for a level.

**5. `orchestrator.py` — deterministic control loop:**
1. Emit an **AI-disclosure greeting** at call start (AI Act Art. 50 transparency — cheap, in scope from day one).
2. Each turn: read user text → dialogue manager updates findings → **deterministic `redflag.check` runs on the updated findings; a hit immediately escalates and ends the call (genuine bypass).**
3. When the model calls `finalize()`: run `set_engine.classify` → level + care channel + rationale.
4. Emit the outcome as text; write the audit record.

**6. `audit.py` — auditable rationale.** One JSON file per interaction: timestamp, full transcript, every findings update, red-flag result, final level/channel/rationale, and the **model id + rules-file version** so a decision is fully reconstructable (thesis O5 / open-reproducible safety spec).

### Open, versioned rules (commitment #2 from day one)

All safety logic lives in human-readable, versioned `rules/*.yaml` + `MAPPING.md`, not buried in Python. This embodies the "open, reproducible safety specification" commitment at near-zero extra cost and makes the engine independently rebuildable.

## Reuse / dependencies

- Greenfield repo — nothing existing to reuse; `pyproject.toml` is new.
- Dependencies: `google-genai` (Gemini + function calling), `pydantic` (findings schema), `pyyaml` (rules), `pytest` (tests). Keep it to these.
- Env: `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) read from environment; document in `README.md`.

## Verification (end-to-end)

The deterministic core is fully testable without the LLM — that's the point of the separation.

- **Unit tests** (`pytest`): `test_set_engine.py` and `test_redflag.py` assert each rule, table-driven from the YAML.
- **Red-flag suite** (`red_flag_suite.yaml` → `test_vignettes.py`): every red-flag scenario must escalate — **target 100% recall** (the thesis's headline safety guarantee).
- **Vignette set** (`vignettes.yaml`): findings → expected SET level; asserts classification matches. This tiny eval set is **not throwaway** — it seeds the thesis's stratified under-triage benchmark.
- **Manual smoke test**: run `python -m triage.cli`, then
  - type a "chest pain radiating to my left arm" scenario → expect **immediate escalation to 112** with rationale (bypass fired);
  - type a "mild sore throat, no fever" scenario → expect a **primary-care / self-care** recommendation;
  - confirm an **audit JSON** was written for each call.

## Out of scope (deferred, with seams left in place)

- **Follow-up module** — the orchestrator and audit log are reusable when we add it.
- **Voice (STT/TTS)** — swap the CLI's `input()`/`print()` for an STT/TTS adapter; the orchestrator is unchanged.
- **Co-official languages, atypical/older-adult speech accessibility** — the deterministic core is language-agnostic; these slot in at the dialogue/STT layer later.
- **Real SET discriminator tables** — replace the placeholder `set_mapping.yaml`; the engine interface stays the same.
