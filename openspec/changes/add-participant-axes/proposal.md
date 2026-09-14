## Why

The team loop speaks one vocabulary borrowed from product and engineering roles, and a workspace member must file an application to join an internal initiative. For the B2B pilot, participation and the business function a person brings are two different things, and an owner should be able to add a colleague directly.

## What Changes

- Split the single team role into a participation (`owner`, `decision_maker`, `contributor`, `observer`) and a business function from a closed list of twelve.
- Let the owner add a workspace member directly with both axes; the self-nomination application keeps working and now names the function the applicant brings.
- Migrate every existing membership and application onto the function axis (craft roles map once), and move the ideas' sought values onto the same axis.
- Refuse unknown functions and the reserved `owner` participation.

## Capabilities

### New Capabilities

- `participant-axes`: an initiative's people are described by participation and business function, and the owner can add them directly.

## Impact

Adds participation and business function columns with check constraints and one data migration (mapping the legacy craft roles), a domain rule with unit tests, the owner-only add operation, the function in the application and read payloads, the explorer filter vocabulary, and French/English labels for both axes. The join-application flow, departures and the workspace boundary are unchanged.

Tickets: GitHub #54 (this slice), #52 (parent spec). The settings-free member picker UI needs a workspace-members endpoint and ships separately.
