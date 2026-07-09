# Thesis proposals

`core-proposal.md` is the canonical, platform-agnostic proposal: a voice agent for SNS triage and follow-up described in terms of capabilities (STT, LLM dialogue manager, deterministic SET triage engine, TTS, telephony) rather than a specific vendor. It is the document to read first and the one to keep up to date as the design evolves.

`platform-options/` holds proposal variants that pin the architecture to a specific hosted platform. These are explorations of *how the core proposal's architecture maps onto a given platform*, not separate theses — the five thesis commitments (SET-grounding, open safety spec, accessibility-stratified evaluation, atypical/older-adult speech support, co-official-language support) and the safety invariant (LLM never assigns the triage level; a deterministic engine does, with red-flag bypass) must hold in every variant.

- `platform-options/elevenlabs.md` — builds the agent natively on the ElevenLabs Agents Platform (platform owns STT/TTS/turn-taking/orchestration; the project owns the SET engine and red-flag check as server-side tools). Adoption is contingent on ElevenLabs granting the requested platform credit grant — see `platform-decision.md` for current status.

If credits are not granted, or a different platform fits better, add a new file under `platform-options/` for that platform rather than rewriting `core-proposal.md`. The core proposal should only change if the SNS-facing design itself changes, not because of a vendor choice.
