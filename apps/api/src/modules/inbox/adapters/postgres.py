from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.branches.adapters.postgres import Contribution
from src.modules.challenge.adapters.postgres import ChallengeFinding, ChallengeRun
from src.modules.decision_spaces.adapters.postgres import (
    DecisionSpace,
    DecisionSpaceParticipant,
)
from src.modules.decisions.adapters.postgres import Decision
from src.modules.experiments.adapters.postgres import (
    Experiment,
    ExperimentOutcome,
    Learning,
)
from src.modules.ideas.adapters.postgres import User, WorkspaceMembership


@dataclass(frozen=True)
class InboxRow:
    """One thing waiting, as the adapter reads it. The service groups these."""

    kind: str
    workspace_id: UUID
    space_id: UUID
    space_question: str
    space_status: str
    subject_id: UUID | None
    detail: str | None
    created_at: datetime


class PostgresInbox:
    """Read-only projection over the tables the other modules own.

    Nothing is written here: the inbox stores no state of its own, so every
    entry is a view of a row another capability already maintains.
    """

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

    async def spaces_answered_by(self, subject: str) -> frozenset[UUID]:
        """Spaces where the subject is the owner or a participant: their own input."""
        user = await self.user_for_subject(subject)
        if user is None:
            return frozenset()
        rows = await self.session.execute(
            select(DecisionSpace.id)
            .outerjoin(
                DecisionSpaceParticipant,
                DecisionSpaceParticipant.space_id == DecisionSpace.id,
            )
            .where(
                (DecisionSpace.owner_id == user.id) | (DecisionSpaceParticipant.user_id == user.id)
            )
        )
        return frozenset(rows.scalars().all())

    async def converging_spaces(self, workspace_ids: frozenset[UUID]) -> list[InboxRow]:
        if not workspace_ids:
            return []
        rows = await self.session.execute(
            select(DecisionSpace)
            .where(
                DecisionSpace.workspace_id.in_(workspace_ids),
                DecisionSpace.status == "CONVERGING",
            )
            .order_by(DecisionSpace.created_at, DecisionSpace.id)
        )
        return [
            InboxRow(
                kind="space_needs_convergence",
                workspace_id=space.workspace_id,
                space_id=space.id,
                space_question=space.question,
                space_status=space.status,
                subject_id=None,
                detail=None,
                created_at=space.created_at,
            )
            for space in rows.scalars().all()
        ]

    async def ready_spaces(self, workspace_ids: frozenset[UUID]) -> list[InboxRow]:
        if not workspace_ids:
            return []
        decided = select(Decision.id).where(Decision.space_id == DecisionSpace.id).exists()
        rows = await self.session.execute(
            select(DecisionSpace)
            .where(
                DecisionSpace.workspace_id.in_(workspace_ids),
                DecisionSpace.status == "READY_TO_DECIDE",
                ~decided,
            )
            .order_by(DecisionSpace.created_at, DecisionSpace.id)
        )
        return [
            InboxRow(
                kind="decision_awaits_commitment",
                workspace_id=space.workspace_id,
                space_id=space.id,
                space_question=space.question,
                space_status=space.status,
                subject_id=None,
                detail=None,
                created_at=space.created_at,
            )
            for space in rows.scalars().all()
        ]

    async def suggested_contributions(self, space_ids: frozenset[UUID]) -> list[InboxRow]:
        if not space_ids:
            return []
        rows = await self.session.execute(
            select(Contribution, DecisionSpace)
            .join(DecisionSpace, DecisionSpace.id == Contribution.space_id)
            .where(
                Contribution.space_id.in_(space_ids),
                Contribution.status == "suggested",
            )
            .order_by(Contribution.created_at, Contribution.id)
        )
        return [
            InboxRow(
                kind="contribution_awaits_confirmation",
                workspace_id=space.workspace_id,
                space_id=space.id,
                space_question=space.question,
                space_status=space.status,
                subject_id=contribution.id,
                detail=contribution.title,
                created_at=contribution.created_at,
            )
            for contribution, space in rows.all()
        ]

    async def proposed_findings(self, space_ids: frozenset[UUID]) -> list[InboxRow]:
        if not space_ids:
            return []
        rows = await self.session.execute(
            select(ChallengeFinding, ChallengeRun, DecisionSpace)
            .join(ChallengeRun, ChallengeRun.id == ChallengeFinding.run_id)
            .join(DecisionSpace, DecisionSpace.id == ChallengeRun.space_id)
            .where(
                ChallengeRun.space_id.in_(space_ids),
                ChallengeFinding.status == "proposed",
            )
            .order_by(ChallengeFinding.created_at, ChallengeFinding.id)
        )
        return [
            InboxRow(
                kind="finding_awaits_resolution",
                workspace_id=space.workspace_id,
                space_id=space.id,
                space_question=space.question,
                space_status=space.status,
                subject_id=finding.id,
                detail=finding.detail,
                created_at=finding.created_at,
            )
            for finding, _run, space in rows.all()
        ]

    async def completed_experiments_without_outcome(
        self, workspace_ids: frozenset[UUID]
    ) -> list[InboxRow]:
        if not workspace_ids:
            return []
        observed = (
            select(ExperimentOutcome.id)
            .where(ExperimentOutcome.experiment_id == Experiment.id)
            .exists()
        )
        rows = await self.session.execute(
            select(Experiment, DecisionSpace)
            .join(DecisionSpace, DecisionSpace.id == Experiment.decision_space_id)
            .where(
                DecisionSpace.workspace_id.in_(workspace_ids),
                Experiment.status == "completed",
                ~observed,
            )
            .order_by(Experiment.created_at, Experiment.id)
        )
        return [
            InboxRow(
                kind="experiment_awaits_outcome",
                workspace_id=space.workspace_id,
                space_id=space.id,
                space_question=space.question,
                space_status=space.status,
                subject_id=experiment.id,
                detail=experiment.title,
                created_at=experiment.created_at,
            )
            for experiment, space in rows.all()
        ]

    async def draft_learnings(self, workspace_ids: frozenset[UUID]) -> list[InboxRow]:
        if not workspace_ids:
            return []
        rows = await self.session.execute(
            select(Learning, Experiment, DecisionSpace)
            .join(Experiment, Experiment.id == Learning.experiment_id)
            .join(DecisionSpace, DecisionSpace.id == Experiment.decision_space_id)
            .where(
                DecisionSpace.workspace_id.in_(workspace_ids),
                Learning.status == "draft",
            )
            .order_by(Learning.created_at, Learning.id)
        )
        return [
            InboxRow(
                kind="learning_awaits_confirmation",
                workspace_id=space.workspace_id,
                space_id=space.id,
                space_question=space.question,
                space_status=space.status,
                subject_id=learning.id,
                detail=learning.text,
                created_at=learning.created_at,
            )
            for learning, _experiment, space in rows.all()
        ]
