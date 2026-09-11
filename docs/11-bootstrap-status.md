# Kollio Phase 0 implementation status

Status as of 2026-09-11: local foundations implemented; Phase 0 is not complete.

## Decisions applied

- Light theme with a blue accent; dark tokens available.
- All implementation code, identifiers, comments and docstrings in English.
- French and English UI/API messages in translation catalogs. User data and historical
  field names are preserved at the import boundary.
- Logto Cloud development tenant configured with the `Kollio Web` Traditional Web
  application and the `Kollio API` resource.
- b.ai / qwen3.8-flash behind LiteLLM, as approved after the VPS audit.
- OpenAI text-embedding-3-large, 1536 dimensions, one shared FR/EN space.
- All 446 ideas in the fresh Prospecteur snapshot imported directly into a private
  workspace. Historical verdicts and scores remain provenance, not Kollio scores.
- Deployment target is the existing Make/Ansible, Compose and Traefik infrastructure.

## Generated foundations

The root manifests, Nuxt application, Nuxt modules, Python workspace member, Alembic
configuration and Dockerfiles originated from the official CLIs. Generated Dockerfiles
were adapted into locked, multi-stage builds. Generated placeholders and per-application
Compose files were archived outside the repository before consolidation.

The npm invocation of nuxi was rejected by the workspace package-manager policy. The
canonical pnpm invocation from the project documentation was used instead:
`pnpm dlx nuxi@latest init apps/web --template minimal --packageManager pnpm --no-gitInit`.
The UI, i18n and ESLint modules were added with the official nuxi module command.

There is one root `pnpm-lock.yaml` and one root `uv.lock`. Resolved container references
are in `infra/images.lock.json`; no floating service tags are used in Compose.

Resolved tools and selected direct dependencies:

| Component | Resolved version |
| --- | --- |
| Node LTS | 24.21.0 |
| Python | 3.14.7 |
| pnpm | 12.4.1 |
| uv CLI | 0.12.7 |
| nuxi | 3.37.0 |
| Nuxt | 4.5.2 |
| Nuxt UI | 4.11.1 |
| Nuxt i18n | 10.6.0 |
| Motion for Vue | 2.4.2 |
| Logto Nuxt SDK | 1.2.11 |
| FastAPI | 0.141.1 |
| LangGraph | 1.2.11 |
| Postgres checkpointer | 3.1.2 |
| LiteLLM Python dependency | 1.100.1 |
| DeepEval | 4.2.2 |
| Hey API generator | 0.99.0 |

TypeScript 7.0.2 is installed under the official native compiler alias. Hey API still
requires the TypeScript compiler API, absent from the native package, so the official
`@typescript/typescript6` compatibility package, resolved at 6.0.2, supplies that API.
This is a verified compatibility boundary, not an arbitrary historical version pin.
See [Microsoft's TypeScript 7 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)
and [the upstream Hey API issue](https://github.com/hey-api/hey-api/issues/4235).

## Implemented behavior and evidence

Final backend verification: 24 tests passed, 2 opt-in live evaluations skipped, Ruff and
strict domain Mypy passed. PostgreSQL integration tests were enabled against a separate
test database. Both live provider calls had already been verified and recorded separately.

- Pure workspace permission rule: the first non-member test failed with an allowing
  implementation, then passed after the minimal rule was implemented.
- Vertical `ideas` slice: Postgres adapter, read use case, Pydantic response and authenticated
  `GET /ideas/{idea_id}`. Non-members receive 404, avoiding idea enumeration.
- JWT signature, issuer, audience, expiry and subject validation; fail closed without
  identity configuration. Token validation tests cover each rejection.
- Logto development issuer `https://fbed5e.logto.app/oidc`, JWKS endpoint, Web application
  identifier and API audience are recorded in `.env.example`. Callback and sign-out URLs
  are registered for localhost and `https://kollio.memolabs.dev`. Secrets remain only in
  the ignored mode-0600 `.env` file.
- Localized API errors, FR/EN routes, catalog key parity and locale propagation.
- LangGraph state includes locale; Postgres checkpoint survives interruption and resume.
- Agent side effects use a database primary key on workflow and step. Replays reuse the
  result; a conflicting input is rejected.
- Live qwen calls returned valid structured findings in FR and EN after an explicit JSON
  schema was added to the English prompt. The first provider response ignored
  `response_format` and was rejected by Pydantic, as required.
- DeepEval records the two evidence-free abstention cases. The strict threshold checks a
  mandatory contract: no evidence means unknown, no citations and the requested locale.
  These cases do not establish overall competition-analysis quality.
- OTel ingestion into the existing Langfuse instance verified through the observations v2
  API. The deployment runs v4 events-only mode; the deprecated traces API returns 404.
  The OTLP header `x-langfuse-ingestion-version=4` enables current ingestion semantics.
  See [Langfuse observations documentation](https://langfuse.com/docs/api-and-data-platform/features/observations-api).
- Nuxt type checking, ESLint and production build passed. Browser checks passed for FR/EN
  navigation, mobile overflow, page errors and the generated API client health request.
- The final API, worker and web images build successfully, including with pnpm 12.4.1.
- Alembic reports no schema drift after applying the two generated migrations.
- GitHub Actions configuration exists; it has not run on GitHub yet. It currently verifies
  lint/types, tests, generated contract drift and builds. Deployment is not wired yet.

## Legacy migration reconciliation

Source: running `prospecteur` container, SQLite file `/data/prospecteur.db`, mounted from
`/opt/prospecteur/data`. A read-only transaction captured all selected tables coherently.
SQLite is confined to this export boundary, never the application runtime or test backend.

Snapshot SHA-256: `41d6fc40f266210ccc0c9dc4f55b6dba96783eebdb5dc3810d862791d3d67936`.
The source SQLite checksum was
`e31becd5fbde603c4e42139833a24076407d25c3941abbb2dc8efd3f730bb862` before and after
the 2026-09-11 extraction.

| Source table | Preserved rows |
| --- | ---: |
| idee | 446 |
| occupant | 206 |
| fusion | 47 |
| correction | 1 |
| envoi | 51 |
| graine | 0 |
| battement | 1 |

Private workspace: `e2dd68da-ab21-502d-b59a-d5fecca416e9`.
All idea source keys become stable UUIDs while original keys remain stored. Each raw
idea row is retained in JSONB provenance. The complete snapshot, including relationships
and history tables, is preserved in `legacy_imports`. Naive timestamps use the audited
Europe/Paris source timezone; explicit offsets remain intact.

A second import of the same snapshot succeeded with the same 446 ideas. Conflicting
existing provenance fails rather than overwriting it. The synthetic importer has no
Logto subject, so no public or accidental membership grants exist.

Legacy code classification:

- Reuse: source facts, historical payloads, citations, existing Langfuse and provider.
- Adapt: competition prompts, evidence handling and fixed evaluation cases. Prospecteur's
  historical kill-on-empty-search rule is not silently turned into a Kollio conclusion.
- Replace: SQLite runtime, monolithic orchestration and shape-only agent testing.
- Exclude: Usine's arbitrary generated-code execution and outbound sending tools.

## Remaining acceptance criteria

1. Verify a real browser login/logout against the configured Logto development tenant,
   map the resulting subject to the imported workspace, and provision a separate
   production tenant before public rollout. Auth module enablement is a build-time switch
   and requires rebuilding the web image.
2. Configure the approved OpenAI key, then verify actual 1536-dimensional FR/EN embeddings,
   storage and retrieval. No fake vectors are presented as multilingual matching proof.
3. Verify b.ai-specific pricing for gateway monetary accounting. The scoped key has a
   configured USD 1 daily ceiling and rate/token limits; exact cost enforcement for this
   custom provider must not be claimed until the price mapping is validated.
4. Extend the agent evaluation corpus beyond abstention, with explicit reviewed criteria.
5. Rehearse backup restoration and PITR before any real-data cutover. The audited VPS
   backup configuration has no offsite destination. The original Prospecteur service and
   data remain intact.
6. Add the stack through an isolated lab-infra worktree and PR, respecting that repository's
   shared-main rule. Wire migration execution before rollout, health checks and CI deployment.
   No VPS deployment, production cutover or GitHub CI success is claimed.
7. Map the real Logto identity to the private imported workspace after identity setup.

No provider secret or migration snapshot is tracked in Git. The local snapshot and environment
files have restrictive permissions. Runtime vendor deprecation warnings remain in the test
output; they did not fail the checks.
