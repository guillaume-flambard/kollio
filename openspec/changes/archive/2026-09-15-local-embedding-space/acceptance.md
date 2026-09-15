# Acceptance evidence — local-embedding-space

Self-hosted FR/EN embedding space (`intfloat/multilingual-e5-small`, 384
dimensions) served by TEI on CPU and routed through LiteLLM under
`kollio-embedding-local` with no API key. Implemented 2026-09-15.

| Spec scenario | Evidence |
| --- | --- |
| FR/EN embedded in the local space (384d, e5 source) | Live spike: TEI `cpu-1.9` returned 2 indexed vectors, 384 dims, OpenAI shape; `test_default_active_space_is_local_multilingual` |
| Incompatible vector rejected, no partial storage | `test_embedding_validation_rejects_*` (unchanged) + OpenAI-path test now declares its 1536 space explicitly |
| Cross-space exclusion, both directions | `test_embedding_spaces_exclude_each_other_in_both_directions` (384-active finds only the 384 row, 1536-active only the 1536 row) + pre-existing one-direction test kept |
| Local path works without OpenAI credential | Committed gateway shape proven live (`api_key: local-tei-no-auth` placeholder + per-entry `drop_params`); full production Settings accepted with no `OPENAI_API_KEY` (`test_complete_production_agentic_runtime_configuration_is_accepted`) |
| Recorded FR-to-EN retrieval ranks expected first | Live recording 2026-09-15: expected 0.8782 vs 0.7441/0.7619/0.7640; `test_recorded_local_retrieval_ranks_expected_counterpart_first` replays `local_retrieval.fr_en.json` with no network |
| Replay without server | Replay test uses only the fixture; no `TEST_DATABASE_URL`, no HTTP |

## Verification runs (2026-09-15)

- Spike: `openai/`-prefixed alias + custom `api_base` + per-entry `drop_params`
  reaches TEI through the pinned gateway image; omitting `api_key` fails
  (LiteLLM requires a client-side value), hence the committed non-credential
  placeholder. TEI digest `sha256:ad950d30…`, model
  `intfloat/multilingual-e5-small` rev `614241f6`.
- `pytest -m 'not live'`: 177 passed, 2 deselected (was 170 before this change).
- Ruff check + format check + strict Mypy on the five gated domain dirs: clean.
  Extra strict run over platform/adapters surfaces 12 pre-existing errors in
  untouched adapter files, outside the CI gate; none in touched files.
- `pnpm lint`, `pnpm typecheck`: exit 0. Locales parity, canonical tokens only.
- Vitest: 32 passed. OpenAPI export + client regen: no drift. `pnpm build` +
  performance budgets: pass.
- Secret scan replicated without git (git binary broken on this machine, Xcode
  license): only hit is the gitignored local `.env`; committed files clean.

## Known boundaries

- OpenAI criteria 2.1/2.5 remain open; this change unblocks matching without
  them and does not close them.
- No quality-parity claim vs `text-embedding-3-large`; the proof covers the
  local space on its own reviewed case.
- The `embeddings` Compose service is declared here; the production rollout
  goes through the `lab-infra` deployment path, not this file directly.
- Production runs no embedding vectors yet, so flipping the default space
  excludes nothing.
