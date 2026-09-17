from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    delete,
    func,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.ideas.adapters.postgres import User, WorkspaceMembership
from src.modules.options.adapters.postgres import Option, OptionEvidence
from src.platform.db import Base

LANG_CHECK = "lang IN ('fr', 'en')"
NAME_CHECK = "length(btrim(name)) > 0"
RANGE_CHECK = "low <= base AND base <= high"
LEVEL_CHECK = "level IN ('optimistic', 'base', 'pessimistic', 'failure')"
ASSUMPTIONS_CHECK = "length(btrim(assumptions)) > 0"


class ScenarioVariable(Base):
    __tablename__ = "scenario_variables"
    __table_args__ = (
        UniqueConstraint("space_id", "name", name="scenario_variables_space_id_name_key"),
        CheckConstraint(NAME_CHECK),
        CheckConstraint(RANGE_CHECK),
        CheckConstraint(LANG_CHECK),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    unit: Mapped[str | None] = mapped_column(String(40))
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    base: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ScenarioRun(Base):
    __tablename__ = "scenario_runs"
    __table_args__ = (
        CheckConstraint(LEVEL_CHECK),
        CheckConstraint(ASSUMPTIONS_CHECK),
        CheckConstraint(LANG_CHECK),
        Index(
            "scenario_runs_one_base_per_option",
            "option_id",
            unique=True,
            postgresql_where=text("level = 'base'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    option_id: Mapped[UUID] = mapped_column(
        ForeignKey("options.id", ondelete="CASCADE"), index=True
    )
    level: Mapped[str] = mapped_column(String(20))
    assumptions: Mapped[str] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ScenarioRunValue(Base):
    __tablename__ = "scenario_run_values"
    __table_args__ = (CheckConstraint("value IS NOT NULL"),)

    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("scenario_runs.id", ondelete="CASCADE"), primary_key=True
    )
    variable_id: Mapped[UUID] = mapped_column(
        ForeignKey("scenario_variables.id", ondelete="CASCADE"), primary_key=True
    )
    value: Mapped[Decimal] = mapped_column(Numeric(18, 6))


class PostgresScenarios:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def memberships(self, subject: str) -> frozenset[UUID]:
        rows = await self.session.execute(
            select(WorkspaceMembership.workspace_id)
            .join(User, User.id == WorkspaceMembership.user_id)
            .where(User.auth_subject == subject)
        )
        return frozenset(rows.scalars().all())

    async def user_for_subject(self, subject: str) -> User | None:
        return await self.session.scalar(select(User).where(User.auth_subject == subject))

    async def space(self, workspace_id: UUID, space_id: UUID) -> DecisionSpace | None:
        return await self.session.scalar(
            select(DecisionSpace).where(
                DecisionSpace.id == space_id,
                DecisionSpace.workspace_id == workspace_id,
            )
        )

    async def participant_ids(self, space_id: UUID) -> frozenset[UUID]:
        rows = await self.session.execute(
            select(DecisionSpaceParticipant.user_id).where(
                DecisionSpaceParticipant.space_id == space_id
            )
        )
        return frozenset(rows.scalars().all())

    async def option(self, space_id: UUID, option_id: UUID) -> Option | None:
        return await self.session.scalar(
            select(Option).where(Option.id == option_id, Option.space_id == space_id)
        )

    async def variables(self, space_id: UUID) -> list[ScenarioVariable]:
        rows = await self.session.execute(
            select(ScenarioVariable)
            .where(ScenarioVariable.space_id == space_id)
            .order_by(ScenarioVariable.name, ScenarioVariable.id)
        )
        return list(rows.scalars().all())

    async def variable(self, space_id: UUID, variable_id: UUID) -> ScenarioVariable | None:
        return await self.session.scalar(
            select(ScenarioVariable).where(
                ScenarioVariable.id == variable_id,
                ScenarioVariable.space_id == space_id,
            )
        )

    async def variable_name_taken(
        self, space_id: UUID, name: str, *, excluding: UUID | None = None
    ) -> bool:
        query = select(ScenarioVariable.id).where(
            ScenarioVariable.space_id == space_id, ScenarioVariable.name == name
        )
        if excluding is not None:
            query = query.where(ScenarioVariable.id != excluding)
        return await self.session.scalar(query) is not None

    async def create_variable(
        self,
        *,
        space_id: UUID,
        name: str,
        unit: str | None,
        low: Decimal,
        base: Decimal,
        high: Decimal,
        lang: str,
    ) -> ScenarioVariable:
        variable = ScenarioVariable(
            space_id=space_id,
            name=name,
            unit=unit,
            low=low,
            base=base,
            high=high,
            lang=lang,
        )
        self.session.add(variable)
        await self.session.flush()
        return variable

    async def update_variable(
        self,
        variable: ScenarioVariable,
        *,
        name: str,
        unit: str | None,
        low: Decimal,
        base: Decimal,
        high: Decimal,
    ) -> ScenarioVariable:
        variable.name = name
        variable.unit = unit
        variable.low = low
        variable.base = base
        variable.high = high
        await self.session.flush()
        await self.session.refresh(variable)
        return variable

    async def delete_variable(self, variable: ScenarioVariable) -> None:
        await self.session.delete(variable)
        await self.session.flush()

    async def runs(self, option_id: UUID) -> list[ScenarioRun]:
        rows = await self.session.execute(
            select(ScenarioRun)
            .where(ScenarioRun.option_id == option_id)
            .order_by(ScenarioRun.created_at, ScenarioRun.id)
        )
        return list(rows.scalars().all())

    async def run(self, option_id: UUID, run_id: UUID) -> ScenarioRun | None:
        return await self.session.scalar(
            select(ScenarioRun).where(ScenarioRun.id == run_id, ScenarioRun.option_id == option_id)
        )

    async def run_levels(self, option_id: UUID) -> frozenset[str]:
        rows = await self.session.execute(
            select(ScenarioRun.level).where(ScenarioRun.option_id == option_id)
        )
        return frozenset(rows.scalars().all())

    async def create_run(
        self,
        *,
        option_id: UUID,
        space_id: UUID,
        level: str,
        assumptions: str,
        created_by: UUID,
        lang: str,
        values: list[tuple[UUID, Decimal]],
    ) -> ScenarioRun:
        run = ScenarioRun(
            option_id=option_id,
            level=level,
            assumptions=assumptions,
            created_by=created_by,
            lang=lang,
        )
        self.session.add(run)
        await self.session.flush()
        await self._write_values(run.id, space_id, values)
        return run

    async def update_run(
        self,
        run: ScenarioRun,
        *,
        space_id: UUID,
        level: str,
        assumptions: str,
        values: list[tuple[UUID, Decimal]],
    ) -> ScenarioRun:
        run.level = level
        run.assumptions = assumptions
        await self.session.flush()
        await self._write_values(run.id, space_id, values)
        await self.session.refresh(run)
        return run

    async def delete_run(self, run: ScenarioRun) -> None:
        await self.session.delete(run)
        await self.session.flush()

    async def values(self, run_id: UUID) -> dict[UUID, Decimal]:
        rows = await self.session.execute(
            select(ScenarioRunValue.variable_id, ScenarioRunValue.value).where(
                ScenarioRunValue.run_id == run_id
            )
        )
        return {variable_id: value for variable_id, value in rows.all()}

    async def runs_with_values(self, option_id: UUID) -> list[tuple[UUID, dict[UUID, Decimal]]]:
        return [(run.id, await self.values(run.id)) for run in await self.runs(option_id)]

    async def evidence_counts(self, option_id: UUID) -> tuple[int, int]:
        rows = await self.session.execute(
            select(OptionEvidence.side, func.count())
            .where(OptionEvidence.option_id == option_id)
            .group_by(OptionEvidence.side)
        )
        counts = {side: count for side, count in rows.all()}
        return counts.get("for", 0), counts.get("against", 0)

    async def _write_values(
        self, run_id: UUID, space_id: UUID, values: list[tuple[UUID, Decimal]]
    ) -> None:
        await self.session.execute(
            delete(ScenarioRunValue).where(ScenarioRunValue.run_id == run_id)
        )
        if not values:
            return
        owned = await self.session.execute(
            select(ScenarioVariable.id).where(
                ScenarioVariable.space_id == space_id,
                ScenarioVariable.id.in_([variable_id for variable_id, _ in values]),
            )
        )
        owned_ids = set(owned.scalars().all())
        for variable_id, value in values:
            if variable_id not in owned_ids:
                continue
            self.session.add(ScenarioRunValue(run_id=run_id, variable_id=variable_id, value=value))
        await self.session.flush()
