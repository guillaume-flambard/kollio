## Purpose

Defines the recoverable production foundation required before Kollio exposes approved private
legacy data on the existing Memo Labs infrastructure.

## ADDED Requirements

### Requirement: Deployment follows the existing infrastructure path
Kollio SHALL deploy through the existing GitHub Actions, private registry, autodeploy,
Make/Ansible, Compose, and Traefik path. Deployment SHALL use this single supported path.

#### Scenario: Main branch build succeeds
- **WHEN** locked lint, type, test, contract, and image checks pass on `main`
- **THEN** the pipeline SHALL publish immutable images eligible for autodeploy

#### Scenario: A required check fails
- **WHEN** any required pipeline check fails
- **THEN** no new Kollio image SHALL become eligible for production rollout

### Requirement: Schema migration precedes application rollout
Deployment SHALL run each schema migration once, verify success, and only then start processes
that depend on the new schema.

#### Scenario: Migration fails
- **WHEN** a production migration exits unsuccessfully
- **THEN** the previous healthy version SHALL remain active and the new version SHALL receive no traffic

#### Scenario: Rollout succeeds
- **WHEN** migrations complete and live and ready probes pass through Traefik
- **THEN** autodeploy SHALL retain the new immutable image revisions

### Requirement: Real data requires a proven recovery path
Production import SHALL not begin until an encrypted backup has been restored into an isolated
database and point-in-time recovery has been demonstrated to a recorded recovery point.

#### Scenario: Recovery rehearsal passes
- **WHEN** the restored database matches expected schema, counts, relationships, and provenance
- **THEN** the approved import MAY proceed from a fresh consistent source snapshot

#### Scenario: Offsite backup is unavailable
- **WHEN** the only recoverable backup resides on the production VPS
- **THEN** production data cutover SHALL remain blocked

### Requirement: Legacy import remains private and reconcilable
The production import SHALL preserve source history, use stable identifiers, create no public
membership, and reconcile counts and provenance before completion.

#### Scenario: Approved snapshot is imported twice
- **WHEN** the same snapshot is imported more than once
- **THEN** the resulting idea count and provenance SHALL remain unchanged

#### Scenario: Existing provenance conflicts
- **WHEN** a source identifier already contains different provenance
- **THEN** the import SHALL fail without overwriting either record

### Requirement: Secrets remain outside repository history
Provider, identity, database, and telemetry secrets MUST be supplied through encrypted deployment
configuration or an operating-system credential store.

#### Scenario: Pull request is checked
- **WHEN** CI scans proposed repository content
- **THEN** secret files, private snapshots, and credential-shaped values SHALL fail the check
