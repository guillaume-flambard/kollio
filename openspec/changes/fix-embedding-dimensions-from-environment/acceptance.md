# Acceptance evidence - fix-embedding-dimensions-from-environment

The active embedding space is chosen by deployment configuration. The switch to
the 1536-dimension space failed at startup because the dimension field accepted
only integers while the environment supplies text, which took the whole stack
down until the variables were removed by hand. This change makes the text form
load while keeping the accepted set unchanged.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| Deployment selects the 1536-dimension space | `test_embedding_space_can_be_configured_from_the_environment` | Passing |
| Unsupported dimension fails closed | `test_settings_reject_a_non_positive_timeout` is unrelated; membership stays enforced by the `Literal[1536, 384]` declaration, and the validator returns an unparseable value untouched so the same validation error is raised | Passing |
| Existing deployments keep the default | `test_development_runtime_allows_provider_free_deterministic_tests` asserts the local 384-dimension space stays the default | Passing |

## Measured cause

On 2026-09-15, deploying the stack with `EMBEDDING_DIMENSIONS: "1536"` stopped
`kollio-migrate` with:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
embedding_dimensions
  Input should be 1536 or 384 [type=literal_error, input_value='1536', input_type=str]
```

Because the migration container exits before the API, the worker and the web
service start, the stack did not come up. Production was restored by removing the
five embedding variables from the deployed compose, returning to the
384-dimension local space.

The failing unit test reproduced the same error with the value supplied through
the environment: `1 failed, 4 passed`.

## Verification runs (2026-09-15)

- `uv run pytest tests/unit/test_agentic_config.py tests/unit/test_embeddings.py -q`
  -> 13 passed.
- `make verify` green end to end: Ruff, the format check, the strict Mypy gate on
  the five domain packages, the API suite at 131 passed / 54 skipped /
  2 deselected, `pnpm lint`, `pnpm typecheck`, the locale guard (468 catalog keys
  cover their usages) and the design token guard.
- Full API suite against a migrated disposable Postgres -> 185 passed,
  2 deselected. A first run showed one failure in
  `tests/performance/test_agent_validation.py::test_ten_thousand_agent_results_validate_within_cpu_budget`,
  a timing test that passes alone in 0.17s; the confirming run was clean, so it
  was machine load, not this change.
- `make contract` regenerated the OpenAPI document and the TypeScript client with
  zero drift, as expected since no API surface changed.
- `make build` built the web, worker and API images.

The live half of scenario one, a deployment starting with the five variables set,
is recorded once the image carrying the coercion is published and the space is
activated.

## Known boundaries

- The live half depends on the API image being published and on the deployment
  being updated afterwards, in that order. Activating the variables before the
  image changes brings the stack down exactly as it did on 2026-09-15.
- No embedding quality claim here: this change only makes the space selectable.
  The recorded retrieval evidence for the 384-dimension space is unchanged.
