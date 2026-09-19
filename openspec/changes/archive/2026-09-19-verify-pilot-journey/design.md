# Design - verify the pilot journey with real authentication

## Context

The browser suite runs against a fixture that mocks every API call, so a green suite says the screens render and nothing about a real sign-in, workspace isolation, persistence or the worker. The development compose file ships no identity provider: it only carries placeholders, `LOGTO_ISSUER`, `LOGTO_JWKS_URL` and `LOGTO_AUDIENCE` for the API and the `NUXT_LOGTO_*` values for the web, all filled from the environment. The pilot hosts its own Logto instance and database, both healthy for days, but its stack environment exposes a single key, `LOGTO_POSTGRES_PASSWORD`, and no management credential, so test identities cannot be created there through the API by an agent.

The lab infrastructure already runs that same Logto image in a stack of its own: a Postgres, a one-shot seed job that runs the CLI seed, and the Logto service. That file is the working model for an isolated identity provider on this machine, and reusing the same image keeps the local verification close to the deployed path without touching it.

The journey under verification is the one the previous ticket delivered: a decision space read as three moments, with its Explore, Converge, Options, Decision, Experiment and Learning sections.

## Goals / Non-Goals

**Goals:**
- Evidence, dated and tied to a commit, that the supported journey completes against a real browser, API, database and worker with real sign-in.
- Refusal proven for an identity that is not a member of the workspace.
- Every provider-dependent behaviour named as live, simulated or unverified, with no claim inferred from recordings.
- Blocking defects the run exposes are filed and fixed here.

**Non-Goals:**
- Running the verification against the pilot or any shared environment.
- A permanent new test framework, or turning the manual run into a CI suite.
- Exercising unsupported journeys or inviting a real team.
- Proving anything about model quality or about authentication the test itself bypasses.

## Decisions

### An isolated local environment rather than the pilot

The ticket asks for an isolated development or staging workspace and no production pollution, and the pilot's identity provider exposes no management credential. Creating identities on the pilot was rejected for both reasons, and a staging deployment on the server was rejected as more moving parts than the evidence needs. The local stack is disposable, synthetic and safe to break.

### Three identities, two members and one outsider

The journey needs two participants who belong to one workspace and a third who does not, so refusal is a real observation rather than an argument. The identities live only in the local identity provider and hold no client data.

### The identity provider is the deployed image, seeded locally

A stub issuer would not be real authentication, which is the one thing this ticket must not fake. The local provider therefore runs the same pinned Logto image with its own Postgres and seed job, as the lab stack does, and the application is pointed at it. The alternative, disabling authentication for the run, is excluded by the delivery contract.

### The record lives in the acceptance file

The evidence is a dated record with the commit and the environment, held in this change's acceptance file, and the run is scripted only as far as is needed to reproduce it. The alternative, a new checked-in harness, was rejected: the ticket explicitly warns against building a second broad test framework, and a run manual enough to observe behaviour is the honest instrument here.

### Blocking defects are fixed here

Anything that stops the journey is reproduced, filed and fixed in this change rather than worked around, because a workaround would quietly invalidate the evidence this change exists to produce.

## Migration Plan

1. Stand up the isolated identity provider and seed its database.
2. Create the workspace's OIDC client and the three identities.
3. Bring up the application stack on the same network, pointing at the local provider, and run migrations.
4. Execute the journey as both participants, then reload and read the state back.
5. Prove refusal with the outsider, cover French, English and a phone width.
6. Record the evidence, the environment and the provider-dependent list in the acceptance file, then tear the environment down.

Rollback means discarding the local environment: no production, contract or data state is involved.

## Risks

- The local provider may need its own console to create the client and the users, which the run must do by hand; if that proves impossible, the run stops and reports the boundary rather than falling back to simulated auth.
- The journey's provider-dependent steps may have no live provider configured locally; those are then marked unverified, which is a finding of this change, not a failure of it.
- A long manual run invites drift; the acceptance file records the exact commit and the exact environment so the record cannot be over-read.
