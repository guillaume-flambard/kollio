## Why

The pivot's parent object exists in the API and nowhere in the product. `docs/00-project-overview.md` §3 makes the Decision Space the container a team converges on, and §4 makes the Space screen the place the Explore → Converge → Options → Decision → Experiment → Learning loop happens. Today `/workspace` still opens the idea Explorer, so a member cannot see, open or steer a Decision Space at all: the entire pivot is unreachable from the product. This is migration step 2's screen half, and it is the first screen slice of the pivot.

## What Changes

- `/workspace` becomes the workspace's Decision Space list: question, owner, status, deadline and participant count per Space, with an honest empty state, and a form to open a new Space from a required question.
- A Space screen at `/workspace/decision-spaces/[spaceId]` frames the question — owner, status, deadline, participants — and carries the six sections the blueprint names: Explore, Converge, Options, Decision, Experiment, Learning.
- Each section is a real route with an honest empty state that says what will live there. The section bodies land with the capabilities that fill them, so none of them pretends to be broken and none of them fabricates content.
- The Space's status is readable, and every transition the API permits from the current status is reachable from the screen.
- The idea Explorer moves to `/workspace/ideas` and keeps working exactly as it does today: nothing pre-pivot is removed, only re-homed.
- Navigation gains Decision spaces before Initiatives, and the active entry is computed explicitly so `/workspace/ideas` is not read as the Spaces list.
- Six Nitro proxy routes carry the existing `decision_spaces` operations to the browser; the API contract itself is unchanged.

## Capabilities

### New Capabilities

- `decision-space-screens`: A workspace member sees the Decision Spaces their workspace owns, opens one from a question, and reaches every section and permitted status transition of that Space from its screen.

## Impact

Adds one page that replaces `/workspace`, one Space shell with six section routes, one moved Explorer page, six Nitro proxy routes, a three-entry workspace navigation and its message keys in both locales, and Playwright evidence with the existing mocked-API pattern. No API change: the `decision-space` capability already ships every operation this screen consumes, so `make contract` must show an unchanged operation count. No agent call and no persistence change.

Tickets: GitHub #119 (migration step 2 of `docs/00` §20, screen half; follows the API slice #109).
