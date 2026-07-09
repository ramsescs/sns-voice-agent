from pathlib import Path

import pytest
import yaml

from triage.findings import ClinicalFindings
from triage.set_engine import CareChannel, classify

VIGNETTES_PATH = Path(__file__).parent / "vignettes.yaml"


def _load_vignettes() -> list[dict]:
    with VIGNETTES_PATH.open() as f:
        return yaml.safe_load(f)


VIGNETTES = _load_vignettes()


@pytest.mark.parametrize("vignette", VIGNETTES, ids=lambda v: v["id"])
def test_vignette_classifies_as_expected(vignette):
    findings = ClinicalFindings(**vignette["findings"])
    result = classify(findings)

    assert result.level == vignette["expected_level"]
    assert result.care_channel == CareChannel(vignette["expected_care_channel"])
    assert result.uncertainty == vignette["expected_uncertainty"]
    assert result.rationale


def test_classify_is_pure():
    findings = ClinicalFindings(presenting_complaint="chest_pain", pain_score=9)
    assert classify(findings) == classify(findings)


@pytest.mark.parametrize(
    "complaint,least_urgent_defined_level",
    [
        ("chest_pain", 4),
        ("breathing_difficulty", 4),
        ("fever", 5),
        ("abdominal_pain", 5),
        ("wound", 5),
    ],
)
def test_missing_discriminators_over_triage_with_uncertainty(
    complaint, least_urgent_defined_level
):
    """Missing data must route upward (more urgent than the complaint's
    least-urgent defined band) and flag uncertainty, never under-triage."""
    findings = ClinicalFindings(presenting_complaint=complaint)
    result = classify(findings)

    assert result.uncertainty is True
    assert result.level < least_urgent_defined_level
    assert result.care_channel != CareChannel.SELF_CARE


def test_levels_are_within_set_range():
    for vignette in VIGNETTES:
        findings = ClinicalFindings(**vignette["findings"])
        result = classify(findings)
        assert 1 <= result.level <= 5
