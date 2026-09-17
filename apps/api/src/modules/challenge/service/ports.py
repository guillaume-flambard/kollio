from collections.abc import Mapping
from typing import Protocol
from uuid import UUID


class ChallengeGateway(Protocol):
    """The Critic of `docs/00-project-overview.md` §7.

    Declared, not implemented: this slice ships the structure the Critic
    writes into. The adapter lands with its own slice and fills the same
    `create_finding` path with a `critic` origin, so no caller changes.
    """

    model: str

    async def challenge(
        self, *, brief: Mapping[str, object], locale: str
    ) -> list[Mapping[str, str]]: ...


class ChallengeQueue(Protocol):
    """Dispatch for a challenge run. Declared so the Critic's slice can queue
    a run without reshaping the service; nothing dispatches yet."""

    async def dispatch(self, run_id: UUID, trace_context: Mapping[str, str]) -> None: ...
