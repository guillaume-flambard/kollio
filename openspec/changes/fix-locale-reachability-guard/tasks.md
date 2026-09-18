# Tasks - fix-locale-reachability-guard

## 1. Widen the guard

- [x] 1.1 Scan `apps/web` and `packages/ui/src`, skipping build output and reports
- [x] 1.2 Recognise `t`, `te`, `$t`, `$te`, `tm` and `rt`, and read `messages.<path>` references from the browser specs
- [x] 1.3 Fail when a catalog key is reached by nothing, and keep the existing missing-key check
- [x] 1.4 Print a final line that describes what is really verified

## 2. Remove the keys the check exposes

- [x] 2.1 Delete the sixteen dead keys from `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json`

## 3. Prove it

- [x] 3.1 Add `--self-test` with fixtures for a missing key, a dead key, a literal, a family, a `tm()` namespace and a test reference
- [x] 3.2 Prove the failure path on the tree with a probe key outside every namespace a spec reads
- [x] 3.3 Confirm the guard is green with 1007 catalog keys

## 4. Close with evidence

- [x] 4.1 Run `pnpm lint`, `pnpm typecheck`, `check_locales`, `check_design_tokens` and `check_ux_coverage`
- [x] 4.2 Run `pnpm build` and the browser suite
- [x] 4.3 Write `acceptance.md` with the scenario to evidence mapping
