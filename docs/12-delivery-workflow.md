# Delivery workflow

Every product change follows one path: need, scenarios, boundary contract, vertical
slice, tests and evaluations, CI, review and merge. Scale the work to the risk.
A copy correction does not need an architecture decision or a new test suite.

## 1. Agree on an observable result

Create or update an OpenSpec change before implementation. Record the user,
expected outcome, exclusions and acceptance scenarios. Give scenarios stable IDs
within the change. Describe successful, empty, refused and failed outcomes when
relevant. Keep BDD examples in the spec; do not duplicate them in a Gherkin suite.
For a bug, a focused regression scenario is sufficient.

The product docs define durable scope and vocabulary. OpenSpec defines the
behavior of each change. Tests provide executable evidence. When they disagree,
resolve the disagreement rather than maintaining competing definitions.

## 2. Define the boundary before splitting work

Agree on request and response fields, errors, authorization, locale and side
effects before consumers and providers diverge. For this FastAPI project, define
Pydantic schemas and route signatures first, export OpenAPI with `make contract`,
and use the generated TypeScript client. Do not hand-edit generated contracts or
create a second manually maintained OpenAPI source. Review compatibility changes
explicitly; a clean generation diff alone does not prove compatibility.

Use typed functions inside a module. Add ports only for external dependencies
such as persistence, LLM calls and agent tools. Validate structured LLM output at
its boundary and preserve idempotency for side effects.

## 3. Implement one complete behavior

A slice covers the necessary UI, HTTP, domain and persistence changes for one
observable result. Keep simple CRUD simple. Reserve tactical DDD for iterations
and matching; keep shared language and invariants explicit for every module.
Use `docs/05-data-model.md` for vocabulary, and link the exact invariant tests.

An agent handoff contains:

- The change path, scenario IDs, outcome and exclusions.
- Relevant domain terms, invariants, contracts and ADRs.
- Owned files, shared files requiring coordination, and dependencies.
- Required commands and evidence to return, including unfinished work.

Do not assign the same shared contract to concurrent agents. A slice is a unit
of delivery, not a requirement to introduce a directory for every use case.

## 4. Choose evidence by risk

| Risk | Required evidence |
| --- | --- |
| Permissions, iterations, scoring, matching, idempotency | Targeted red/green domain tests |
| Database behavior and workspace isolation | HTTP/integration tests on disposable PostgreSQL |
| User journeys | Playwright assertions on visible outcomes, including FR/EN |
| Isolated component behavior | Existing Vitest component tests where useful |
| Agent quality | Recorded evaluations and schema checks; bounded live evaluations when needed |
| Boundary changes | Contract regeneration, consumer checks, compatibility review |

Browser tests with simulated API responses prove UI behavior only. They do not
prove authentication, backend authorization, persistence or provider quality.
Record that boundary in the acceptance evidence. Never add a production auth
bypass for testing. Live provider calls remain opt-in and budgeted.

## 5. Close the change with evidence

Maintain an `acceptance.md` beside the OpenSpec change. Map each scenario to a
test or a specific manual check, with known gaps. Task checkboxes record actual
completion; a passing subset does not complete the whole change.

Before merge:

- Run `make verify` with a migrated, disposable `TEST_DATABASE_URL`.
- Regenerate changed contracts and review the diff; CI checks reproducibility.
- Run the production build and review the resulting change.
- Update acceptance evidence, specs and any affected decisions.
- Require the `verify` GitHub Actions job through repository branch rules.

`make verify` includes component and browser tests. Install Chromium once with
`pnpm --dir apps/web exec playwright install chromium` (CI adds `--with-deps`).
CI retains browser failure traces and rejects focused tests. The workflow file
cannot itself enforce branch protection; verify the repository rule separately.
Publication depends on `verify`; live evaluations are a separate opt-in job.

## Decisions and sources

Write an ADR in `docs/decisions/` only for a durable choice with meaningful
alternatives. Include status, context, decision, alternatives, consequences and
supersession links. A changed decision gets a new ADR; preserve the old rationale.

- [ADR 0001](decisions/0001-scenario-led-delivery.md)
- [Pilot acceptance evidence](../openspec/changes/archive/2026-09-15-browse-private-ideas/acceptance.md)
- [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- [Playwright practices](https://playwright.dev/docs/best-practices)
- [Playwright server lifecycle](https://playwright.dev/docs/test-webserver)
- [Playwright simulated APIs](https://playwright.dev/docs/mock)

Repository limitation checked on 2026-09-13: GitHub returned HTTP 403 for branch
protection and requested GitHub Pro or a public repository. Required merge checks
are therefore not confirmed/enforced by this change. Do not claim otherwise.
