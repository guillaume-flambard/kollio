# Verification evidence

Verified locally on 2026-09-13.

| Requirement | Evidence and result |
| --- | --- |
| Changes connect outcomes to evidence | AGENTS.md links the workflow; private browsing has a scenario-to-test table; ADR 0001 records the decision |
| Component verification | `pnpm test:ui`: 8 passed |
| Browser verification | `pnpm test:browser`: 8 passed, Chromium, FR/EN |
| Back navigation | BROWSE-02 failed in both locales before the pagination fix and passed afterward |
| Anonymous workspace refusal | Extended parametrized HTTP test passes for idea, workspace list and workspace ideas |
| Backend integrity | `pytest -m 'not live'`: 54 passed, including 9 PostgreSQL integration tests; 2 live tests deselected |
| Static checks | Ruff, Ruff formatting, strict domain Mypy, ESLint, Nuxt typecheck and locale parity all passed |
| Production build | `pnpm build`: passed |
| Spec validity | OpenSpec strict validation passed for this change and `browse-private-ideas` |
| CI wiring | Component/browser steps belong to `verify`; existing `publish` depends on `verify`; failure artifacts retained; `forbidOnly` enabled in CI |
| Merge enforcement | GitHub branch-protection read returned HTTP 403 requesting GitHub Pro or public visibility; enforcement not activated |

PostgreSQL used a dedicated disposable `kollio_test_delivery` database, migrated
through all five revisions. The container was stopped and removed after tests.
The first `make verify` passed backend checks then found generated browser reports
in the lint input. ESLint now ignores those generated directories; all remaining
verification commands were rerun successfully. No live provider calls were made.

The browser suite simulates API responses in a client-rendered fixture. Real Logto,
SSR and deployment smoke checks were not run. CI was edited and inspected locally;
a hosted CI run, merge, publication and deployment are not claimed. Docker images
were not rebuilt for this test/docs change.
