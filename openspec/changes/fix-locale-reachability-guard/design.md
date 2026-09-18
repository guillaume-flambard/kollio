# Design - fix the locale guard

## Context

`scripts/check_locales.mjs` guards the two web catalogs. It flattens `fr.json` and `en.json` into dotted paths, asserts both key sets match for `apps/web/i18n/locales` and `apps/api/src/locales`, then walks `apps/web/app` and reads every `t(...)` call: a literal must exist in the catalog, and a template or a concatenation only needs one catalog entry starting with its static prefix. Nothing reads the catalogs in the other direction.

The audit recorded two consequences. The final line claimed that all catalog keys cover their usages, which was never checked. And a template such as `t(\`ideas.detail.roles.${role}\`)` passed as long as one key started with `ideas.detail.roles.`, which is how seven dead `ideas.role.*` keys survived and reached the profile screen as raw key paths.

A throwaway reachability probe over 172 files measured `1023` catalog keys, `777` literal usages, `39` dynamic families, `61` test references, no family matching nothing, and `41` candidates of which `16` are truly dead: `auth.pending`, `decisionSpaces.list.deadline`, `hero.action`, `hero.description`, `hero.eyebrow`, `hero.title`, `meta.description`, `meta.title`, `navigation.workspace`, `principles.challenge.description`, `principles.challenge.title`, `principles.idea.description`, `principles.idea.title`, `principles.label`, `principles.team.description`, `principles.team.title`. Each has a living counterpart the code actually uses: `landing.hero.*`, `landing.meta.*`, `landing.navigation.workspace`, `workspace.settings.principles.*`, `decisionSpaces.list.deadlineLine`.

## Goals / Non-Goals

**Goals:**

- Fail the guard when a catalog key is reached by nothing in the web app or the UI package.
- Widen the scan to `apps/web` and `packages/ui/src`, and recognise `t`, `te`, `$t`, `$te`, `tm` and `rt`.
- Keep the checks that already exist: FR/EN parity in both catalogs, and every used key exists.
- Make the final line describe what is really verified.
- Prove the new behaviour with the guard's own `--self-test`.
- Remove the keys the new check exposes from both catalogs.

**Non-Goals:**

- Detecting dead keys inside a namespace a browser spec reads wholesale.
- Changing the naming conventions, the catalog shape or the API catalogs.
- Closing the other i18n findings of the audit.

## Decisions

### Read reachability from the same evidence the guard already trusts

The guard already parses every `t(...)` call. The reverse check reuses that reading: a catalog key is reachable when a literal uses it, when a dynamic family covers it, or when a browser spec reaches for it through `messages.<path>`. No second source of truth is introduced, and a reviewer can trace any verdict back to a file.

### Count a whole-namespace read as covering its subtree

`apps/web/tests/browser/initiative-type.spec.ts:52` casts `messages.ideas` to a record, and `apps/web/app/composables/useInitiativeTypeOptions.ts:4` walks a whole subtree with `tm('ideas.initiativeType')`. Both read keys the guard cannot enumerate, so both cover their subtree. The trade is honest and bounded: a dead key outside such a namespace fails the guard, a dead key inside one does not, and the acceptance evidence states that limit instead of hiding it.

### Keep one script with a `--self-test` flag

`scripts/check_design_tokens.mjs` already proves itself on fixtures through `--self-test`, so the locale guard follows the same shape and a reviewer can watch it fail without touching the catalogs. A browser test would move a Node script check into the web suite, where it does not belong.

### Report both directions in one run

Missing and unreachable keys print together with a single count and the doc reference, so one run tells the whole story instead of the reader having to fix one direction to see the other.

## Migration Plan

1. Rewrite the guard, keeping the imported helpers and the parity assertion, and run `node scripts/check_locales.mjs --self-test`.
2. Delete the 16 dead keys from both catalogs and run the guard until it is green.
3. Prove the failure path with a probe key outside every namespace a spec reads, then remove the probe.
4. Run lint, types, the guards, the build and the browser suite.

Rollback: revert the commit. It restores the previous guard and the 16 keys, and no runtime behaviour depends on either.
