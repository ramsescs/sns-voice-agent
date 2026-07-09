# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repository currently contains only planning documents for a bachelor's thesis (TFG) — there is no application code, build system, package manifest, or test suite yet. There are no build/lint/test commands to run.

## What this project is

A proposed voice-agent system that performs **triage** and **post-contact follow-up** for patients of the Spanish public health system (Sistema Nacional de Salud, SNS). The full design rationale lives in `thesis-proposals/` (see `thesis-proposals/README.md` for how the files there relate):

- `thesis-proposals/core-proposal.md` — the canonical, **platform-agnostic** proposal: STT → LLM dialogue manager → deterministic SET triage engine → TTS, described by capability rather than vendor. Read this first; it is the source of truth for the thesis commitments and the safety architecture.
- `thesis-proposals/platform-options/elevenlabs.md` — a fully worked-out variant that builds the same agent **natively on the ElevenLabs Agents Platform** (platform owns STT/TTS/turn-taking/orchestration; the project owns only the SET engine and red-flag check as server-side tools the agent calls). Adoption is **contingent on an ElevenLabs platform credit grant that has not yet been approved** — see `thesis-proposals/platform-decision.md` for current status and the fallback rule if it isn't.
- Additional files may be added under `thesis-proposals/platform-options/` for other vendors/self-hosted setups if ElevenLabs doesn't pan out. Do not pick or hardcode a platform in code or docs outside `platform-options/` until `platform-decision.md` records a final decision.

All proposal variants share the same five thesis commitments, which should inform any future implementation decisions:

1. **SET-grounding** — prioritisation logic is anchored on the *Sistema Español de Triaje* (SET), the SNS's accredited five-level triage standard (Manchester Triage System is a comparator only, not the basis).
2. **Open, reproducible safety specification** — the deterministic safety layer (SET discriminator mapping, escalation rules, rationale) must be specified openly enough to be independently rebuilt, unlike closed commercial pipelines.
3. **Under-triage benchmark stratified by accessibility** — the primary safety metric (under-triage rate) is always reported broken down by speech profile, age, and language, never only as an aggregate.
4. **Accessibility for atypical and older-adult speech** — these ASR-degradation-prone populations are a first-class design/evaluation target; degradation must route toward escalation, never toward a silent misclassification.
5. **Co-official-language support** — Spanish plus at least one co-official language (catalán, euskera, or gallego), including intra-call code-switching.

## Architectural invariant (applies regardless of which platform is eventually chosen)

The LLM/dialogue layer never assigns the triage level itself. A separate deterministic component maps structured clinical findings onto SET levels, and a red-flag detector can bypass the conversational flow at any time to force emergency escalation. Any future implementation should preserve this separation between conversational intelligence and clinical safety logic, since it is the basis for the auditability and regulatory claims made in both proposals (EU AI Act high-risk classification, MDR SaMD, GDPR/LOPDGDD for health data).

No real or identifiable patient data is used anywhere in this project — only synthetic vignettes and public speech corpora (e.g. TORGO for atypical speech).
