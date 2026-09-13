from uuid import UUID

from src.modules.iterations.adapters.postgres import IdeaAnalysis, Iteration, PostgresIterations


def analysis_state(analysis: IdeaAnalysis | None, *, expected: bool) -> str:
    """Honest display state: resolved, running, abstained, or unavailable.

    `expected` marks whether an analysis run has been requested for the
    viewed iteration (deposit-time runs are always requested, so a missing
    row means the run is still in flight).
    """
    if analysis is None:
        return "running" if expected else "unavailable"
    return "resolved" if analysis.realism_score is not None else "abstained"


async def analysis_for_view(
    repository: PostgresIterations, idea_id: UUID, viewed: Iteration
) -> IdeaAnalysis | None:
    effective = viewed
    if viewed.proposal_status == "pending" and viewed.parent_id is not None:
        parent = await repository.get(idea_id, viewed.parent_id)
        if parent is not None:
            effective = parent
    return await repository.analysis_for_iteration(effective.id)
