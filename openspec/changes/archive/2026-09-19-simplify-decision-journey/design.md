# Design - simplify the decision journey

## Context

A decision space page (`apps/web/app/pages/workspace/decision-spaces/[spaceId].vue`) renders a header (question, status, owner, deadline, participants), a status transition form, then a `nav.space-sections` holding one link per section. That list comes from `sections = ['explore', 'converge', 'options', 'decision', 'experiment', 'learning']`, each label from `decisionSpaces.section.<section>.label`, and the active section is marked by comparing the current path with the localized section path. The six routes live under `decision-spaces/[spaceId]/` and each renders `SpaceSection`, which today only prints a pending line while its payload loads.

`apps/web/CONTEXT.md` fixes the vocabulary: SpaceShell is the shell of a decision space with its question, its facts, its status, the six section routes and the permitted transitions; Explore is independent exploration and proposing a Contribution; Converge is reading and correcting the confirmed map, with nothing inferred; Options are viable paths that are never scored or ranked; the Decision section challenges an option and records the decision; the Experiment section edits scenario ranges and compares the expected with the observed; the Learning section waits for a person to confirm a lesson.

The issue behind this change asks for three visible moments and for no new mechanics: the six routes stay addressable, and the navigation groups them.

## Goals / Non-Goals

**Goals:**
- A newcomer reads the space navigation as three plain-language moments and knows where to start.
- Each moment states what it holds when it is empty, and what to do next.
- Deep links, the active state, keyboard use, the mobile layout and both locales behave exactly as they do today.
- No section loses content, and no write is invented, defaulted or auto-confirmed.

**Non-Goals:**
- New domain behaviour, new API fields or automatic convergence.
- Renaming routes or moving content between sections.
- An onboarding tour or a terminology lesson.

## Decisions

### Group the existing routes instead of adding new ones

The three moments are a reading of the six routes, not a new layer: the first moment (the decision to frame) contains Explore and Converge, the second (the choice and its reasons) contains Options and Decision, and the third (what happened) contains Experiment and Learning. Adding three more routes would have meant three empty pages, three redirects and a second navigation to keep in sync. The alternative, replacing the six routes with three, was rejected because every deep link in the product, in the docs and in the acceptance records points at a section.

### Label the moments in the catalogs, from the current route

Each moment carries a label and a one-line description in French and English, and a moment is active when the current route belongs to its sections. That keeps one source of truth for the active state, and it keeps the translations out of the component, which is what the locale guard requires.

### An empty moment says what it holds

A space with nothing in it should still read as a path. Each moment therefore states, when none of its sections has content, what it will hold and which action comes next. The content check reads what the space already returns (the counts the sections already use), so nothing is invented and no new request is added; when the data needed for a statement is not available, the moment says what it holds and stops there rather than guessing.

### Keep the detailed controls where they are

The sections stay as they are, with their own controls, provenance and confirmation. The change is the navigation above them and the orientation of the space page; nothing inside a section moves.

## Migration Plan

1. Add the three moments, their labels and their descriptions to the French and English catalogs.
2. Group the section links in the space navigation under those moments, keeping every route, every localized path and the active state.
3. Give each moment an empty state on the space index, with the next action when one is known.
4. Add the browser regression, run the gates, and check the space page in both locales at desktop and phone width.

Rollback is a revert of the commit: no data, contract or runtime state is involved.
