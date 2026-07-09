# sns-voice-agent
A Voice-Agent Triage and Follow-up System for the Spanish Public Health System, with Co-official-Language Coverage and Accessibility for Atypical and Older-Adult Speech

See `MVP_PLAN.md` for the architecture this MVP implements, and
`thesis-proposals/` for the full design rationale.

## Install

```
pip install -e .
```

## Environment variables

The dialogue layer (added in a later slice) calls Gemini via the
`google-genai` SDK, which reads its API key from either:

- `GEMINI_API_KEY`, or
- `GOOGLE_API_KEY`

No key is required to install the package or run the test suite — the
deterministic core (findings schema, red-flag detector, SET engine) is
fully testable without the LLM.

## Tests

```
pytest
```

