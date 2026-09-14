# Align the workspace UI on the shared design tokens (#69)

Five values used variable names absent from `packages/ui/src/tokens.css`,
so their hardcoded fallback always won: visually aligned with the design
system, not driven by it.

| File | Before | After |
| --- | --- | --- |
| deposit.vue | `var(--kollio-border, #E8E3EA)` | `var(--ui-border)` |
| deposit.vue | `var(--kollio-surface, #FFFFFF)` | `var(--ui-bg-elevated)` |
| deposit.vue | `var(--kollio-ink, #252229)` | `var(--ui-text)` |
| deposit.vue | `color: #D47A70` | `var(--ui-error)` |
| deposit.vue | `var(--kollio-heading, #493B57)` | `var(--kollio-heading)` |
| people/[userId].vue | `var(--kollio-surface-accented, #EEE8F2)` | `var(--ui-bg-accented)` |
| IterationTimeline.vue | `var(--question-clay, #D47A70)` | `var(--kollio-question)` |
| SketchAnnotation.vue | fallbacks `#493b57`, `#ddd3e8` | token only |

Rendered colours are unchanged (the canonical tokens resolve to the same
values). Result: zero literal colours in `apps/web/app` and no
`--kollio-*` name absent from the token file. The automated guard is #70.
