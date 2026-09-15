import json
import math
from pathlib import Path

import pytest

from src.platform.config import Settings
from src.platform.embeddings import format_passage, format_query, validate_vectors

LOCAL_RETRIEVAL_FIXTURE = (
    Path(__file__).parent.parent / "evals" / "fixtures" / "local_retrieval.fr_en.json"
)


def cosine(left: list[float], right: list[float]) -> float:
    norm = math.sqrt(sum(value * value for value in left) * sum(value * value for value in right))
    return sum(a * b for a, b in zip(left, right, strict=True)) / norm


def test_embedding_validation_rejects_count_mismatch():
    with pytest.raises(ValueError, match="count or index"):
        validate_vectors([[0.0, 1.0]], 2, 2)


def test_embedding_validation_rejects_dimension_mismatch():
    with pytest.raises(ValueError, match="dimension"):
        validate_vectors([[0.0]], 1, 2)


def test_default_active_space_is_local_multilingual():
    settings = Settings(_env_file=None, environment="development", database_url="")
    assert settings.embedding_model == "kollio-embedding-local"
    assert settings.embedding_source_model == "intfloat/multilingual-e5-small"
    assert settings.embedding_dimensions == 384
    validate_vectors([[0.0] * 384], 1, settings.embedding_dimensions)


def test_openai_space_remains_explicitly_selectable():
    settings = Settings(
        _env_file=None,
        environment="development",
        database_url="",
        embedding_model="kollio-embedding",
        embedding_source_model="text-embedding-3-large",
        embedding_dimensions=1536,
    )
    assert settings.embedding_dimensions == 1536
    with pytest.raises(ValueError, match="dimension"):
        validate_vectors([[0.0] * 384], 1, settings.embedding_dimensions)


def test_e5_prefix_helpers_use_configured_prefixes():
    settings = Settings(_env_file=None, environment="development", database_url="")
    assert format_query("lancer une campagne", settings) == "query: lancer une campagne"
    assert format_passage("launch a campaign", settings) == "passage: launch a campaign"


def test_openai_space_uses_no_prefix():
    settings = Settings(
        _env_file=None,
        environment="development",
        database_url="",
        embedding_model="kollio-embedding",
        embedding_source_model="text-embedding-3-large",
        embedding_dimensions=1536,
        embedding_query_prefix="",
        embedding_passage_prefix="",
    )
    assert format_query("lancer une campagne", settings) == "lancer une campagne"
    assert format_passage("launch a campaign", settings) == "launch a campaign"


def test_recorded_local_retrieval_ranks_expected_counterpart_first():
    """Replay of the 2026-09-15 live TEI recording: no network, no server."""
    recording = json.loads(LOCAL_RETRIEVAL_FIXTURE.read_text())
    assert recording["provenance"]["dimensions"] == 384
    assert recording["provenance"]["source_model"] == "intfloat/multilingual-e5-small"
    settings = Settings(_env_file=None, environment="development", database_url="")
    assert settings.embedding_dimensions == recording["provenance"]["dimensions"]
    assert settings.embedding_source_model == recording["provenance"]["source_model"]
    cases = recording["cases"]
    validate_vectors([case["vector"] for case in cases], len(cases), 384)
    query = cases[recording["query_index"]]["vector"]
    expected = cases[recording["expected_index"]]["vector"]
    expected_score = cosine(query, expected)
    for index, case in enumerate(cases):
        if index in (recording["query_index"], recording["expected_index"]):
            continue
        assert expected_score > cosine(query, case["vector"])
