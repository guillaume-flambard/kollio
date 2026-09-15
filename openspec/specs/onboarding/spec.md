# onboarding Specification

## Purpose

Let a workspace capture its non-negotiables and key indicators alongside its profile, objectives and constraints, through a seven-question wizard that completes with partial answers.

## Requirements

### Requirement: The company context carries principles and key metrics
The workspace company context SHALL carry two more workspace-private, lang-stamped lists alongside objectives and constraints: **principles** (non-negotiables, a title and optional detail) and **key metrics** (a name and optional value, unit, observed date and source). They SHALL be readable in `GET /workspaces/{workspace_id}/company-context` and SHALL be created or updated through `POST`/`PATCH` on `.../company-context/principles` and `.../company-context/metrics`. A caller outside the workspace SHALL be refused everywhere, the same 404 as the rest of the context.

#### Scenario: Principles and metrics read
- **WHEN** a workspace member reads the company context
- **THEN** the response carries the principles and the key metrics alongside the objectives and constraints

#### Scenario: Principle created
- **WHEN** a member posts a principle with a title and optional detail
- **THEN** the system persists it for that workspace

#### Scenario: Metric created
- **WHEN** a member posts a metric with a name and optional value, unit, observed date and source
- **THEN** the system persists it for that workspace

#### Scenario: Outsider refused
- **WHEN** a caller outside the workspace reads or writes principles or metrics
- **THEN** the system responds 404

### Requirement: The settings screen opens a seven-question wizard (ONB-01)
The settings screen SHALL open with a seven-question wizard; with nothing filled, all seven questions SHALL read as pending.

#### Scenario: Fresh workspace
- **WHEN** a member opens the wizard on a workspace with no context saved
- **THEN** all seven questions read as pending

### Requirement: A member answers any subset and saves (ONB-02)
A member SHALL answer any subset and save; every entered answer SHALL persist in the model (profile PUT plus one POST per new objective, constraint, principle and metric), and the wizard SHALL complete with partial answers.

#### Scenario: Partial answers persist
- **WHEN** a member answers a subset of the questions and saves
- **THEN** the entered answers persist (profile PUT plus one POST per new objective, constraint, principle and metric)
- **AND** the wizard completes with the partial answers

### Requirement: Skipped and answered questions are distinguished after a save (ONB-03)
A skipped question SHALL stay visibly pending after a save; an answered one SHALL not.

#### Scenario: Skip then save
- **WHEN** a member skips a question, answers another and saves
- **THEN** the skipped question stays visibly pending
- **AND** the answered one does not

### Requirement: Saving twice does not duplicate (ONB-04)
Saving the same wizard twice SHALL not duplicate a row that is already stored, matched by trimmed, case-insensitive title or name.

#### Scenario: Save twice
- **WHEN** the same wizard is saved twice
- **THEN** no already-stored row is duplicated
- **AND** matching is by trimmed, case-insensitive title or name

### Requirement: Non-negotiables and indicators have enrichment forms (ONB-05)
Non-negotiables and key indicators SHALL have their own enrichment forms, so a question can be completed after startup.

#### Scenario: Enrich after startup
- **WHEN** a member opens the enrichment form for a non-negotiable or a key indicator
- **THEN** the question can be completed after startup

### Requirement: The context is invisible to a non-member (ONB-06)
The context, including principles and metrics, SHALL be invisible to a non-member: read SHALL be a 404, and every write SHALL be refused.

#### Scenario: Non-member reads the context
- **WHEN** a non-member requests the company context
- **THEN** the system responds 404

#### Scenario: Non-member writes
- **WHEN** a non-member attempts any context write
- **THEN** the system refuses it

### Requirement: The wizard behaves identically in FR and EN (ONB-07)
The wizard SHALL behave identically in French and English; every label SHALL come from the catalogs.

#### Scenario: French and English
- **WHEN** the wizard runs in French, then in English
- **THEN** every label comes from the catalogs
- **AND** behavior is identical
