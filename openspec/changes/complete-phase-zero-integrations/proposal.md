## Why

Kollio's local foundation is working, but Phase 0 cannot be accepted until identity,
multilingual embeddings, production data recovery, and the existing Netcup deployment path
are proven end to end. Completing these integrations now keeps Phase 1 from building on
unverified security, data, and operational assumptions.

## What Changes

- Run Logto OSS on the lab and configure its Traditional Web application and API resource,
  then verify SSR sign-in, callback, sign-out, JWT validation, and private workspace access.
- Provision OpenAI embeddings through LiteLLM and prove that French and English inputs share
  one 1,536-dimensional `text-embedding-3-large` vector space.
- Rehearse backup, restore, and point-in-time recovery before importing the approved
  Prospecteur snapshot into the production private workspace.
- Publish the private Kollio repository, run the locked GitHub Actions pipeline, and deploy
  through the existing Make/Ansible, Compose, Traefik, and autodeploy system.
- Configure explicit b.ai pricing metadata and enforce the existing LiteLLM key budget.
- Extend recorded agent evaluations with reviewed competition cases from Prospecteur.

## Capabilities

### New Capabilities

- `identity/private-workspace-auth`: Logto-backed browser sessions and API authorization for
  access to private workspace ideas.
- `matching/multilingual-embeddings`: Compatible FR/EN embeddings with model, dimension,
  language, and provenance controls.
- `operations/production-foundations`: Recoverable Postgres data, locked CI, and deployment
  through the existing lab infrastructure.
- `agents/evidence-evaluation`: Recorded, structured evaluation cases that detect competition
  judgment regressions without changing inputs over time.

### Modified Capabilities

None. This repository has no existing OpenSpec capability specifications.

## Impact

The change affects the Nuxt Logto runtime configuration, FastAPI identity mapping, LiteLLM
model metadata, pgvector persistence and tests, GitHub Actions, migration tooling, and the
separate `lab-infra` repository. It creates self-hosted Logto and external GitHub resources, uses the
existing Langfuse service, and imports the already approved 446-idea snapshot only after a
successful recovery rehearsal.
