from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.branches.adapters.postgres import Contribution
from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.ideas.adapters.postgres import User, WorkspaceMembership
from src.modules.options.adapters.postgres import Option
from src.platform.db import Base

RUN_STATUS_CHECK = "status IN ('OPEN', 'RUNNING', 'COMPLETED', 'FAILED')"
KIND_CHECK = (
    "kind IN ('unsupported_assumption', 'contradictory_evidence', 'hidden_dependency', "
    "'failure_mode', 'causal_claim', 'missing_success_criteria')"
)
SEVERITY_CHECK = "severity IN ('low', 'medium', 'high')"
ORIGIN_CHECK = "origin IN ('human', 'critic')"
FINDING_STATUS_CHECK = "status IN ('proposed', 'confirmed', 'dismissed')"
DETAIL_CHECK = "length(btrim(detail)) > 0"
LANG_CHECK = "lang IN ('fr', 'en')"


class ChallengeRun(Base):
    __tablename__ = "challenge_runs"
    __table_args__ = (
        CheckConstraint(RUN_STATUS_CHECK),
        CheckConstraint(LANG_CHECK),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    space_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_spaces.id", ondelete="CASCADE"), index=True
    )
    option_id: Mapped[UUID] = mapped_column(
        ForeignKey("options.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(12))
    opened_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    model: Mapped[str | None] = mapped_column(String(200))
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChallengeFinding(Base):
    __tablename__ = "challenge_findings"
    __table_args__ = (
        CheckConstraint(KIND_CHECK),
        CheckConstraint(SEVERITY_CHECK),
        CheckConstraint(ORIGIN_CHECK),
        CheckConstraint(FINDING_STATUS_CHECK),
        CheckConstraint(DETAIL_CHECK),
        CheckConstraint(LANG_CHECK),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("challenge_runs.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(10))
    detail: Mapped[str] = mapped_column(Text)
    origin: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(12))
    contribution_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("contributions.id", ondelete="SET NULL")
    )
    lang: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PostgresChallenge:
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

    async def space(self, space_id: UUID) -> DecisionSpace | None:
        return await self.session.get(DecisionSpace, space_id)

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

    async def contribution(self, space_id: UUID, contribution_id: UUID) -> Contribution | None:
        return await self.session.scalar(
            select(Contribution).where(
                Contribution.id == contribution_id,
                Contribution.space_id == space_id,
            )
        )

    async def create_run(
        self, *, space_id: UUID, option_id: UUID, opened_by: UUID, lang: str
    ) -> ChallengeRun:
        run = ChallengeRun(
            space_id=space_id,
            option_id=option_id,
            status="RUNNING",
            opened_by=opened_by,
            model=None,
            lang=lang,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def run(self, option_id: UUID, run_id: UUID) -> ChallengeRun | None:
        return await self.session.scalar(
            select(ChallengeRun).where(
                ChallengeRun.id == run_id, ChallengeRun.option_id == option_id
            )
        )

    async def list_runs(self, option_id: UUID) -> list[ChallengeRun]:
        rows = await self.session.execute(
            select(ChallengeRun)
            .where(ChallengeRun.option_id == option_id)
            .order_by(ChallengeRun.created_at, ChallengeRun.id)
        )
        return list(rows.scalars().all())

    async def findings(self, run_id: UUID) -> list[ChallengeFinding]:
        rows = await self.session.execute(
            select(ChallengeFinding)
            .where(ChallengeFinding.run_id == run_id)
            .order_by(ChallengeFinding.created_at, ChallengeFinding.id)
        )
        return list(rows.scalars().all())

    async def create_finding(
        self,
        *,
        run_id: UUID,
        kind: str,
        severity: str,
        detail: str,
        origin: str,
        status: str,
        contribution_id: UUID | None,
        lang: str,
    ) -> ChallengeFinding:
        finding = ChallengeFinding(
            run_id=run_id,
            kind=kind,
            severity=severity,
            detail=detail,
            origin=origin,
            status=status,
            contribution_id=contribution_id,
            lang=lang,
        )
        self.session.add(finding)
        await self.session.flush()
        return finding

    async def finding(self, run_id: UUID, finding_id: UUID) -> ChallengeFinding | None:
        return await self.session.scalar(
            select(ChallengeFinding).where(
                ChallengeFinding.id == finding_id, ChallengeFinding.run_id == run_id
            )
        )

    async def resolve_finding(
        self, finding: ChallengeFinding, status: str, lang: str
    ) -> ChallengeFinding:
        finding.status = status
        finding.lang = lang
        await self.session.flush()
        await self.session.refresh(finding)
        return finding

    async def complete_run(self, run: ChallengeRun, lang: str) -> ChallengeRun:
        run.status = "COMPLETED"
        run.lang = lang
        await self.session.flush()
        await self.session.refresh(run)
        return run
