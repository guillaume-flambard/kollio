"""Seed a deterministic Faktus workspace for the pilot demo path.

This is the "seeded workspace" the pilot acceptance (#62) starts from: one
Faktus company, its full company context (profile, objectives, constraints,
principles and metrics), two members and one deposited initiative with its
first iteration. Everything uses fixed uuid5 ids and upserts, so the seed is
idempotent and `--reset` removes exactly what it created. The demo then runs
deposit-adjacent steps onward in the interface, not here.
"""

import argparse
import asyncio
import hashlib
import json
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.modules.company_context.adapters.postgres import (
    CompanyConstraint,
    CompanyMetric,
    CompanyObjective,
    CompanyPrinciple,
    CompanyProfile,
)
from src.modules.ideas.adapters.postgres import Idea, User, Workspace, WorkspaceMembership
from src.modules.iterations.adapters.postgres import Iteration
from src.platform.config import get_settings

FAKTUS_WORKSPACE_ID = uuid5(NAMESPACE_URL, "kollio:faktus:workspace")
OWNER_ID = uuid5(NAMESPACE_URL, "kollio:faktus:user:camille")
CHALLENGER_ID = uuid5(NAMESPACE_URL, "kollio:faktus:user:jules")
IDEA_ID = uuid5(NAMESPACE_URL, "kollio:faktus:idea:offline-field-app")
LANG = "fr"


def _fid(kind: str, key: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"kollio:faktus:{kind}:{key}")


def ensure_seed_allowed(environment: str) -> None:
    if environment == "production":
        raise RuntimeError("The Faktus seed is disabled in production")


_PROFILE: dict[str, Any] = {
    "name": "Faktus",
    "description": "Un SaaS B2B qui transforme les signaux marketing épars en décisions.",
    "business_model": "Abonnement annuel, self-serve avec un accompagnement léger.",
    "products_services": "Application web et intégration Slack pour collecter les signaux clients.",
    "customer_segments": "Responsables marketing de B2B en amorçage, de 2 à 12 personnes.",
    "markets": "France et Europe germanophone.",
    "structure": "Neuf personnes, autofinancées, vente portée par la fondatrice.",
}

_OBJECTIVES: list[dict[str, Any]] = [
    {"key": "pilots", "title": "Signer cinq pilotes payants", "priority": True},
    {
        "key": "time-to-insight",
        "title": "Passer sous un jour pour le premier apprentissage d'une équipe",
        "priority": False,
    },
    {
        "key": "cadence",
        "title": "Lancer une expérience par équipe et par semaine",
        "priority": False,
    },
]

_CONSTRAINTS: list[dict[str, Any]] = [
    {"key": "bootstrapped", "title": "Autofinancé, pas de recrutement terrain", "detail": None},
    {
        "key": "team",
        "title": "Équipe produit de deux personnes",
        "detail": "Pas de recrutement pendant le pilote.",
    },
    {
        "key": "runway",
        "title": "Fenêtre de pilote de six semaines",
        "detail": "Après quoi la décision d'investissement est prise.",
    },
]

_PRINCIPLES: list[dict[str, Any]] = [
    {"key": "no-discount", "title": "Pas de croissance portée par la remise", "detail": None},
    {"key": "self-serve", "title": "Self-serve d'abord, pas de démo sous clé", "detail": None},
    {
        "key": "privacy",
        "title": "Les données d'un espace ne quittent jamais son locataire",
        "detail": None,
    },
]

_METRICS: list[dict[str, Any]] = [
    {
        "key": "activation",
        "name": "Taux d'activation",
        "value": "32",
        "unit": "%",
        "source": "Analytique produit",
    },
    {
        "key": "time-to-insight",
        "name": "Temps jusqu'au premier apprentissage",
        "value": "3",
        "unit": "jours",
        "source": "Journal des pilotes",
    },
    {
        "key": "experiments",
        "name": "Expériences par équipe et par semaine",
        "value": "1",
        "unit": "",
        "source": None,
    },
]

_MEMBERS: list[dict[str, Any]] = [
    {
        "id": OWNER_ID,
        "display_name": "Camille Laurent",
        "handle": "camille.l",
        "business_function": "marketing",
    },
    {
        "id": CHALLENGER_ID,
        "display_name": "Jules Martin",
        "handle": "jules.m",
        "business_function": "operations",
    },
]

_INITIATIVE: dict[str, Any] = {
    "title": "Compagnon mobile hors ligne pour équipes terrain",
    "pitch": (
        "Une application terrain qui ne bloque jamais quand le signal disparaît, pour que "
        "les équipes continuent de saisir leurs retours clients même sans réseau."
    ),
    "initiative_type": "hypothesis",
}


async def _upsert(
    session: AsyncSession, model: Any, values: dict[str, Any], keys: list[Any]
) -> None:
    await session.execute(
        insert(model).values(**values).on_conflict_do_update(index_elements=keys, set_=values)
    )


async def seed_faktus(session: AsyncSession) -> dict[str, int]:
    await _upsert(session, Workspace, {"id": FAKTUS_WORKSPACE_ID, "name": "Faktus"}, [Workspace.id])

    for member in _MEMBERS:
        user = {
            "id": member["id"],
            "auth_subject": None,
            "display_name": member["display_name"],
            "handle": member["handle"],
            "roles": [],
            "bio": None,
            "avatar_key": None,
            "is_demo": True,
        }
        await _upsert(session, User, user, [User.id])
        await session.execute(
            insert(WorkspaceMembership)
            .values(
                workspace_id=FAKTUS_WORKSPACE_ID,
                user_id=member["id"],
                role="admin" if member["id"] == OWNER_ID else "member",
            )
            .on_conflict_do_nothing()
        )

    await _upsert(
        session,
        CompanyProfile,
        {"workspace_id": FAKTUS_WORKSPACE_ID, "lang": LANG, **_PROFILE},
        [CompanyProfile.workspace_id],
    )

    for objective in _OBJECTIVES:
        await _upsert(
            session,
            CompanyObjective,
            {
                "id": _fid("objective", objective["key"]),
                "workspace_id": FAKTUS_WORKSPACE_ID,
                "title": objective["title"],
                "state": "active",
                "priority": objective["priority"],
                "lang": LANG,
            },
            [CompanyObjective.id],
        )

    for constraint in _CONSTRAINTS:
        await _upsert(
            session,
            CompanyConstraint,
            {
                "id": _fid("constraint", constraint["key"]),
                "workspace_id": FAKTUS_WORKSPACE_ID,
                "title": constraint["title"],
                "detail": constraint["detail"],
                "state": "active",
                "lang": LANG,
            },
            [CompanyConstraint.id],
        )

    for principle in _PRINCIPLES:
        await _upsert(
            session,
            CompanyPrinciple,
            {
                "id": _fid("principle", principle["key"]),
                "workspace_id": FAKTUS_WORKSPACE_ID,
                "title": principle["title"],
                "detail": principle["detail"],
                "state": "active",
                "lang": LANG,
            },
            [CompanyPrinciple.id],
        )

    for metric in _METRICS:
        await _upsert(
            session,
            CompanyMetric,
            {
                "id": _fid("metric", metric["key"]),
                "workspace_id": FAKTUS_WORKSPACE_ID,
                "name": metric["name"],
                "value": metric["value"],
                "unit": metric["unit"] or None,
                "observed_at": None,
                "source": metric["source"],
                "state": "active",
                "lang": LANG,
            },
            [CompanyMetric.id],
        )

    idea_values = {
        "id": IDEA_ID,
        "slug": f"faktus-{IDEA_ID.hex[:8]}",
        "title": _INITIATIVE["title"],
        "pitch": _INITIATIVE["pitch"],
        "owner_id": OWNER_ID,
        "workspace_id": FAKTUS_WORKSPACE_ID,
        "stage": "seed",
        "initiative_type": _INITIATIVE["initiative_type"],
        "lang": LANG,
        "visibility": "workspace",
        "source": None,
        "source_id": None,
        "provenance": {},
        "sought_roles": ["engineering"],
    }
    await _upsert(session, Idea, idea_values, [Idea.id])

    iteration_id = _fid("iteration", "head")
    await _upsert(
        session,
        Iteration,
        {
            "id": iteration_id,
            "idea_id": IDEA_ID,
            "parent_id": None,
            "author_id": OWNER_ID,
            "message": "Dépôt initial de l'initiative",
            "lang": LANG,
            "payload": {
                "title": idea_values["title"],
                "pitch": idea_values["pitch"],
                "stage": "seed",
            },
            "branch": "main",
            "proposal_status": None,
            "rationale": None,
            "short_hash": hashlib.sha256(iteration_id.bytes).hexdigest()[:12],
            "revision": 1,
        },
        [Iteration.id],
    )

    await session.flush()
    return {
        "workspace": 1,
        "members": len(_MEMBERS),
        "objectives": len(_OBJECTIVES),
        "constraints": len(_CONSTRAINTS),
        "principles": len(_PRINCIPLES),
        "metrics": len(_METRICS),
        "ideas": 1,
    }


async def reset_faktus(session: AsyncSession) -> dict[str, int]:
    user_ids = [member["id"] for member in _MEMBERS]
    await session.execute(delete(Iteration).where(Iteration.idea_id == IDEA_ID))
    await session.execute(delete(Idea).where(Idea.id == IDEA_ID))
    await session.execute(
        delete(CompanyMetric).where(CompanyMetric.workspace_id == FAKTUS_WORKSPACE_ID)
    )
    await session.execute(
        delete(CompanyPrinciple).where(CompanyPrinciple.workspace_id == FAKTUS_WORKSPACE_ID)
    )
    await session.execute(
        delete(CompanyConstraint).where(CompanyConstraint.workspace_id == FAKTUS_WORKSPACE_ID)
    )
    await session.execute(
        delete(CompanyObjective).where(CompanyObjective.workspace_id == FAKTUS_WORKSPACE_ID)
    )
    await session.execute(
        delete(CompanyProfile).where(CompanyProfile.workspace_id == FAKTUS_WORKSPACE_ID)
    )
    await session.execute(
        delete(WorkspaceMembership).where(WorkspaceMembership.workspace_id == FAKTUS_WORKSPACE_ID)
    )
    await session.execute(delete(Workspace).where(Workspace.id == FAKTUS_WORKSPACE_ID))
    await session.execute(delete(User).where(User.id.in_(user_ids)))
    return {"workspace": 1, "ideas": 1}


async def run(reset: bool) -> dict[str, int]:
    settings = get_settings()
    ensure_seed_allowed(settings.environment)
    engine = create_async_engine(settings.database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as session:
            return await (reset_faktus(session) if reset else seed_faktus(session))
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.reset))))
