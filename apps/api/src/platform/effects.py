import hashlib
import json
from datetime import datetime

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from src.platform.db import Base


class AgentResult(Base):
    __tablename__ = "agent_results"
    workflow_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    step_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    input_hash: Mapped[str]
    result: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


async def save_result(
    sessions: async_sessionmaker, workflow_id: str, step_id: str, input_data: dict, result: dict
) -> dict:
    digest = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
    async with sessions.begin() as session:
        await session.execute(
            insert(AgentResult)
            .values(
                workflow_id=workflow_id,
                step_id=step_id,
                input_hash=digest,
                result=result,
            )
            .on_conflict_do_nothing()
        )
        saved = (
            await session.execute(
                select(AgentResult).where(
                    AgentResult.workflow_id == workflow_id,
                    AgentResult.step_id == step_id,
                )
            )
        ).scalar_one()
        if saved.input_hash != digest:
            raise ValueError("Idempotency key reused for a different input")
        return saved.result
