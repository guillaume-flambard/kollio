# Kollio Design Direction

## Approved direction

Kollio uses the **Living Canvas** interaction model with the **Aubergine** palette. The interface should feel airy, rounded, light, and collaborative. It reveals context through interaction instead of displaying every available fact at once.

## Visual language

- **Canvas:** porcelain `#F7F5F7`.
- **Surface:** white `#FFFFFF`.
- **Ink:** soft black `#252229`.
- **Primary:** deep aubergine `#493B57`.
- **Active wash:** dusty lilac `#DDD3E8`.
- **Open question:** clay rose `#D47A70`.
- **Verified evidence:** muted citron `#899744`.
- **Pending:** warm ochre `#A57932`.
- **Radii:** 16px for main surfaces, 10 to 12px for rows and controls, fully rounded shapes only for avatars and compact status dots.
- **Depth:** thin neutral borders and soft offset shadows only when a surface is elevated.
- **Type:** modern sans serif throughout; monospace is reserved for hashes and measured values.

## Signature interaction

The active state is a translucent felt-tip wash behind the lower third of a label or selected phrase. Its lower edge is slightly irregular, but the effect remains precise and restrained. The same gesture identifies active navigation, selected text, the current panel, and linked questions.

Selected passages can connect to a person, question, or evidence item through a thin curved line. The line is contextual and transient. It must not become permanent diagram clutter.

## Buttons

The primary action uses an ink surface with a dusty-lilac felt-tip stroke extending slightly beneath it. Hover draws the stroke from left to right and moves the arrow by a few pixels. Press compresses the control slightly. Secondary actions remain quiet text or outline controls.

## Motion

- Draw the felt-tip wash in 160 to 220ms with an exponential ease-out.
- Draw contextual connection lines in 220 to 300ms after the selection is visible.
- Replace side-panel content with a short spatial transition of 180 to 240ms.
- Move button arrows by no more than 3px on hover and return immediately on cancellation.
- Preserve final semantic state independently from animation completion.
- Under reduced motion, render the final state immediately and keep only essential color changes.

## Composition

- Keep navigation slim and persistent on wide screens.
- Give the idea narrative the largest uninterrupted reading area.
- Use a contextual companion panel for team, open questions, and evidence.
- Show one active relationship at a time.
- Use progressive disclosure for detailed scores, evidence, and history.
- Avoid generic card grids, pill badges, oversized metrics, dense dashboards, and decorative charts.

## Future theming

Workspace administrators will eventually be able to select semantic brand colors in application settings. Theme values must preserve the semantic roles, contrast targets, and interaction grammar defined here.
