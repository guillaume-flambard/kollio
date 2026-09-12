---
name: Kollio Living Canvas
description: An airy workspace where ideas, evidence, and collaborators stay visibly connected.
colors:
  primary-aubergine: "#493B57"
  active-wash: "#DDD3E8"
  canvas-porcelain: "#F7F5F7"
  surface-white: "#FFFFFF"
  surface-muted: "#F2EFF3"
  surface-accented: "#EEE8F2"
  border-soft: "#E8E3EA"
  ink-soft-black: "#252229"
  ink-muted: "#6F6877"
  question-clay: "#D47A70"
  question-wash: "#F5DEDB"
  evidence-citron: "#899744"
  pending-ochre: "#A57932"
typography:
  display:
    fontFamily: "Bricolage Grotesque, system-ui, sans-serif"
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Geist, system-ui, sans-serif"
    fontSize: "clamp(1.875rem, 3vw, 3rem)"
    fontWeight: 600
    lineHeight: 1.08
    letterSpacing: "-0.04em"
  title:
    fontFamily: "Geist, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "Geist, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.75
  label:
    fontFamily: "Geist, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.5
  mono:
    fontFamily: "Geist Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: "10px"
  md: "12px"
  lg: "16px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "14px"
  lg: "22px"
components:
  primary-action:
    backgroundColor: "{colors.ink-soft-black}"
    textColor: "{colors.surface-white}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "0 10px 0 18px"
    height: "44px"
  workspace-surface:
    backgroundColor: "{colors.surface-white}"
    textColor: "{colors.ink-soft-black}"
    rounded: "{rounded.lg}"
    padding: "28px"
  navigation-item:
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "0 12px"
    height: "44px"
  linked-passage:
    backgroundColor: "{colors.active-wash}"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.sm}"
  empty-state:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.lg}"
    padding: "20px"
  provenance-card:
    backgroundColor: "{colors.surface-accented}"
    textColor: "{colors.ink-soft-black}"
    rounded: "{rounded.lg}"
    padding: "20px"
---

# Design System: Kollio Living Canvas

## Overview

**Creative North Star: "The Living Canvas"**

The canonical visual reference is stored at
`docs/assets/design/approved-idea-detail.png`. Desktop implementation reviews
must compare against it at 1536 by 1024 before changing the shared primitives.

Kollio's authenticated workspace is a quiet, collaborative canvas. Porcelain surrounds white working surfaces, deep aubergine carries intent, and soft felt-tip marks reveal the current thread of attention. The interface keeps the idea narrative dominant while related people, questions, and evidence remain close enough to inspect without breaking the reading flow.

The system reveals detail through deliberate interaction. A selected phrase can expose its provenance, a companion panel changes with the user's focus, and long content expands only on request. The interface is bilingual, light first, responsive, keyboard usable, and honest when collaboration or evidence has not arrived yet.

**Key Characteristics:**

- Airy reading surfaces with restrained structural depth.
- Lower-third felt-tip marks that carry active state and provenance.
- One visible relationship between the narrative and its current context.
- Progressive disclosure that preserves the idea as the main reading object.
- Real source labels, identifiers, and empty states instead of invented activity.

## Colors

The palette pairs warm porcelain neutrals with a low-chroma aubergine family. Clay, citron, and ochre retain semantic meaning for questions, verified evidence, and pending work.

### Primary

- **Deep Aubergine:** Carries actions, focus, active connections, and restrained emphasis.
- **Dusty Lilac Wash:** Marks the lower third of active labels and selected passages without turning them into badges.

### Secondary

- **Clay Rose:** Identifies open questions or unresolved human judgment.
- **Muted Citron:** Identifies verified evidence and positive status.
- **Warm Ochre:** Identifies pending or incomplete work.

### Neutral

- **Porcelain Canvas:** Holds the workspace and its subtle radial atmosphere.
- **White Surface:** Holds the idea narrative and contextual companion.
- **Muted and Accented Surfaces:** Separate secondary content through tone instead of extra elevation.
- **Soft Black and Muted Ink:** Preserve a clear reading hierarchy without harsh contrast.
- **Soft Border:** Defines surfaces and controls when tonal separation alone is insufficient.

### Named Rules

**The Felt-Tip Rule.** Active labels use a short lower-edge brush mark. Linked passages use a diffuse, irregular full-height wash. Both treatments follow the text width and never become full-row selection bars.

**The Semantic Accent Rule.** Clay, citron, and ochre communicate product meaning. Do not use them as arbitrary decoration.

## Typography

**Display Font:** Bricolage Grotesque with a system sans serif fallback

**Body Font:** Geist with a system sans serif fallback

**Label/Mono Font:** Geist Mono for hashes, source identifiers, and measured values

**Character:** Geist makes dense product content calm and direct. Bricolage Grotesque is reserved for expressive brand moments; the authenticated workspace keeps headings in Geist so the work remains foregrounded.

### Hierarchy

- **Display:** Bold and compact for brand-led public surfaces only.
- **Headline:** Semibold with tight tracking for idea titles. It scales fluidly from mobile to wide screens.
- **Title:** Semibold for major content sections and companion headings.
- **Body:** Regular with generous line height. Narrative passages stay near 72 characters per line.
- **Label:** Medium weight for navigation, actions, metadata, and tab labels.
- **Mono:** Regular and compact for technical identifiers when their exact form matters.

### Named Rules

**The Narrative First Rule.** The idea title and pitch carry the strongest type. Counts, dates, stages, and source metadata remain quieter.

## Layout

At the 1536px reference viewport, the desktop workspace uses a 180px navigation rail, a 870px narrative surface, and a 392px contextual companion. The outer margin and 14px content gap preserve the geometry of the approved reference while fluid clamps scale the same proportions down to the desktop breakpoint.

At widths below 1024px, navigation becomes a compact top bar, the idea and companion stack in one column, and the curved relationship is hidden. The companion drops its viewport-height minimum so its real content determines its height. On narrow screens the primary action follows the idea summary and metadata instead of preceding the title. Subject separators remain attached to their labels when rows wrap.

Long pitches begin in a bounded reading window with a tonal fade and an explicit expand control. Companion tabs replace content in place. Detailed evidence, history, and team context appear only when relevant or requested.

**The One Relationship Rule.** Show at most one active link between a passage and its contextual target. Render it only while both endpoints are visible.

## Elevation & Depth

Living Canvas is flat by default. Borders and tonal layers establish structure; a single ambient shadow lifts the two principal workspace surfaces (`0 10px 30px rgba(73, 59, 87, 0.055)`). The canvas adds faint lilac and clay radial washes without competing with content.

### Shadow Vocabulary

- **Workspace Ambient:** A broad, low-opacity aubergine shadow for the narrative and companion surfaces.

### Named Rules

**The Structural Depth Rule.** Elevate the main work surfaces once. Use borders or tonal fills for everything nested inside them.

## Shapes

Main surfaces and nested content blocks use gently rounded 16px corners. Navigation items and primary actions use 12px corners; compact controls may use 10px. Fully round shapes are reserved for avatars, status dots, and small markers. The felt-tip gesture is the deliberate exception: its asymmetric lower edge should look hand-drawn while remaining controlled.

## Components

The production primitives live in `apps/web/app/components/kollio`. Reuse
`KollioFeltMark`, `KollioPrimaryAction`, and `KollioContextTabs` across workspace
screens. Structural surfaces use the shared `kollio-surface` class. New screens
must consume these primitives and the semantic tokens from `@kollio/ui` instead
of duplicating their geometry, colors, or interaction states.

### Primary Actions

- **Shape:** A compact 44px control with 12px corners.
- **Color:** Soft Black holds White Surface text; Dusty Lilac appears as a small offset stroke below the control.
- **Hover / Focus:** Hover draws the stroke from left to right and moves the arrow by no more than 3px. Keyboard focus uses the shared 2px aubergine outline with a 3px offset.
- **Active:** Pressing compresses the control slightly without changing its semantic state.

### Workspace Surfaces

- **Shape:** White surfaces with 16px corners, a Soft Border, and Workspace Ambient depth.
- **Role:** The largest surface holds the narrative. The narrower sticky surface holds the contextual companion.
- **Internal structure:** Nested sections use borders or muted tonal fills instead of independent cards and shadows.

### Navigation

- **Desktop:** A slim persistent rail with 44px rows and quiet outline icons. The active label receives a lower-third felt-tip mark.
- **Mobile:** A 64px sticky top bar preserves the brand, locale switch, and sign-out action.
- **Unavailable destinations:** Keep future destinations visible but clearly disabled. Do not imply that they are interactive.

### Contextual Companion

- **Tabs:** Team, questions, and evidence share an accessible three-tab rail. Arrow keys move between tabs; Home and End jump to the first and last tab.
- **Panel change:** Content enters with a short 200ms spatial transition. Reduced-motion users receive the final state immediately.
- **Empty state:** A muted 16px surface explains the absence of data in plain language and keeps counts at zero.

### Linked Passages

- **Annotation:** A translucent Dusty Lilac wash follows the selected words with softly blurred, irregular edges. The passage remains readable and behaves as a real button.
- **Connection:** Activating the passage opens its related panel and draws one 1.75px curved aubergine line in 260ms. A 4.5px source dot anchors the curve. The line disappears when either endpoint leaves the viewport and stays hidden in the stacked layout.
- **Provenance:** The target names the typed source, such as Prospecteur, preserves the source identifier, and exposes available constraint and channel data without fabricating missing evidence.

## Do's and Don'ts

### Do:

- **Do** keep the idea narrative wider and visually stronger than its metadata or companion content.
- **Do** use lower-edge marks for active labels and full-height washes for linked passages.
- **Do** reveal long text, evidence, history, and collaboration context only when the user asks or the current state needs them.
- **Do** preserve real provenance labels and identifiers exactly at the data boundary.
- **Do** state zero activity and missing evidence plainly.
- **Do** render the final semantic state immediately when reduced motion is requested.

### Don't:

- **Don't** show more than one curved relationship at a time.
- **Don't** turn semantic accents into decorative chips, oversized metrics, or permanent diagram clutter.
- **Don't** fill the workspace with independent card grids or nested shadows.
- **Don't** invent contributors, questions, evidence, or activity to make an empty state look complete.
- **Don't** let secondary controls compete with the main reading flow.
