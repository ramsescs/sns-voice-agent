# Bachelor's Thesis Proposal

## A Voice-Agent Triage and Follow-up System for the Spanish Public Health System, Built on the ElevenLabs Agents Platform: Co-official-Language Coverage and Accessibility for Atypical and Older-Adult Speech

---

## 1. Introduction

The Spanish public health system (Sistema Nacional de Salud, SNS) operates under severe and growing demand pressure. The SNS handles close to 400 million primary-care consultations and around 35 million emergency-department (ED) visits per year, and a substantial fraction of those contacts are either non-urgent cases that could be resolved at a lower level of care or, conversely, urgent cases that arrive late because the patient did not know where to go. The *Consejo Interterritorial del SNS* approved a National Artificial Intelligence Strategy for the SNS in November 2025, explicitly endorsing AI to support patient triage and resource allocation while insisting that the final clinical decision remains with the professional.

This thesis designs, builds, and evaluates a **conversational voice agent** that performs two coordinated functions for SNS patients — symptom-based **triage** and post-contact **follow-up** — and does so **natively on the ElevenLabs Agents Platform**. Rather than building a bespoke voice pipeline, this work treats a modern hosted agentic voice platform as the substrate and asks a focused, practical research question: *how safely, accessibly, and multilingually can a clinical triage agent be built on such a platform, and where are its limits?*

The clinical logic that must not be improvised — the *Sistema Español de Triaje* (SET) prioritisation and the emergency red-flag check — is implemented as **deterministic server-side tools that the agent calls** (via the platform's webhook/tool and MCP mechanisms). The platform owns speech-to-text (STT), turn-taking, text-to-speech (TTS), and conversation orchestration; the project owns the SET engine and the safety tool behind a stable API.

This work is centred on four exploration axes, chosen to match both the SNS context and the capabilities of the platform:

1. **Platform-native clinical agent.** Building the triage + follow-up agent within ElevenLabs, with the SET engine and red-flag check as called tools, and evaluating how well a hosted agentic platform supports a safety-critical clinical use case.
2. **Safety within an agentic platform.** Implementing a high-priority safety tool and a workflow design that enforces conservative escalation, and *honestly characterising* the verifiability limits of safety when control flow is owned by a probabilistic agent rather than by deterministic code (Section 4.5).
3. **Co-official-language coverage — Catalan and Galician.** Using Catalan and Galician as the co-official languages of study, evaluating the platform's STT and TTS quality on them for a clinical task, including intra-call code-switching with Spanish.
4. **Accessibility for atypical and older-adult speech.** Evaluating and adapting the agent for people with speech/language disabilities and older adults — the populations for whom ASR degrades most — using the platform's turn-taking controls, keyterm prompting, and confidence signals.

The central thesis is that a *human-in-the-loop* voice agent built on a hosted platform can absorb a meaningful volume of low-complexity triage and follow-up interactions and improve access — **provided** that clinical safety is enforced through called tools and workflow design, that the platform's limits are measured rather than assumed, and that the accessibility and language coverage are evaluated on the populations and languages that matter for the SNS.

### 1.1 Motivation

Three converging factors make this an appropriate and timely TFG:

- **Clinical need:** ED overcrowding and primary-care waiting lists are persistent structural problems in the SNS. Telephone triage exists (autonomic-community lines, 112/061) but is nurse-time-limited.
- **Platform maturity:** hosted agentic voice platforms now bundle low-latency STT, sophisticated turn-taking, expressive multilingual TTS, server-side tool calling, and telephony, making it feasible for a single student to build and evaluate a working clinical voice agent in one semester — and making the *platform itself* a worthwhile object of study.
- **Policy and access alignment:** the 2025 SNS AI Strategy provides an institutional mandate; the EU AI Act and Spain's accessibility legislation (Ley 11/2023) provide the compliance scaffolding (Section 8).

### 1.2 Scope and boundaries

The system **assists** triage; it does not replace the clinical professional and never issues a definitive diagnosis. Fixed, non-negotiable constraints:

- Any output that prioritises or routes a patient is a *recommendation*, governed by conservative, pre-approved escalation rules.
- On detection of an emergency red flag (e.g. chest pain with radiation, signs of stroke, anaphylaxis, suicidal ideation), the agent must hand off to emergency services (112) / a human, and must do so under a workflow that makes this the enforced, highest-priority path (the architectural realities and limits of this within a hosted agent are analysed in Section 4.5).
- Linguistic scope is fixed as Spanish plus **Catalan and Galician**, including intra-call code-switching.
- Accessibility for atypical and older-adult speech is a design and evaluation target, not an afterthought; the agent must degrade toward escalation, never toward silent misclassification.

The prototype is a **research artefact and is not placed on the market**, and uses only synthetic vignettes and public speech corpora — no real patient data.

---

## 2. Objectives

### 2.1 General objective

To design, implement, and evaluate a prototype voice-agent system for SNS triage and post-contact follow-up, **built on the ElevenLabs Agents Platform with the SET prioritisation and red-flag checks implemented as deterministic called tools**, evaluating the platform's clinical suitability, its safety-enforcement and verifiability characteristics, its Catalan and Galician coverage, and its accessibility for atypical and older-adult speech.

### 2.2 Specific objectives

1. **O1 — Requirements & SET grounding.** Analyse the SNS triage context and encode the *Sistema Español de Triaje* (SET) as a deterministic, machine-executable specification to be exposed as a tool.
2. **O2 — Platform agent architecture.** Design the ElevenLabs agent: conversation/workflow design, system prompt, the tool interface for the SET engine and the red-flag check, telephony, and the boundary between platform-owned and project-owned components.
3. **O3 — SET engine & safety tools.** Implement the server-side SET prioritisation tool and the red-flag/escalation tool with auditable, human-readable rationale per decision, behind a stable API the agent calls.
4. **O4 — Triage & follow-up flows.** Implement the structured triage interview and the post-contact follow-up workflow (recovery monitoring, adherence checks, escalation, scheduling, interaction record) as agent workflows.
5. **O5 — Safety enforcement & honest verifiability analysis.** Implement workflow- and prompt-level enforcement of the safety path (e.g. forced tool invocation, conservative defaults, scope refusal) **and** analyse and measure the residual risk that the agent fails to call or fails to honour the safety tool — i.e. the verifiability cost of platform-owned control flow.
6. **O6 — Co-official-language evaluation (Catalan & Galician).** Evaluate the platform's STT and TTS on Catalan and Galician for the triage task, including intra-call code-switching with Spanish, and report triage accuracy and under-triage by language.
7. **O7 — Accessibility for atypical & older-adult speech.** Evaluate and adapt the agent for dysarthric/atypical and older-adult speech using the platform's turn-taking settings, keyterm prompting, and confidence/quality signals; report under-triage stratified by speech profile and define the confidence-aware repair/escalation behaviour.
8. **O8 — Evaluation.** Evaluate the full prototype on clinical vignettes / simulated patients against a SET reference, with **under-triage rate as the primary safety metric, reported stratified by language and by speech profile**, plus safety-tool reliability, latency, and usability.
9. **O9 — Regulatory & socio-economic analysis.** Produce the regulatory analysis (EU AI Act, MDR, GDPR/LOPDGDD including third-party voice processing and EU data residency, plus accessibility duties under Ley 11/2023 and EN 301 549) and the socio-economic/SDG and budget analysis.

Each objective maps to a verification criterion in Section 7.

---

## 3. State of the Art

The proposal sits at the intersection of clinical triage protocols, AI-assisted triage, and voice agents in health.

**Clinical triage protocols.** The *Sistema Español de Triaje* (SET, derived from the Andorran MAT) is the accredited five-level triage standard of the SNS and is adopted here as the grounding protocol; the Manchester Triage System (MTS) is used only as a comparator. These protocols define discriminators assigning each patient to one of five priority levels with maximum waiting times, giving an auditable reference logic.

**AI-assisted triage.** Recent literature reports AI can improve triage precision and reduce documentation burden, while emphasising AI must remain subordinate to clinical judgement. Spoken natural-language intake by patients themselves remains comparatively under-explored, and under-triage is the recurring safety concern.

**Voice agents in health, and hosted agentic platforms.** Clinical voice systems (Tucuvi/LOLA, Infermedica, Hippocratic AI, Corti) have converged on *hybrid* designs — an LLM for conversation around a non-probabilistic core (Bayesian engine, decision trees, rules) for the decision. They are mostly built on bespoke or proprietary stacks. A distinct, less-studied question is what happens when the *same hybrid idea* is implemented on a **general-purpose hosted agentic voice platform**, with the deterministic core exposed as a called tool. This is increasingly how real products are built, yet the academic literature rarely evaluates the *platform itself* for a safety-critical clinical task — its STT quality on minority languages and atypical speech, its turn-taking for older speakers, and crucially the safety-verifiability implications of letting a probabilistic agent own the control flow. That platform-evaluation gap, for the SNS context and in Catalan/Galician, is where this thesis contributes.

The final SoTA review will include a comparative table of the systems above across design axes (architecture, disclosed models, language and accessibility coverage), plus a focused analysis of the called-tool vs. server-orchestrated control-flow patterns and their respective safety properties (Section 4.5), and an "excluded players" note (administrative voice agents, single-task clinical AI).

---

## 4. Proposed System Design

### 4.1 Architecture overview

The system is an ElevenLabs agent whose conversational behaviour is platform-managed and whose clinical decisions are delegated to project-owned tools:

```
 Patient ──▶ Telephony / SIP ──▶  ┌──────────────────────────────────────────────┐
 (voice)                          │  ElevenLabs Agents Platform                    │
                                  │  STT (Scribe v2 Realtime) · turn-taking ·      │
                                  │  LLM orchestration · workflow · TTS (v3)       │
                                  └───────┬───────────────────────────────▲────────┘
                                          │ tool calls (webhook / MCP)     │ results + rationale
                          ─ ─ ─ ─ ─ ─ ─ ─ │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │ ─ ─  project-owned server ─
                                  ┌───────▼───────────────┐    ┌───────────┴─────────────┐
                                  │  SET triage tool       │    │  Red-flag / escalation  │
                                  │  (deterministic, SET)  │    │  tool (deterministic)   │
                                  │  → level + care channel│    │  → emergency? → 112/human│
                                  └───────┬────────────────┘    └─────────────────────────┘
                                          │
                                  ┌───────▼────────┐ ┌───────────┐ ┌──────────────────┐
                                  │  Audit log     │ │ Record    │ │ Follow-up sched. │
                                  └────────────────┘ └───────────┘ └──────────────────┘
```

The agent conducts the spoken interview; at defined points (and, for red flags, as an enforced step) it calls the project-owned tools. The SET tool returns a level, a care channel, and a structured rationale; the red-flag tool returns an emergency determination. The agent then communicates the outcome and, on emergency, follows the hand-off workflow.

### 4.2 SET engine and safety tools (project-owned)

- **SET triage tool.** A deterministic service mapping the structured findings collected during the interview onto SET discriminators, returning level (1–5), recommended care channel, an uncertainty indicator, and a human-readable rationale. It is versioned and unit-tested independently of the agent.
- **Red-flag / escalation tool.** A deterministic check for emergency discriminators; a positive result returns an unambiguous "escalate to 112/human" instruction with rationale.
- Both tools are exposed over a stable API (webhook tools and/or an MCP server registered with the agent), return structured JSON, and log every call for audit.

### 4.3 Triage and follow-up flows

- **Triage flow.** A workflow-guided spoken interview eliciting the discriminator information SET requires (pain, bleeding, consciousness, time course, vital-sign proxies), invoking the SET tool to obtain the level and care channel, and invoking the red-flag tool throughout.
- **Follow-up flow.** Triggered after a clinical contact; a natural but workflow-bounded dialogue covering recovery, symptom evolution, and adherence, escalating via the safety tool when warning signs appear, and persisting an interaction summary for the record.

### 4.4 Accessibility and language handling (within the platform)

- **Turn-taking for older/atypical speakers.** Use the platform's configurable turn model and turn eagerness/timeout settings (patient end-pointing, longer timeouts) so slower speech and pauses are not cut off or mis-segmented.
- **Keyterm prompting.** Bias STT toward clinically important Spanish/Catalan/Galician terms and red-flag vocabulary so critical words are less likely to be mis-transcribed.
- **Confidence/quality-aware repair.** Use the platform's transcript/confidence signals so low-confidence turns trigger confirmation/repair prompts or conservative escalation rather than a silent guess.
- **Language & code-switching.** Configure Catalan and Galician alongside Spanish and exercise the platform's language-detection/switching so a patient beginning in one language and slipping into another is still understood.

### 4.5 Safety and the honest verifiability trade-off

This design deliberately places the SET and red-flag logic *behind tools the agent calls*, which has a consequence the thesis confronts directly rather than hides. Because the hosted agent owns the control flow, it — not deterministic code — decides whether and when to call a tool and how to act on the result. A *true* "bypass the LLM" is therefore not architecturally available on the platform; what is available is **enforcement by design**: workflow nodes that force the red-flag tool to run, forced/required tool invocation, conservative defaults (escalate under uncertainty), scope refusals, and system-prompt constraints.

The thesis treats the residual risk as a first-class research object:

- It measures how reliably the agent (a) calls the safety tool when it should, and (b) honours an "escalate" result rather than over-talking or re-routing it.
- It contrasts this called-tool pattern with a server-orchestrated alternative (where deterministic code owns control flow and a genuine bypass is possible), making explicit what is gained (platform speed, turn-taking, multilingual STT/TTS, telephony) and what is traded (verifiable determinism).
- It frames the platform's safety-tooling (forced tools, guardrails, workflow gating) as *mitigations* whose effectiveness is empirically tested, not assumed.

This honesty is itself a contribution: a measured account of how safe a hosted agentic platform can be made for clinical triage, and where its verifiability ceiling lies.

### 4.6 Technology stack

- **ElevenLabs Agents Platform** — STT (Scribe v2 Realtime), configurable turn-taking, LLM orchestration and workflows, expressive multilingual TTS (v3), keyterm prompting, telephony (SIP/Twilio etc.), and server-side tools/MCP. EU data residency and zero-retention modes are noted for the GDPR analysis (Section 8.3).
- **Project-owned server** — the SET engine, the red-flag tool, scheduling, audit logging, and (simulated) record integration, exposed to the agent as webhook tools / an MCP server.
- No real patient data is processed; evaluation uses synthetic vignettes and public speech corpora.

---

## 5. Methodology

Iterative, incremental, with continuous evaluation:

1. **Analysis** — requirements, SET grounding (O1), SoTA including the platform-evaluation and control-flow analysis.
2. **Design** — agent/workflow design, tool interface, safety enforcement model (O2, O5).
3. **Incremental implementation** — SET engine and safety tools first (O3), then triage and follow-up flows (O4), then accessibility and Catalan/Galician configuration (O6, O7).
4. **Evaluation** — clinical-vignette and simulated-patient testing against the SET reference, stratified by language and speech profile, plus safety-tool reliability testing (O8).
5. **Regulatory and socio-economic analysis** — in parallel from the design phase (O9).

Verification is built into each iteration: unit tests for the deterministic SET and red-flag tools, scripted dialogue and tool-invocation tests using the platform's simulation/eval features, and a held-out vignette set.

---

## 6. Tools and Resources

Development laptop; an **ElevenLabs account with donated academic credits** (Agents Platform, Scribe STT, v3 TTS, keyterm prompting, telephony); a project-owned server runtime for the SET engine and safety tools (webhook/MCP); the SET protocol documentation as the triage reference; a corpus of synthetic clinical vignettes; public atypical-speech corpora (e.g. TORGO) and Catalan/Galician speech resources for the language and accessibility evaluation; and, ideally, informal validation input from a clinical professional. No real or identifiable patient data is processed at any stage.

---

## 7. Evaluation Plan

| Objective | Verification criterion | Metric / method |
|---|---|---|
| O3/O8 Triage | Agreement with SET reference on vignette set | Accuracy, weighted κ vs. SET; **under-triage rate** as primary safety metric |
| O6 Language | Triage preserved across Catalan, Galician, and code-switching | STT WER per language on clinical audio; under-triage and κ per language and on code-switching vignettes |
| O7 Accessibility | Atypical/older-adult speech handled safely | STT WER and under-triage per speech profile (typical / mild / severe atypical / older-adult); share of low-confidence turns resolved via repair/escalation |
| O5 Safety enforcement | Red-flag scenarios trigger and are honoured | Tool-invocation recall (did the agent call the safety tool when required?) and escalation-honouring rate; target 100% recall on a red-flag suite |
| O5 Verifiability | Residual platform risk is quantified | Rate and analysis of cases where the agent fails to call or fails to honour the safety tool; comparison vs. server-orchestrated control |
| O3/O4 Latency | Spoken turn latency acceptable | End-to-end response time including tool round-trips |
| O4 Follow-up | Correct escalation on deteriorating-patient scripts | Escalation precision/recall on scripted follow-up cases |
| O3–O7 Usability | Comprehension and acceptance | Simulated-user questionnaire (e.g. SUS), including older-adult personas |
| O3/O5 Explainability | Each decision has an auditable rationale | Review of tool-returned rationale completeness and audit-log integrity |

Under-triage (classifying a serious case as non-urgent) is the headline safety metric and is reported **stratified by language and speech profile**, so a system safe "on average" but dangerous for Galician-speaking or dysarthric or older patients is revealed as such. A distinctive secondary metric is **safety-tool reliability** — how dependably the hosted agent calls and honours the deterministic safety logic — which operationalises the verifiability analysis of Section 4.5. All evaluation uses synthetic/clinician-reviewed vignettes and public speech corpora; vignettes are a proxy for live patients, stated as a limitation.

---

## 8. Regulatory Framework

### 8.1 EU AI Act

A triage system that prioritises or routes patients is highly likely to be a **high-risk AI system** under the EU AI Act. The Act entered into force on 1 August 2024; under the May 2026 "Omnibus" agreement the high-risk obligations were postponed (stand-alone Annex III systems to 2 December 2027; AI in regulated products such as medical devices to 2 August 2028), while the **Article 50 transparency obligations** — including disclosing to the patient that they are interacting with an AI — proceed from 2 August 2026 and are reflected in the design (AI disclosure at call start). The thesis analyses the high-risk obligations a production version would meet: risk management, data governance, logging/traceability, human oversight, accuracy/robustness, and technical documentation — and how building on a third-party platform distributes those responsibilities between platform and deployer.

### 8.2 Medical Device Regulation (MDR)

Software providing information used for clinical decisions (triage prioritisation) generally qualifies as a **medical device (SaMD) under Regulation (EU) 2017/745 (MDR)**, typically Class IIa+ under Rule 11, requiring CE marking and a Notified Body. The thesis analyses the classification and conformity pathway a production version would face, including the implications of the clinical logic residing in a project-owned tool versus the conversational layer residing in a third-party platform. The prototype itself is a research artefact and is not placed on the market.

### 8.3 Data protection: GDPR and LOPDGDD

Health data are a *special category* under **GDPR** and Spain's **LOPDGDD (Ley Orgánica 3/2018)**; voice recordings and transcripts are additionally sensitive. Because the architecture sends audio to a third-party platform (ElevenLabs) for STT/TTS, the analysis explicitly covers third-party processing: the need for a data-processing agreement, use of the platform's **EU data residency and zero-retention modes**, and HIPAA/BAA-style controls where relevant. For the prototype this is unproblematic — only synthetic vignettes and public corpora are used (no personal data) — but the production analysis addresses residency, sub-processing, and the option of an EU-hosted/decoupled STT if residency cannot be guaranteed. The prototype avoids real patient data, eliminating personal-data processing during development.

### 8.4 Technical standards and ethics; accessibility law

Relevant standards include ISO 14971, IEC 62304, ISO/IEC 42001, and harmonised AI Act standards. **Accessibility carries legal weight**: Spain's Ley 11/2023 (transposing the European Accessibility Act) requires digital accessibility for people with disabilities from 28 June 2025 and reaches emergency communications, assessed against WCAG and EN 301 549; combined with the right to address the administration in a co-official language, a public-facing SNS triage agent has concrete obligations on both the disability and language axes — reframing the accessibility and Catalan/Galician work (O6, O7) as compliance requirements, not extras. Ethically, the project upholds the 2025 SNS AI Strategy principle that AI supports but does not replace the clinician, with explicit attention to equity for atypical speech, accents, co-official languages, and limited digital literacy — exactly what the stratified evaluation measures.

---

## 9. Socio-economic Environment and SDGs

**Economic.** Triage is nurse-time-limited; a voice agent safely handling low-complexity contacts could reduce cost per interaction and shift clinician time to higher-acuity work. Building on a hosted platform lowers development cost and time but introduces per-minute/per-character platform costs and vendor dependence, weighed against MDR/AI Act conformity, integration, and ongoing oversight costs. A realistic net impact may be modest until those amortise; the thesis presents this honestly, including downside scenarios and the lock-in risk of platform dependence.

**Social / health-equity.** This is where the project's commitments carry their weight. Benefits: improved access (24/7, in Spanish, Catalan, and Galician, usable by older, low-literacy, and visually impaired patients via voice). The accessibility and co-official-language axes are analysed as legal duties (Ley 11/2023, EN 301 549; co-official-language rights), not only ethical goods. Risks, treated honestly: the digital divide, exclusion of patients with atypical speech if STT is not handled safely, automation bias, and the safety-verifiability ceiling of platform-owned control flow. The stratified under-triage evaluation and the safety-tool-reliability metric are the concrete mechanisms by which these risks are measured rather than assumed away.

**Environmental.** Platform inference has an energy/carbon cost; the analysis weighs this against avoided patient travel and unnecessary in-person visits.

**SDG alignment.** Primarily **SDG 3 (Good Health and Well-being)**; secondarily **SDG 10 (Reduced Inequalities)** via accessibility and minority-language support, **SDG 9 (Industry, Innovation, Infrastructure)**, and **SDG 8** (clinical workforce conditions).

---

## 10. Budget

Indicative budget for the elaboration of the TFG (research prototype, not production deployment):

| Item | Assumption | Estimated cost (EUR) |
|---|---|---|
| Human resources (student) | ~300 h of work at a junior-engineer reference rate | ~6,000 |
| Tutoring/supervision | Supervisor hours (institutional) | ~1,500 |
| ElevenLabs platform (STT/TTS/agent/telephony) | Voice + agent usage during development; **covered by donated ElevenLabs academic credits** | ~0 (in-kind) |
| Compute — project server & any LLM | Hosting for the SET/safety tools; incidental model usage | ~150–350 |
| Software & tools | Mostly open-source; misc. licences/services | ~100 |
| Hardware | Existing development laptop (amortised) | ~200 |
| Documentation/dissemination | Printing, possible publication fees | ~150 |
| **Total (indirect costs excl.)** | | **≈ 8,100–8,300** |

Final figures will use the institution's standard cost rates and an overhead/indirect-cost percentage. The voice and agent layer is provided in-kind through donated ElevenLabs academic credits, noted here for transparency.

---

## 11. Work Plan and Timeline

Indicative plan over a single academic semester (~4 months):

| Phase | Weeks | Output |
|---|---|---|
| Analysis, SoTA, SET grounding (O1) | 1–3 | Requirements + SET specification |
| Agent & tool architecture, safety enforcement design (O2, O5) | 3–5 | Design document + tool interface |
| SET engine & safety tools (O3) | 4–7 | Deterministic tools + audit logging |
| Triage & follow-up flows on platform (O4) | 6–10 | Working agent prototype |
| Catalan/Galician + accessibility configuration (O6, O7) | 8–11 | Multilingual, accessibility-tuned agent |
| Safety-reliability & verifiability testing (O5) | 11–12 | Tool-invocation/honouring results |
| Stratified evaluation (O8) | 12–14 | Under-triage by language & speech profile |
| Regulatory/socio-economic analysis + writing (O9) | parallel + 14–16 | Full thesis report |

---

## 12. Expected Contributions

1. A working **platform-native** SNS triage + follow-up voice agent, built on ElevenLabs with the SET prioritisation and red-flag checks as deterministic called tools.
2. An **empirical evaluation of a hosted agentic voice platform for a safety-critical clinical task** — including the novel, honestly-framed **safety-tool reliability** metric (how dependably the agent calls and honours the deterministic safety logic) and an explicit account of the verifiability ceiling of platform-owned control flow.
3. A **Catalan and Galician** evaluation of the platform's STT/TTS for clinical triage, including intra-call code-switching — minority-language clinical coverage that is rarely measured.
4. An **accessibility evaluation for atypical and older-adult speech**, with platform-level adaptations (turn-taking, keyterm prompting, confidence-aware repair) and under-triage reported per speech profile.
5. A grounded regulatory and socio-economic analysis (AI Act, MDR, GDPR/LOPDGDD with third-party-processing and EU-residency analysis, Ley 11/2023 and EN 301 549, SDGs) for a realistic platform-based SNS deployment.

---

## 13. References (to be expanded)

- Consejo Interterritorial del SNS — *Estrategia de Inteligencia Artificial del SNS* (Nov 2025).
- Regulation (EU) 2024/1689 (Artificial Intelligence Act) and the May 2026 Omnibus amendments.
- Regulation (EU) 2017/745 (MDR); MDCG guidance on SaMD qualification/classification (Rule 11).
- Regulation (EU) 2016/679 (GDPR); Ley Orgánica 3/2018 (LOPDGDD).
- Ley 11/2023 (European Accessibility Act transposition); EN 301 549; WCAG.
- ISO 14971; IEC 62304; ISO/IEC 42001.
- Sistema Español de Triaje (SET) documentation; Manchester Triage Group (comparator).
- ElevenLabs documentation: Agents Platform, Scribe v2 / v2 Realtime STT (language support and WER tiers — Catalan and Galician in the ≤5% WER tier), v3 TTS, keyterm prompting, turn-taking configuration, telephony, tools/MCP, EU data residency and zero-retention.
- Comparator clinical voice systems and disclosed architectures: Tucuvi/LOLA (LLM + decision trees), Infermedica (LLM + Bayesian knowledge base), Hippocratic AI (Polaris constellation), Corti (healthcare foundation models); Ada, Mediktor.
- Atypical-speech / ASR-accessibility literature; dysarthric-speech corpora (e.g. TORGO); Catalan/Galician speech resources.
- Recent literature on AI-assisted emergency triage (e.g. *Medicina Clínica*, 2024; nursing systematic reviews, 2025).
