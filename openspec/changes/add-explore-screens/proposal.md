## Why

`docs/00-project-overview.md` §5 makes Explore the first half of a Decision Space's loop: each participant explores independently in a Branch, and nothing becomes shared reasoning until it is proposed as a Contribution and a human confirms it. §12 makes the personal Branch, the Proposal and the Review the collaboration model. The API has shipped all of it since the pivot foundation (`branches`: six operations), and no screen has ever reached it: the Explore section of a Space is an honest empty state that says what will live there.

This is migration step 3's screen half. Without it the pivoted product can be created and listed but not used: nobody can put their own thinking into a Space, and the shared reasoning a Space converges on has no way to be born.

## What Changes

- The Explore section at `/workspace/decision-spaces/[spaceId]/explore` becomes real: a participant creates a Branch with its raw material (a name, the material itself, and whether the Branch is private or shared).
- Every Branch is listed with its visibility stated in words, its raw material readable, and who created it and when.
- Proposing a Contribution from a Branch lands in the right place: a proposal is made from one Branch, with its kind (idea, claim, evidence, objection, constraint), its title, an optional body, an optional source and an optional tool or model.
- The two states a Contribution can be in are visibly different: what waits for a human is listed apart from what is confirmed, and a Contribution awaiting confirmation carries the action that confirms it.
- Every Contribution shows its provenance: author, Branch, source, tool/model and the moment it was added. An absent source or tool is stated as absent rather than left blank or invented.
- Five Nitro proxy routes carry the existing `branches` operations to the browser; the API contract itself is unchanged, so `make contract` must be a no-op.

## Capabilities

### New Capabilities

- `explore-screens`: A participant explores independently inside a Decision Space, sees which Branch is private and which is shared, proposes a Contribution from Branch material, and reads every Contribution's state and provenance.

## Impact

Adds the Explore section body, five Nitro proxy routes, and the Explore message keys in both locales, with Playwright evidence using the existing mocked-API pattern. No API change (`branches` already ships every operation this screen consumes), no migration, no agent call. One boundary is honest rather than new: the HTTP route for proposing a Contribution always records a human proposal, so it always arrives `confirmed`; a Contribution in the `suggested` state is only reachable once the AI proposer ships, which is why the awaiting-confirmation list is evidenced with mocked responses and recorded as a boundary in `acceptance.md`.

Tickets: GitHub #120 (migration step 3 of `docs/00` §20, screen half; follows the API slice #110).
