## Context

See `proposal.md` for motivation and `specs/idea-evaluation-workspace/spec.md` for observable behavior. The current Nuxt interface has authenticated idea list and detail routes backed by generated API contracts. Constraint, evidence, iteration, and team APIs will arrive in later vertical slices.

## Goals / Non-Goals

**Goals:**

- Establish Living Canvas and the Mineral palette as reusable interface grammar.
- Improve the current workspace shell and idea surfaces using only available data.
- Prepare contextual relationships and motion without coupling the UI to fabricated records.
- Keep all copy localized and all states keyboard accessible.

**Non-Goals:**

- Add missing constraint, evidence, iteration, or team backend capabilities.
- Add workspace theme settings in this change.
- Reproduce the approved mockup with placeholder production data.

## Decisions

### Semantic tokens carry the Mineral palette

Shared CSS tokens will define canvas, surface, ink, petrol, sea-glass wash, tangerine question, moss verified, and ochre pending roles. Components consume roles rather than palette names. This makes future workspace theming possible without changing component behavior.

### Felt-tip washes are CSS geometry

Active washes use a pseudo-element or background-size transition with a controlled irregular clip path. This avoids image assets, keeps the effect themeable, and supports immediate rendering under reduced motion. A plain text and focus treatment remains visible if the decorative layer is unavailable.

### Relationships use an overlay local to the idea workspace

Contextual lines will be rendered as accessible, pointer-events-disabled SVG paths positioned over the central and companion regions. The underlying relationship remains semantic through `aria-controls`, selected tab state, and focus movement. On narrow screens the line is omitted because the related content moves into document flow.

### Motion communicates causal order

Selection appears first, the relationship path draws second, and companion content settles last. Motion effects never gate application state and in-flight animations are replaceable. Motion for Vue handles component transitions; CSS handles small hover and wash effects.

### Missing product slices use honest empty states

The initial implementation updates the visual shell and available idea data. It does not display invented people, questions, evidence, scores, or iterations. Companion sections appear only when their contracts exist, or as clearly labeled empty states when the route requires them.

### The primary button uses a split action surface

The action label sits on a light bordered surface and the arrow occupies an integrated petrol segment. The entire control remains one semantic button or link with one focus target.

## Risks / Trade-offs

- [Irregular washes can reduce legibility] -> Keep opacity low, limit the wash to the lower third, and verify contrast with real text.
- [Connection lines can become clutter] -> Render only the current relationship and remove lines on narrow layouts.
- [The approved concept includes unavailable data] -> Implement only fields supplied by generated contracts and add later slices through OpenSpec.
- [Future theme colors could break semantics] -> Validate contrast and semantic role completeness before accepting a workspace theme.

## Migration Plan

1. Introduce semantic tokens and browser-surface styling.
2. Update the authenticated workspace shell and existing idea list/detail routes.
3. Verify French and English layouts at supported breakpoints.
4. Add contextual panels as their backend capabilities become available.
5. Roll back by reverting the token and view changes; no data migration is required.
