import pytest

from src.platform.embeddings import validate_vectors


def test_embedding_validation_rejects_count_mismatch():
    with pytest.raises(ValueError, match="count or index"):
        validate_vectors([[0.0, 1.0]], 2, 2)


def test_embedding_validation_rejects_dimension_mismatch():
    with pytest.raises(ValueError, match="dimension"):
        validate_vectors([[0.0]], 1, 2)
