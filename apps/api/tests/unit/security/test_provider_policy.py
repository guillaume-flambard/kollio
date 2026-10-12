from uuid import UUID

import pytest

from src.modules.security.domain.provider_policy import (
    ProviderNotApprovedError,
    authorize_transmission,
)

WORKSPACE = UUID("00000000-0000-0000-0000-000000000001")
OTHER_WORKSPACE = UUID("00000000-0000-0000-0000-000000000002")


def test_unapproved_provider_cannot_receive_selected_workspace_material():
    with pytest.raises(ProviderNotApprovedError):
        authorize_transmission(
            workspace_id=WORKSPACE,
            provider_workspace_id=WORKSPACE,
            provider_is_approved=False,
            excerpt_workspace_ids=(WORKSPACE,),
        )


def test_excerpt_from_another_workspace_is_refused():
    with pytest.raises(ProviderNotApprovedError):
        authorize_transmission(
            workspace_id=WORKSPACE,
            provider_workspace_id=WORKSPACE,
            provider_is_approved=True,
            excerpt_workspace_ids=(WORKSPACE, OTHER_WORKSPACE),
        )


def test_prototype_provider_refuses_sensitive_material():
    with pytest.raises(ProviderNotApprovedError):
        authorize_transmission(
            workspace_id=WORKSPACE,
            provider_workspace_id=WORKSPACE,
            provider_is_approved=True,
            excerpt_workspace_ids=(WORKSPACE,),
            provider_usage_mode="prototype",
            material_sensitivity="sensitive",
        )
