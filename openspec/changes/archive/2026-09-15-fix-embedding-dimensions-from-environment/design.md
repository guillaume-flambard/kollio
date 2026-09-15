## Context

`apps/api/src/platform/config.py` declares the active embedding space with three
fields, including `embedding_dimensions: Literal[1536, 384] = 384`. The two
allowed values are the two spaces the system supports, and the type is what keeps
a typo from selecting a third.

Pydantic settings read the process environment, where every value is text. A
Literal of integers matches types exactly, so the text form `"1536"` is not a
member and validation fails. The failure happens while the settings object is
built, which is at import time for anything that reads configuration, including
`alembic/env.py`. The migration container therefore exits before the API, the
worker and the web service start, and the stack stays down.

That is what happened on 2026-09-15 during the switch to the 1536-dimension
space. Nothing had ever set the variable, so the field had always been satisfied
by its default and the trap had never been exercised.

## Goals / Non-Goals

**Goals:**

- A deployment can select either supported space through environment variables.
- The accepted set of dimensions stays exactly `1536` and `384`.
- An unsupported value still fails closed, with the field named in the error.

**Non-Goals:**

- Changing which spaces are supported.
- Deciding which space this deployment should run.
- Making other fields lenient: only `embedding_dimensions` has the problem.

## Decisions

### Coerce the text form before the membership rule runs

A `@field_validator("embedding_dimensions", mode="before")` converts a `str` with
`int()`, returns the value untouched when it is not a `str`, and returns it
untouched when `int()` fails. The Literal rule then runs on whatever comes out.

Alternatives considered and rejected:

- Declaring the field `int` and validating membership by hand. That duplicates
  what the Literal already expresses and loses the declaration-level guarantee.
- Declaring it `str` and converting at each use site. The value is used as a
  number in several places, and every new use site would have to remember.
- Parsing JSON in the environment. That would make `EMBEDDING_DIMENSIONS` accept
  a quoted string, which is a worse contract to explain than accepting the plain
  number a compose file already writes.

A value `int()` cannot parse travels unchanged to the Literal, which rejects it,
so the failure mode stays the same validation error as before.

### Keep the regression in the settings unit test

The existing settings test file already covers the two spaces from explicit
arguments, which is precisely why it never caught this: passing `1536` as an
argument is an integer, so it exercises a path the environment never takes. The
new test sets the environment and builds the settings with no argument, which is
how a deployment supplies it.

## Migration Plan

1. Add the validator with its regression test; run the suite.
2. Ship the API image through the normal path.
3. Only then activate the 1536-dimension space in the deployment that needs it.

Rollback is removing the validator and unsetting `EMBEDDING_DIMENSIONS`, which
restores the previous space and the previous startup behaviour. No data
migration: stored vectors carry their own model and dimensions, and retrieval
excludes rows from a space that is not active.
