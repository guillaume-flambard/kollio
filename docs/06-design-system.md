# 06: Design system

## Approved direction

Kollio uses the **Living Canvas** interaction model with the **Aubergine** palette. The product is light-first, airy, rounded, and collaborative. It reveals relationships through interaction instead of presenting a dense dashboard.

Earlier Collective.work-inspired mockups and the blue editorial direction are superseded by this document and the root `DESIGN.md`.

## Non negotiable

This direction is the reference. Every later screen **extends** it; nothing replaces it, and no page introduces its own palette, card style or spacing scale. All styling goes through the canonical tokens in `packages/ui/src/tokens.css` and the shared theme in `packages/ui/src/theme.ts`. A page never writes a literal colour, a spacing length, a font weight, a line height, or a variable name that does not exist in the token file (the fallback would silently win, and the drift would be invisible). Issues #69 and #70 close the current drift and add the automated guard.

## Brand mark

The Kollio mark is an open lowercase `k` built from two rounded gestures meeting around a small seed. The aubergine stem represents a stable shared workspace, the lavender stroke represents contributions moving an idea forward, and the muted citron seed marks the point where they meet.

- Production asset: `apps/web/public/brand/kollio-mark.svg`.
- The mark always appears with the `Kollio` wordmark in navigation when space permits.
- The wordmark uses Geist at weight 700 with tight tracking.
- The mark may appear alone below 32px or where the product name is already visible.
- Preserve clear space equal to the seed diameter around the mark.
- Do not recolor individual strokes, rotate the mark, place it in a badge, or add gradients and shadows.

## Typography

- Interface and headings: Geist. The weight scale is closed at the four weights the loaded families actually provide, and no other value is valid: `--kollio-weight-regular` 400, `--kollio-weight-medium` 500, `--kollio-weight-strong` 600, `--kollio-weight-display` 700. A screen never writes a bare number for `font-weight`: a weight the typefaces do not provide is silently resolved to a different face, so the drift stays invisible.
- Line heights come from the named scale: `--kollio-leading-display` 1.04, `--kollio-leading-heading` 1.2, `--kollio-leading-body` 1.6, `--kollio-leading-relaxed` 1.72. A screen never writes a bare number for `line-height`.
- Data and hashes: Geist Mono.
- Fallback: `system-ui` and `monospace` respectively.

## Default semantic palette

| Role | Value |
|---|---|
| Canvas | `#F7F5F7` |
| Surface | `#FFFFFF` |
| Ink | `#252229` |
| Primary interaction | `#493B57` |
| Active wash | `#DDD3E8` |
| Open question | `#D47A70` |
| Verified evidence | `#899744` |
| Pending | `#A57932` |

Dark-mode values remain available as an alternative theme and must preserve the same semantic roles. Workspace-specific color settings are a later capability. They must pass contrast validation before activation.

## Shape and depth

- Main surfaces: 16px radius.
- Rows and controls: 10 to 12px radius.
- Fully rounded geometry: avatars and compact status dots only.
- Borders: thin and neutral.
- Shadows: soft, offset, and reserved for overlays or raised controls.

## Spacing

- The scale is closed and named: `--kollio-space-xs` 4, `--kollio-space-sm` 8, `--kollio-space-md` 14, `--kollio-space-lg` 22, `--kollio-space-xl` 32, `--kollio-space-2xl` 48, `--kollio-space-3xl` 64 and `--kollio-space-4xl` 96, in px.
- Vertical rhythm between sections takes the upper steps; spacing inside a block takes the lower ones.
- A screen never writes a bare pixel value for `margin`, `padding`, `gap`, or an inset. If a needed step is missing, the scale is extended in `tokens.css` rather than improvised at the call site. Responsive spacing may scale over the named steps with `clamp()`.

## Signature active state

Active text receives a translucent felt-tip wash behind its lower third. The lower edge may be slightly irregular. The treatment must remain precise and readable. It applies consistently to navigation, tabs, selected passages, linked questions, and evidence.

A selected passage may connect to one person, question, or evidence item through a thin curved line. Only the current relationship is visible. On narrow screens the related content moves into the document flow and the line disappears.

## Primary action

The primary action is one semantic ink-colored control with a dusty-lilac felt-tip stroke extending slightly beneath it. Hover moves the arrow by no more than 3px and draws the stroke from left to right. Press feedback is subtle and immediate.

## Motion

- Felt-tip wash: 160 to 220ms.
- Relationship line: 220 to 300ms after selection.
- Companion panel change: 180 to 240ms.
- Use exponential ease-out and cancel in-flight motion when state changes.
- Application state must never depend on an animation completion event.
- `prefers-reduced-motion` renders final states immediately.

## Implementation rules

- Map semantic tokens through Nuxt UI and shared CSS.
- Put every interface string behind FR and EN i18n keys.
- Use only Kollio-owned SVG icons and illustrations; never use emoji or third-party icon packs.
- Author functional icons once in a shared component with a 24px coordinate system, rounded joins, restrained asymmetry, and `currentColor` strokes.
- Keep narrative spot illustrations as reusable SVG assets. Paper grain and felt-tip texture belong inside the SVG and must remain subtle at small sizes.
- Raster images may be used as visual exploration references, but recurring product and marketing artwork ships as vector assets. Exception 2026-09-13: the avatar sprite, empty-state, and error illustrations ship as raster; their vector redraw is tracked follow-up work, not a waiver of this rule.
- Keep keyboard focus visible and touch targets at least 44px.
- Avoid pill badges, generic card grids, oversized metrics, decorative charts, gradients outside the felt-tip washes defined above, glass effects, and dense simultaneous panels.
