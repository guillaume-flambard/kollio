## Context

`embed()` posts OpenAI-shaped embedding requests to `settings.llm_base_url +
"/embeddings"` (LiteLLM), and `store_embeddings` / `similar_idea_ids` already
scope rows by model and dimensions: the primary key includes both, and
retrieval excludes other spaces. `Settings` hardcodes
`embedding_dimensions: Literal[1536]` and defaults to the `kollio-embedding`
alias, which needs `OPENAI_API_KEY`. The LiteLLM config already defines that
alias; no local alias or server exists.

## Goals / Non-Goals

**Goals:**

- One deployment uses one explicit embedding space, with no credential needed
  for the local space.
- OpenAI and local rows coexist in the same tables without cross-space matches.
- A real recorded proof that the local space retrieves FR-to-EN, replayable in
  CI with no server.

**Non-Goals:**

- Removing OpenAI support, rows, or criteria 2.1/2.5.
- Quality parity claims against `text-embedding-3-large`.
- GPU inference, a second vendor, or frontend/contract changes.

## Decisions

### Serve multilingual-e5-small via Text Embeddings Inference on CPU
`intfloat/multilingual-e5-small` (118M parameters, 384 dimensions) is the
smallest E5 multilingual model with credible cross-lingual retrieval. The
official HuggingFace TEI image, digest-pinned, serves it on CPU in ~200MB RAM
behind the existing Compose network. Alternative considered: Ollama with
`bge-m3` (heavier, ~1.2GB, 1024 dims). TEI plus e5-small is the lighter fit
for "gratuit et pas lourd".

### Route through LiteLLM under kollio-embedding-local
The application keeps posting OpenAI-shaped requests to the gateway; only the
alias changes. LiteLLM gains a `kollio-embedding-local` entry pointing at the
TEI host with no `api_key`. First implementation spike must confirm LiteLLM
translates gateway embedding calls to the TEI backend; fallback is a narrow
TEI client behind the same `embed()` signature.

### Parameterize the active space, keep per-row provenance
`Settings` becomes `embedding_model` (alias, default
`kollio-embedding-local`), `embedding_source_model` (default
`intfloat/multilingual-e5-small`), `embedding_dimensions: Literal[1536, 384]`
(default 384). Validation in `validate_vectors` / `store_embeddings` and the
retrieval filter read the active settings; stored rows are untouched and old
spaces are excluded automatically by the existing model-plus-dimension scope.

### Follow the E5 prefix convention
E5 models expect `query:`-prefixed queries and `passage:`-prefixed indexed
texts. Both prefixes are applied in one place (`embed()` call sites for ideas
and retrieval queries) so index and query time stay consistent. The convention
is recorded in code, not assumed.

### Record once, replay in CI
One live run against the real TEI server captures the reviewed FR/EN vectors
as a fixture (with provenance: model, dims, server digest, date). CI asserts
ranking, dimension, and exclusion rules from the fixture with no network, the
same pattern as the recorded agent evaluations. A live opt-in job re-records
when the model or server changes.

## Migration Plan

1. Add the TEI service, LiteLLM alias, and settings without changing the
   default active space; all existing tests pass unchanged.
2. Flip the default active space to local; OpenAI rows remain stored but
   excluded from retrieval.
3. Record the local FR-to-EN proof fixture and add replay tests.
4. Rollback restores the previous default alias; no data migration either way
   since rows carry their own space.
