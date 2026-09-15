# Workspace members endpoint

## Why

The owner can add a participant directly (#54) but no surface can offer a
picker: the web app has no way to list a workspace's members. Without it,
the owner-add flow is API-only.

## What changes

- `GET /workspaces/{workspace_id}/members` returns the members of a
  workspace to a member of that workspace: id, display name and role.
- A non-member gets 404 with `workspace_not_found`, never a distinction
  between absent and forbidden.

## Out of scope

- The owner add-participant form on the initiative detail: it is a
  separate slice (its own ticket), consuming this endpoint.
