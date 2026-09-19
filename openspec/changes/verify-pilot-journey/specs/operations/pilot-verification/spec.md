# operations/pilot-verification Specification

## Purpose

A pilot milestone may only be claimed on evidence produced against a real runtime: a real browser, a real sign-in, the API, the database and the worker. This capability records what that evidence must contain and what a run with simulated responses may not be used to claim.

## ADDED Requirements

### Requirement: The supported journey is verified against a real runtime (LIVE-PATH-01)

The supported decision-space journey SHALL be exercised on an isolated environment with real authentication and durable records, and the evidence SHALL name the commit and the environment it was produced on.

#### Scenario: LIVE-PATH-01 Two participants complete the journey

- **WHEN** two authenticated participants use an isolated workspace
- **THEN** they frame one question with two options, contribute, record a reasoned decision, create its experiment, enter an outcome and confirm a learning
- **AND** reloading as an authorised participant shows the same records
- **AND** the evidence names the commit and the environment

#### Scenario: LIVE-PATH-02 A non-member is refused

- **WHEN** an identity that is not a member of the workspace requests the private decision or its learning
- **THEN** it can read neither and change neither
- **AND** the refusal is observed, not argued

#### Scenario: LIVE-PATH-03 A failed request stays recoverable

- **WHEN** a request fails during the journey
- **THEN** the interface explains it and keeps the input recoverable
- **AND** no success is reported and nothing is committed twice

#### Scenario: LIVE-PATH-04 Both locales and a phone width are covered

- **WHEN** the journey runs in French and in English
- **THEN** both paths are exercised against the real backend
- **AND** a phone width is checked during the same run

#### Scenario: LIVE-PATH-05 Provider-dependent behaviour is labelled

- **WHEN** the run touches behaviour that depends on a model provider
- **THEN** each such behaviour is listed as live, simulated or unverified
- **AND** live model calls stay behind the existing budgeted opt-in
- **AND** provider quality is never inferred from recordings

#### Scenario: LIVE-PATH-06 Blocking defects are fixed, never bypassed

- **WHEN** the run exposes a defect that blocks the journey
- **THEN** it is filed with a reproduction and fixed before the milestone is called complete
- **AND** authentication is never bypassed to get past it
