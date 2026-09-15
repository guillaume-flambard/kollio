# Acceptance - add-ux-flow-auditor

## Tooling spike (Tranche 0) - decided 2026-09-15

Playwright side: ran `explorer.spec.ts` + `deposit.spec.ts` (both spike flows,
FR+EN): 17 passed, 1 failed in ~3.5 min, zero setup (existing config, mocks,
fixtures). Failure evidence automatic: screenshot + trace.zip + error-context.

agent-browser side (v0.37.1, `npm i -g` + `install` required): fast CDP loop and
clean session isolation, but no request-mocking story. Against the bare fixture
server (no API backend) both `/workspace` and `/workspace/deposit` rendered
zero interactive elements. It needs a real backend or a mock API server the repo
does not have.

- [x] Playwright MCP and agent-browser each run against Explorer filter and
  Deposit submit flows.
- [x] Decision recorded here with rationale (setup cost, mock fidelity,
  evidence quality).
- [x] Decision: Playwright (existing `page.route` mock pattern) is the
  auditor's browser tooling. agent-browser stays available for exploratory
  passes against live environments only, never as audit evidence.

Side finding (not this change's scope, no product edit): `DEPOSIT-01` fr fails
deterministically with a blank page while en passes; locale keys exist in both
catalogs, and `deposit.spec.ts` `mockIo` does not mock `/api/session` unlike
`explorer.spec.ts`. Suspected test-side mock gap. Follow-up filed as #98.

## Skill (Tranche 1)

- [x] `.agents/skills/ux-flow-auditor/SKILL.md` exists; token path
  (`packages/ui/src/tokens.css`), CONTEXT.md path (`apps/web/CONTEXT.md`),
  and example spec reference (`apps/web/tests/browser/explorer.spec.ts`)
  all resolve (verified 2026-09-15).
- [x] Evidence: this file + `SKILL.md` identifier grammar section.

## Agent (Tranche 2)

- [x] `.agents/skills/ux-flow-auditor/agents/product-auditor.yaml` defines a
  read-only auditor (audit + evidence writes allowed; UI/API/token edits
  denied; `browser_tooling: playwright-existing-mock-pattern`).
- [x] Evidence: `agents/product-auditor.yaml` (agent definition). First live
  audit done 2026-09-15: `explorer.spec.ts` 8/8 passed (51.7s, FR+EN, single
  clean run after killing a conflicting background full-suite runner in the
  same process tree). Record:
  `.agents/skills/ux-flow-auditor/evidence/2026-09-15-explorer-filter.md` +
  raw `evidence/2026-09-15-explorer-filter.spec-output.txt`. Real finding:
  realism filter (`.domain-filter` button) is `display:none` below 761px with
  no mobile alternative; role select survives (44px targets kept).

## Coverage gate (Tranche 3)

- [x] `scripts/check_ux_coverage.mjs` passes on the seed registry.
- [x] `scripts/check_ux_coverage.mjs` fails on a deliberately broken row.
- [x] Evidence (verified 2026-09-15): seed registry prints `coverage: ok`
  (exit 0); appended probe row
  `Explorer.Filter.Toolbar.BrokenProbe ... does-not-exist.spec.ts | AUDITED`
  prints `coverage: Explorer.Filter.Toolbar.BrokenProbe: missing or empty
  evidence ...` (exit 1); registry restored, gate green again. CI wiring is in
  place: the `verify` job of `.github/workflows/ci.yml` runs
  `node scripts/check_ux_coverage.mjs` after the other guards.

## Coverage expansion (2026-09-15)

- [x] Registry expanded from 2 rows to 43 rows, spanning all 11 browser spec
  families in `apps/web/tests/browser/`.
- [x] Every spec ran sequentially, one file at a time, one worker. Per-file
  summaries: deposit 10 passed (22.7s), explorer 10 passed (15.2s),
  company-context 26 passed (32.4s), profiles 4 passed (10.1s), responsive
  10 passed (15.5s), proposal 4 passed (10.3s), initiative-type 6 passed
  (11.6s), timeline 2 passed (7.0s), experiments 18 passed (27.1s), team
  10 passed (19.6s), owner-actions 7 passed (20.3s). No run failed or needed a
  re-run.
- [x] Evidence: `evidence/2026-09-15-<flow>.md` records plus raw
  `.spec-output.txt` per family; every AUDITED row links a non-empty record.
- [x] `node scripts/check_ux_coverage.mjs` prints `coverage: ok` (exit 0) on
  the expanded registry.
- Product findings recorded (not fixed, read-only audit): EN placeholder
  mismatch on `ideas.profile.onIdea` / `ideas.profile.roleIn`; browser-locale
  dates in `people/[userId].vue`; localised string bound to `<time datetime>`
  in `IterationTimeline.vue`; duplicate, never-pressed `ideas.explorer.recent`
  rail control; analysis polling has no timeout state in `deposit.vue`;
  `--ui-warning` pending badge and 75% `--ui-text-muted` disabled nav entries
  below AA; `--ui-error` unused in settings and profile error states; literal
  `white`, `12px` radii and rem font sizes bypass the token scale in
  `deposit.vue` and `index.vue`; TEAM-03 does not exercise the apply action.
