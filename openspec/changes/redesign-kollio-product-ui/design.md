## Context

See `proposal.md` for motivation and `specs/idea-evaluation-workspace/spec.md` for observable behavior. The current Nuxt interface has authenticated idea list and detail routes backed by generated API contracts. The idea detail now needs a narrow team slice so avatar, membership, and collaborator interactions can be evaluated without hard-coded frontend records.

## Goals / Non-Goals

**Goals:**

- Establish Living Canvas and the Aubergine palette as reusable interface grammar.
- Improve the current workspace shell and idea surfaces using only available data.
- Prepare contextual relationships and motion using explicit development fixtures rather than hard-coded frontend records.
- Keep all copy localized and all states keyboard accessible.

**Non-Goals:**

- Add missing constraint, evidence, or iteration backend capabilities.
- Add workspace theme settings in this change.
- Reproduce the approved mockup with placeholder production data.

## Decisions

### Semantic tokens carry the Aubergine palette

Shared CSS tokens will define canvas, surface, ink, aubergine, dusty-lilac wash, clay-rose question, muted-citron verified, and ochre pending roles. Components consume roles rather than palette names. This makes future workspace theming possible without changing component behavior.

### Felt-tip washes are CSS geometry

Active washes use a pseudo-element or background-size transition with a controlled irregular clip path. This avoids image assets, keeps the effect themeable, and supports immediate rendering under reduced motion. A plain text and focus treatment remains visible if the decorative layer is unavailable.

### Relationships use an overlay local to the idea workspace

Contextual lines will be rendered as accessible, pointer-events-disabled SVG paths positioned over the central and companion regions. The underlying relationship remains semantic through `aria-controls`, selected tab state, and focus movement. On narrow screens the line is omitted because the related content moves into document flow.

### The idea library is a calm two-column index

The library keeps filtering in a narrow rail and gives the remaining width to readable idea rows. Each row includes its sequence, title, short narrative, stage, date, and a direct route to the idea. The library does not reserve a permanent third column for a preview because that compresses the narrative and makes the screen read like an administration table.

### Motion communicates causal order

Selection appears first, the relationship path draws second, and companion content settles last. Motion effects never gate application state and in-flight animations are replaceable. Motion for Vue handles component transitions; CSS handles small hover and wash effects.

### Missing product slices use honest empty states

Questions, evidence, scores, and iterations remain honest empty states until their contracts exist. Collaborators come from persisted idea memberships. Development profiles are synthetic by design, carry no login subject or password, and are never embedded as frontend constants.

### Demo collaboration data is explicit and reversible

The demo seed refuses to run when the application environment is production. It uses stable UUIDs, updates its own marked profiles idempotently, and can remove only the records it owns. This keeps visual development reproducible without confusing fixtures with real people or granting them authentication access.

### The primary button uses an ink surface and active stroke

The action label and arrow sit on one ink surface with a dusty-lilac felt-tip stroke extending beneath it. The entire control remains one semantic button or link with one focus target.

## Risks / Trade-offs

- [Irregular washes can reduce legibility] -> Keep opacity low, limit the wash to the lower third, and verify contrast with real text.
- [Connection lines can become clutter] -> Render only the current relationship and remove lines on narrow layouts.
- [The approved concept includes unavailable data] -> Implement only fields supplied by generated contracts and add later slices through OpenSpec.
- [Future theme colors could break semantics] -> Validate contrast and semantic role completeness before accepting a workspace theme.

## Migration Plan

1. Introduce Aubergine semantic tokens and browser-surface styling.
2. Update the authenticated workspace shell and existing idea list/detail routes.
3. Add the collaborator schema, generated contract, and development seed.
4. Verify French and English layouts at supported breakpoints.
5. Add remaining contextual panels as their backend capabilities become available.
6. Roll back demo content with the reset command before reverting its schema migration.
