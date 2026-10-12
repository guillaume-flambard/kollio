## Context

See `proposal.md`. The current web application has a shared token file, but substantial page-local styling across the workspace, legacy Idea surfaces, the Decision Space shell, and six section routes. The product specification defines three visible moments while the current shell exposes six peer sections and a raw lifecycle control.

## Goals / Non-Goals

**Goals:**

- Establish a reusable connected-workspace design language before redesigning individual decision sections.
- Make Inbox and Decision Space the reference routes for hierarchy, action priority, responsive behaviour, and FR/EN visual evidence.
- Preserve API behaviour, URLs, locale keys, permissions, and existing browser-test fixtures while changing presentation and interaction hierarchy.

**Non-Goals:**

- Redesigning the marketing landing page, public product, legacy Idea detail, or Deposit flow in this change.
- Changing decision lifecycle rules, authorization, data shapes, or the six section capabilities.
- Adding a component library, third-party icon set, new font dependency, or a new visual theme.

## Decisions

### Use the quiet decision workbench as the connected-product direction

The workspace will use Geist for interface and display text, a light neutral canvas, semantic aubergine for primary action, and lavender only for selection or an explained relationship. Texture and felt-tip marks will be reserved for an active relationship rather than repeated as ornamental treatment.

This replaces the current mixture of display and annotation fonts, broad washes, card treatments, and handwritten notes. Keeping the existing mixed direction would preserve visual familiarity but would not solve the competing-language problem.

### Build primitives before route redesign

The change will establish shared page frame, header, action, status, reasoning block, feedback state, and navigation primitives backed only by canonical tokens. Reference routes will consume them before later section work begins.

This costs a small upfront extraction but prevents Options, Experiment, and other large route files from reproducing the current drift. A page-by-page polish would be quicker initially but would create new one-off CSS.

### Prioritise presentation from existing Inbox data

The UI will choose a deterministic primary next action from entries already returned by the four Inbox sections. It will retain the source grouping, ordering, privacy boundaries, and destinations, so no API or scoring change is required.

This avoids inventing a new ranking service. The trade-off is that the first policy remains intentionally simple and must be explicit in tests.

### Organise the Space shell by three moments without changing section routes

Explore and Converge form the framing moment; Options and Decision form the choice moment; Experiment and Learning form the reality moment. The six current URLs remain valid and the active sub-section stays directly addressable.

This gives new members a product narrative while retaining deep links, back-button behaviour, and all existing browser fixtures. Replacing routes with a single dynamic canvas would be visually tempting but would add navigation and test risk without proving a user benefit.

### Turn lifecycle transition selection into a contextual action

The shell will expose the currently permitted action as a clear outcome, then disclose the permitted target when needed. Reopening preserves the reason requirement. The API remains the authority for allowed transitions.

This replaces an implementation-facing select control. It does not guess a transition or hide a transition the lifecycle permits.

### Test visual contracts at the routes that establish the system

Browser specs will cover FR/EN Inbox and Decision Space reference states at desktop and phone widths, including empty and failure states where they exist. Component tests will cover shared primitives; existing mocked route tests remain presentation evidence only.

## Risks / Trade-offs

- [A visual refactor accidentally changes permissions or lifecycle behaviour] -> Keep API contracts unchanged and retain behaviour assertions before replacing route markup.
- [A deterministic next-action policy hides work] -> Render every existing populated Inbox section below the primary action and test that the selected action links to one of those entries.
- [Token enforcement blocks legitimate responsive work] -> Extend the canonical token scale when a durable step is needed instead of allowing local values.
- [Desktop hierarchy collapses on phones] -> Design the Space moment navigation as a document-flow element before adding desktop layout enhancements.
- [Legacy routes create a second product after the shell changes] -> Preserve their URLs for compatibility but remove them from primary navigation, then decide their future in a later scoped change.

## Migration Plan

1. Add the shared primitives and token guard with no API or route-contract change.
2. Replace workspace navigation and Inbox, preserving the existing Inbox response and route destinations.
3. Replace the Decision Space shell, preserving the six nested routes and lifecycle request behaviour.
4. Run component, browser, locale, responsive, type, and production-build checks; capture reference evidence.
5. Deploy as an ordinary web-client change. Roll back by reverting the web and token commit; no data migration is required.
