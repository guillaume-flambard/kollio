# Verify the pilot journey with real authentication

## Why

The simplified journey has only ever run against simulated API responses. The browser suite mocks every call it makes, so it proves rendering and says nothing about authentication, workspace isolation, persistence, the worker or a live provider. The milestone this project is chasing is one real decision taken by two people, and the gate before inviting that team is evidence that the journey survives a real browser, API, database and worker with real sign-in, and that a non-member is refused. Nothing in the repository records that evidence today.

## What Changes

- Stand up an isolated local environment with its own identity provider and three synthetic identities: two who belong to a workspace and one who does not.
- Run the decision-space journey end to end on it: frame a question with two options, contribute as both people, record a reasoned decision, create its experiment, enter an outcome, confirm a learning, then reload as an authorized participant and read the same state back.
- Prove refusal: the third identity can read and change nothing in that workspace.
- Record the evidence in the acceptance file with the exact commit, the environment, the requests and their outcomes, the rows read back after a reload, and an explicit list of provider-dependent behaviour marked live, simulated or unverified.
- Fix any blocking defect the run exposes, with a reproduction, instead of working around it.
- Keep the French and English paths and a phone-width layout inside the run.

## Capabilities

### New Capabilities

- `operations/pilot-verification`: the record that a pilot journey works against a real runtime, and the rules for what may be claimed from a simulated run.

### Modified Capabilities

None.

## Impact

Adds a local verification environment (an identity provider plus the application stack) and this change. Any blocking defect the run exposes is fixed here, which is where the real code diff will land. No production data, no client data, no change to the pilot deployment, no new dependency, and no secret in the repository: the environment is local and every identity and every record in it is synthetic.

## Out of Scope

- Touching production or using client data.
- A second broad test framework: the existing e2e and browser infrastructure is reused, with recorded manual evidence where that is the honest instrument.
- Claiming that model output is validated in general, or inferring provider quality from recordings.
- Changing the journey the previous ticket delivered, unless the run finds a blocking defect in it.
