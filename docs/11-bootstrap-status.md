# Kollio Phase 0 implementation status

Status as of 2026-09-15: foundations are deployed, production data is reconciled, the
self-hosted Logto OSS production flow is verified, and every Phase 0 acceptance criterion
is verified against the live deployment. The 1,536-dimension multilingual space is active
and reached through OpenRouter; browser authentication, workspace isolation, graph resume
with locale, retrieval and Langfuse ingestion were all confirmed on production. The agent
evaluation corpus remains the one item to extend as product behavior grows.

## Decisions applied

- Light theme with a blue accent; dark tokens available.
- All implementation code, identifiers, comments and docstrings in English.
- French and English UI/API messages in translation catalogs. User data and historical
  field names are preserved at the import boundary.
- Logto OSS 1.43.0 is self-hosted with a dedicated PostgreSQL database, a public OIDC
  endpoint, and an SSH-only Admin Console. The Cloud development tenant remains test-only.
- b.ai / qwen3.8-flash behind LiteLLM, as approved after the VPS audit.
- OpenAI `text-embedding-3-large`, 1536 dimensions, one shared FR/EN space,
  reached through OpenRouter so a single credential covers the provider and no
  OpenAI account is needed. It is routed through LiteLLM as `kollio-embedding`
  and has been the active production space since 2026-09-15.
- Since 2026-09-15 a second, default embedding space is self-hosted:
  `intfloat/multilingual-e5-small`, 384 dimensions, served by pinned TEI
  `cpu-1.9` on CPU and routed through LiteLLM as `kollio-embedding-local`
  with no API key. One space is active per deployment; rows carry their own
  model and dimensions and retrieval excludes other spaces. The
  1536-dimension space is active and verified; the self-hosted space is the
  opt-in alternative.
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

Final backend verification: 37 tests passed, 2 opt-in live evaluations skipped, Ruff and
strict domain Mypy passed. PostgreSQL integration tests ran against a separate test
database. The authorized b.ai live evaluation passed two cases for approximately
USD 0.000556.

- Pure workspace permission rule: the first non-member test failed with an allowing
  implementation, then passed after the minimal rule was implemented.
- Vertical `ideas` slice: Postgres adapter, read use case, Pydantic response and authenticated
  `GET /ideas/{idea_id}`. Non-members receive 404, avoiding idea enumeration.
- JWT signature, issuer, audience, expiry and subject validation; fail closed without
  identity configuration. Token validation tests cover each rejection.
- The production issuer `https://auth.example.com/oidc`, JWKS endpoint, Web
  application identifier, and API audience are recorded in `.env.example`. Callback and
  sign-out URLs cover localhost and `https://kollio.example.com`. Secrets remain in the
  macOS password manager and encrypted infrastructure configuration.
- Logto OSS 1.43.0 runs from a digest-pinned image with a dedicated PostgreSQL database.
  Its public OIDC discovery and JWKS endpoints pass over HTTPS, while the Admin Console is
  reachable only through an SSH tunnel to VPS loopback.
- The self-hosted `Kollio Web` client and `Kollio API` resource use the production callback,
  post-sign-out URL, and audience. A fresh production owner completed registration, login,
  two audience-bound token exchanges, and logout through the public domains.
- The production owner subject maps to exactly one admin membership in the imported private
  workspace. The deterministic authorization integration tests continue to cover both member
  access and non-member isolation.
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
- The final API, worker, web and LiteLLM images build successfully, including with pnpm
  12.4.1, and are published to GHCR only after the required verification job succeeds.
- Alembic reports no schema drift after applying the three generated migrations.
- [GitHub Actions run 34643244503](https://github.com/guillaume-flambard/kollio/actions/runs/34643244503)
  passed installation, lint, type checks, all 37 tests, Alembic, OpenAPI drift and builds,
  then published all four images. [Failed run 34643053400](https://github.com/guillaume-flambard/kollio/actions/runs/34643053400)
  stopped before publication, proving that a required failure cannot publish a deployable
  revision.

## Production deployment and recovery evidence

The deployment is declared in `lab-infra` and uses its existing Make, Ansible, Compose,
Traefik and autodeploy path. [Pull request 51](https://github.com/guillaume-flambard/lab-infra/pull/51)
introduced the stack and [pull request 52](https://github.com/guillaume-flambard/lab-infra/pull/52)
added the encrypted environment, deterministic WAL ownership and recovery tooling.
[Pull request 53](https://github.com/guillaume-flambard/lab-infra/pull/53) corrected defects found
by the live PITR rehearsal. All infrastructure checks passed through the supported lab
deployment path.

- Public `https://kollio.example.com/` and `/api/health` return HTTP 200. Postgres,
  Redis, LiteLLM, API and web report healthy. As verified on 2026-09-13, production still
  runs the earlier ARQ worker revision `9f13572`; the Taskiq and LangGraph workflow remains
  pending in pull request 11.
- Alembic and LiteLLM migrations complete successfully before their dependent services.
  A controlled migration command exiting 42 made Compose exit 1 while the existing API
  container identifier and image stayed unchanged and public health continued to return 200.
- The production import ran twice from snapshot
  `41d6fc40f266210ccc0c9dc4f55b6dba96783eebdb5dc3810d862791d3d67936`.
  Both runs retained exactly 446 ideas and one immutable legacy import record.
- A Logto development user signed in through the production callback. `/api/session`
  returned the mapped subject, and the authenticated BFF returned imported private idea
  `8ff5003d-ac47-5368-b722-e6d532161ebd`. Signing out cleared the session and restored the
  signed-out interface. The mapped user has one admin membership in the private import
  workspace, with zero unintended memberships. No password is retained in the repository
  or this evidence record.
- Workflow `phase-zero-resume-2f536960-2db0-4ed1-a238-53264465db63` resumed through a
  newly opened Postgres checkpointer without a second gateway call and retained locale `fr`.
- A production OpenTelemetry span for `GET /openapi.json` reached Langfuse at
  `2026-09-11T20:34:50.760Z` through the v4 observations path.
- The 2026-09-11 backup produced 18 encrypted offsite files. A fresh GitHub clone retrieved
  `kollio-postgres.dump.age`; decryption with the configured identity yielded a valid
  733,315-byte Postgres archive with 469 entries.
- That offsite archive restored into an isolated, networkless Postgres 18 container with
  446 ideas, one workspace, one legacy import, five checkpoints, no orphan owner or
  workspace references, 446 distinct source identifiers and no empty idea provenance.
- The PITR rehearsal restored to `2026-09-11 20:47:39.659431+00`. It found the controlled
  pre-target row once and the post-target row zero times, using a base backup with SHA-256
  `8ccbc89b45a0d0dddeac05bbb9c6e01e78e602b57a0188870c90f3b5ac73ae27` and 38 archived
  WAL files.

## Live verification of production integrations (2026-09-15)

These checks close the remaining Phase 0 integration criteria against the public
deployment.

- Public liveness and readiness through Traefik return HTTP 200 on
  `https://kollio.example.com/` and on `https://kollio.example.com/api/health`, with
  `{"status": "ok"}` from the API.
- Browser authentication: signing in through the hosted Logto form, reached from
  `https://kollio.example.com/sign-in`, lands on
  `https://kollio.example.com/workspace` (`Espace de travail`). The signed-in page
  renders in the account locale (French), reports 447 initiatives, and carries the
  workspace query parameter `e2dd68da-ab21-502d-b59a-d5fecca416e9` together with the
  private pilot idea `f8a15602-5da0-48c5-b89d-ce49ca6610b1`. Signing out restores the
  anonymous landing page, and revisiting a protected route redirects to the hosted
  Logto sign-in page, confirming the session is cleared.
- Workspace isolation: a token for the member subject `owxezmxney3k` receives HTTP 200
  from `/workspaces` and from the private idea, while a token for the unmapped subject
  `141u5fsh1dqf` receives an empty collection and HTTP 404 `Idée introuvable`. The
  not-found response means a private idea does not disclose its existence.
- LangGraph resume with preserved locale: thread `6b121a13-8235-46cf-96d1-90ff9110f270`
  resumes from the Postgres checkpointer with the `__start__` channel still holding
  `workflow_id`, `locale` `fr`, `title`, `pitch` and `evidence`, so the locale travels
  with the workflow across steps.
- Multilingual retrieval in the active space: the gateway `GET /v1/models` lists
  `kollio-embedding`, five texts return 1536-dimension vectors, and cosine similarity is
  0.7855 for a French and an English pair on the same subject against 0.2290 for the
  French text and an unrelated one.
- Langfuse trace ingestion: production OpenTelemetry spans arrive through the v4
  observations path, the same route recorded above.

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

1. Extend the reviewed agent evaluation corpus beyond the current competition cases as
   product behavior expands.

The 1,536-dimensional FR/EN embedding criterion was satisfied on 2026-09-15: the active
space is reached through OpenRouter, and real multilingual vectors are stored and
retrieved, with no fake vectors presented as matching proof. Independent of this, the
self-hosted 384-dimensional e5-small space remains proven by a recorded real FR-to-EN
retrieval case.

The only existing lab OpenAI credential returned `401 invalid_api_key` during the live
embedding check on 2026-09-12. Kollio's copy was immediately cleared and re-encrypted; no
invalid credential remains active in the Kollio stack.

No provider secret or migration snapshot is tracked in Git. The local snapshot and environment
files have restrictive permissions. Runtime vendor deprecation warnings remain in the test
output; they did not fail the checks.
