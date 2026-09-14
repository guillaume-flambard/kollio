"""Team formation rules: the handshake that fills an idea's loop.

Decided in wayfinder ticket "Team join loop" (#16):
the apply-accept handshake mirrors the proposal semantics in
`src/modules/iterations/domain/rules.py`; the role vocabulary is closed
(owner is implicit and never selectable); departures are recorded,
never deleted.
"""

from dataclasses import dataclass
from typing import Final

ROLES: Final[frozenset[str]] = frozenset(
    {"designer", "dev", "commercial", "growth", "data", "product"}
)


class TeamRuleError(ValueError):
    """Raised when a team handshake transition is invalid."""


class TeamAuthorizationError(LookupError):
    """Raised when an actor cannot perform a team transition."""


Role = str


@dataclass(frozen=True)
class ApplicationDecision:
    role: Role
    note: str


@dataclass(frozen=True)
class ResolutionDecision:
    status: str
    rationale: str | None = None


@dataclass(frozen=True)
class DepartureDecision:
    record: bool = True


def decide_application(
    *,
    actor_is_owner: bool,
    actor_is_member: bool,
    role: str,
    note: str,
    already_pending: bool,
) -> ApplicationDecision:
    if role not in ROLES or role == "owner":
        raise TeamRuleError(f"Unknown or reserved role: {role}")
    if actor_is_owner:
        raise TeamAuthorizationError("The owner is already in the loop")
    if not actor_is_member:
        raise TeamAuthorizationError("Only workspace members can apply")
    if not note.strip():
        raise TeamRuleError("A note explains what the applicant brings")
    if already_pending:
        raise TeamRuleError("One pending application per user per idea")
    return ApplicationDecision(role=role, note=note)


def decide_acceptance(*, is_owner: bool, current_status: str) -> ResolutionDecision:
    if not is_owner:
        raise TeamAuthorizationError("Only the owner can accept an application")
    if current_status != "pending":
        raise TeamRuleError("Only a pending application can be accepted")
    return ResolutionDecision(status="accepted")


def decide_rejection(*, is_owner: bool, current_status: str, rationale: str) -> ResolutionDecision:
    if not is_owner:
        raise TeamAuthorizationError("Only the owner can reject an application")
    if current_status != "pending":
        raise TeamRuleError("Only a pending application can be rejected")
    if not rationale.strip():
        raise TeamRuleError("A rejection explains itself in a short rationale")
    return ResolutionDecision(status="rejected", rationale=rationale.strip())


def decide_departure(*, actor_is_owner: bool, actor_is_member: bool) -> DepartureDecision:
    if actor_is_owner and not actor_is_member:
        raise TeamAuthorizationError("Only a member can be removed by the owner")
    return DepartureDecision(record=True)
