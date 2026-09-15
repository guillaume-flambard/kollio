# Workspace members

`GET /workspaces/{workspace_id}/members` returns the workspace's members
(id, display name, role) when the caller belongs to it, ordered by display
name. A caller who does not belong gets 404 so the endpoint does not reveal
which workspaces exist.
