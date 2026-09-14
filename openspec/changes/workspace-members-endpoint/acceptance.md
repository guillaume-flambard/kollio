# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| A member lists the workspace members | `tests/integration/test_workspace_members.py` asserts both names and both roles |
| An outsider is denied | the same test asserts 404 with `workspace_not_found` |

## Gaps

- No UI consumes it yet: the owner add-participant form is the follow-up
  ticket.
- Members are listed without their participation on a given initiative;
  the form will pass both axes to the existing add endpoint.
