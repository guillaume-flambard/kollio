## 1. Landing copy

- [x] 1.1 Write the French copy for the `landing.*` namespace in `apps/web/i18n/locales/fr.json`: metadata, navigation, hero, outcome benefits, trust line, method steps, final call to action and the initiative preview.
- [x] 1.2 Write the matching English copy in `apps/web/i18n/locales/en.json`, in sentence case with imperative actions and typographic apostrophes.
- [x] 1.3 Swap the `#method` and `#teams` section identifiers in `apps/web/app/pages/index.vue` so each navigation entry resolves to the section it names.

## 2. Locale guard

- [x] 2.1 Extend `scripts/check_locales.mjs` to scan `apps/web/app` for `t()`, `$t()` and `te()` usages and fail when a static key is absent from the catalogs.
- [x] 2.2 Require a template or concatenated key to match at least one catalog prefix, so dynamic families are covered without enumerating runtime values.
- [x] 2.3 Prove the guard fails on a key removed from both catalogs and passes once it is restored.
- [x] 2.4 Document the extended guard in `docs/08-conventions-and-testing.md`.

## 3. Verification

- [x] 3.1 Run `make verify` and the API test suite.
- [x] 3.2 Build the web app for production.
- [x] 3.3 Confirm the served landing renders copy instead of keys, in French and English.
