## Why

Activating the 1536-dimension embedding space for a deployment means setting five
environment variables. The first attempt to start the stack with them failed:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
embedding_dimensions
  Input should be 1536 or 384 [type=literal_error, input_value='1536', input_type=str]
```

`Settings.embedding_dimensions` is declared `Literal[1536, 384]`. Environment
variables always arrive as text, and a Literal of integers matches types exactly,
so the field rejected every value an operator could set. No deployment had ever
set it before, which is why the trap stayed hidden until this switch.

The failure was not graceful: the container that runs migrations exits before the
API, the worker and the web service start, so the whole stack stayed down until
the five variables were removed from the deployed compose by hand. Production is
back on the previous 384-dimension space.

## What Changes

Coerce the text form of `embedding_dimensions` before the Literal rule runs, so
`EMBEDDING_DIMENSIONS=1536` loads as the integer `1536`. The accepted set stays
exactly `1536` and `384`; any other value still fails closed with the same
validation error.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `matching/multilingual-embeddings`: the active space was already described as
  fixed per deployment by configuration, but that configuration path accepted
  only integers, never the text an environment supplies. The requirement now
  states that the deployment can actually select the space this way.

## Impact

- `apps/api/src/platform/config.py`: one field validator, running before
  validation.
- `apps/api/tests/unit/test_agentic_config.py`: one regression test that reads
  the values from the environment rather than passing them as arguments.
- No contract, migration, database or frontend change.
- Rollback: remove the validator and stop setting `EMBEDDING_DIMENSIONS`.

## Out of Scope

- Changing the accepted dimension set.
- Deciding which space a given deployment should run.
- Other fields: `llm_request_timeout_seconds` is a float and already coerces
  from text, and `environment` is a Literal of strings.
