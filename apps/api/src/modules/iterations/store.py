from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import insert

from src.agents.schemas import ConstraintAnalysis
from src.modules.iterations.adapters.postgres import IdeaAnalysis, PostgresIterations


async def save_analysis(
    repository: PostgresIterations,
    idea_id: UUID,
    iteration_id: UUID,
    analysis: ConstraintAnalysis,
    *,
    model: str,
) -> IdeaAnalysis:
    await repository.session.execute(
        insert(IdeaAnalysis)
        .values(
            id=uuid4(),
            idea_id=idea_id,
            iteration_id=iteration_id,
            realism_score=analysis.realism_score,
            constraints={
                key: dimension.model_dump(mode="json")
                for key, dimension in analysis.constraints.items()
            },
            locale=analysis.locale,
            model=model,
        )
        .on_conflict_do_nothing(index_elements=["iteration_id"])
    )
    await repository.session.flush()
    stored = await repository.analysis_for_iteration(iteration_id)
    assert stored is not None
    return stored


async def store_raw_analysis(
    repository: PostgresIterations,
    idea_id: UUID,
    iteration_id: UUID,
    payload: dict,
    *,
    model: str,
) -> IdeaAnalysis:
    return await save_analysis(
        repository, idea_id, iteration_id, ConstraintAnalysis.model_validate(payload), model=model
    )
