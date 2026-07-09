from pathlib import Path

import pytest
import yaml

from triage.findings import ClinicalFindings
from triage.redflag import _RULES_PATH, check

_SUITE_PATH = Path(__file__).parent / "red_flag_suite.yaml"

_NON_MATCHING_FINDINGS = {
    "presenting_complaint": "fever",
    "pain_score": 1,
    "bleeding": "none",
    "consciousness": "alert",
    "breathing_difficulty": "none",
    "chest_pain": False,
    "chest_pain_radiating": False,
    "stroke_signs_fast": False,
    "allergic_reaction_severe": False,
    "suicidal_ideation": False,
}


def _load_rules() -> dict:
    return yaml.safe_load(_RULES_PATH.read_text())


def _load_suite() -> dict:
    return yaml.safe_load(_SUITE_PATH.read_text())


_RULES = _load_rules()["rules"]
_SCENARIOS = _load_suite()["scenarios"]


@pytest.mark.parametrize("rule", _RULES, ids=[r["id"] for r in _RULES])
def test_each_rule_fires_on_matching_findings(rule):
    findings = ClinicalFindings(**{**_NON_MATCHING_FINDINGS, **rule["conditions"]})
    result = check(findings)
    assert result.fired is True
    assert result.rule_id == rule["id"]
    assert result.rationale == rule["rationale"].strip()


@pytest.mark.parametrize("rule", _RULES, ids=[r["id"] for r in _RULES])
def test_each_rule_does_not_fire_on_non_matching_findings(rule):
    findings = ClinicalFindings(**_NON_MATCHING_FINDINGS)
    result = check(findings)
    assert result.fired is False
    assert result.rule_id is None
    assert result.rationale is None


@pytest.mark.parametrize("scenario", _SCENARIOS, ids=[s["name"] for s in _SCENARIOS])
def test_red_flag_suite_always_escalates(scenario):
    findings = ClinicalFindings(**scenario["findings"])
    result = check(findings)
    assert result.fired is True, f"scenario '{scenario['name']}' failed to escalate"


def test_rules_file_carries_a_version():
    rules = _load_rules()
    assert isinstance(rules["version"], str) and rules["version"]


def test_result_carries_rules_version_on_miss_and_hit():
    miss = check(ClinicalFindings(**_NON_MATCHING_FINDINGS))
    hit = check(
        ClinicalFindings(**{**_NON_MATCHING_FINDINGS, "suicidal_ideation": True})
    )
    assert miss.rules_version == _load_rules()["version"]
    assert hit.rules_version == _load_rules()["version"]
