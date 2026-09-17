# Acceptance evidence — add-members-screens

Change: `openspec/changes/add-members-screens`
Tickets: GitHub #126 (migration of membership, screen half; follows the API slices for workspaces and ideas)
Date: 2026-09-17
Delivered by this change: the Members section of `/workspace/settings`. It lists the workspace's members with their roles, and manages the membership of a chosen initiative — the waiting join requests with who asked, accepting one, refusing one with a reason, removing a member and adding a participant — while the navigation entry stops saying Company context and says Settings. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
|---|---|---|
| The members of a workspace are listed | `tests/browser/members.spec.ts::MEMBERS-01` (each member with the role label of the workspace) | passing |
| A workspace with a single member | `::MEMBERS-01` (the roster renders its members without the empty line) | passing |
| The members could not be read | `::MEMBERS-09` (an alert names the failure and the section still renders) | passing |
| The section asks which initiative to manage | `::MEMBERS-03`, `::MEMBERS-05`, `::MEMBERS-06`, `::MEMBERS-07` (each action runs against the chosen initiative) | passing |
| A workspace with no initiative says so | `::MEMBERS-10` | passing |
| A waiting request is listed | `::MEMBERS-02` (the requester and the note the request carries) | passing |
| Nothing is waiting | `::MEMBERS-03` (after accepting, the empty line replaces the list) | passing |
| A request is accepted | `::MEMBERS-03` (the request leaves the waiting list and the person enters the team without a manual reload) | passing |
| A refusal without a reason is refused | `::MEMBERS-04` (the section says a reason is needed and sends nothing) | passing |
| A refusal with a reason is recorded | `::MEMBERS-05` (the reason travels with the request) | passing |
| A participant is added | `::MEMBERS-07` (the workspace member, the participation and the function are sent, and the person enters the team) | passing |
| A member is removed | `::MEMBERS-06` (the person leaves the team and stops being offered as a candidate) | passing |
| Adding nobody is refused | `::MEMBERS-08` (the form says a member is needed and sends nothing) | passing |
| A refused action is shown | `::MEMBERS-04`, `::MEMBERS-08` (a refused action reports itself in the section instead of looking done) | passing |
| The section says what it is not | `::MEMBERS-10` (an initiative is needed because membership is decided per initiative) | passing |
| No score, ranking or verdict | `::MEMBERS-01` through `::MEMBERS-10` render no score, ranking or verdict for a person | passing |
| A French section | every scenario above runs in `fr` | passing |
| An English section | every scenario above runs in `en` | passing |
| Isolation, permissions and the membership rules | `apps/api/tests/integration/test_team.py` and the workspace integration suite (proved against a disposable PostgreSQL, not by a browser against mocked routes) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **310 passed**, of which `tests/browser/members.spec.ts` contributes **20** (10 scenarios × FR/EN).

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so the specs prove nothing about authentication, workspace isolation, the membership rules or persistence. Those are proved by the API integration suite against a disposable PostgreSQL (`apps/api/tests/integration/test_team.py`).
- **Membership is decided per initiative in this API, and the section says so.** There is no join request and no invite at the workspace level: `IdeaResponse.join_requests` is the only place a waiting request is readable, and accepting, refusing, adding a participant and removing a member all require an `idea_id`. The section therefore lists the workspace roster and manages the membership of a chosen initiative, in one sentence telling the reader that.
- **The section is rendered and the API refuses.** The web app knows the authenticated subject, not the caller's effective rights, so the membership controls are drawn and a refusal is displayed in the section's alert instead of hiding actions. The authorisation rule itself is asserted at the API level.
- **Renaming the navigation entry.** `navigation.settings` now reads Settings in English and Réglages in French, the route stays `/workspace/settings`, and the browser spec that asserted the old label (`apps/web/tests/browser/responsive.spec.ts`) was updated.
- **Locale gate.** `node scripts/check_locales.mjs` → FR/EN match on **1000** catalog keys (952 before this slice; the rename and the `workspace.settings.members` block are counted here).
- **Design-token gate.** `node scripts/check_design_tokens.mjs` → only canonical tokens.
- **UX coverage gate.** `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types.** `pnpm lint` and `pnpm typecheck` are clean.
- **Build.** `pnpm build` → Build complete.
- **No API change.** No route, schema or migration was touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op.
- **Two pre-existing browser specs had to move with the section.** The Members section emits its own read alert, so the single assertion in `company-context.spec.ts::SETTINGS-06` that looked for "the" alert is now scoped to the first one (the page's action alert). Its controls also had to honour the 44px touch-target floor the a11y audit measures, which is what the `.settings-members` `min-height` rules exist for.

## Explicitly deferred (not gaps)

- The participant axes and the matching between people and initiatives (`docs/00-project-overview.md` §15) stay frozen; this section shows membership, never matching.
- The Memory Retriever (§11) and the `Relevant prior memory` section it will feed.
- The remaining screen slice: #127 Inbox, which takes `/workspace` and moves the list of decision spaces to `/workspace/decision-spaces`.

## Known gaps

- No browser test forces the API to refuse a membership action (403). The alert region that would show it is asserted by `::MEMBERS-09`, and the rule itself is proved in `apps/api/tests/integration/test_team.py`.
