## Why

Kollio's connected product currently combines a legacy initiative marketplace with a Decision Space workflow. Its screens expose lifecycle mechanics before the next human action, and each section uses a different visual grammar. This makes the completed decision loop harder to understand and undermines the real-pilot milestone.

## What Changes

- Establish a quiet decision workbench as the connected-product visual direction: one interface typeface, restrained semantic colour, durable reading surfaces, and relationship cues used only when they explain reasoning.
- Create shared workspace primitives and token enforcement so page-level CSS cannot introduce a competing spacing, type, control, or status language.
- Rework the workspace Inbox around a clearly prioritised next action while retaining every existing waiting-work category and its privacy boundaries.
- Rework the Decision Space shell around the three product moments: frame the decision, choose with reasons, and record reality. Keep the six addressable section routes, but group them within those moments.
- Replace the raw lifecycle transition form with a contextual, readable action that offers only API-permitted transitions.
- Preserve the existing APIs, domain model, routes, authored content, permissions, and FR/EN behaviour. Legacy Idea routes remain reachable but leave the primary navigation.
- Add visual and browser evidence for the reference screens at desktop and phone widths in French and English.

## Capabilities

### New Capabilities

- `decision-workspace-experience`: the shared visual, interaction, and evidence contract for Kollio's connected decision workspace.

### Modified Capabilities

- `decision-inbox`: the reader sees one prioritised next action without losing the four bounded waiting-work sections.
- `decision-space-screens`: the Space shell groups its six routes into the three product moments and presents lifecycle progress as a contextual human action.
- `responsive`: the redesigned Inbox and Decision Space shell retain their primary action and readable hierarchy at phone and tablet widths.

## Impact

Affected code is confined to `apps/web`, its locale catalogs, browser and component tests, and the canonical tokens in `packages/ui`. No API route, persistence schema, generated client, provider, or authorization rule changes. The active `verify-pilot-journey` change remains independent and is the source of truth for live-runtime verification.
