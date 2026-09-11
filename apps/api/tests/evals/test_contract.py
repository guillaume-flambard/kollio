import pytest
from pydantic import ValidationError

from src.agents.schemas import GateFinding
from src.platform.llm import validate_finding


def test_unstructured_llm_output_is_rejected():
    with pytest.raises(ValidationError):
        GateFinding.model_validate({"verdict": "yes", "reason": "Trust me"})


def test_unapproved_llm_fields_are_rejected():
    with pytest.raises(ValidationError):
        GateFinding.model_validate(
            {
                "verdict": "unknown",
                "reason": "Missing evidence",
                "source_ids": [],
                "established_facts": [],
                "locale": "en",
                "execute": "send_email",
            }
        )


def test_unknown_evidence_identifier_is_rejected_before_side_effects():
    finding = GateFinding(
        verdict="kill",
        reason="A named product already serves the same workflow.",
        source_ids=["unknown-source"],
        established_facts=[],
        locale="en",
    )
    with pytest.raises(ValueError, match="unknown evidence"):
        validate_finding(finding, "en", {"known-source"})


def test_wrong_locale_is_rejected_before_side_effects():
    finding = GateFinding(
        verdict="unknown",
        reason="Les preuves sont insuffisantes.",
        source_ids=[],
        established_facts=[],
        locale="fr",
    )
    with pytest.raises(ValueError, match="wrong locale"):
        validate_finding(finding, "en", set())
