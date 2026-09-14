import re
from pathlib import Path
from typing import get_args

import pytest

from src.modules.ideas.api.schemas import InitiativeType
from src.modules.ideas.domain.initiative import (
    INITIATIVE_TYPES,
    InitiativeTypeError,
    validate_initiative_type,
)

ADAPTER = Path(__file__).resolve().parents[3] / "src/modules/ideas/adapters/postgres.py"
MIGRATION = (
    Path(__file__).resolve().parents[3] / "alembic/versions/7b1f0c2e9a55_add_initiative_type.py"
)

EXPECTED = frozenset(
    {
        "idea",
        "hypothesis",
        "campaign",
        "opportunity",
        "decision",
        "experiment",
        "pricing",
        "market",
        "partnership",
        "internal_improvement",
    }
)


def test_the_domain_list_is_the_decided_set():
    assert INITIATIVE_TYPES == EXPECTED


def test_a_known_type_is_accepted():
    assert validate_initiative_type("campaign") == "campaign"


def test_an_unknown_type_is_refused():
    with pytest.raises(InitiativeTypeError):
        validate_initiative_type("startup")


def test_a_blank_type_is_refused():
    with pytest.raises(InitiativeTypeError):
        validate_initiative_type("   ")


def test_the_api_literal_mirrors_the_domain_list():
    assert frozenset(get_args(InitiativeType)) == INITIATIVE_TYPES


def test_the_database_check_mirrors_the_domain_list():
    constraint = ADAPTER.read_text()
    match = re.search(r'"initiative_type IN \(([^)]*)\)"', constraint)
    assert match is not None, "the adapter check constraint was not found"
    listed = frozenset(re.findall(r"'([a-z_]+)'", match.group(1)))
    assert listed == INITIATIVE_TYPES


def test_the_migration_mirrors_the_domain_list():
    migration = MIGRATION.read_text()
    listed = frozenset(re.findall(r'^\s{4}"([a-z_]+)",$', migration, flags=re.MULTILINE))
    assert listed == INITIATIVE_TYPES
