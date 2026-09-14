"""Seed deterministic collaboration profiles for local product development."""

import argparse
import asyncio
import hashlib
import json
from datetime import timedelta
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.modules.ideas.adapters.postgres import (
    Idea,
    IdeaMembership,
    User,
    WorkspaceMembership,
)
from src.platform.config import get_settings
from src.platform.import_legacy import WORKSPACE_ID

DEMO_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "handle": "camille.l",
        "display_name": "Camille Laurent",
        "roles": ["product", "strategy"],
        "bio": "Turns early signals into focused product experiments.",
        "avatar_key": "lilac",
        "business_function": "product",
    },
    {
        "handle": "sofia.p",
        "display_name": "Sofia Pereira",
        "roles": ["design", "research"],
        "bio": "Designs clear product flows from messy user needs.",
        "avatar_key": "rose",
        "business_function": "product",
    },
    {
        "handle": "malik.k",
        "display_name": "Malik Kone",
        "roles": ["engineering", "platform"],
        "bio": "Builds reliable product foundations and developer tools.",
        "avatar_key": "ochre",
        "business_function": "engineering",
    },
    {
        "handle": "noor.r",
        "display_name": "Noor Rahman",
        "roles": ["ai", "data"],
        "bio": "Tests where applied AI creates measurable product value.",
        "avatar_key": "citron",
        "business_function": "data",
    },
    {
        "handle": "elena.r",
        "display_name": "Elena Rossi",
        "roles": ["growth", "sales"],
        "bio": "Finds practical routes from a useful idea to its first customers.",
        "avatar_key": "coral",
        "business_function": "marketing",
    },
    {
        "handle": "jules.m",
        "display_name": "Jules Martin",
        "roles": ["operations", "finance"],
        "bio": "Challenges assumptions with operational and financial evidence.",
        "avatar_key": "sage",
        "business_function": "operations",
    },
)


def demo_user_id(handle: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"kollio:demo-user:{handle}")


def ensure_demo_data_allowed(environment: str) -> None:
    if environment == "production":
        raise RuntimeError("Demo data is disabled in production")


async def seed_demo_data(session: AsyncSession) -> dict[str, int]:
    profile_ids = [demo_user_id(profile["handle"]) for profile in DEMO_PROFILES]
    for profile, user_id in zip(DEMO_PROFILES, profile_ids, strict=True):
        values = {
            "id": user_id,
            "auth_subject": None,
            "display_name": profile["display_name"],
            "handle": profile["handle"],
            "roles": profile["roles"],
            "bio": profile["bio"],
            "avatar_key": profile["avatar_key"],
            "is_demo": True,
        }
        await session.execute(
            insert(User)
            .values(**values)
            .on_conflict_do_update(index_elements=[User.id], set_=values)
        )
        await session.execute(
            insert(WorkspaceMembership)
            .values(workspace_id=WORKSPACE_ID, user_id=user_id, role="member")
            .on_conflict_do_nothing()
        )

    ideas = list(
        (
            await session.scalars(
                select(Idea)
                .where(Idea.workspace_id == WORKSPACE_ID, Idea.source == "prospecteur")
                .order_by(Idea.created_at.desc(), Idea.id)
            )
        ).all()
    )
    membership_count = 0
    for idea in ideas:
        digest = hashlib.sha256(idea.id.bytes).digest()
        member_count = 2 + digest[0] % 3
        start = digest[1] % len(DEMO_PROFILES)
        stage = (
            "team_formed" if digest[2] % 11 == 0 else "iterating" if digest[2] % 3 == 0 else "seed"
        )
        if idea.stage != stage:
            idea.stage = stage
        for offset in range(member_count):
            profile_index = (start + offset) % len(DEMO_PROFILES)
            profile = DEMO_PROFILES[profile_index]
            joined_at = idea.created_at + timedelta(hours=profile_index + 1)
            await session.execute(
                insert(IdeaMembership)
                .values(
                    idea_id=idea.id,
                    user_id=profile_ids[profile_index],
                    participation="contributor",
                    business_function=profile["business_function"],
                    joined_at=joined_at,
                )
                .on_conflict_do_update(
                    index_elements=[IdeaMembership.idea_id, IdeaMembership.user_id],
                    set_={
                        "participation": "contributor",
                        "business_function": profile["business_function"],
                        "joined_at": joined_at,
                    },
                )
            )
            membership_count += 1
    await session.flush()
    return {"users": len(DEMO_PROFILES), "ideas": len(ideas), "memberships": membership_count}


async def reset_demo_data(session: AsyncSession) -> dict[str, int]:
    profile_ids = [demo_user_id(profile["handle"]) for profile in DEMO_PROFILES]
    memberships = await session.execute(
        delete(IdeaMembership).where(IdeaMembership.user_id.in_(profile_ids))
    )
    await session.execute(
        delete(WorkspaceMembership).where(WorkspaceMembership.user_id.in_(profile_ids))
    )
    users = await session.execute(delete(User).where(User.id.in_(profile_ids)))
    await session.execute(
        update(Idea)
        .where(Idea.workspace_id == WORKSPACE_ID, Idea.source == "prospecteur")
        .values(stage="seed")
    )
    return {
        "users": users.rowcount or 0,
        "memberships": memberships.rowcount or 0,
    }


async def run(reset: bool) -> dict[str, int]:
    settings = get_settings()
    ensure_demo_data_allowed(settings.environment)
    engine = create_async_engine(settings.database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as session:
            return await (reset_demo_data(session) if reset else seed_demo_data(session))
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.reset))))
