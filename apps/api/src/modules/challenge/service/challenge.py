from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

import httpx

from src.modules.challenge.adapters.postgres import (
    ChallengeFinding,
    ChallengeRun,
    PostgresChallenge,
)
from src.modules.challenge.domain.access import can_read_challenge, can_write_challenge
from src.modules.challenge.domain.brief import (
    BriefError,
    BriefEvidence,
    BriefOption,
    build_brief,
)
from src.modules.challenge.domain.coverage import Coverage, compute_coverage
from src.modules.challenge.domain.critic import CriticFindingError, validate_candidates
from src.modules.challenge.domain.findings import (
    FindingShapeError,
    arriving_status,
    validate_detail,
)
from src.modules.challenge.domain.lifecycle import (
    InvalidRunTransition,
    complete_run,
)
from src.modules.challenge.domain.vocabularies import (
    ChallengeVocabularyError,
    validate_kind,
    validate_severity,
)
from src.modules.challenge.service.ports import ChallengeGateway, ChallengeQueue
from src.modules.decision_spaces.adapters.postgres import DecisionSpace


class ChallengeNotFoundError(LookupError):
    """Raised when the workspace, space, option, run or finding is not visible."""


class ChallengeValidationError(ValueError):
    """Raised when a request breaks a challenge rule."""


class ChallengeForbiddenError(LookupError):
    """Raised when a workspace member is neither the owner nor a participant."""


QUEUE_FAILED_REASON = "The challenge could not be queued for the Critic"
EMPTY_RESULT_REASON = "The Critic proposed no findings"
SPACE_GONE_REASON = "The decision space no longer exists"
OPTION_GONE_REASON = "The option no longer exists"


@dataclass(frozen=True)
class RunSnapshot:
    run: ChallengeRun
    findings: list[ChallengeFinding]
    coverage: Coverage


@dataclass(frozen=True)
class SpaceChallenges:
    runs: list[ChallengeRun]
    findings: list[ChallengeFinding]
    coverage: Coverage


async def _authorize_read(repository: PostgresChallenge, workspace_id: UUID, subject: str) -> None:
    if not can_read_challenge(workspace_id, await repository.memberships(subject)):
        raise ChallengeNotFoundError


async def _authorize_write(
    repository: PostgresChallenge, space: DecisionSpace, subject: str, workspace_id: UUID
) -> UUID:
    user = await repository.user_for_subject(subject)
    if user is None:
        raise ChallengeNotFoundError
    if not can_write_challenge(space.owner_id, await repository.participant_ids(space.id), user.id):
        raise ChallengeForbiddenError
    return user.id


async def _space(
    repository: PostgresChallenge, workspace_id: UUID, space_id: UUID
) -> DecisionSpace:
    space = await repository.space(space_id)
    if space is None or space.workspace_id != workspace_id:
        raise ChallengeNotFoundError
    return space


async def _option(repository: PostgresChallenge, space_id: UUID, option_id: UUID) -> None:
    if await repository.option(space_id, option_id) is None:
        raise ChallengeNotFoundError


async def _run(repository: PostgresChallenge, option_id: UUID, run_id: UUID) -> ChallengeRun:
    run = await repository.run(option_id, run_id)
    if run is None:
        raise ChallengeNotFoundError
    return run


async def list_challenges(
    repository: PostgresChallenge,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
) -> SpaceChallenges:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    runs = await repository.list_runs(option_id)
    findings = [finding for run in runs for finding in await repository.findings(run.id)]
    return SpaceChallenges(
        runs=runs,
        findings=findings,
        coverage=compute_coverage((f.kind, f.status) for f in findings),
    )


async def read_challenge(
    repository: PostgresChallenge,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    subject: str,
) -> RunSnapshot:
    await _authorize_read(repository, workspace_id, subject)
    await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    run = await _run(repository, option_id, run_id)
    findings = await repository.findings(run.id)
    return RunSnapshot(
        run=run,
        findings=findings,
        coverage=compute_coverage((f.kind, f.status) for f in findings),
    )


async def open_challenge(
    repository: PostgresChallenge,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    subject: str,
    *,
    lang: str,
    queue: ChallengeQueue,
    trace_context: Mapping[str, str],
) -> ChallengeRun:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    actor_id = await _authorize_write(repository, space, subject, workspace_id)
    run = await repository.create_run(
        space_id=space.id, option_id=option_id, opened_by=actor_id, lang=lang
    )
    try:
        await queue.dispatch(run.id, trace_context)
    except Exception:
        return await repository.fail_run(run, QUEUE_FAILED_REASON, lang)
    return run


async def record_finding(
    repository: PostgresChallenge,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    subject: str,
    *,
    kind: str,
    severity: str,
    detail: str,
    contribution_id: UUID | None,
    origin: str = "human",
    lang: str,
) -> ChallengeFinding:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    run = await _run(repository, option_id, run_id)
    await _authorize_write(repository, space, subject, workspace_id)

    try:
        validate_kind(kind)
        validate_severity(severity)
        status = arriving_status(origin)
        cleaned = validate_detail(detail)
    except (ChallengeVocabularyError, FindingShapeError) as error:
        raise ChallengeValidationError(str(error)) from error

    if contribution_id is not None:
        if await repository.contribution(space.id, contribution_id) is None:
            raise ChallengeValidationError(
                "a finding can only reference a contribution of the same space"
            )

    return await repository.create_finding(
        run_id=run.id,
        kind=kind,
        severity=severity,
        detail=cleaned,
        origin=origin,
        status=status,
        contribution_id=contribution_id,
        lang=lang,
    )


async def resolve_finding(
    repository: PostgresChallenge,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    finding_id: UUID,
    subject: str,
    *,
    resolution: str,
    lang: str,
) -> ChallengeFinding:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    await _run(repository, option_id, run_id)
    await _authorize_write(repository, space, subject, workspace_id)

    finding = await repository.finding(run_id, finding_id)
    if finding is None:
        raise ChallengeNotFoundError
    return await repository.resolve_finding(finding, resolution, lang)


async def complete_challenge(
    repository: PostgresChallenge,
    workspace_id: UUID,
    space_id: UUID,
    option_id: UUID,
    run_id: UUID,
    subject: str,
    *,
    lang: str,
) -> ChallengeRun:
    await _authorize_read(repository, workspace_id, subject)
    space = await _space(repository, workspace_id, space_id)
    await _option(repository, space_id, option_id)
    await _authorize_write(repository, space, subject, workspace_id)

    run = await _run(repository, option_id, run_id)
    try:
        complete_run(run.status)
    except InvalidRunTransition as error:
        raise ChallengeValidationError(str(error)) from error
    return await repository.complete_run(run, lang)


def _gateway_failure(error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return f"The model gateway answered {error.response.status_code}"
    return f"The Critic could not answer: {type(error).__name__}"


async def execute_run(
    repository: PostgresChallenge,
    gateway: ChallengeGateway,
    run_id: UUID,
    locale: str,
) -> ChallengeRun:
    run = await repository.run_by_id(run_id)
    if run is None:
        raise ChallengeNotFoundError
    if run.status != "RUNNING":
        return run

    space = await repository.space(run.space_id)
    if space is None:
        return await repository.fail_run(run, SPACE_GONE_REASON, locale)
    option = await repository.option(run.space_id, run.option_id)
    if option is None:
        return await repository.fail_run(run, OPTION_GONE_REASON, locale)

    evidence = await repository.confirmed_evidence(run.space_id, run.option_id)
    try:
        brief = build_brief(
            question=space.question,
            option=BriefOption(
                title=option.title,
                proposal=option.proposal,
                mechanism=option.mechanism,
                upside=option.upside,
                cost=option.cost,
                risks=option.risks,
                critical_assumptions=option.critical_assumptions,
                success_metrics=option.success_metrics,
            ),
            evidence=[
                BriefEvidence(
                    contribution_id=contribution.id,
                    side=side,
                    title=contribution.title,
                    body=contribution.body,
                )
                for side, contribution in evidence
            ],
        )
    except BriefError as error:
        return await repository.fail_run(run, str(error), locale)

    run = await repository.set_run_model(run, gateway.model)

    try:
        raws = await gateway.challenge(brief=brief.payload, locale=locale)
    except Exception as error:
        return await repository.fail_run(run, _gateway_failure(error), locale)

    try:
        candidates = validate_candidates(raws, allowed_contribution_ids=brief.contribution_ids)
    except CriticFindingError as error:
        return await repository.fail_run(run, str(error), locale)

    if not candidates:
        return await repository.fail_run(run, EMPTY_RESULT_REASON, locale)

    for candidate in candidates:
        await repository.create_finding(
            run_id=run.id,
            kind=candidate.kind,
            severity=candidate.severity,
            detail=candidate.detail,
            origin="critic",
            status="proposed",
            contribution_id=candidate.contribution_id,
            lang=locale,
        )
    return await repository.complete_run(run, locale)
