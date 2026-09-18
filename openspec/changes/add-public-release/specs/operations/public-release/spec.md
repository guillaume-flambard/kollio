# operations/public-release Specification

## Purpose

A public repository is a state the project keeps, not an action taken once. It carries the terms a reader and a contributor operate under, it says how to run the stack and how to propose a change, and it holds no map of the operator's machines.

## ADDED Requirements

### Requirement: The repository carries the Apache-2.0 license (PR-01)

The repository SHALL carry the Apache-2.0 license text at its root, and the README SHALL name that license, so a reader knows the terms without asking.

#### Scenario: A reader looks for the license

- **WHEN** someone opens the repository root
- **THEN** a `LICENSE` file holds the Apache-2.0 text
- **AND** the README states that the project is published under Apache-2.0

### Requirement: A contributor finds how to participate (PR-02)

The repository SHALL explain how to run the stack, how to propose a change, how to behave in the project and how to report a vulnerability, so a contributor does not have to guess.

#### Scenario: A newcomer wants to propose a change

- **WHEN** someone opens the contributing guide
- **THEN** it lists the local setup commands, the change discipline of the repository (one behavior per change, a conventional single-line commit) and the sign-off each commit must carry
- **AND** a code of conduct, a security policy and issue and pull request templates exist beside it

### Requirement: Examples, documents and archived records use placeholder infrastructure (PR-03)

Example configuration, development defaults, deployment notes, documents and archived evidence SHALL use placeholder hosts, documentation addresses and relative paths instead of the operator's, so publishing does not hand out a map of one machine, while every record keeps its meaning.

#### Scenario: A reader opens the example environment

- **WHEN** someone reads `.env.example`
- **THEN** every host is `example.com` or one of its subdomains and every path is relative
- **AND** no example file, document or archived record carries the operator's host names, server address or home directory

#### Scenario: An archived record stays readable

- **WHEN** someone reads an archived acceptance file
- **THEN** the recorded commands, status codes and sizes are unchanged
- **AND** only the host name has become a placeholder

### Requirement: The README orients a newcomer (PR-04)

The README SHALL state the product in one paragraph, give a quickstart, keep the documentation order and mention the license, and its status section SHALL describe the product the repository actually holds.

#### Scenario: A newcomer opens the repository

- **WHEN** someone reads the README for the first time
- **THEN** the product paragraph, the quickstart, the documentation order and the license are all present
- **AND** the status section describes the current product rather than a superseded backend
