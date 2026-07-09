from types import SimpleNamespace

from triage.dialogue import DEFAULT_MODEL, DialogueManager, TOOLS
from triage.findings import ClinicalFindings


def _function_call(name, args):
    return SimpleNamespace(name=name, args=args)


def _part(*, function_call=None, text=None):
    return SimpleNamespace(function_call=function_call, text=text)


def _response(parts):
    content = SimpleNamespace(role="model", parts=parts)
    candidate = SimpleNamespace(content=content)
    return SimpleNamespace(candidates=[candidate])


class _FakeClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


def test_update_findings_tool_call_becomes_validated_findings_update():
    args = {"presenting_complaint": "chest_pain", "pain_score": 7}
    response1 = _response([_part(function_call=_function_call("update_findings", args))])
    response2 = _response([_part(text="Got it.")])
    client = _FakeClient([response1, response2])
    manager = DialogueManager(client)

    turn = manager.step("My chest hurts a lot.")

    assert turn.findings == ClinicalFindings(
        presenting_complaint="chest_pain", pain_score=7
    )
    assert turn.rejected_update is None
    assert manager.findings == turn.findings


def test_invalid_update_findings_payload_is_rejected_without_corrupting_state():
    good_args = {"presenting_complaint": "chest_pain", "pain_score": 3}
    bad_args = {"pain_score": 99}
    responses = [
        _response([_part(function_call=_function_call("update_findings", good_args))]),
        _response([_part(text="OK.")]),
        _response([_part(function_call=_function_call("update_findings", bad_args))]),
        _response([_part(text="Got it.")]),
    ]
    client = _FakeClient(responses)
    manager = DialogueManager(client)

    manager.step("My chest hurts.")
    turn = manager.step("It's about a 99 out of 10.")

    assert turn.findings is None
    assert turn.rejected_update is not None
    assert manager.findings == ClinicalFindings(
        presenting_complaint="chest_pain", pain_score=3
    )


def test_update_findings_merges_partial_updates_across_turns():
    responses = [
        _response(
            [
                _part(
                    function_call=_function_call(
                        "update_findings", {"presenting_complaint": "fever"}
                    )
                )
            ]
        ),
        _response([_part(text="Okay.")]),
        _response(
            [
                _part(
                    function_call=_function_call(
                        "update_findings", {"onset": "since yesterday"}
                    )
                )
            ]
        ),
        _response([_part(text="Thanks.")]),
    ]
    client = _FakeClient(responses)
    manager = DialogueManager(client)

    manager.step("I have a fever.")
    turn = manager.step("It started yesterday.")

    assert turn.findings == ClinicalFindings(
        presenting_complaint="fever", onset="since yesterday"
    )


def test_finalize_is_recognised_and_surfaced():
    response = _response([_part(function_call=_function_call("finalize", {}))])
    client = _FakeClient([response])
    manager = DialogueManager(client)

    turn = manager.step("That's everything.")

    assert turn.finalized is True
    assert turn.findings is None


def test_text_reply_is_surfaced_without_a_tool_call():
    response = _response([_part(text="Can you describe the pain?")])
    client = _FakeClient([response])
    manager = DialogueManager(client)

    turn = manager.step("My chest hurts.")

    assert turn.reply_text == "Can you describe the pain?"
    assert turn.finalized is False
    assert turn.findings is None


def test_no_code_path_produces_a_triage_level():
    forbidden = {"level", "triage_level", "set_level", "care_channel", "urgency"}
    assert forbidden.isdisjoint(ClinicalFindings.model_fields)

    declared_params = set()
    for declaration in TOOLS[0].function_declarations:
        if declaration.parameters and declaration.parameters.properties:
            declared_params.update(declaration.parameters.properties)
    assert forbidden.isdisjoint(declared_params)


def test_model_id_is_exposed_for_the_audit_log():
    client = _FakeClient([])
    manager = DialogueManager(client)
    assert manager.model == DEFAULT_MODEL

    other = DialogueManager(client, model="gemini-2.5-pro")
    assert other.model == "gemini-2.5-pro"
