from uuid import UUID

from src.modules.experiments.domain.lifecycle import ExperimentRuleError


class ExperimentLinkError(ExperimentRuleError):
    """Raised when an experiment's decision space link is invalid."""


def validate_link(
    *,
    idea_workspace_id: UUID | None,
    space_id: UUID | None,
    space_workspace_id: UUID | None,
    option_id: UUID | None,
    option_space_id: UUID | None,
) -> None:
    """An experiment may join a decision space of its idea's workspace, and one of its options.

    The caller resolves the space and the option and passes what it found, so a
    missing row and a foreign row are both refused rather than silently linked.
    """
    if option_id is not None and space_id is None:
        raise ExperimentLinkError("an option is only linked together with its space")
    if space_id is not None and space_workspace_id != idea_workspace_id:
        raise ExperimentLinkError("the decision space belongs to another workspace")
    if option_id is not None and option_space_id != space_id:
        raise ExperimentLinkError("the option does not belong to the linked decision space")
