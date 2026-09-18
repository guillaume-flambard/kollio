# Design - fix explorer accessibility

## Context

The explorer at `/workspace/ideas` renders inside the workspace layout. Two accessibility checks fail on the rendered page, both recorded in `.agents/skills/ux-flow-auditor/evidence/a11y-report.md` and proved by the raw measurements kept in `.agents/skills/ux-flow-auditor/evidence/2026-09-18-a11y-probe.json`.

The search field has no accessible name. `apps/web/app/pages/workspace/ideas/index.vue:118-122` wraps the input in a `<label class="ideas-search">` that carries no text: it holds a decorative `<svg aria-hidden="true">`, the input, and a decorative filter glyph. The rendered measurement recorded `ariaLabel: null`, `ariaLabelledby: null` and `labelText: ""`, with the placeholder as the only string. A placeholder is not a name: once the field holds a value, the only cue is gone.

The page exposes two main landmarks, one nested in the other. `apps/web/app/layouts/workspace.vue:80` opens the layout's `<main id="main" class="workspace-main min-w-0">` and `apps/web/app/pages/workspace/ideas/index.vue:150` opens `<main class="ideas-results">` inside it. The rendered measurement recorded `{id: "main", nested: false}` and `{id: "", cls: "ideas-results", nested: true}`. The other two surfaces measured in the same pass, the person profile and the inbox shell, each expose one main landmark, so the nesting is local to this page.

## Goals / Non-Goals

**Goals:**

- The search field has a short, localized accessible name in French and English, with the placeholder kept as a hint.
- `/workspace/ideas` exposes exactly one main landmark, the one the workspace layout provides.
- A browser scenario fails if either property regresses, in both locales.

**Non-Goals:**

- Renaming the two navigation landmarks that share a name (A11Y-3) and adding a level-1 heading to the person profile (A11Y-5): the adversarial review records both as advisory rather than conformance failures.
- Changing the API, the contract, the existing catalogue keys, or the visual design.
- Widening `scripts/check_locales.mjs` to catch value-level keys.

## Decisions

### Name the field with its own key rather than reusing the placeholder

`ideas.explorer.search` already carries the sentence the field shows as a placeholder. Pointing `aria-label` at it would make assistive technology read the same long sentence twice, once as the name and once as the hint. A short key, `ideas.explorer.searchLabel`, keeps the name and the hint distinct, and it lives in both catalogues, which the parity gate checks. The alternative, adding a visually hidden `<span>` inside the existing `<label>`, was rejected as a larger markup change for the same result.

### Make the results container a div instead of giving it a role

The results column is a container, not the page's main content: the layout already owns the main landmark, and the column holds a header, the list and the pagination. Turning it into `<div class="ideas-results">` removes the duplicate landmark without adding a role. Every style rule targets `.ideas-results` and its children by class, so no rule changes. A `<section aria-label="...">` was rejected because it would add a landmark where none is needed.

### Regress on the rendered name and the landmark count

The scenario asserts the accessible name through `getByRole('searchbox', { name })` and the landmark count through `page.locator('main')`. Asserting the field's presence or its placeholder would pass against the defect, which is how it survived: the audit's first pass measured the field, and the browser suite never looked at its name.

## Migration Plan

1. Apply the two edits in `apps/web/app/pages/workspace/ideas/index.vue`.
2. Add `ideas.explorer.searchLabel` to `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json`.
3. Add the `EXPLORER-08` scenario to `apps/web/tests/browser/explorer.spec.ts`.
4. Confirm the scenario fails against the previous markup, then run the gates.

Rollback is a revert of the commit: no data, contract or runtime state is involved.
