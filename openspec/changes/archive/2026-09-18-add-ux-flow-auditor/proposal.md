## Why

Kollio's product surface (Explorer, IdeaDetail, Deposit, Timeline) is growing browser
coverage (11 Playwright specs with FR/EN loops and mocked API routes), but audits of
that surface are ad hoc: no stable identifiers for flows/screens/actions, no
evidence rule, and no registry linking audits to the flows they claim to cover.
Reviews therefore cannot answer "was this flow audited, and where is the evidence?".

## What Changes

- Add a minimal `ux-flow-auditor` skill: stable FEATURE/FLOW/SCREEN/ACTION/STATE
  identifiers and an AUDITED-only-with-evidence rule grounded in the Living Canvas
  design system and the project domain vocabulary.
- Add one scoped `product-auditor` agent that runs the skill through the existing
  Playwright setup (mocked API routes, `EXPLORER-01`-style scenario IDs, FR/EN loop).
- Add a flow coverage registry (`COVERAGE.md`) plus a light local gate script that
  fails when an audit claims a flow with no evidence file.
- Spike (Tranche 0): compare Playwright MCP against agent-browser on two real flows
  before locking the agent's browser tooling.

## Capabilities

### New Capabilities

- `ux/ux-flow-auditor`: Evidence-bound UX flow audits with stable flow identifiers.

### Modified Capabilities

None. This change adds agent-side audit process only; it modifies no product
behavior, no API contract, and no design tokens.

## Impact

Affects `.agents/skills/`, `openspec/changes/add-ux-flow-auditor/`, and one local
check script. No runtime, migration, or infrastructure impact. Out of scope:
Storybook stories, UI UX Pro Max as default reviewer, any product UI change.
