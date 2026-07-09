"""Gemini-driven conversation layer.

Wraps a `google-genai` client and conducts the patient interview through two
function-calling tools, `update_findings` and `finalize`. The model is never
asked for, and this module never emits, a SET level — `DialogueTurn.findings`
only ever carries a validated `ClinicalFindings`; level assignment is
`set_engine.classify`'s job.

`DialogueManager` is the conversation step the orchestrator (slice 003)
drives: call `step()` once per user utterance and inspect the returned
`DialogueTurn`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from google.genai import types
from pydantic import ValidationError

from triage.findings import (
    BleedingSeverity,
    BreathingDifficultySeverity,
    ClinicalFindings,
    ConsciousnessLevel,
    PresentingComplaint,
)

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are a triage interview assistant for the Spanish public
health system (SNS). Your only job is to ask short, specific discriminator
questions that help characterise the patient's presenting complaint, and to
record what you learn by calling `update_findings`.

Rules you must always follow:
- Ask one short question at a time. Do not lecture or explain.
- Never diagnose a condition, never suggest or name a medication or
  treatment, and never tell the patient how serious their situation is or
  what level of care they need. That decision is made by a separate
  deterministic system after the interview, not by you.
- If the patient asks you to diagnose them, prescribe something, or asks
  anything outside the scope of a triage interview, politely decline and
  redirect to the next discriminator question.
- Call `update_findings` every time you learn something new, even if the
  interview is not finished. Partial updates are expected and welcome.
- Call `finalize` once you have asked enough discriminator questions to
  characterise the complaint, or the patient has nothing more to add.
- You never produce a triage level, urgency category, or care recommendation
  of any kind, in tool calls or in your spoken replies.
"""

_PRESENTING_COMPLAINT_SCHEMA = types.Schema(
    type=types.Type.STRING,
    enum=[c.value for c in PresentingComplaint],
)
_BLEEDING_SCHEMA = types.Schema(
    type=types.Type.STRING,
    enum=[c.value for c in BleedingSeverity],
)
_CONSCIOUSNESS_SCHEMA = types.Schema(
    type=types.Type.STRING,
    enum=[c.value for c in ConsciousnessLevel],
)
_BREATHING_DIFFICULTY_SCHEMA = types.Schema(
    type=types.Type.STRING,
    enum=[c.value for c in BreathingDifficultySeverity],
)

_UPDATE_FINDINGS_DECLARATION = types.FunctionDeclaration(
    name="update_findings",
    description=(
        "Record clinical findings learned so far from the patient. Only "
        "include fields you have just learned; omitted fields keep their "
        "previously recorded value."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "presenting_complaint": _PRESENTING_COMPLAINT_SCHEMA,
            "pain_score": types.Schema(type=types.Type.INTEGER, minimum=0, maximum=10),
            "bleeding": _BLEEDING_SCHEMA,
            "consciousness": _CONSCIOUSNESS_SCHEMA,
            "breathing_difficulty": _BREATHING_DIFFICULTY_SCHEMA,
            "chest_pain": types.Schema(type=types.Type.BOOLEAN),
            "chest_pain_radiating": types.Schema(type=types.Type.BOOLEAN),
            "stroke_signs_fast": types.Schema(type=types.Type.BOOLEAN),
            "allergic_reaction_severe": types.Schema(type=types.Type.BOOLEAN),
            "suicidal_ideation": types.Schema(type=types.Type.BOOLEAN),
            "onset": types.Schema(type=types.Type.STRING),
        },
    ),
)

_FINALIZE_DECLARATION = types.FunctionDeclaration(
    name="finalize",
    description="Call when the interview is complete and no further discriminator questions are needed.",
    parameters=types.Schema(type=types.Type.OBJECT, properties={}),
)

TOOLS = [
    types.Tool(
        function_declarations=[_UPDATE_FINDINGS_DECLARATION, _FINALIZE_DECLARATION]
    )
]


@dataclass
class DialogueTurn:
    """One round-trip of the interview: the model's reply plus any
    side-effects (a findings update, or the interview finishing)."""

    reply_text: Optional[str] = None
    findings: Optional[ClinicalFindings] = None
    rejected_update: Optional[str] = None
    finalized: bool = False


class DialogueManager:
    """Drives the patient interview via a `google-genai` client.

    Accumulates `update_findings` tool-call arguments into a single
    `ClinicalFindings`, re-validating on every call so an invalid payload is
    rejected without corrupting previously confirmed findings.
    """

    def __init__(self, client: Any, model: str = DEFAULT_MODEL) -> None:
        self._client = client
        self.model = model
        self.findings: Optional[ClinicalFindings] = None
        self._findings_data: dict[str, Any] = {}
        self._history: list[Any] = []

    def step(self, user_text: str) -> DialogueTurn:
        self._history.append(
            types.Content(role="user", parts=[types.Part(text=user_text)])
        )
        response = self._client.models.generate_content(
            model=self.model,
            contents=self._history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=TOOLS,
            ),
        )
        return self._process_response(response)

    def _process_response(self, response: Any) -> DialogueTurn:
        candidate = response.candidates[0]
        self._history.append(candidate.content)

        turn = DialogueTurn()
        for part in candidate.content.parts or []:
            function_call = getattr(part, "function_call", None)
            if function_call is not None:
                self._dispatch_tool_call(function_call, turn)
            elif getattr(part, "text", None):
                turn.reply_text = (turn.reply_text or "") + part.text
        return turn

    def _dispatch_tool_call(self, function_call: Any, turn: DialogueTurn) -> None:
        if function_call.name == "update_findings":
            turn.findings, turn.rejected_update = self.apply_update_findings(
                dict(function_call.args or {})
            )
        elif function_call.name == "finalize":
            turn.finalized = True

    def apply_update_findings(
        self, args: dict[str, Any]
    ) -> tuple[Optional[ClinicalFindings], Optional[str]]:
        """Merge `args` into the accumulated findings and validate the
        result. On failure, leaves previously confirmed findings untouched
        and returns the rejection reason instead of raising."""
        merged = {**self._findings_data, **args}
        try:
            findings = ClinicalFindings(**merged)
        except ValidationError as exc:
            return None, str(exc)
        self._findings_data = merged
        self.findings = findings
        return findings, None
