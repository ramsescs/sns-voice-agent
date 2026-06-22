# Platform decision status

**Status (2026-06-20): pending.** Implementation platform is not yet chosen.

## Context

The core proposal (`core-proposal.md`) is written platform-agnostically: STT, an LLM dialogue manager, a deterministic SET triage/red-flag engine, and TTS, without committing to a vendor. `platform-options/elevenlabs.md` is a fully worked-out variant of that architecture on the ElevenLabs Agents Platform.

ElevenLabs adoption depends on a platform credit grant requested from ElevenLabs, which has not yet been approved.

## Decision rule

- **If the ElevenLabs credit grant is approved:** proceed with `platform-options/elevenlabs.md` as the implementation basis, since it is already fully specified.
- **If it is not approved (or approved too late / with insufficient credit):** fall back to a self-hosted or alternative-vendor implementation of the same core architecture (open/self-hosted STT+TTS, or another hosted voice-agent platform with comparable tool-calling and telephony support). Add a new file under `platform-options/` documenting that variant before writing any code.

Either path must preserve the architectural invariant in `core-proposal.md` Section 4.1: the LLM/dialogue layer never assigns the SET triage level; a separate deterministic component does, and a red-flag detector can bypass the conversational flow to force escalation.

## Update this file

Update the status line above as soon as ElevenLabs responds, and record the date and outcome. Once a platform is chosen, note it here and treat that choice as fixed for the remainder of the implementation phase unless something forces a change.
