## 1. Identity Configuration and Mapping

- [x] 1.1 Record the Logto issuer, JWKS URL, Web application identifier, and API audience in safe configuration examples and bootstrap documentation, and verify no secret value is tracked by Git.
- [x] 1.2 Configure the Nuxt Logto module for the registered localhost and production callbacks, API resource, SSR session, and sign-out redirects, and verify the Nuxt type check passes.
- [x] 1.3 Add persistent Logto subject-to-user and workspace membership mapping for the imported private workspace, and verify integration tests cover owner and non-member identities.
- [x] 1.4 Complete a real localhost browser sign-in and sign-out, then verify an authenticated owner can read an imported idea while an unmapped identity receives the private not-found response.
- [ ] 1.5 Provision the production Logto tenant and production credentials through the approved credential store, and verify its issuer, callbacks, audience, and JWKS independently of the development tenant.

## 2. Multilingual Embeddings

- [ ] 2.1 Provision the OpenAI embedding credential through LiteLLM configuration without committing it, and verify the gateway can resolve the `kollio-embedding` alias.
- [x] 2.2 Persist model, 1,536-dimension space, source language, source identifier, and provenance metadata with each embedding, and verify migration and repository integration tests pass on Postgres with pgvector.
- [x] 2.3 Validate provider response count, index, and vector dimensions before transactional storage, and verify malformed responses leave no partial vectors.
- [x] 2.4 Exclude incompatible model or dimension spaces during retrieval, and verify an integration test cannot match across incompatible spaces.
- [ ] 2.5 Run the reviewed real FR-to-EN retrieval case through LiteLLM, and verify the expected semantic counterpart ranks ahead of unrelated candidates.

## 3. Agent and Gateway Evidence

- [x] 3.1 Add explicit b.ai `qwen3.8-flash` pricing metadata and the approved generation budget to LiteLLM, and verify a recorded request produces non-empty cost accounting.
- [x] 3.2 Add immutable reviewed Prospecteur competition fixtures for named competitors, empty observed landscapes, competitor-authored content, and failed research, and verify every fixture records provenance and expected semantics.
- [x] 3.3 Enforce structured competition outputs, requested locale, and evidence identifier validation before side effects, and verify invalid schema and unknown-citation tests pass.
- [x] 3.4 Run recorded DeepEval cases without provider credentials in CI, and verify the suite makes no network call and fails a known regression fixture.
- [x] 3.5 Add the opt-in live evaluation job with provider, rate, and budget gates, and verify budget exhaustion reports incomplete cases and fails the authorized run.

## 4. Repository and Locked CI

- [x] 4.1 Reauthenticate GitHub CLI interactively, create or connect the private Kollio repository, and verify the local remote targets the intended private repository.
- [x] 4.2 Push the baseline with `pnpm-lock.yaml` and `uv.lock`, and verify a clean checkout installs with `pnpm install --frozen-lockfile` and `uv sync --locked --all-packages`.
- [x] 4.3 Enforce lint, type, unit, integration, OpenAPI drift, secret scanning, and image build checks in GitHub Actions, and verify the full pull request workflow is green without provider secrets.
- [x] 4.4 Publish immutable API, worker, web, and LiteLLM image revisions only after required checks pass, and verify a deliberately failing required check publishes no deployable revision.

## 5. Recovery and Production Import

- [x] 5.1 Configure encrypted offsite Postgres backup storage through the existing lab infrastructure, and verify a backup object is readable from outside the VPS without exposing credentials.
- [x] 5.2 Restore the encrypted backup into an isolated Postgres instance and reconcile schema, row counts, relationships, checkpoints, and provenance, and verify the rehearsal report has no unexplained difference.
- [x] 5.3 Demonstrate point-in-time recovery to a recorded timestamp after a controlled write, and verify the recovered database includes the pre-point record and excludes the post-point record.
- [x] 5.4 Capture a fresh consistent read-only Prospecteur snapshot and checksum, and verify the source SQLite file remains byte-for-byte unchanged after extraction.
- [x] 5.5 Import all approved ideas idempotently into the production private workspace with stable identifiers and provenance, and verify a second run changes neither counts nor records.
- [x] 5.6 Map the approved Logto owner identity to the imported workspace, and verify no public or unintended membership exists.

## 6. Existing Infrastructure Deployment

- [x] 6.1 Create an isolated `lab-infra` worktree branch and add the Kollio Compose stack, encrypted environment references, Traefik routes, health probes, registry images, migration job, and autodeploy metadata with no Coolify reference.
- [x] 6.2 Run `make check` in the isolated worktree and verify every Ansible, Compose, secret-reference, and infrastructure check passes before opening the pull request.
- [x] 6.3 Review and merge the `lab-infra` pull request, then verify GitHub Actions publishes immutable images and the existing autodeploy timer rolls out Kollio without a manual VPS edit.
- [x] 6.4 Verify the schema migration runs once before application startup and that a simulated migration failure leaves the previous healthy revision serving traffic.
- [ ] 6.5 Verify production live and ready probes through Traefik, browser authentication and workspace isolation, LangGraph resume with preserved locale, multilingual retrieval, and Langfuse trace ingestion.
- [x] 6.6 Record resolved runtimes, package versions, image digests, backup evidence, import reconciliation, and deployment evidence in the Phase 0 status document, and verify every acceptance criterion links to reproducible evidence.
