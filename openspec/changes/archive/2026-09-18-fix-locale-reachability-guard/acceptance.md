# Acceptance evidence - fix-locale-reachability-guard

`scripts/check_locales.mjs` compared the two catalogs and checked that every key the web app uses exists, then claimed that all catalog keys covered their usages without ever reading the catalogs the other way. The audit recorded the gap as I18N-2 and I18N-4: a template such as `t(`ideas.detail.roles.${role}`)` only needed one catalog key starting with `ideas.detail.roles.`, so the seven dead `ideas.role.*` keys survived and printed as raw key paths on the person profile. This change makes the guard fail on unreachable catalog keys, adds a `--self-test`, tells the truth in its final line, and removes the sixteen dead keys the new check exposes.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A used key is absent from the catalogs | `node scripts/check_locales.mjs --self-test` covers a fixture calling `t('ideas.absent')` among five cases: `Locale guard self-test passed.` only holds when that key is reported and the other four are accepted | Passing |
| A catalog key is reached by nothing | Probe on the real tree: adding `orphanProbe.dead` to both catalogs made the guard print `unreachable orphanProbe.dead (in apps/web/i18n/locales, no source reaches it)` and exit 1; removing it returned the tree to 1007 keys with exit 0 | Passing |
| A dynamic family stays accepted | `--self-test` accepts a catalog key under a template family (`t(`ideas.detail.roles.${role}`)`), a namespace read by `tm('ideas.initiativeType')`, and a key taken from a spec reference (`messages.ideas.profile.ownedTitle`) | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- Not applicable. The guard runs in `make verify` and in Foundations CI and never ships with the app, and every key this change removes was unused, so no served string changes. Nothing was observed on kollio.example.com for that reason, not because the check was skipped.

Local, before deploy:

- `node scripts/check_locales.mjs --self-test`: `Locale guard self-test passed.` (exit 0).
- `node scripts/check_locales.mjs`: `FR/EN catalogs match (1007 web keys): every key the code uses exists, and every catalog key is reachable from apps/web or packages/ui/src.` (exit 0).
- Reachability measured before the change by a throwaway probe: 172 files scanned, 1023 catalog keys, 777 literal usages, 39 dynamic families, 61 test references, no family matching nothing, 41 candidates of which 16 dead.
- The sixteen dead keys were removed from `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json` (30 changed lines in each), taking both catalogs from 1023 to 1007 keys with parity intact.
- `pnpm --dir apps/web exec playwright test`: the full suite reported `317 passed, 3 failed` in 29.9m on a loaded machine, against `330 passed (14.3m)` for the suite before this change. The three failures (`TEAM-01` and `TEAM-07` in `fr`, `EXPERIMENT-16` in `en`) were 15-second render timeouts, and re-running the two files alone returned `48 passed (1.5m)`.

## Known boundaries

- A browser spec that reads a whole namespace (`messages.ideas as unknown as ...` in `apps/web/tests/browser/initiative-type.spec.ts:52`) and a `tm()` read of a namespace cover every key under it, so dead keys inside such a namespace are not detected. The check errs toward missing a dead key, never toward reporting a live one.
- The guard reads `apps/web` and `packages/ui/src`. A key used only by the API catalogs or by a script outside those roots would look unreachable.
- Dead keys are removed from the catalogs, not from git history: the sixteen lines are recoverable from the parent commit.
- The three full-run failures recorded above are load flakes, not behaviour: the same scenarios pass in the other locale in that very run, the isolated re-run is green, and none of the sixteen removed keys belongs to the team panel or the experiment section. They are kept in the record rather than explained away.
