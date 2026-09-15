# Guard the design system against undefined tokens and literal colours (#70)

`scripts/check_design_tokens.mjs` scans `apps/web/app` (`.vue`, `.css`) and
fails on:

- a literal colour outside `packages/ui/src/tokens.css`;
- a `--kollio-*` name absent from the token file, which is the invisible
  case: the hardcoded fallback wins at runtime and review sees nothing.

`--ui-*` names come from Nuxt UI (present in the generated `ui.css`) and
are exempt; a variable declared in the same file counts as local.

Wired into `make verify` and Foundations CI next to the locale check, with
`--self-test` proving it still fails on a fixture that carries an undefined
token name and a literal colour, and passes a token-only file. Documented
in `docs/08-conventions-and-testing.md`.
