"""Team formation rules: participation, business function and the handshake.

Wayfinder ticket "Team join loop" (#16) fixed the apply-accept handshake;
ticket "Participant roles vs craft roles" (#48) split it in two axes: a
participation role (owner, decision-maker, contributor, observer) and a
business function from a closed list. The owner is implicit and never
granted as a participation. Departures are recorded, never deleted.
"""

from dataclasses import dataclass
from typing import Final

PARTICIPATION_ROLES: Final[frozenset[str]] = frozenset(
    {"owner", "decision_maker", "contributor", "observer"}
)
BUSINESS_FUNCTIONS: Final[frozenset[str]] = frozenset(
    {
        "marketing",
        "sales",
        "finance",
        "product",
        "engineering",
        "customer_success",
        "operations",
        "legal",
        "hr",
        "data",
        "direction",
        "other",
    }
)
# The craft roles of the first slice, mapped once onto the function axis.
LEGACY_ROLE_TO_FUNCTION: Final[dict[str, str]] = {
    "designer": "product",
    "dev": "engineering",
    "commercial": "sales",
    "growth": "marketing",
    "data": "data",
    "product": "product",
    "owner": "direction",
}
GRANTABLE_PARTICIPATIONS: Final[frozenset[str]] = PARTICIPATION_ROLES - {"owner"}
DEFAULT_PARTICIPATION: Final[str] = "contributor"


class TeamRuleError(ValueError):
    """Raised when a team handshake transition is invalid."""


class TeamAuthorizationError(LookupError):
    """Raised when an actor cannot perform a team transition."""


@dataclass(frozen=True)
class ApplicationDecision:
    function: str
    note: str


@dataclass(frozen=True)
class MembershipDecision:
    participation: str
    function: str


@dataclass(frozen=True)
class ResolutionDecision:
    status: str
    rationale: str | None = None


@dataclass(frozen=True)
class DepartureDecision:
    record: bool = True


def validate_function(value: str) -> str:
    if value not in BUSINESS_FUNCTIONS:
        raise TeamRuleError(f"Unknown business function: {value}")
    return value


def validate_grantable_participation(value: str) -> str:
    if value not in GRANTABLE_PARTICIPATIONS:
        raise TeamRuleError(f"Unknown or reserved participation: {value}")
    return value


def decide_application(
    *,
    actor_is_owner: bool,
    actor_is_member: bool,
    function: str,
    note: str,
    already_pending: bool,
) -> ApplicationDecision:
    validate_function(function)
    if actor_is_owner:
        raise TeamAuthorizationError("The owner is already in the loop")
    if not actor_is_member:
        raise TeamAuthorizationError("Only workspace members can apply")
    if not note.strip():
        raise TeamRuleError("A note explains what the applicant brings")
    if already_pending:
        raise TeamRuleError("One pending application per user per idea")
    return ApplicationDecision(function=function, note=note)


def decide_addition(
    *,
    actor_is_owner: bool,
    target_is_workspace_member: bool,
    participation: str,
    function: str,
) -> MembershipDecision:
    if not actor_is_owner:
        raise TeamAuthorizationError("Only the owner can add a participant")
    if not target_is_workspace_member:
        raise TeamRuleError("Only workspace members can join an initiative")
    validate_grantable_participation(participation)
    validate_function(function)
    return MembershipDecision(participation=participation, function=function)


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
