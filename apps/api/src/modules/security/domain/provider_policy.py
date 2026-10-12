from collections.abc import Iterable
from uuid import UUID


class ProviderNotApprovedError(PermissionError):
    """Raised before any workspace material can reach a model provider."""


def authorize_transmission(
    *,
    workspace_id: UUID,
    provider_workspace_id: UUID,
    provider_is_approved: bool,
    excerpt_workspace_ids: Iterable[UUID],
    provider_usage_mode: str = "production",
    material_sensitivity: str = "internal",
) -> None:
    """Refuse egress unless the provider and every selected excerpt share a workspace."""
    if provider_workspace_id != workspace_id or not provider_is_approved:
        raise ProviderNotApprovedError("The model provider is not approved for this workspace")
    if any(excerpt_workspace_id != workspace_id for excerpt_workspace_id in excerpt_workspace_ids):
        raise ProviderNotApprovedError("Every selected excerpt must belong to this workspace")
    if provider_usage_mode == "prototype" and material_sensitivity == "sensitive":
        raise ProviderNotApprovedError("Prototype providers cannot receive sensitive material")
