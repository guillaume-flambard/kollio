# Proposal — add-converge-screens

## Why

`docs/00-project-overview.md` §6 makes Converge the flagship differentiator of the pivot: the living map of the collective reasoning, where Agreements, Conflicts, Alternatives, Unknowns, assumption hotspots and duplicates become visible, and where the human correction is what turns a suggestion into canonical structure. The API slice shipped that structure (`converge` module: relations, clusters, the read that returns confirmed Contributions only), and no screen reaches it. A Space can be created, its Explore section can collect Contributions, and the reasoning they carry still has nowhere to be read or corrected together. This is the screen half of migration step 4.

## What Changes

The `converge` section of a Decision Space becomes real, at `/workspace/decision-spaces/[spaceId]/converge`:

- the map of the Space's confirmed Contributions is shown, each with the kind it carries and the group a human placed it in (or that it is not grouped);
- a member asserts a Relation between two Contributions, choosing one of the eight kinds, and sees every Relation with its kind and its two ends; a Relation can be deleted;
- a member creates a Cluster, adds Contributions to it, removes one, and deletes the Cluster — a Contribution belongs to one Cluster at a time, so adding it moves it;
- a Space with no confirmed Contribution says so and points at Explore instead of rendering an empty canvas.

Seven Nitro proxies carry the `converge` operations. The API contract is unchanged, so `make contract` is a no-op.

## Capabilities

### New Capabilities

- `converge-screens`: the Converge section of a Decision Space, its map, its Relations and its Clusters.

## Impact

Adds the body of the Converge section, seven proxies under `apps/web/server/api/workspaces/[workspaceId]/decision-spaces/[spaceId]/`, the `decisionSpaces.converge.*` keys in both locales, and Playwright evidence against mocked API routes. No API change, no migration, no agent call.

Two boundaries belong in `acceptance.md`. First, the ticket asks for merge and split of Clusters, and the API exposes neither: seven operations only, none of them combining or splitting a Cluster, so the screen cannot offer what the API cannot do. Second, the map read carries confirmed Contributions only, so material that has not been confirmed never appears on the map, and the screen cannot show it.

Tickets: GitHub #121 (migration step 4 of `docs/00-project-overview.md` §20, screen half; follows the API slice #111).
