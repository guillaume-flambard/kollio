## 1. Boundary and helpers

- [x] 1.1 Add a failing unit test for the chat helper: the payload carries
  `enable_thinking` false and the client is built with the configured timeout.
- [x] 1.2 Add `Settings.llm_request_timeout_seconds` (default 600) and create
  `apps/api/src/platform/llm_chat.py` with `chat_payload` and `chat_client`.

## 2. Rewire the gateways

- [x] 2.1 Add a failing regression test asserting the analysis gateway's
  outbound body carries `enable_thinking` false, reusing the queued-client
  capture pattern, and that the routed model and strict schema are unchanged.
- [x] 2.2 Build the payload and client in the constraint analysis adapter
  through the helper.
- [x] 2.3 Build the payload and client in the competition gateway through the
  helper.

## 3. Verification

- [x] 3.1 Run Ruff, strict Mypy on the touched packages, and the unit suite.
- [x] 3.2 Run the contract drift check, the Postgres integration suite and the
  production build.

## 4. Live acceptance

- [x] 4.1 Deploy the API and worker through the lab-infra path.
- [x] 4.2 Re-run the pilot loop in production and record the analysis
  completing with a score and five factors.
- [x] 4.3 Write `acceptance.md` mapping each scenario to its evidence and
  naming the remaining gaps.
