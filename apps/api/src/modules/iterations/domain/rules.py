from dataclasses import dataclass
from typing import Literal
from uuid import UUID

ProposalStatus = Literal["pending", "accepted", "rejected"]


class IterationRuleError(ValueError):
    """Base error for a rejected iteration transition."""


class AuthorizationError(IterationRuleError):
    """Raised when an actor cannot perform an iteration transition."""


class ConflictError(IterationRuleError):
    """Raised when a client attempts to write from a stale branch head."""


class InvalidTransitionError(IterationRuleError):
    """Raised when an iteration lifecycle transition is invalid."""


@dataclass(frozen=True)
class CreationDecision:
    parent_id: UUID | None
    proposal_status: ProposalStatus | None


@dataclass(frozen=True)
class ResolutionDecision:
    parent_id: UUID | None
    proposal_status: ProposalStatus


@dataclass(frozen=True)
class RejectionDecision:
    status: ProposalStatus
    rationale: str


def _require_current_parent(
    expected_parent_id: UUID | None,
    current_parent_id: UUID | None,
) -> None:
    if expected_parent_id != current_parent_id:
        raise ConflictError("The branch has changed since it was read")


def decide_creation(
    *,
    is_owner: bool,
    branch: str,
    expected_parent_id: UUID | None,
    current_branch_head_id: UUID | None,
) -> CreationDecision:
    _require_current_parent(expected_parent_id, current_branch_head_id)
    if branch == "main":
        if not is_owner:
            raise AuthorizationError("Only the idea owner can append to main")
        return CreationDecision(parent_id=current_branch_head_id, proposal_status=None)
    return CreationDecision(parent_id=current_branch_head_id, proposal_status="pending")


def decide_acceptance(
    *,
    is_owner: bool,
    branch: str,
    proposal_status: str | None,
    expected_main_parent_id: UUID | None,
    current_main_head_id: UUID | None,
) -> ResolutionDecision:
    if not is_owner:
        raise AuthorizationError("Only the idea owner can accept a proposal")
    if branch == "main" or proposal_status != "pending":
        raise InvalidTransitionError("Only a pending proposal can be accepted")
    _require_current_parent(expected_main_parent_id, current_main_head_id)
    return ResolutionDecision(parent_id=current_main_head_id, proposal_status="accepted")


def decide_rejection(
    *,
    is_owner: bool,
    branch: str,
    proposal_status: str | None,
    rationale: str,
) -> RejectionDecision:
    if not is_owner:
        raise AuthorizationError("Only the idea owner can reject a proposal")
    if branch == "main" or proposal_status != "pending":
        raise InvalidTransitionError("Only a pending proposal can be rejected")
    if not rationale.strip():
        raise IterationRuleError("A rejection explains itself in a short rationale")
    return RejectionDecision(status="rejected", rationale=rationale.strip())


def decide_rollback(
    *,
    is_owner: bool,
    expected_main_parent_id: UUID | None,
    current_main_head_id: UUID | None,
) -> CreationDecision:
    if not is_owner:
        raise AuthorizationError("Only the idea owner can restore an iteration")
    _require_current_parent(expected_main_parent_id, current_main_head_id)
    return CreationDecision(parent_id=current_main_head_id, proposal_status=None)
