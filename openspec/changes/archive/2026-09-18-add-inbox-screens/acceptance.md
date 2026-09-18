# Acceptance evidence — add-inbox-screens

Change: `openspec/changes/add-inbox-screens`
Tickets: GitHub #127 (migration step 9 of `docs/00-project-overview.md` §20, screen half; follows the API slice #117)
Date: 2026-09-17
Delivered by this change: the Decision Inbox at `/workspace`. It reads the four sections the API computes, leads every entry to the space and the section where it can be acted on, bounds each section and stays honest about the question it cannot yet answer. The decision spaces list moves to `/workspace/decision-spaces` and the navigation gains an Inbox entry. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| A member reads the inbox | `tests/browser/inbox.spec.ts::INBOX-01` (heading, intro and the four sections rendered) | passing |
| The four sections are filled from the answer | `::INBOX-01` (one entry per section, each with its own kind) | passing |
| Nothing waits | `::INBOX-05` (one honest empty state instead of invented work) | passing |
| An entry leads to its space and section | `::INBOX-02` (each entry links to `/workspace/decision-spaces/space-one/<section>?workspace=workspace-one`) | passing |
| Work waiting on the reader is told apart | `::INBOX-04` (a contribution and a finding named apart, with the detail the API sends) | passing |
| A bounded section reports what it does not show | `::INBOX-03` (one entry shown, three reported as remaining) | passing |
| An empty section is named as empty | `::INBOX-06` (each empty section keeps its heading and says it is empty) | passing |
| The unanswered question is named | `::INBOX-07` (the memory section states why it cannot answer yet) | passing |
| No empty memory list | `::INBOX-07` (the memory block renders no list and no empty line) | passing |
| The list is reached at its new route | `tests/browser/decision-spaces.spec.ts::DECISION-SPACES-01`, `::DECISION-SPACES-02` (listing and empty state at `/workspace/decision-spaces`) | passing |
| The inbox points at the list | `::INBOX-09` (the link to `/workspace/decision-spaces`) | passing |
| Four entries, one active | `decision-spaces.spec.ts::DECISION-SPACES-09` (Inbox active on `/workspace`, Decision spaces inactive) | passing |
| The spaces entry is active on the list | `decision-spaces.spec.ts::DECISION-SPACES-09` (Decision spaces active on `/workspace/decision-spaces`, Inbox inactive) | passing |
| The inbox could not be read | `inbox.spec.ts::INBOX-08` (heading and intro kept, the failure shown as an alert) | passing |
| A French inbox | every scenario in `inbox.spec.ts` runs in `fr` | passing |
| An English inbox | every scenario in `inbox.spec.ts` runs in `en` | passing |
| No score, no ranking | `inbox.spec.ts::INBOX-01` and `::INBOX-05` (the screen renders counts of what waits, never a score or a ranking) | passing |
| Isolation, permissions and the sections | `apps/api/tests/integration/test_decision_inbox.py` (proved against a disposable PostgreSQL: the reader's workspaces, the section rules and the bound) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **328 passed**, of which `tests/browser/inbox.spec.ts` contributes **18** (9 scenarios × FR/EN).

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove what the screen renders and where it links. Which workspace a reader may see, which space belongs in which section, the ordering and the bound are proved against a disposable PostgreSQL in `apps/api/tests/integration/test_decision_inbox.py`.
- **One request, no workspace parameter.** A member can belong to several workspaces, so the inbox is read by a single `GET /api/inbox` call; the proxy passes the optional `limit` only when it is a number, so an empty query value can never reach the API as an invalid bound.
- **The fifth section is absent from the answer, not just from the screen.** `DecisionInboxResponse` carries four sections and `openspec/specs/decision-inbox/spec.md` states that no prior memory section is returned while no capability surfaces confirmed Learnings; the screen repeats that reason in words instead of rendering an empty list.
- **The space list moved without changing.** `git mv` put the list at `/workspace/decision-spaces`; its own `acceptance.md` in `openspec/changes/add-decision-space-screens/` is still accurate for the list itself, and the five exact `/workspace` visits in `decision-spaces.spec.ts` now point at the new route.
- **The navigation grew a fourth entry.** `decision-spaces.spec.ts::DECISION-SPACES-09` was rewritten: the Inbox is active on `/workspace`, Decision spaces on `/workspace/decision-spaces`, Initiatives on `/workspace/ideas`.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 1029 catalog keys cover their usages.` (1000 before this slice: `navigation.inbox` and the `inbox` block).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` and `pnpm typecheck` are clean.
- **Build**: `pnpm build` → `Build complete!` (5.6 MB total, 1.45 MB gzip).
- **No API change**: no route, schema or migration was touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op.

## Explicitly deferred (not gaps)

- **The Memory Retriever (§11)** and the section it will feed: prior confirmed Learnings with their provenance, which is what would let the fifth question be answered at all.
- **Paging inside a section.** Each section reports how many entries it does not show; asking for more is a read parameter the API already accepts, and no screen offers it yet.
- **The P1 items of `docs/00-project-overview.md`** (browser extension, Slack/Notion/Drive, notifications, revisit alerts).

## Known gaps

- No browser spec forces a refused inbox read (403) from the API: the proxy forwards the status and the alert path is covered by `::INBOX-08`, while the permission rule itself is proved in `apps/api/tests/integration/test_decision_inbox.py`.
