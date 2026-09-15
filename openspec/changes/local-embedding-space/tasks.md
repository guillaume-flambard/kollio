## 1. Gateway and server spike

- [x] 1.1 Confirm LiteLLM translates an OpenAI-shaped embedding request to the
  TEI backend for `intfloat/multilingual-e5-small`; if not, define the narrow
  TEI-client fallback behind the same `embed()` signature.
- [x] 1.2 Pin the TEI image digest and record the model revision used.

## 2. Active embedding space

- [x] 2.1 Add failing tests for 384-dimensional validation and for retrieval
  excluding 1536-dimensional rows when the local space is active (and vice
  versa).
- [x] 2.2 Parameterize `Settings` (`embedding_model` default
  `kollio-embedding-local`, `embedding_source_model`,
  `embedding_dimensions: Literal[1536, 384]` default 384) and verify existing
  OpenAI-path tests pass with the space set to 1536.
- [x] 2.3 Apply the E5 `query:` / `passage:` prefix convention at the idea and
  query call sites and verify prefix tests pass.

## 3. Deployment configuration

- [x] 3.1 Add the pinned TEI CPU service to Compose and the
  `kollio-embedding-local` LiteLLM alias with no API key, and verify no secret
  is tracked by Git.
- [x] 3.2 Verify the production validator still fails closed on missing
  Postgres, Redis, Logto, gateway, and telemetry without requiring
  `OPENAI_API_KEY` for the local path.

## 4. Recorded retrieval proof

- [x] 4.1 Run the reviewed real FR-to-EN case once against the live local
  server, record vectors with provenance (model, dims, server digest, date),
  and verify the expected counterpart ranks ahead of unrelated candidates.
- [x] 4.2 Add CI replay tests (no network, no server) for ranking, dimension,
  and space-exclusion from the recording.
- [x] 4.3 Run Ruff, strict Mypy, unit and Postgres integration suites,
  contract drift check, and the production build.

## 5. Close-out

- [x] 5.1 Write `acceptance.md` mapping each scenario to its test or check,
  noting the OpenAI criteria 2.1/2.5 remain open and unblocked-by-this-change.
- [x] 5.2 Update `docs/11-bootstrap-status.md` and
  `docs/12-agentic-stack-2026.md` for the second space and its default.
