# Acceptance evidence — add-converge-screens

Change: `openspec/changes/add-converge-screens`
Tickets: GitHub #121 (migration step 4 of `docs/00-project-overview.md` §20, screen half; follows the API slice #111)
Date: 2026-09-17
Delivered by this change: the Converge section of a Decision Space. It renders the map the API already holds (the Space's confirmed Contributions, the Relations a human asserted between them, and the Clusters a human built), and it gives a member the controls to correct that map: assert and remove a Relation, create, delete and fill a Cluster. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| A member reads the map | `tests/browser/converge.spec.ts::CONVERGE-02` (each Contribution with its kind and its group) | passing |
| A Contribution in no group says it is not grouped | `tests/browser/converge.spec.ts::CONVERGE-03` | passing |
| A Space with nothing to converge says so | `tests/browser/converge.spec.ts::CONVERGE-01` (the empty state and its link to Explore) | passing |
| The map could not be read | `tests/browser/converge.spec.ts::CONVERGE-12` (a 500 on the map request renders the load failure) | passing |
| A Relation is asserted | `tests/browser/converge.spec.ts::CONVERGE-04` (the POST body carries both ends and the chosen kind) | passing |
| A Relation to itself is refused before the request | `tests/browser/converge.spec.ts::CONVERGE-05` (no request is sent) | passing |
| A Relation is removed | `tests/browser/converge.spec.ts::CONVERGE-06` (the Relation leaves the list after the map is read again) | passing |
| No Relation is an empty state | `tests/browser/converge.spec.ts::CONVERGE-06` (the Relations block says there is none) | passing |
| A Cluster is created | `tests/browser/converge.spec.ts::CONVERGE-07` | passing |
| A Cluster without a title is refused before the request | `tests/browser/converge.spec.ts::CONVERGE-08` (no request is sent) | passing |
| A Contribution is added and then removed | `tests/browser/converge.spec.ts::CONVERGE-09` and `::CONVERGE-10` (it leaves the Cluster and stays on the map) | passing |
| A Cluster is deleted | `tests/browser/converge.spec.ts::CONVERGE-11` (its Contributions stay, ungrouped) | passing |
| The kinds are written in French | `tests/browser/converge.spec.ts` (the whole file runs twice, once per locale) | passing |
| The kinds are written in English | `tests/browser/converge.spec.ts` (second pass of the loop) | passing |
| Nothing names a verdict | `tests/browser/converge.spec.ts::CONVERGE-13` (no verdict, score, ranking or prediction in the rendered text) | passing |
| The Space's reasoning stays isolated per Space | `apps/api/tests/integration/test_converge_map.py` (the browser specs mock every `/api/**` route, so isolation is proved by the API suite of #111, archive `2026-09-17-add-converge-map`) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **188 passed**, of which `tests/browser/converge.spec.ts` contributes **26** (13 scenarios × FR/EN). Standing gates for this slice: `pnpm --dir apps/web exec playwright test decision-spaces.spec.ts` → **22 passed** (the two scenarios that walk the six sections still hold, because the section title and body render unconditionally).

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove neither authentication, nor workspace isolation, nor the write permissions, nor persistence. Those are proved on disposable PostgreSQL by `apps/api/tests/integration/test_converge_map.py` (see the archived `openspec/changes/archive/2026-09-17-add-converge-map/acceptance.md`).
- **The map is built without a model.** The section only renders and corrects what the API holds; nothing here detects, merges or scores a Relation or a Cluster.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 652 catalog keys cover their usages.` (592 before this slice; 60 keys added in both locales).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` and `pnpm typecheck` are clean.
- **Production build**: `pnpm build` completes, generating the Nitro route for the Converge section.
- **No API change**: no route, schema or migration is touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op for this slice.

## Explicitly deferred (not gaps)

- **Merging and splitting a Cluster.** The slice ticket mentions both; the `converge` API exposes neither (seven operations, none combines or splits a Cluster). They need an API operation first, so they are deferred rather than faked in the screen.
- **A Contribution that waits for a human.** The map read carries confirmed Contributions only, so a `suggested` Contribution never reaches Converge. It becomes visible in the Space once a human confirms it in Explore (#120).
- **Ordering and layout controls** (moving Contributions, ordering Clusters) are not part of the ticket.
- **The AI that proposes a map** (Convergence Engine, §13) belongs to a later slice; this one corrects a map a human built.
- Downstream sections: Options (#122), Decision (#123), Experiment (#124), Learning (#125), Members (#126), Inbox (#127).

## Known gaps

- None beyond the boundaries above.
