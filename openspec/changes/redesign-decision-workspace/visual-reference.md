# Selected visual reference

## Approval

The product owner approved the custom Living Canvas reconciliation direction on 2026-09-19. It supersedes the generic dashboard-like reconciliation exploration.

The same language is now the reference for the Inbox and Decision Space shell at desktop and 375px:

- light, quiet, paper-like workspace with a narrow functional rail;
- Kollio-owned, rounded SVG icons with restrained asymmetry;
- source material treated as readable paper, not interchangeable cards;
- aubergine for primary action, lavender for selected relationships, coral only for open disagreement;
- one inspected relationship at a time, drawn with a fine curved connector;
- a living brief that distinguishes resolved reasoning from open uncertainty;
- narrow layouts turn side relationships into document flow rather than shrinking a desktop dashboard.

## Acceptance checklist

| Contract | Canonical implementation |
| --- | --- |
| Interface type and hierarchy | `--font-sans`, `--kollio-weight-*`, `--kollio-leading-*`, `--kollio-text-*` |
| Airy connected-workspace rhythm | `--kollio-space-*` |
| Paper surfaces and quiet borders | `--ui-bg`, `--ui-bg-elevated`, `--ui-border`, `--kollio-radius-*`, `--kollio-shadow` |
| Primary action | `--kollio-action`, `--kollio-on-action`, `KollioPrimaryAction` |
| Selected relationship | `--kollio-active-wash`, `--kollio-active-ink`, `KollioFeltMark`, `KollioRelationshipConnector` |
| Open disagreement | `--kollio-question`, `--kollio-question-wash` |
| Verified reasoning | `--kollio-verified` |
| Motion | felt wash 160-220ms; connector 220-300ms; companion changes 180-240ms; reduced motion is immediate |
| Icons | `KollioIcon` and reusable Kollio-owned SVG assets only |

## Non-negotiable refusals

No generic SaaS card grid, metric dashboard, third-party icon set, annotation font in connected workspaces, decorative gradient, glass panel, pill-heavy navigation or page-local visual value is accepted.
