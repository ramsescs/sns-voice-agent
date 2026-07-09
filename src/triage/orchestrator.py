"""Deterministic control loop tying dialogue, redflag, and set_engine together.

Control flow and level assignment are deterministic Python; only findings
extraction is LLM-mediated (in `dialogue`). After every findings update the
red-flag check runs and a hit ends the call immediately — the genuine bypass.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from triage import redflag, set_engine
from triage.redflag import RedFlagResult
from triage.set_engine import TriageResult

GREETING = (
    "Hello — you are speaking with an automated AI triage assistant, not a "
    "human clinician. I will ask a few short questions to help direct you to "
    "the right care. This is not a medical diagnosis. If this may be a "
    "life-threatening emergency, hang up and call 112 now."
)


@dataclass
class OrchestratorOutput:
    reply_text: Optional[str] = None   # model's next question (call continues)
    message: Optional[str] = None      # terminal outcome text (call ended)
    ended: bool = False
    kind: Optional[str] = None         # "red_flag" | "classification" | None
    red_flag: Optional[RedFlagResult] = None
    triage: Optional[TriageResult] = None


def _escalation_message(rf: RedFlagResult) -> str:
    return f"⚠️  EMERGENCY — call 112 now.\n{rf.rationale}"


def _classification_message(r: TriageResult) -> str:
    note = "  (uncertain — routed conservatively upward)" if r.uncertainty else ""
    return (
        f"Recommended care: SET level {r.level} — {r.care_channel.value}.{note}\n"
        f"{r.rationale}"
    )


class Orchestrator:
    def __init__(
        self,
        dialogue: Any,
        *,
        redflag_check: Callable = redflag.check,
        classify: Callable = set_engine.classify,
    ) -> None:
        self._dialogue = dialogue
        self._redflag_check = redflag_check
        self._classify = classify
        self._ended = False

    @property
    def greeting(self) -> str:
        return GREETING

    def handle_turn(self, user_text: str) -> OrchestratorOutput:
        if self._ended:
            raise RuntimeError("call has already ended")
        turn = self._dialogue.step(user_text)

        # 1) Red-flag bypass — runs on any fresh findings, before finalize.
        if turn.findings is not None:
            # TODO: Delete after testing
            print(f"[DEBUG] findings: {turn.findings.dict()}")
            rf = self._redflag_check(turn.findings)
            if rf.fired:
                self._ended = True
                # TODO(006/004): write audit record here.
                return OrchestratorOutput(
                    message=_escalation_message(rf),
                    ended=True, kind="red_flag", red_flag=rf,
                )

        # 2) Finalize -> deterministic SET classification.
        if turn.finalized:
            self._ended = True
            findings = self._dialogue.findings
            if findings is None:
                return OrchestratorOutput(
                    message="Interview ended before enough information was "
                            "gathered to triage.",
                    ended=True, kind=None,
                )
            result = self._classify(findings)
            # TODO(006/004): write audit record here.
            return OrchestratorOutput(
                message=_classification_message(result),
                ended=True, kind="classification", triage=result,
            )

        # 3) Otherwise, continue the interview.
        return OrchestratorOutput(reply_text=turn.reply_text, ended=False)
