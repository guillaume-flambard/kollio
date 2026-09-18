# Tasks - add-public-release

## 1. Carry the license and the community files

- [x] 1.1 Add `LICENSE` with the Apache-2.0 text
- [x] 1.2 Add `CONTRIBUTING.md` with the local setup, the change discipline and the DCO sign-off
- [x] 1.3 Add `CODE_OF_CONDUCT.md` with the Contributor Covenant 2.1
- [x] 1.4 Add `SECURITY.md` with the private disclosure path
- [x] 1.5 Add the issue templates and the pull request template under `.github/`

## 2. Orient a newcomer

- [x] 2.1 Rewrite `README.md` with the product paragraph, the quickstart, the documentation order and the license

## 3. Use placeholder infrastructure

- [x] 3.1 Replace the hosts in `.env.example` and the development defaults in `docker-compose.yml`
- [x] 3.2 Replace the default audience in `apps/api/src/platform/config.py` and the asset URL in `apps/web/logto/sign-in-experience.css`
- [x] 3.3 Replace the hosts in `docs/11-bootstrap-status.md` and `docs/decisions/0002-branded-logto-sign-in-experience.md`
- [x] 3.4 Replace the hosts in the seven archived `acceptance.md`, the archived `proposal.md` and the journey audit

## 4. Close with evidence

- [x] 4.1 Run `pnpm lint`, `pnpm typecheck`, the locale, token and coverage guards, `pnpm build` and the browser suite
- [x] 4.2 Write `acceptance.md` with the scenario to evidence mapping
