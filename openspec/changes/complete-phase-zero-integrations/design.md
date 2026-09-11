## Context

See `proposal.md` for motivation. Local Nuxt, FastAPI, Postgres, pgvector, Redis, LangGraph,
LiteLLM, and Langfuse foundations already pass their checks. Remaining work crosses identity,
provider, GitHub, backup, and deployment boundaries. Production is managed from the separate
`lab-infra` repository, whose shared `main` checkout cannot be edited directly.

## Goals / Non-Goals

**Goals:**

- Establish end-to-end evidence for every remaining Phase 0 criterion.
- Keep credentials out of Git while making configuration reproducible.
- Make data cutover recoverable and reversible.
- Preserve one deployment path through the current lab infrastructure.

**Non-Goals:**

- Implement Phase 1 product journeys.
- Import Usine's generated-code execution or outbound messaging tools.
- Claim broad matching quality from one multilingual smoke case.
- Replace the existing infrastructure or observability services.

## Decisions

### Use Logto Cloud with a Traditional Web application and API resource

The Nuxt server owns the browser session and requests an access token for the Kollio API resource.
FastAPI validates the token independently and maps its subject to local membership. Callback and
sign-out URLs cover localhost and production. Credentials enter ignored local environment files
and encrypted `lab-infra` configuration only.

Self-hosting Logto was rejected because it adds another stateful service before identity
customization is needed and does not remove the need for end-to-end login proof.

### Keep all model traffic behind LiteLLM

The application keeps the `kollio-default` and `kollio-embedding` aliases. OpenAI supplies the
embedding model while b.ai remains the approved generation provider. LiteLLM receives explicit
qwen3.8-flash pricing before monetary budget enforcement becomes acceptance evidence.

Calling OpenAI directly was rejected because it would split provider policy, budgets, and
credentials across application adapters.

### Reject mixed vector spaces

Embedding writes occur transactionally after the complete response passes count, index, and
dimension validation. Model, dimension, language, source identifier, and provenance are persisted.
A model or dimension change creates a new compatible space and a controlled re-embedding run.

Overwriting vectors in place was rejected because it can silently invalidate similarity results.

### Make recovery a cutover gate

An encrypted backup is restored into isolated Postgres, reconciled, and exercised through
point-in-time recovery. Only passing evidence permits a fresh read-only Prospecteur snapshot to be
imported into production. The original SQLite data remains untouched during validation.

Using the original SQLite file as the only rollback was rejected because it cannot restore new
identity mappings, checkpoints, gateway state, or post-import writes.

### Integrate through an isolated lab-infra worktree and pull request

The stack, encrypted environment, probes, registry build entries, and migration command are
prepared on a dedicated worktree branch. `make check` must pass before merge. GitHub Actions
publishes immutable revisions; the existing timer performs rollout and restoration.

Direct VPS edits were rejected because they bypass the deployment lock, checks, and recovery path.

### Separate recorded and live agent evaluations

Reviewed fixed inputs and outputs run on every CI execution. Live calls are opt-in and budgeted.
Deterministic metrics enforce schema, locale, citations, and verdict contracts. Subjective quality
criteria require reviewed rubrics and calibrated examples.

Mandatory live calls on every pull request were rejected because they expose secrets to untrusted
contexts, introduce provider flakiness, and consume unrelated budget.

## Risks / Trade-offs

- [Cloud identity requires interactive verification] -> Hand off only the passkey step, then
  automate configuration and verify the resulting resources.
- [Custom qwen pricing may be absent] -> Record provider pricing and test spend accounting before
  treating USD budgets as enforced.
- [One multilingual case can hide matching weakness] -> Limit Phase 0 to compatibility and one
  reviewed ranking; expand retrieval evaluations in Phase 1.
- [A migration can outlive rollout timeouts] -> Run it as one locked pre-rollout job and retain the
  previous revision until health checks pass.
- [The VPS has no offsite destination] -> Configure encrypted offsite storage and verify restore
  before production import.
- [GitHub CLI authentication is invalid] -> Reauthenticate interactively and never embed a personal
  token in the repository.

## Migration Plan

1. Complete Logto resources and verify localhost sign-in, sign-out, API audience, and membership.
2. Add the OpenAI credential and verify stored cross-language retrieval.
3. Reauthenticate GitHub CLI, create the private repository, push the baseline, and obtain green CI.
4. Configure encrypted offsite backup, restore into isolation, and prove point-in-time recovery.
5. Prepare Kollio in an isolated `lab-infra` worktree, run `make check`, merge the infrastructure
   pull request, and observe autodeploy health.
6. Capture a fresh Prospecteur snapshot, import it idempotently, reconcile it, and map the owner.
7. Verify production auth, isolation, graph resume, retrieval, and Langfuse ingestion.

Rollback retains the previous immutable images and pre-import recovery point. Any failed migration,
health check, reconciliation, or identity verification returns traffic and data to that state while
leaving Prospecteur unchanged.
