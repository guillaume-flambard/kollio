# API client

The generated TypeScript client (`@kollio/api-client`). The contract boundary between the web app and the API: the web app talks to the API only through it.

## Language

**Contract**:
The OpenAPI document in `contracts/` that both sides code against. Generated from the API, never hand-edited on the client side.
_Avoid_: Schema alone, spec (as a vague noun)

**GeneratedClient**:
The TypeScript client produced from the contract by `generate:client`. Regenerated, never patched by hand.
_Avoid_: SDK, wrapper, fetch helper
