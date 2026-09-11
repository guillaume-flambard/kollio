"""Import the approved Prospecteur snapshot without inventing product scores."""

import argparse
import asyncio
import hashlib
import json
from datetime import datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.ideas.adapters.postgres import Idea, User, Workspace
from src.platform.config import get_settings
from src.platform.db import Base

WORKSPACE_ID = uuid5(NAMESPACE_URL, "kollio:workspace:prospecteur")
IMPORTER_ID = uuid5(NAMESPACE_URL, "kollio:user:legacy-import")


class LegacyImport(Base):
    __tablename__ = "legacy_imports"
    snapshot_hash: Mapped[str] = mapped_column(primary_key=True)
    source: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSONB)


async def import_snapshot(path: Path):
    raw = await asyncio.to_thread(path.read_bytes)
    snapshot = json.loads(raw)
    if snapshot["source"] != "prospecteur":
        raise ValueError("Unsupported legacy source")
    digest = hashlib.sha256(raw).hexdigest()
    rows = snapshot["tables"]["idee"]
    engine = create_async_engine(get_settings().database_url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as session:
            await session.execute(
                insert(Workspace)
                .values(id=WORKSPACE_ID, name="Prospecteur import")
                .on_conflict_do_nothing()
            )
            await session.execute(
                insert(User)
                .values(
                    id=IMPORTER_ID,
                    display_name="Legacy importer",
                    auth_subject=None,
                )
                .on_conflict_do_nothing()
            )
            await session.execute(
                insert(LegacyImport)
                .values(
                    snapshot_hash=digest,
                    source="prospecteur",
                    payload=snapshot,
                )
                .on_conflict_do_nothing()
            )
            for row in rows:
                idea_id = uuid5(NAMESPACE_URL, "kollio:prospecteur:" + row["cle"])
                charge = json.loads(row["charge"])
                created_at = datetime.fromisoformat(row["cree_le"])
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=ZoneInfo(snapshot["source_timezone"]))
                pitch = "\n\n".join(
                    str(charge[key]) for key in ("probleme", "produit", "client") if charge.get(key)
                )
                await session.execute(
                    insert(Idea)
                    .values(
                        id=idea_id,
                        slug="prospecteur-" + idea_id.hex,
                        title=row["titre"],
                        pitch=pitch,
                        owner_id=IMPORTER_ID,
                        workspace_id=WORKSPACE_ID,
                        stage="seed",
                        lang="fr",
                        visibility="workspace",
                        created_at=created_at,
                        source="prospecteur",
                        source_id=row["cle"],
                        provenance=row,
                    )
                    .on_conflict_do_nothing()
                )
                actual = await session.get(Idea, idea_id)
                if (
                    actual is None
                    or actual.provenance != row
                    or actual.workspace_id != WORKSPACE_ID
                ):
                    raise ValueError(
                        "Existing idea conflicts with snapshot; no data was overwritten"
                    )
            imported = (
                await session.scalars(select(Idea.source_id).where(Idea.source == "prospecteur"))
            ).all()
            if not {row["cle"] for row in rows}.issubset(set(imported)):
                raise ValueError("Import reconciliation failed")
        return {"snapshot_hash": digest, "ideas": len(rows), "workspace_id": str(WORKSPACE_ID)}
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(import_snapshot(args.snapshot))))
