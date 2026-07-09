"""Live smoke test for the Gemini conversation layer.

Skipped automatically when GEMINI_API_KEY is not set, so CI passes without
credentials. Run locally after placing the key in .env.
"""

import os

import pytest
from google import genai

from triage.dialogue import DEFAULT_MODEL, DialogueManager, DialogueTurn


@pytest.fixture(scope="module")
def manager():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")
    client = genai.Client(api_key=api_key)
    return DialogueManager(client)


def test_step_returns_a_dialogue_turn(manager):
    turn = manager.step("I have chest pain.")
    assert isinstance(turn, DialogueTurn)


def test_step_produces_a_reply_or_findings(manager):
    turn = manager.step("It started about an hour ago.")
    assert turn.reply_text or turn.findings


def test_model_calls_update_findings_at_some_point(manager):
    assert manager.findings is not None, (
        "Expected at least one update_findings call across the interview so far"
    )


def test_no_triage_level_in_reply_text(manager):
    turn = manager.step("The pain is about a 7 out of 10.")
    if turn.reply_text:
        lower = turn.reply_text.lower()
        forbidden = {
            "level 1",
            "level 2",
            "level 3",
            "level 4",
            "level 5",
            "urgent care",
            "emergency",
        }
        assert not any(phrase in lower for phrase in forbidden), (
            f"Model leaked a triage recommendation: {turn.reply_text!r}"
        )


def test_model_id_matches_default(manager):
    assert manager.model == DEFAULT_MODEL
