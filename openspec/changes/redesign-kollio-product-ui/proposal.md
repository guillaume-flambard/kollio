## Why

Kollio's current workspace interface exposes the available data but does not yet express the product's core loop: understand an idea, inspect the evidence, and choose the next experiment. The replacement should make that decision flow obvious while establishing a simpler visual system that can scale across future product slices.

## What Changes

- Replace the current generic workspace presentation with a calm, compact product shell.
- Introduce a consistent radius, border, spacing, and elevation system for navigation, panels, rows, controls, and status chips.
- Reframe idea detail around three levels: idea context, constraints, and contextual evidence.
- Keep the next experiment visible as the primary action without turning the page into a dashboard.
- Add a compact iteration history and a contextual comparison mode for evidence changes.
- Preserve French and English interface behavior, responsive layouts, keyboard access, and reduced-motion support.
- Add development-only collaboration profiles and idea memberships so team interactions can be evaluated with realistic, clearly synthetic data.

## Capabilities

### New Capabilities

- `idea-evaluation-workspace`: Covers the interaction and presentation requirements for understanding an idea, inspecting constraints and evidence, and starting the next experiment.

### Modified Capabilities

None.

## Impact

- Affects the Nuxt workspace layout, idea list and detail views, shared visual tokens, localized copy, and related UI tests.
- Extends the idea detail contract with workspace-isolated collaborators while keeping authentication and deployment architecture unchanged.
