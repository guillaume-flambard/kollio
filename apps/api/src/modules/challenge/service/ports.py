from collections.abc import Mapping
from typing import Protocol
from uuid import UUID


class ChallengeGateway(Protocol):
    """The Critic of `docs/00-project-overview.md` §7.

    One call per run: a brief built from the Option and its confirmed evidence
    goes in, candidate findings come out. `challenge/adapters/critic.py`
    implements it against the model gateway; a fake drives the same port in
    tests so the execution path is proved without a live model.
    """

    model: str

    async def challenge(
        self, *, brief: Mapping[str, object], locale: str
    ) -> list[Mapping[str, object]]: ...


class ChallengeQueue(Protocol):
    """Dispatch for a challenge run.

    `challenge/adapters/taskiq.py` implements it over Taskiq; a fake drives the
    same port in tests so no test reaches Redis.
    """

    async def dispatch(self, run_id: UUID, trace_context: Mapping[str, str]) -> None: ...
