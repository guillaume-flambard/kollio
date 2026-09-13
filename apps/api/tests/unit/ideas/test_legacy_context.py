from src.modules.ideas.api.routes import legacy_context


def test_legacy_context_exposes_only_typed_prospecteur_fields():
    context = legacy_context(
        {
            "cle": "idea-key",
            "domaine": "AI teams",
            "verdict": "kill",
            "porte_fatale": "competition",
            "charge": '{"canal":"GitHub","pourquoi_maintenant":"Evaluation is maturing"}',
            "private_extra": "must not be exposed",
        }
    )

    assert context is not None
    assert context.model_dump() == {
        "source": "prospecteur",
        "source_id": "idea-key",
        "domain": "AI teams",
        "verdict": "kill",
        "fatal_constraint": "competition",
        "channel": "GitHub",
        "why_now": "Evaluation is maturing",
    }


def test_legacy_context_ignores_records_without_a_source_identifier():
    assert legacy_context({"charge": "not-json"}) is None
