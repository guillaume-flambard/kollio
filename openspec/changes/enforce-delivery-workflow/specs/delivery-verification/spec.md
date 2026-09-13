## ADDED Requirements

### Requirement: Changes connect outcomes to evidence
Each nontrivial product change SHALL define acceptance scenarios and identify the
checks that prove them, including simulated boundaries and outstanding criteria.

#### Scenario: Agent prepares a product change
- **WHEN** an agent begins a product change
- **THEN** it follows the delivery workflow referenced by AGENTS.md
- **AND** it links scenarios, relevant contracts and durable decisions to the work

### Requirement: Verification includes browser and component checks
Local verification and CI SHALL execute component and browser acceptance tests.

#### Scenario: A browser acceptance assertion fails
- **WHEN** a browser scenario fails in CI
- **THEN** the verify job fails and publication cannot proceed
- **AND** browser failure artifacts are retained

#### Scenario: A focused test is committed
- **WHEN** CI discovers a Playwright test marked only
- **THEN** browser verification fails

### Requirement: Private browsing preserves navigation and locale
The browser acceptance suite SHALL check opening an idea, pagination, empty
results and inaccessible idea presentation in French and English.

#### Scenario: Member returns from the second page
- **WHEN** a member selects Previous on page two
- **THEN** the first page's ideas are visible again
- **AND** the active locale is preserved

#### Scenario: Member views an original French idea in English
- **WHEN** a member opens the idea from the English browsing interface
- **THEN** the detail URL remains in the English locale
- **AND** the original title and pitch remain unchanged
