# ADR 0001: Deliver behavior through scenarios and vertical slices

Status: accepted
Date: 2026-09-13

## Context

Kollio already uses OpenSpec, a modular monolith, generated API clients and targeted
domain tests. Component tests were available but not invoked by CI. Browser
acceptance and a shared scenario-to-evidence convention were missing. Agents need
small assignments with a verifiable result and explicit business constraints.

## Decision

Use the workflow in `docs/12-delivery-workflow.md`. Keep behavioral scenarios in
OpenSpec, map them to tests in each change's acceptance document, and deliver one
complete behavior per slice. Define boundary schemas before consumers depend on
them. Preserve FastAPI as the OpenAPI generation source. Use DDD and TDD on the
critical domain, with recorded evaluations for agents.

Add browser acceptance and component tests to the existing CI verification job.
The initial browser suite extends the real Nuxt app in an isolated client-rendered
test fixture and simulates HTTP responses. Backend integration tests remain the
proof of access control. Production authentication and SSR configuration do not
change. Require a real authenticated deployment smoke check for changes to those
boundaries; the browser fixture cannot validate them.

## Alternatives

A separate Cucumber suite would duplicate scenario text and add glue code.
Handwritten OpenAPI alongside generated OpenAPI would introduce two sources.
Full DDD layers in CRUD modules would enlarge the context without protecting a
new invariant. Real provider calls on every PR would add cost and variability.
These alternatives are not adopted.

## Consequences

Every nontrivial change must link its expected behavior to evidence. Browser
failures now block the verification job and retain debugging artifacts. The
initial browser suite can miss SSR or authentication integration failures; the
acceptance document must keep that limitation visible. Branch protection must
require the verification job to prevent merging a failing PR.
