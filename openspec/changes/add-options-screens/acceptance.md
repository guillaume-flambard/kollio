# Acceptance evidence — add-options-screens

Change: `openspec/changes/add-options-screens`

Tickets: GitHub #122 (migration step 5 of `docs/00-project-overview.md` §20, screen half; follows the API slice #112)

Date: 2026-09-17

Delivered by this change: the Options section of a Decision Space. A member lists the viable
paths the Space holds, writes one with the fields `docs/00` §7 names, edits it, deletes it,
and links the Space's confirmed Contributions to it as evidence for or against. Nothing in
the section scores, ranks or rates an Option. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that
exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| A Space with no Option | `tests/browser/options.spec.ts::OPTIONS-01` (the empty state names itself and offers the create action) | passing |
| The Options of a Space are listed | `tests/browser/options.spec.ts::OPTIONS-12` (two Options listed, each with its title and its proposal) | passing |
| An Option that carries no evidence says so | `tests/browser/options.spec.ts::OPTIONS-02` and `::OPTIONS-12` (the option says no evidence is linked instead of rendering an empty list) | passing |
| The section could not be read | `tests/browser/options.spec.ts::OPTIONS-13` (a failing read says so and the section title stays readable) | passing |
| An Option is created with its title and proposal | `tests/browser/options.spec.ts::OPTIONS-02` (the POST carries the two required fields with the six narrative fields null, the Option is listed, and no narrative field is rendered) | passing |
| The fields a member does provide are kept | `tests/browser/options.spec.ts::OPTIONS-03` (mechanism and cost travel in the POST and are rendered under their labels; the untouched fields stay absent) | passing |
| An Option without a title is refused | `tests/browser/options.spec.ts::OPTIONS-04` (the section says a title is required and no POST is sent) | passing |
| An Option without a proposal is refused | `tests/browser/options.spec.ts::OPTIONS-05` (the section says a proposal is required and no POST is sent) | passing |
| An Option is edited | `tests/browser/options.spec.ts::OPTIONS-06` (the mechanism is patched and read back) | passing |
| An Option is deleted | `tests/browser/options.spec.ts::OPTIONS-11` (the Option leaves the list, the empty state appears and the section still renders) | passing |
| A confirmed Contribution is linked and read back | `tests/browser/options.spec.ts::OPTIONS-07` (the link is POSTed on the against side and the Contribution is rendered under it) | passing |
| A linked Contribution is unlinked | `tests/browser/options.spec.ts::OPTIONS-10` (the link is DELETEd and the side says it carries no evidence again) | passing |
| Only confirmed Contributions are offered | `tests/browser/options.spec.ts::OPTIONS-08` (the confirmed Contribution is the only candidate offered; the suggested one is not) | passing |
| Nothing to link | `tests/browser/options.spec.ts::OPTIONS-09` (the linking form says there is no confirmed Contribution to link and offers no empty choice) | passing |
| A member reads the section (no score, rank, rating or prediction) | `tests/browser/options.spec.ts::OPTIONS-12` (no element carries a score, a rank or a rating marker, and the only per-Option summary is its evidence count) | passing |
| A French reader | `tests/browser/options.spec.ts` describes `fr` (all thirteen scenarios run with the French catalog) | passing |
| An English reader | `tests/browser/options.spec.ts` describes `en` (the same thirteen scenarios run with the English catalog) | passing |
| A Space's Options stay inside their Space | `apps/api/tests/integration/test_options.py` (isolation, permissions and the refusal of an unconfirmed Contribution are proved server-side) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **214 passed**, of which
`tests/browser/options.spec.ts` contributes **26** (13 scenarios × FR/EN). `tests/browser/decision-spaces.spec.ts`
still passes its 22 scenarios.

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove
  neither authentication, nor workspace isolation, nor the domain rules, nor persistence.
  Those are proved by `apps/api/tests/integration/test_options.py` on disposable PostgreSQL.
- **The list read carries no evidence.** The API's `list_options` returns `OptionResponse`,
  which holds no evidence; the section therefore re-reads each Option through `get_option`
  to know whether it carries evidence. That is a client-side composition, not a second source
  of truth.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all
  702 catalog keys cover their usages.` (652 before this slice; 50 keys added in both locales).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app
  uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` and `pnpm typecheck` are clean.
- **Build**: `pnpm build` completes with the section's route in the Nitro output.
- **No API change**: no route, schema or migration was touched, so `contracts/openapi.json`
  and the generated client are unchanged and `make contract` is a no-op for this slice.

## Explicitly deferred (not gaps)

- The Convergence Engine (§13) that would propose Options from the map is a later slice; the
  section only carries what a member wrote.
- The Decision section (#123), the Experiment section (#124), the Learning section (#125),
  Members (#126) and the Decision Inbox (#127) stay as they are until their own slices.

## Known gaps

- None beyond the boundaries above.
