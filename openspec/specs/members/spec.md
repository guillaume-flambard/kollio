# members Specification

## Purpose

Expose a workspace's members to the workspace's own members, without revealing which workspaces exist.

## Requirements

### Requirement: Workspace members are listed to members only
`GET /workspaces/{workspace_id}/members` SHALL return the workspace's members (id, display name, role) when the caller belongs to it, ordered by display name, and SHALL return 404 to a caller who does not belong so the endpoint does not reveal which workspaces exist.

#### Scenario: Member lists the members
- **WHEN** a workspace member requests the workspace's members
- **THEN** the system returns each member's id, display name and role, ordered by display name

#### Scenario: Non-member lists the members
- **WHEN** an authenticated caller who does not belong to the workspace requests its members
- **THEN** the system responds 404
- **AND** discloses no member
