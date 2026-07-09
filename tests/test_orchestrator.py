import pytest
from types import SimpleNamespace  # noqa: F401 (only if needed)

from triage.dialogue import DialogueTurn
from triage.findings import ClinicalFindings
from triage.orchestrator import Orchestrator


class FakeDialogue:
    """Scripted stand-in for DialogueManager."""
    def __init__(self, turns, model="fake-model"):
        self._turns = list(turns)
        self.findings = None
        self.model = model

    def step(self, user_text):
        turn = self._turns.pop(0)
        if turn.findings is not None:
            self.findings = turn.findings   # mirror accumulation
        return turn


def test_greeting_discloses_ai():
    g = Orchestrator(FakeDialogue([])).greeting.lower()
    assert "ai" in g or "automated" in g


def test_red_flag_bypass_ends_call_with_escalation():
    findings = ClinicalFindings(presenting_complaint="chest_pain", chest_pain_radiating=True)
    orch = Orchestrator(FakeDialogue([DialogueTurn(findings=findings)]))

    out = orch.handle_turn("my chest pain shoots down my left arm")

    assert out.ended and out.kind == "red_flag"
    assert out.red_flag.fired
    assert "112" in out.message
    with pytest.raises(RuntimeError):   # call is over
        orch.handle_turn("...")


def test_non_red_flag_path_reaches_set_classification():
    findings = ClinicalFindings(presenting_complaint="fever", pain_score=2)
    orch = Orchestrator(FakeDialogue([
        DialogueTurn(reply_text="How long have you had it?", findings=findings),
        DialogueTurn(finalized=True),
    ]))

    first = orch.handle_turn("I have a mild fever")
    assert not first.ended            # no red flag; interview continues

    final = orch.handle_turn("since yesterday, that's all")
    assert final.ended and final.kind == "classification"
    assert final.triage.level == 5
    assert final.triage.care_channel.value == "self-care"
