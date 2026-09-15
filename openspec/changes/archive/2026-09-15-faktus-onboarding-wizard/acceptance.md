# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| ONB-01 wizard opens, seven questions pending when empty | `tests/browser/company-context.spec.ts` ONBOARD-01 (FR and EN) |
| ONB-02 partial answers persist across all seven | ONBOARD-02 asserts the profile PUT plus the objectives, constraints, principles and metrics POSTs and their payloads |
| ONB-03 skipped questions stay pending | ONBOARD-03 asserts the per-step `data-answered` markers and the pending count after a partial save |
| ONB-04 saving twice does not duplicate | ONBOARD-06 asserts exactly one `/objectives` POST across two saves |
| ONB-05 principles and metrics are enrichable after startup | ONBOARD-04 and ONBOARD-05 create, edit and archive a principle and a metric |
| ONB-06 outsider denied everywhere | `tests/integration/test_company_context.py` `test_non_member_is_refused_on_principles_and_metrics` asserts 404 on read, create and patch |
| Principle and metric lifecycles | `test_principle_lifecycle` and `test_metric_lifecycle` (states, `lang`, illegal transition 422, read-back) |
| ONB-07 FR and EN identical | every settings/onboarding scenario runs in both locales; `check_locales` parity |
| Schema | migration `a1f7c3d9e2b4`, `alembic check` reports no drift |

## How to run

```
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"
export DATABASE_URL="postgresql+asyncpg://memo@localhost/kollio_test_faktus"
export TEST_DATABASE_URL="$DATABASE_URL"
export REDIS_URL="redis://localhost:63799/0"
make verify
pnpm --dir apps/web exec playwright test company-context.spec.ts
```

## Gaps

- The browser checks run on **simulated API responses**: they prove the wizard
  UI, not authentication, workspace authorization or persistence. Those are the
  API integration tests above.
- Principles and metrics are **not yet consumed by the analysis engine**; this
  slice only makes them storable and editable. Feeding them into the launch
  context is analysis-side follow-up work.
- The wizard does not gate on completion: an empty or partial context never
  blocks the first analysis, matching #50 and #52.
