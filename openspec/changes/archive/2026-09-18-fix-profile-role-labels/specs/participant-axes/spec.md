# Spec delta - participant-axes

## Purpose

The people around an initiative are described by two axes, participation and business function, and a person also carries craft roles across initiatives. The interface states each of those values in the reader's language.

## ADDED Requirements

### Requirement: Every participant axis value renders as a localized label (PRL-01)

The web SHALL resolve each participant axis value through the label family that owns its vocabulary: a person's craft roles through the roles family and a membership's business function through the function family. The web SHALL NOT render a translation key path where a value label belongs.

#### Scenario: A profile renders craft roles the legacy vocabulary does not cover

- **WHEN** a profile carries the craft roles `engineering` and `platform`
- **THEN** the profile shows the localized label for each role in the active locale
- **AND** no rendered text contains a translation key path

#### Scenario: A profile renders a membership's business function

- **WHEN** a profile lists a membership whose business function is `finance`
- **THEN** the membership line shows the localized label for that function in the active locale

#### Scenario: An explorer row renders a collaborator's craft role

- **WHEN** an idea's first collaborator carries the craft role `engineering`
- **THEN** the explorer row's expertise badge shows the localized label for that role in the active locale
