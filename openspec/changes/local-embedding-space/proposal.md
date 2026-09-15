## Why

Phase 0 criteria 2.1 and 2.5 are blocked: the only lab OpenAI credential returns
`401 invalid_api_key`, and the spec forbids substituting fake vectors. There is
no valid key and none is expected. Without an embedding space, multilingual
matching stays unverified and Phase 1 builds on an unproven retrieval claim.

A self-hosted multilingual embedding model removes the credential dependency
entirely: no key, no per-token billing, ~200MB RAM on CPU. The persistence
layer already isolates vector spaces by model and dimensions, so a second space
coexists with the OpenAI rows without corrupting them.

## What Changes

- Serve `intfloat/multilingual-e5-small` (118M parameters, 384 dimensions,
  shared FR/EN space) from a pinned Text Embeddings Inference container on the
  existing Compose network, routed through LiteLLM under a new
  `kollio-embedding-local` alias with no API key.
- Parameterize the active embedding space (`embedding_model`,
  `embedding_source_model`, `embedding_dimensions` accepting 1536 or 384) so a
  deployment uses one space at a time. Stored rows keep their own model and
  dimensions; retrieval keeps excluding incompatible spaces.
- Keep the OpenAI `kollio-embedding` alias supported and opt-in for later; the
  local space becomes the development and default space.
- Prove the local space with a reviewed real FR-to-EN retrieval case, recorded
  once against the real server and replayed in CI without it.

## Capabilities

### New Capabilities

None. This change extends the existing `matching/multilingual-embeddings`
capability with a second space.

### Modified Capabilities

- `matching/multilingual-embeddings`: add a self-hosted 384-dimensional
  FR/EN space alongside the approved 1,536-dimensional OpenAI space, with
  per-space provenance and the same incompatibility exclusion.

## Impact

Touches `Settings`, the LiteLLM model list, Compose (one pinned CPU service),
the embedding platform module, and embedding tests. No contract, frontend, or
migration change: existing tables already key rows by model and dimensions.
Uses the existing BAI-independent local network; adds no secret and no vendor
dependency. OpenAI criteria 2.1/2.5 stay open until a valid credential exists;
this change does not close them, it unblocks matching without them.

## Out of Scope

- Removing the OpenAI space or its rows.
- Claiming quality parity with `text-embedding-3-large`; the recorded proof
  covers the local space only, on its own reviewed case.
- GPU inference or a second hosted provider.
