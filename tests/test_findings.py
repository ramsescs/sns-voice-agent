import pytest
from pydantic import ValidationError

from triage.findings import ClinicalFindings


def test_full_valid_findings_round_trips():
    data = {
        "presenting_complaint": "chest_pain",
        "pain_score": 7,
        "bleeding": "none",
        "consciousness": "alert",
        "breathing_difficulty": "mild",
        "chest_pain": True,
        "chest_pain_radiating": True,
        "stroke_signs_fast": False,
        "allergic_reaction_severe": False,
        "suicidal_ideation": False,
        "onset": "started 20 minutes ago",
    }
    findings = ClinicalFindings(**data)
    assert findings.model_dump() == data


def test_partial_findings_are_representable():
    findings = ClinicalFindings(presenting_complaint="fever")
    assert findings.presenting_complaint == "fever"
    assert findings.pain_score is None
    assert findings.bleeding is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"pain_score": -1},
        {"pain_score": 11},
        {"presenting_complaint": "headache"},
        {"bleeding": "a_lot"},
        {"consciousness": "asleep"},
        {"breathing_difficulty": "moderate"},
    ],
)
def test_invalid_input_is_rejected(overrides):
    data = {"presenting_complaint": "chest_pain", **overrides}
    with pytest.raises(ValidationError):
        ClinicalFindings(**data)


def test_no_triage_level_field_on_model():
    field_names = set(ClinicalFindings.model_fields)
    forbidden = {"level", "triage_level", "set_level"}
    assert field_names.isdisjoint(forbidden)
