## Context

The selected visual reference presents Kollio as an initiative portfolio for internal teams. Its central visual follows one initiative from signal to evidence and an open question, then to a documented decision.

## Decisions

### The product explains the promise

The hero includes a real interface-shaped preview rather than an abstract illustration. It remains demonstration content and never implies that public visitor data has been loaded.

### The landing uses existing visual primitives

The page consumes the shared Aubergine tokens and the existing primary action and brand components. The initiative preview is isolated as a reusable component so later platform and use-case pages can reuse the same workflow grammar.

### B2B trust appears in the primary viewport

Private spaces, roles and permissions, and traceable analysis appear beside the primary value proposition. Public community mechanics remain outside the initial message.

### Responsive flow becomes sequential

At narrow widths, the three workflow stages stack in source order and decorative relationship paths disappear. Every relationship remains understandable from labels and grouping alone.

### Visual marks are components

Relationship curves use explicit endpoints in the reference coordinate system. Hand-drawn arrows and felt-tip emphasis are separate reusable SVG components with their own motion and reduced-motion behavior. Pages do not approximate these marks with unrelated borders, clip paths, or one-off pseudo-elements.

### Outcome artwork belongs to the product

The three outcome benefits use original SVG illustrations derived from the same tactile paper language as the product empty states. SVG filters provide a restrained paper grain while native paths preserve sharp rendering at every density. A typed component owns the asset mapping, intrinsic dimensions, lazy loading, and decorative accessibility behavior so other marketing screens can reuse the artwork without duplicating paths or markup.

The same artwork component also serves the method and final call-to-action sections. Each asset declares its native dimensions to prevent layout shifts and preserve its intended composition.

## Risks / Trade-offs

- [The preview can become too dense] -> Limit each stage to one primary example and progressively hide secondary details on small screens.
- [Demonstration data can look live] -> Present it inside a clearly bounded product preview and avoid user-specific claims.
- [Decorative annotations can reduce clarity] -> Keep them sparse, non-semantic, and disabled under reduced motion.
- [Generated artwork can become visually noisy at small sizes] -> Use compact isolated compositions, fixed aspect ratios, and no surrounding icon container.
