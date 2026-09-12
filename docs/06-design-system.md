# 06: Design system

## Approved direction

Kollio uses the **Living Canvas** interaction model with the **Mineral** palette. The product is light-first, airy, rounded, and collaborative. It reveals relationships through interaction instead of presenting a dense dashboard.

Earlier Collective.work-inspired mockups and the blue editorial direction are superseded by this document and the root `DESIGN.md`.

## Typography

- Interface and headings: Geist, weights 400 to 700.
- Data and hashes: Geist Mono.
- Fallback: `system-ui` and `monospace` respectively.

## Default semantic palette

| Role | Value |
|---|---|
| Canvas | `#F6F5F1` |
| Surface | `#FFFFFF` |
| Ink | `#202522` |
| Primary interaction | `#164B46` |
| Active wash | `#BFE3D7` |
| Open question | `#E8744F` |
| Verified evidence | `#557A62` |
| Pending | `#A57932` |

Dark-mode values remain available as an alternative theme and must preserve the same semantic roles. Workspace-specific color settings are a later capability. They must pass contrast validation before activation.

## Shape and depth

- Main surfaces: 16px radius.
- Rows and controls: 10 to 12px radius.
- Fully rounded geometry: avatars and compact status dots only.
- Borders: thin and neutral.
- Shadows: soft, offset, and reserved for overlays or raised controls.

## Signature active state

Active text receives a translucent felt-tip wash behind its lower third. The lower edge may be slightly irregular. The treatment must remain precise and readable. It applies consistently to navigation, tabs, selected passages, linked questions, and evidence.

A selected passage may connect to one person, question, or evidence item through a thin curved line. Only the current relationship is visible. On narrow screens the related content moves into the document flow and the line disappears.

## Primary action

The primary action is one semantic control with a light bordered label area and an integrated filled primary-color arrow segment. Hover moves the arrow by no more than 3px and draws the active edge. Press feedback is subtle and immediate.

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
- Use one consistent SVG icon family; never use emoji as icons.
- Keep keyboard focus visible and touch targets at least 44px.
- Avoid pill badges, generic card grids, oversized metrics, decorative charts, gradients, glass effects, and dense simultaneous panels.
