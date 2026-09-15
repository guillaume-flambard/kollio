---
name: ux-flow-auditor
description: Evidence-bound UX flow audits for Kollio screens. Use when asked to audit a flow, screen, or user journey in the web app.
disable-model-invocation: true
---

# UX Flow Auditor

Audit Kollio product flows against Living Canvas and the domain vocabulary.
An audit without evidence is not an audit: no flow is marked AUDITED unless an
evidence file exists and is linked.

## Identifier grammar

Address every audit target as:

```
FEATURE.FLOW.SCREEN.ACTION[.STATE]
```

- Segments use the domain vocabulary in `apps/web/CONTEXT.md` (Explorer,
  IdeaDetail, Initiative, Deposit, Timeline, Companion, WorkspaceArea,
  Observer). Never invent synonyms.
- Never use generic prefixes such as `PROJ-`.
- Example: `Explorer.Filter.Toolbar.ApplyRole`, `Deposit.Submit.Form.Confirm`.

## Grounding

- **Design:** evaluate color, spacing, radius, and type against the semantic
  tokens in `packages/ui/src/tokens.css` (`--ui-*`, `--kollio-*`). Cite token
  names, never hex literals.
- **Locale:** audit FR and EN separately using locale message keys, following
  the FR/EN loop pattern in `apps/web/tests/browser/explorer.spec.ts`.
- **Behavior:** reuse the existing browser spec pattern: mocked API routes
  with typed responses from `@kollio/api-client`, explicit `waitForResponse`,
  scenario IDs (`EXPLORER-01` style).

## Evidence record

Each audit produces a record with:

1. The stable identifier.
2. The locale(s) audited.
3. The linked scenario ID(s) and their result.
4. The evidence file path(s): spec output, screenshot, or trace stub.
   Paths must exist and files must be non-empty.
5. Findings, each citing the semantic token or locale key involved.

## The rule

`AUDITED` requires items 1-4. Missing or empty evidence means the flow stays
`UNAUDITED`, and the coverage gate (`scripts/check_ux_coverage.mjs`) fails any
registry row that claims otherwise.
