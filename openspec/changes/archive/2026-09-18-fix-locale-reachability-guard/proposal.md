# Fix the locale guard so it fails on unreachable catalog keys

## Why

The locale guard, `scripts/check_locales.mjs`, only checks one direction. It reads the FR and EN catalogs, asserts they expose the same keys, then walks `apps/web/app` and fails when a key the code uses is absent, or when a template or concatenated key has no catalog entry starting with its static prefix. Nothing walks the other way, so a catalog key nothing reaches is invisible, and the closing line claims more than the check performs: `all 1023 catalog keys cover their usages`, while no catalog to usage check exists.

That gap is not theoretical. The i18n audit (`.agents/skills/ux-flow-auditor/evidence/i18n-report.md`, findings I18N-2 and I18N-4) names it as the root cause that let the whole legacy `ideas.role.*` family survive: those seven keys were dead, the guard said nothing, and a profile page reading a live value through the dead family printed key paths on screen.

A measurement of the tree before this change, with a throwaway script that reimplements the reachability rules (`/tmp/locale-reachability2.mjs`, 172 files scanned): 1023 catalog keys, 777 exact usages, 39 dynamic families, 61 test references, `unusedFamilies: 0`, and 41 candidate keys of which **16 are confirmed dead** once the false positives are removed. The 16 are leftovers of an earlier landing and vocabulary: `auth.pending`, `decisionSpaces.list.deadline`, `hero.action`, `hero.description`, `hero.eyebrow`, `hero.title`, `meta.description`, `meta.title`, `navigation.workspace`, and the seven `principles.*` keys. The code uses `landing.hero.*`, `landing.meta.*`, `landing.navigation.workspace`, `workspace.settings.principles.*` and `decisionSpaces.list.deadlineLine` instead.

## What Changes

- The guard reads every source under `apps/web` and `packages/ui/src`, skipping build and report directories, instead of `apps/web/app` alone, and it recognizes the `t`, `te`, `tm` and `rt` APIs, so a namespace read through `tm()` counts as reached.
- It keeps the existing checks (FR/EN parity for the web and API catalogs, and every key the code uses exists) and adds the reverse one: every web catalog key must be reachable by a literal use, by a dynamic family (a template or a concatenation), or by a test reference such as `messages.ideas.profile.ownedTitle`. An unreachable key fails the guard and is printed as `unreachable <key> (in apps/web/i18n/locales, no source reaches it)`.
- It reports both problems in one run, and its closing line states what was actually verified.
- It gains a `--self-test` flag, like `scripts/check_design_tokens.mjs`, which audits five fixtures and proves the guard still catches a missing key and a dead key while accepting a literal use, a dynamic family, a `tm()` namespace and a test reference.
- The 16 confirmed dead keys are removed from `apps/web/i18n/locales/fr.json` and `en.json`, keeping strict parity (1023 to 1007 keys on both sides).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vocabulary`: add a requirement that the two catalogs stay in step in both directions, so a key nobody reaches is a failure rather than a silent leftover.

## Impact

Touched files: `scripts/check_locales.mjs` (the guard), `apps/web/i18n/locales/fr.json`, `apps/web/i18n/locales/en.json` (the removals), and this change.

No application code, contract, migration, database or API change: the removals are keys no source reached, and the guard is a development check. Adds no dependency and no secret. `make verify` already calls the guard, so the new check runs there and in Foundations CI without further wiring.

## Out of Scope

- Fixing I18N-3 (the configured date and number formats nothing uses) and I18N-5 (the participation labels family that does not exist): separate findings with their own risk.
- Detecting dead keys inside a namespace a test reads whole, for example `messages.ideas as unknown as ...` in `initiative-type.spec.ts`: the guard treats that namespace as reached, and guessing which keys such a spec iterates at runtime is out of reach.
- Changing the key naming convention or renaming namespaces.
