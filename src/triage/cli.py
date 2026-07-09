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
