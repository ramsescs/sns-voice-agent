# Implementation plan — Orchestrator + CLI (issue 006)

> Handoff spec for the Antigravity CLI coding agent. Self-contained: every
> interface it needs is quoted below, so it does not need to re-read the whole
> package. Implements `issues/006-orchestrator-cli.md`.

## Context

The triage core already exists and is tested in isolation: `findings.py`
(Pydantic contract), `dialogue.py` (Gemini interview → findings, never a level),
`redflag.py` (deterministic 112 bypass), `set_engine.py` (deterministic SET
mapping). What's missing is the piece that wires them into one runnable flow and
a text entrypoint. `orchestrator.py`, `cli.py` are currently one-line stubs.

The point of this slice is the **genuine red-flag bypass**: control flow and
level assignment are deterministic Python; only findings *extraction* is
LLM-mediated. After every findings update, `redflag.check` runs and a hit ends
the call before any further question or finalize.

**Deviation from issue 006 (approved):** the audit-log wiring is **out of scope
for now** — skip AC #4 and the audit assertions in the integration test. Leave a
seam (a TODO at each terminal point) so `audit.py` can be added later without
reshaping the loop.

## Scope

Build exactly two files and one test:

- `src/triage/orchestrator.py` — deterministic control loop.
- `src/triage/cli.py` — `python -m triage.cli` text entrypoint.
- `tests/test_orchestrator.py` — AFK integration test with a mocked dialogue.

Do **not** touch `findings.py`, `dialogue.py`, `redflag.py`, `set_engine.py`, or
the `rules/*.yaml`. Match the existing style: `from __future__ import
annotations`, module docstring, dataclasses, type hints.

## Interfaces you depend on (already implemented — do not change)

```python
# triage.findings
class ClinicalFindings(BaseModel):
    presenting_complaint: PresentingComplaint          # required
    pain_score: Optional[int]                          # 0..10
    bleeding / consciousness / breathing_difficulty: enums
    chest_pain / chest_pain_radiating / stroke_signs_fast: Optional[bool]
    allergic_reaction_severe / suicidal_ideation: Optional[bool]
    onset: Optional[str]

# triage.dialogue
class DialogueTurn:            # dataclass
    reply_text: Optional[str] = None          # model's next question
    findings: Optional[ClinicalFindings] = None  # set only when updated this turn
    rejected_update: Optional[str] = None
    finalized: bool = False

class DialogueManager:
    def __init__(self, client, model="gemini-2.5-flash"): ...
    findings: Optional[ClinicalFindings]      # accumulated across turns
    model: str
    def step(self, user_text: str) -> DialogueTurn: ...

# triage.redflag
@dataclass(frozen=True)
class RedFlagResult:
    fired: bool; rule_id: Optional[str]; rationale: Optional[str]; rules_version: str
def check(findings: ClinicalFindings) -> RedFlagResult   # pure

# triage.set_engine
class CareChannel(str, Enum):   # .value in {"self-care","primary-care appointment","urgent care","emergency/112"}
class TriageResult(BaseModel):
    level: int; care_channel: CareChannel; rationale: str; uncertainty: bool
def classify(findings: ClinicalFindings) -> TriageResult  # pure
```

The orchestrator depends only on the `dialogue` object's **duck-typed surface**
(`.step()`, `.findings`, `.model`) so the test can pass a fake without a Gemini
client.

## `src/triage/orchestrator.py`

Loop per the plan (`MVP_PLAN.md` §Key components 5): red-flag bypass first, then
finalize→classify, else continue the interview. Greeting is AI-disclosure (AI Act
Art. 50). Inject `redflag.check` / `set_engine.classify` as defaults so tests can
override them, but the default wiring uses the real deterministic functions.

```python
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
```

Key correctness points:
- Red-flag check is **before** finalize in the same turn, so if a turn both
  updates findings and finalizes, a fired red flag wins (AC #2).
- `self._ended` makes a second `handle_turn` after any terminal outcome raise —
  the call is truly over (AC #2).
- Classification reads `self._dialogue.findings` (the accumulated findings), not
  `turn.findings` (which is None on a finalize-only turn).

## `src/triage/cli.py`

```python
"""Text chat entrypoint: `python -m triage.cli`.

Thin wrapper over the orchestrator using input()/print(); this is the seam a
voice STT/TTS adapter replaces later. Reads GEMINI_API_KEY (or GOOGLE_API_KEY).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai

from triage.dialogue import DialogueManager
from triage.orchestrator import Orchestrator


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("Set GEMINI_API_KEY (or GOOGLE_API_KEY) in your environment or .env")

    orch = Orchestrator(DialogueManager(genai.Client(api_key=api_key)))
    print(orch.greeting)
    while True:
        try:
            user = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[call ended]")
            return
        if not user:
            continue
        out = orch.handle_turn(user)
        if out.reply_text:
            print(f"agent> {out.reply_text}")
        if out.ended:
            print(f"\nagent> {out.message}")
            return


if __name__ == "__main__":
    main()
```

Greeting prints **before** the first `input()` (AC #1).

## `tests/test_orchestrator.py` (AFK, no API key)

Uses a scripted `FakeDialogue` for control flow but the **real** `redflag.check`
and `set_engine.classify`, so the findings below must genuinely fire / classify
against the current `rules/*.yaml`:
- `chest_pain` + `chest_pain_radiating=True` → red-flag rule `chest_pain_radiating` fires.
- `fever` + `pain_score=2` → no red flag; SET rule `fever_low_pain` → level 5, `self-care`.

```python
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
```

## Verification

```bash
pip install -e .                 # src-layout; makes `triage` importable
pytest tests/test_orchestrator.py   # AFK, no API key — must pass
pytest                              # whole suite still green
```

Manual live smoke test (HITL, needs `GEMINI_API_KEY` in env or `.env`):

```bash
python -m triage.cli
```
- "chest pain radiating to my left arm" → immediate 112 escalation, call ends.
- "mild sore throat, no fever" → SET level + self-care / primary-care outcome.

## Acceptance checklist (issue 006, audit rows deferred)

- [x] AC #1 greeting before first question — CLI prints `orch.greeting` first.
- [x] AC #2 red-flag hit → 112, ends call immediately, before finalize.
- [x] AC #3 finalize (no red flag) → SET level + channel + rationale as text.
- [ ] AC #4 audit JSON — **deferred; seam left as TODO.**
- [x] AC #5 `python -m triage.cli` runs interactively end to end.
- [x] AC #6 integration test: mocked dialogue, both paths (audit assertion dropped).
