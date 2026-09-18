# Spec the inbox screens

## Why

`docs/00-project-overview.md` section 4 makes the Decision Inbox the home of a
workspace: the screen that answers what needs attention. The API already answers
that question. `read_decision_inbox` reads the state the other capabilities
store and returns four sections, and no screen reaches it. `/workspace` still
serves the list of decision spaces, so the question the product starts from has
no answer in the product.

## What Changes

- `/workspace` becomes the Decision Inbox: the four sections the API computes
  (spaces to converge, work waiting on the reader, spaces ready for a decision,
  work needing a learning), each entry naming what waits and leading to the
  space and the section where it can be acted on, each section saying when it is
  empty, and an honest empty state when nothing waits at all.
- The screen says that the fifth section of section 4, relevant prior memory, is
  not answered yet, because the capability that would surface a confirmed
  Learning with its provenance does not exist. An empty list there would assert
  that no relevant memory exists, which nothing supports.
- The list of decision spaces moves to `/workspace/decision-spaces`, unchanged.
- The navigation gains an Inbox entry pointing at `/workspace`, and its Decision
  spaces entry points at the new path.
- One Nitro proxy is added for `read_decision_inbox`. No API change.

## Capabilities

### New Capabilities

`inbox-screens`: the Decision Inbox screen, its sections, its bounds, its empty
states and its honest silence about relevant prior memory.

### Modified Capabilities

None. The API capability `inbox` is unchanged.

## Impact

Four web files change, one is added, and the space list moves: the page at
`/workspace`, the new page at `/workspace/decision-spaces`, the navigation, the
two catalogues, one Nitro proxy and two browser specs. `contracts/openapi.json`
and the generated client are untouched, so `make contract` is a no-op.

Tickets: GitHub #127 (migration step 9 of `docs/00-project-overview.md` section 20, screen half; follows the API slice #117).
