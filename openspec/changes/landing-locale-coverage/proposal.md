## Why

The public landing page renders raw translation keys in production (`landing.hero.eyebrow`,
`landing.preview.signal.title`) instead of copy. The page was written against a `landing.*`
namespace that was never added to the FR and EN catalogs. `make verify` stayed green anyway,
because `scripts/check_locales.mjs` only compared the FR catalog to the EN catalog: a key used in
code but absent from both was invisible to the guard.

Two section anchors were swapped as well, so the navigation entry labelled "Method" and the hero
link "See the method" both landed on the benefits section.

## What Changes

- Add the missing `landing.*` copy to `apps/web/i18n/locales/fr.json` and
  `apps/web/i18n/locales/en.json`: 65 keys on each side, covering page metadata, navigation, the
  hero, the outcome benefits, the trust line, the three method steps, the final call to action and
  the initiative preview.
- Swap the `#method` and `#teams` section identifiers in `apps/web/app/pages/index.vue` so every
  navigation entry resolves to the section it names.
- Extend `scripts/check_locales.mjs` with a usage coverage check: every static `t()`, `$t()` and
  `te()` key used in `apps/web/app` must exist in the catalogs, and a template or concatenated key
  must match at least one catalog entry.
- Document the extended guard in `docs/08-conventions-and-testing.md`.

## Capabilities

### Modified Capabilities

- `b2b-product-landing`: the landing copy exists in both catalogs, its navigation anchors resolve to
  the sections they name, and the locale guard rejects a key that is used in the web app but absent
  from the catalogs.

## Impact

- `apps/web/i18n/locales/fr.json`, `apps/web/i18n/locales/en.json`
- `apps/web/app/pages/index.vue`
- `scripts/check_locales.mjs` (runs in `make verify` and the `check_locales` CI gate)
- `docs/08-conventions-and-testing.md`
- No API, schema, or generated contract change. No new dependency.
