## Context

See `proposal.md` for motivation. The web app already has a working Playwright
pattern (`apps/web/tests/browser/explorer.spec.ts`): mocked API routes, typed
responses from `@kollio/api-client`, scenario IDs (`EXPLORER-01`), and an FR/EN
loop over locale message catalogs. Design authority is Living Canvas
(`packages/ui/src/tokens.css`, semantic `--ui-*` / `--kollio-*` tokens, no hex
literals). Domain vocabulary is fixed (`apps/web/CONTEXT.md`: Explorer,
IdeaDetail, Initiative, Deposit, Timeline, Companion, WorkspaceArea, Observer).

## Goals / Non-Goals

**Goals:**

- Every UX audit names the exact flow/screen/action/state it covers, using
  identifiers stable across runs.
- No flow is ever marked AUDITED without a linked evidence file (spec run,
  screenshot, or trace stub).
- The auditor runs inside existing conventions: Playwright mocks, i18n keys,
  Living Canvas tokens, domain vocabulary.

**Non-Goals:**

- Product UI changes of any kind.
- Storybook introduction (zero stories exist; deferred until the auditor proves
  value on real flows).
- UI UX Pro Max as default reviewer (kept as opt-in second opinion only).

## Decisions

### Stable FEATURE/FLOW/SCREEN/ACTION/STATE identifiers, no generic PROJ prefix

Audit targets compose as `FEATURE.FLOW.SCREEN.ACTION[.STATE]` using domain words
(Explorer, Deposit, Timeline), never generic `PROJ-*` IDs. Rationale: generic IDs
collide across features and cannot be mapped to coverage; domain words are
already canonical in `apps/web/CONTEXT.md`.

### AUDITED-only-with-evidence as a gate, not a guideline

The coverage script fails when a registry row claims AUDITED with a missing or
empty evidence path. Rationale: a guideline rots; a failing check is the only
form of this rule that survives contact with deadlines.

### One scoped agent on existing Playwright mocks

The `product-auditor` agent reuses the established spec pattern (route mocks,
`waitForResponse`, FR/EN loop) and audits FR and EN separately, because locale
strings change layout and the existing suite already treats locale as a
first-class axis. Real-backend audits are out of scope for this change.

### Tranche 0 spike before locking browser tooling

Playwright MCP vs agent-browser is decided by running both against two real
flows (Explorer filter, Deposit submit) and comparing setup cost, mock fidelity,
and evidence quality. The decision and its rationale land in `acceptance.md`
before Tranche 2 starts. Default hypothesis: Playwright MCP wins through
incumbency (config, 11 specs, fixtures already exist).

## Risks

- Identifier drift as screens evolve: mitigated by deriving names from
  `CONTEXT.md` vocabulary and reviewing the registry in each audit change.
- Evidence stubs without substance (empty screenshots): mitigated by requiring
  non-empty evidence paths plus the linked scenario ID in the registry.
