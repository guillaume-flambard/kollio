# Spec the members screens

## Why

Membership is implemented in the API: `workspaces` lists the workspaces a person belongs to and their members, and `ideas` carries join requests, their acceptance and rejection, the addition of a participant and the removal of a member. No screen reaches any of it. A workspace member cannot see who shares their workspace, cannot answer a request to join an initiative, and cannot add or remove anyone, even though every operation exists.

`/workspace/settings` is where the PRD places membership, and today that screen only carries the company context, with a navigation entry that says Company context.

## What Changes

- The Settings section gains a Members section:
  - the workspace's roster, each member with their display name and their role;
  - the choice of which initiative to manage, because membership belongs to an initiative in this product;
  - the initiative's waiting join requests, each with the name of the person who asked and the note they wrote, behind an accept action and a refuse action that requires a reason;
  - the initiative's team, with a remove action, and a form that adds a participant with a participation and a business function;
  - two honest notes: membership is managed per initiative, and matching between people and initiatives is not surfaced here.
- The navigation entry stops saying Company context and says Settings in English and Réglages in French. The route stays `/workspace/settings`.
- A browser spec covers the section, and the responsive spec that asserted the old navigation label is updated.

## Capabilities

### New Capabilities

- `members-screens`: the Members section of `/workspace/settings`.

### Modified Capabilities

None. The API capability `members` is unchanged.

## Impact

The section reads the workspace's members, the workspace's initiatives, and one initiative's detail, and writes through the operations that already exist for join requests, participant addition and member removal. No HTTP operation is added, changed or removed, so `make contract` is a no-op.

Two boundaries are recorded rather than hidden:

- **Membership is per initiative.** There is no workspace-level membership operation: join requests are readable only through an initiative's detail, and accepting, refusing, adding and removing all require an initiative. The section therefore shows the workspace roster and manages the membership of a chosen initiative, and it says so.
- **The section is rendered and the API refuses.** The web client knows the authenticated subject but not the caller's effective rights, so the controls are always rendered and a refusal is shown instead of hiding actions.

Out of scope: the participant axes and the matching between people and initiatives (`docs/00-project-overview.md` §15), which stay frozen, and the Memory Retriever (§11).

Tickets: GitHub #126 (migration of membership, screen half; follows the API slices for workspaces and ideas).
