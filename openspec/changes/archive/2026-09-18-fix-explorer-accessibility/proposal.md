# Fix explorer accessibility

## Why

The idea explorer at `/workspace/ideas` fails two accessibility checks that a screen reader user meets as soon as the page opens.

The search field has no accessible name. `apps/web/app/pages/workspace/ideas/index.vue:118-122` wraps the input in a `<label class="ideas-search">` that carries no text: the label holds a decorative `<svg aria-hidden="true">`, the input itself, and a decorative filter glyph. There is no `aria-label` and no `aria-labelledby`, and a placeholder is not a name, so assistive technology announces an unnamed search box whose only cue disappears once the field holds a value. The rendered measurement recorded `ariaLabel: null`, `ariaLabelledby: null`, `labelText: ""`, with the placeholder as the only string.

The page also renders two `<main>` landmarks, one nested inside the other. `apps/web/app/layouts/workspace.vue:80` opens `<main id="main" class="workspace-main min-w-0">` and `apps/web/app/pages/workspace/ideas/index.vue:150` opens a second `<main class="ideas-results">` inside it. A document may expose one main landmark, and nesting them is invalid HTML, so landmark navigation offers two candidates for the same content. The rendered measurement recorded `mains: [{id: "main", nested: false}, {id: "", cls: "ideas-results", nested: true}]`.

Both are recorded as A11Y-1 and A11Y-2 in `.agents/skills/ux-flow-auditor/evidence/a11y-report.md`. A11Y-1 maps to WCAG 4.1.2 (Name, Role, Value, level A) and A11Y-2 to WCAG 1.3.1 (Info and Relationships, level A). This change fixes the two, and the dated audit report stays as the record of what was found.

## What Changes

- Give the search input an accessible name through a new `ideas.explorer.searchLabel` key in both catalogs, applied as `aria-label` on the input, so the name is short and the existing `ideas.explorer.search` string keeps its role as the placeholder hint.
- Turn the page's `<main class="ideas-results">` into `<div class="ideas-results">`, keeping the class and every style, so the workspace layout holds the only main landmark on the screen.
- Add a browser regression that fails when the search field has no accessible name or when `/workspace/ideas` exposes more than one main landmark, run in both locales.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workspace-idea-browsing`: add a requirement that the browsing surface exposes a single main landmark and names its search field, so the explorer can be operated with assistive technology.

## Impact

Touched files: `apps/web/app/pages/workspace/ideas/index.vue` (the search input and the results container), `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json` (one key each), and `apps/web/tests/browser/explorer.spec.ts` (one scenario).

No contract, migration, database or API change: both findings live in the rendered markup. Adds no dependency and no secret. `COVERAGE.md` and `a11y-report.md` stay pointed at the audit as the dated record of what was found.

## Out of Scope

- Fixing A11Y-3 (two navigation landmarks share one name) and A11Y-5 (the person profile has no level-1 heading), which the adversarial review records as advisory rather than conformance failures.
- Widening `scripts/check_locales.mjs` so it catches value-level keys.
- Auditing the decision-space sections or the authenticated journey, which stay outside the current evidence.
