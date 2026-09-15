# Landing locale coverage

## Context

`apps/web/app/pages/index.vue` and `apps/web/app/components/kollio/LandingInitiativeFlow.vue` read
the whole public landing from a `landing.*` namespace. The namespace was never written into
`apps/web/i18n/locales/fr.json` and `en.json`, so every lookup fell back to the key itself, on the
server and in the browser. The page shipped that way because the locale guard only compared the two
catalogs to each other.

## Decisions

### Copy is authored, not invented

The landing brief in `docs/01-product-spec.md`, `docs/02-strategy-and-moat.md` and
`docs/06-design-system.md` sets the vocabulary and the tone. The copy reuses what already exists in
the catalogs rather than coining new product words: "initiative", "constraint", "realism score",
"deposit", "workspace", and `Initiative` rather than `Idea` in B2B text
(`apps/web/CONTEXT.md`).

### The guard scans usages, not only the catalogs

`scripts/check_locales.mjs` keeps the FR/EN parity assertion and adds a line-by-line scan of
`apps/web/app` for `t(…)`, `$t(…)` and `te(…)`. A static key must exist in the catalog. A template
key (`` t(`landing.method.${step}.title`) ``) or the single concatenated key
(`t('ideas.function.' + request.business_function)`) is reduced to its static prefix and must match
at least one catalog entry, which proves the family exists without enumerating runtime values.

The prefix rule is deliberately loose. Enumerating dynamic values would need the domain types the web
app does not own, and a stricter check would fail on values the API may add later.

### Section anchors are part of the copy

A navigation label that jumps to the wrong section reads as a copy bug to the visitor. The two
swapped identifiers are fixed in the same change.

## Alternatives considered

- **Fix only the failing keys, leave the guard alone.** Rejected: the guard is what let the
  regression ship, and the same class of bug would return silently.
- **Hardcode the landing text in the components.** Rejected: `docs/06-design-system.md` makes FR/EN
  keys non-negotiable for every interface string.
- **Ship the landing in one language.** Rejected: multilingual support from day one is a project
  non-negotiable.
