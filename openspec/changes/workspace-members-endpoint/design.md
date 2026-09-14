# Design

- The membership check and the member query both go through
  `WorkspaceMembership` joined on `User`, matching how every other
  workspace-scoped reader decides visibility.
- The check is a separate query from the listing so an outsider is denied
  before any member data is loaded, and the denial is a 404 rather than a
  403 to avoid leaking that the workspace exists.
- Ordering is by display name then id, so the picker is stable across
  requests and testable.
