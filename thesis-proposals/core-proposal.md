# Bachelor's Thesis Proposal

## Voice-Agent and LLM-Based Triage and Follow-up System for Patients of the Spanish Public Health System (Sistema Nacional de Salud)

---

## 1. Introduction

The Spanish public health system (Sistema Nacional de Salud, SNS) operates under severe and growing demand pressure. The SNS handles close to 400 million primary-care consultations and around 35 million emergency-department (ED) visits per year, and a substantial fraction of those contacts are either non-urgent cases that could be resolved at a lower level of care or, conversely, urgent cases that arrive late because the patient did not know where to go. Both failure modes degrade outcomes and waste scarce clinical time. At the same time, the *Consejo Interterritorial del SNS* approved a **National Artificial Intelligence Strategy for the SNS in November 2025**, explicitly endorsing AI to support patient triage and resource allocation while insisting that the final clinical decision remains with the professional. This thesis proposes a system that sits squarely inside that policy direction.

The proposed system is a **conversational voice agent**, driven by a Large Language Model (LLM), that performs two coordinated functions for SNS patients:

1. **Triage / symptom intake** — the patient describes their symptoms in natural spoken language; the agent conducts a structured clinical interview, maps the responses onto a recognised triage protocol, and produces a prioritisation and a care-channel recommendation (self-care, primary care appointment, urgent care, or emergency / 112).
2. **Post-contact follow-up** — after a consultation, discharge, or procedure, the agent proactively calls or is called by the patient to monitor recovery, check medication adherence, detect warning signs (red flags), and escalate to a human professional when needed.

The central thesis is that a *human-in-the-loop* voice agent can safely absorb a large volume of low-complexity triage and follow-up interactions, improving access and freeing clinical staff, **provided** that it is engineered with explicit clinical safety rails, regulatory compliance, and rigorous evaluation.

This work is deliberately centred on five commitments that, taken together, distinguish it from existing commercial systems and define its contribution:

1. **SET-grounding.** The prioritisation logic is anchored explicitly on the *Sistema Español de Triaje* (SET), the accredited five-level standard of the SNS, rather than on a proprietary or protocol-agnostic engine.
2. **Open and reproducible safety specification.** The deterministic safety layer — its SET discriminator mapping, escalation rules, and decision rationale — is specified openly and in enough detail to be independently rebuilt and challenged, in contrast to the certified-but-closed pipelines of commercial vendors.
3. **Under-triage benchmark stratified by accessibility.** Safety is measured primarily by *under-triage rate*, reported not as a single aggregate but broken down by speech profile, age, and language, so that the metric reflects the populations most at risk of failure.
4. **Support for people with speech disabilities and older adults.** These populations — for whom automatic speech recognition (ASR) degrades most — are treated as a primary design and evaluation target rather than an assumed beneficiary of "voice".
5. **Support for Spain's co-official languages.** The system is designed and evaluated for Spanish and at least one co-official language (catalán, euskera, or gallego), including realistic mid-call code-switching.

These five points recur throughout the document and are the axes against which the design (Section 4), the evaluation (Sections 6–7), and the contributions (Section 12) are organised.

This document follows the structure required by the TFG rubric. The **Regulatory Framework** (Section 8) develops the applicable legislation, technical standards, and privacy/security analysis. The **Socio-economic Environment and SDGs** (Section 9) and the **Budget** (Section 10) are presented as dedicated sections, as recommended by the evaluation guidelines.

### 1.1 Motivation

Three converging factors make this an appropriate and timely TFG:

- **Clinical need:** ED overcrowding and primary-care waiting lists are persistent structural problems in the SNS. Telephone triage already exists (e.g. autonomic-community health lines and 112/061), but it is staffed by nurses whose time is the bottleneck.
- **Technical maturity:** modern speech-to-text (STT), text-to-speech (TTS), and instruction-tuned LLMs now make natural, low-latency spoken dialogue feasible, including in Spanish and co-official languages.
- **Policy alignment:** the 2025 SNS AI Strategy provides an institutional mandate, and the EU AI Act provides the compliance scaffolding (see Section 8).

### 1.2 Scope and boundaries

The system **assists** triage; it does not replace the clinical professional, and it never issues a definitive diagnosis. Two boundaries are fixed from the outset and treated as non-negotiable design constraints:

- Any output that prioritises or routes a patient is a *recommendation* that is either acted on by a professional or governed by conservative, pre-approved escalation rules.
- Detection of any emergency red flag (e.g. chest pain with radiation, signs of stroke, anaphylaxis, suicidal ideation) immediately bypasses the LLM dialogue and routes the patient to emergency services (112).
- Accessibility is a design constraint, not an afterthought: the system must degrade *safely* (toward escalation, never toward silent misclassification) when ASR confidence drops, which is the predictable failure mode for atypical speech and older-adult voices.
- Linguistic scope is fixed as Spanish plus at least one co-official language; the system must handle code-switching within a single call rather than assuming a single language per patient.

---

## 2. Objectives

### 2.1 General objective

To design, implement, and evaluate a prototype voice-agent system, based on LLMs and a recognised clinical triage protocol, that performs symptom-based triage and post-contact follow-up for SNS patients in a safe, auditable, and regulation-compliant manner.

### 2.2 Specific objectives

1. **O1 — Requirements & SET grounding.** Analyse the triage requirements of the SNS context and adapt the *Sistema Español de Triaje* (SET) as the explicit reference standard for the agent's prioritisation logic, mapping its discriminators into a machine-executable specification. (MTS is considered only as a comparator; SET is the grounding standard.)
2. **O2 — Conversational architecture.** Design a modular voice-agent architecture integrating STT, an LLM dialogue manager, and TTS, with a deterministic clinical-safety layer separate from the LLM.
3. **O3 — Triage module.** Implement the structured symptom-intake interview and a mapping from the dialogue to a SET level and care-channel recommendation, with explicit red-flag detection.
4. **O4 — Follow-up module.** Implement the post-contact follow-up workflow (recovery monitoring, adherence checks, escalation), including scheduling and a patient record of each interaction.
5. **O5 — Open, reproducible safety & explainability layer.** Implement the deterministic safety layer (red-flag bypass, refusal of out-of-scope requests, uncertainty/low-ASR-confidence handling) and produce, for each interaction, an auditable, human-readable rationale. The layer's discriminator mapping, rules, and rationale format are specified openly so the result can be independently reproduced.
6. **O6 — Accessibility-stratified evaluation.** Evaluate the prototype on clinical vignettes / simulated patients against a SET reference standard, with **under-triage rate as the primary safety metric, reported stratified by speech profile (typical / mild / severe atypical speech, older-adult speech) and by language**, alongside safety, latency, and usability.
7. **O7 — Accessibility for speech disabilities and older adults.** Treat atypical-speech and older-adult users as a first-class design target: characterise where ASR degrades, and implement a confidence-aware response strategy (confirmation, repair, escalation) so degradation routes toward safety rather than misclassification.
8. **O8 — Co-official-language support.** Design and evaluate the system for Spanish and at least one co-official language, including handling of intra-call code-switching, and document the resource and performance gaps encountered.
9. **O9 — Regulatory & socio-economic analysis.** Produce the regulatory-framework analysis (EU AI Act, MDR, GDPR/LOPDGDD, plus the accessibility obligations of Ley 11/2023 and EN 301 549) and the socio-economic/SDG and budget analysis.

Each objective maps to a measurable verification criterion in Section 7 to support the rubric's "objectives are met and verified" requirement.

---

## 3. State of the Art

The proposal sits at the intersection of three areas:

**Clinical triage protocols.** The *Sistema Español de Triaje* (SET, derived from the Andorran MAT) is the accredited five-level triage standard of the SNS and is adopted here as the grounding protocol; the Manchester Triage System (MTS) is the other dominant five-level standard and is used only as a comparator. These protocols define discriminators that assign each patient to one of five priority levels with associated maximum waiting times, giving the project a validated, auditable reference logic rather than a black box. Grounding specifically on SET — rather than on a proprietary engine or a protocol-agnostic, client-configured workflow as commercial systems use — is one of the five defining commitments of this work.

**AI-assisted triage.** Recent literature (e.g. work indexed in *Medicina Clínica* and nursing reviews, 2024–2025) reports that AI can improve triage precision and reduce time and documentation burden, while consistently emphasising that AI must remain a support tool subordinate to nursing/medical judgement. Most existing work uses structured data or text; spoken natural-language intake by patients themselves is comparatively under-explored.

**Conversational and voice agents in health.** Text-based symptom checkers (e.g. Ada, Mediktor) exist commercially but raise documented concerns about under-triage and safety, and the app/text modality itself excludes low-literacy and some disabled users. A more directly comparable group of *voice-first clinical* agents has emerged: Tucuvi (LOLA), a Madrid-based, Class IIb-certified voice agent spanning triage and follow-up and deployed in SNS hospitals; Infermedica, whose certified Conversational Triage combines an LLM with a Bayesian medical knowledge base; Hippocratic AI, a follow-up-focused "constellation" of proprietary models; and Corti, a European decision-support system that detects critical conditions on emergency calls. A key, honest observation frames this proposal: the credible clinical players have **converged on a hybrid architecture** — an LLM for conversation wrapped around a non-probabilistic core (Bayesian engine, decision trees, or rule sets) for the actual decision. Separating the safety layer from the LLM is therefore no longer, by itself, the novelty.

What these systems do **not** offer — and where this work is positioned — is the intersection of the five commitments in Section 1: explicit **SET-grounding** (the commercial engines are proprietary or protocol-agnostic), an **open and reproducible** specification of the safety layer (theirs are certified but closed), an **under-triage benchmark stratified by accessibility** (none publish error rates broken down by speech disability, age, or language), first-class **support for speech-disabled and older-adult users** (voice is marketed as accessible, but ASR is documented to degrade sharply for exactly these populations, and no vendor publishes stratified accuracy), and clinical-grade **co-official-language support** (treated at most as a roadmap item). The novelty is thus not architectural separation per se but *what the separated, open layer is grounded in and evaluated against*.

The state-of-the-art review in the final thesis will include a comparative table of these tools across the design axes above (including their disclosed architectures and, where public, underlying models), plus an honest "excluded players" note covering administrative voice agents and single-task clinical AI, motivating the design choices in Section 4.

---

## 4. Proposed System Design

### 4.1 Architecture overview

The system is organised as a pipeline with a clear separation between conversational intelligence and clinical safety:

```
            ┌──────────────────────────────────────────────────────┐
 Patient ──▶│  Telephony / app voice channel                        │
 (voice)    └───────────────┬──────────────────────────────────────┘
                            │ audio
                    ┌───────▼────────┐      ┌────────────────────────┐
                    │  STT (ASR)     │      │  Red-flag detector      │
                    │  speech→text   │─────▶│  (deterministic rules)  │──┐ emergency?
                    └───────┬────────┘      └────────────────────────┘  │ → 112 / human
                            │ text                                       │
                    ┌───────▼────────────────────────────┐             │
                    │  LLM Dialogue Manager               │◀────────────┘
                    │  - structured interview             │
                    │  - protocol-guided questioning      │
                    │  - tool/function calls              │
                    └───────┬─────────────────────────────┘
                            │ structured findings
                    ┌───────▼─────────────────────────────┐
                    │  Triage Engine (MTS/SET mapping)     │  ← deterministic, auditable
                    │  → priority level + care channel     │
                    └───────┬─────────────────────────────┘
                            │
              ┌─────────────┼───────────────────┐
       ┌──────▼─────┐ ┌─────▼──────┐    ┌────────▼─────────┐
       │  TTS reply │ │  Audit log │    │  Follow-up sched.│
       └────────────┘ └────────────┘    └──────────────────┘
```

The key architectural decision is that **the LLM does not assign the triage level on its own**. The LLM conducts the conversation and extracts structured clinical findings; a separate, deterministic **Triage Engine** maps those findings onto **SET** discriminators. This makes the prioritisation logic auditable, testable, and explainable — directly addressing the safety and regulatory concerns of medical AI. As noted in Section 3, this hybrid separation is now common among clinical vendors; the distinguishing commitments here are that the engine is grounded specifically on SET and that its mapping, rules, and rationale format are **specified openly and reproducibly** rather than as a closed component. The same separation also provides the natural insertion point for the accessibility safeguards (Section 4.6): ASR confidence is treated as an input to the deterministic layer, so low-confidence speech triggers repair or escalation instead of a silent guess.

### 4.2 Triage module

- Conducts a guided spoken interview, asking the discriminator questions required by the chosen protocol (pain, bleeding, consciousness, vital-sign proxies, time course, etc.).
- Continuously runs a **red-flag detector** in parallel; any hit triggers immediate emergency escalation regardless of dialogue state.
- Outputs a triage level (1–5), a recommended care channel, a confidence/uncertainty indicator, and a structured rationale.

### 4.3 Follow-up module

- Triggered after a clinical contact (discharge, post-op, chronic-condition check).
- Runs a scripted but natural follow-up dialogue: recovery progress, symptom evolution, medication adherence, appointment reminders.
- Escalates to a human professional when warning signs appear or when adherence/recovery is off-track.
- Persists an interaction summary suitable for inclusion in the patient record.

### 4.4 Safety, guardrails, and explainability

- Deterministic red-flag bypass (independent of the LLM).
- Conservative defaults: under uncertainty, the system **over-triages** (routes upward), since under-triage is the dangerous error.
- Scope enforcement: the agent refuses diagnosis, prescription, and any out-of-scope request.
- Full audit trail and per-interaction human-readable rationale.
- Clear AI-disclosure to the patient at the start of every interaction (an AI Act transparency obligation, see Section 8).
- **Open specification.** The discriminator mapping, escalation rules, and rationale schema are documented as a reproducible artefact (released with the thesis), so an independent party can rebuild the layer and re-run the benchmark. This openness is the deliberate contrast with the certified-but-closed engines of commercial vendors and is what lets the safety claims be externally verified rather than asserted.

### 4.6 Accessibility: speech disabilities and older adults

Voice is often assumed to be inherently accessible; in practice ASR degrades sharply for atypical speech (dysarthria and related conditions) and for older-adult voices (slower rate, lower intensity and pitch, more frequent pauses), which are precisely the SNS populations most likely to need triage. This system treats those users as a primary target rather than an assumed beneficiary:

- **Confidence-aware dialogue.** Per-utterance ASR confidence is surfaced to the deterministic layer. Low confidence does not produce a silent best-guess; it triggers explicit confirmation, rephrasing/repair strategies, or — when a clinically relevant finding cannot be confirmed — conservative escalation. Degradation thus routes toward safety.
- **Interaction design** suited to slower, non-standard speech: tolerant turn-taking and end-of-speech detection, short unambiguous prompts, and no penalising timeouts.
- **Evaluation** of the above is built into O6: under-triage is reported per speech profile, so the safety cost for these users is measured, not assumed. Existing dysarthric-speech corpora (e.g. TORGO) and older-adult speech samples are used so that no real patient data is required.

### 4.7 Co-official languages

The system targets Spanish plus at least one co-official language (catalán, euskera, or gallego). This is both a constitutional/administrative expectation for a public-sector service and a documented technical gap, since these are lower-resource languages with weaker ASR/LLM support than Spanish.

- **Language handling** covers detection and, critically, **intra-call code-switching** — common among older bilingual speakers who may begin in one language and slip into another — rather than assuming one fixed language per patient.
- **Build on existing resources** rather than training from scratch: open Iberian-language models and benchmarks (e.g. the Ilenia/Latxa ecosystem, Iberobench) provide the substrate; the contribution is evaluating them on a *clinical triage* task and checking whether SET discriminators survive translation and code-switching.
- **Evaluation** reports under-triage by language (O6), and the resource/performance gaps encountered are documented as a finding in their own right.

### 4.5 Candidate technology stack (to be finalised in O2)

Open/Spanish- and co-official-language-capable STT and TTS components; an instruction-tuned LLM accessed through a controlled function-calling interface; a rules engine for the SET triage mapping; and a lightweight backend for scheduling, logging, and (simulated) record integration. STT selection explicitly weighs performance on atypical and older-adult speech and on co-official languages, not only on typical-Spanish accuracy, and must expose per-utterance confidence for the safeguards in Section 4.6. Where feasible, on-premise / EU-hosted or open-weight models will be preferred to ease the GDPR data-residency analysis. No real patient data is used in the prototype.

---

## 5. Methodology

The project follows an iterative, incremental methodology with continuous evaluation:

1. **Analysis** — requirements, SET grounding (O1), state-of-the-art review.
2. **Design** — architecture and open safety model (O2, O5).
3. **Incremental implementation** — triage module first (O3), then accessibility and co-official-language support (O7, O8), then follow-up module (O4), then guardrails/explainability hardening (O5).
4. **Evaluation** — clinical-vignette and simulated-patient testing against the SET reference, stratified by speech profile and language (O6).
5. **Regulatory and socio-economic analysis** — developed in parallel from the design phase onward (O9).

Verification is built into each iteration (unit tests for the deterministic triage engine, scripted dialogue tests, and a held-out vignette set), satisfying the rubric's emphasis on adequate verification of objectives.

## 6. Evaluation Plan

| Objective | Verification criterion | Metric / method |
|---|---|---|
| O3 Triage | Agreement with SET reference on vignette set | Accuracy, weighted κ vs. SET reference; **under-triage rate** as primary safety metric |
| O6 Stratified safety | Under-triage does not concentrate in vulnerable groups | **Under-triage rate reported per speech profile** (typical / mild / severe atypical / older-adult) **and per language** (Spanish + co-official); gaps quantified |
| O5 Safety | All red-flag scenarios escalate correctly | 100% recall target on a red-flag test suite |
| O7 Accessibility | Low ASR confidence routes to repair/escalation, never silent misclassification | Behaviour on a degraded-speech test set; share of low-confidence turns resolved safely |
| O8 Language | Correct triage preserved across language and code-switching | Under-triage and κ on co-official-language and code-switching vignettes |
| O3/O4 Latency | Spoken turn latency acceptable for conversation | End-to-end response time (target conversational threshold) |
| O4 Follow-up | Correct escalation on deteriorating-patient scripts | Escalation precision/recall on scripted follow-up cases |
| O5 Openness | Safety layer is independently reproducible | Released specification + scripts allow re-running the benchmark from the artefact alone |
| O3–O7 Usability | Patient comprehension and acceptance | Simulated-user questionnaire (e.g. SUS), including older-adult personas |
| O5 Explainability | Each decision has an auditable rationale | Manual review of rationale completeness |

Under-triage (classifying a serious case as non-urgent) is treated as the critical failure mode and is the headline safety metric. The defining evaluation choice of this thesis is that under-triage is **not** reported only in aggregate: it is stratified by speech profile, age, and language, so that a system which is safe "on average" but dangerous for dysarthric or bilingual older patients is revealed as such rather than passing. All evaluation uses synthetic/clinician-reviewed vignettes and public speech corpora; vignettes are a proxy for live patients and this limitation is stated explicitly.

## 7. Expected Contributions

1. A **SET-grounded** voice-agent prototype that integrates LLM-driven dialogue with a deterministic, protocol-anchored triage engine — grounding the decision logic on the SNS's own accredited standard rather than a proprietary or protocol-agnostic engine.
2. An **open and reproducible** safety-layer specification — discriminator mapping, escalation rules, rationale schema, and evaluation scripts released as an artefact — so the safety claims can be independently rebuilt and challenged, unlike the certified-but-closed pipelines of commercial vendors.
3. An **accessibility-stratified under-triage benchmark**: the critical safety metric reported by speech profile, age, and language, exposing failures concentrated in vulnerable groups that an aggregate number would hide.
4. **First-class support for people with speech disabilities and older adults**, via a confidence-aware dialogue strategy that turns the predictable ASR-degradation failure mode into safe escalation rather than silent misclassification.
5. **Co-official-language support**, including intra-call code-switching, with a documented analysis of the resource and performance gaps for catalán/euskera/gallego on a clinical task.
6. A grounded regulatory and socio-economic analysis (AI Act, MDR, GDPR/LOPDGDD, plus Ley 11/2023 and EN 301 549 accessibility duties, and the SDGs) for a realistic SNS deployment.
