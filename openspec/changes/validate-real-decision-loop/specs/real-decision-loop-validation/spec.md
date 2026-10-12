## Purpose

Validate that a private team can use Kollio for a real decision, observe its outcome, and return voluntarily while preserving the confidentiality of its decision content.

## ADDED Requirements

### Requirement: A real decision loop is evidenced without retaining decision content
The validation record SHALL establish that two distinct authenticated participants used one private Decision Space for a real decision in their own words, recorded a Decision Record, observed an experiment outcome, and confirmed a learning. The record SHALL retain only pseudonymized participant roles, lifecycle milestones, and evidence references; it SHALL NOT copy decision text, source material, credentials, or model prompts.

#### Scenario: Two participants complete a first real loop
- **WHEN** two distinct pilot participants use a private Decision Space
- **THEN** the validation record identifies an owner and a second participant by pseudonymized role
- **AND** it records evidence references for contribution, Decision Record, observed outcome, and confirmed learning milestones

#### Scenario: A participant does not complete the loop
- **WHEN** a pilot participant abandons the Decision Space before a Decision Record, observed outcome, or confirmed learning exists
- **THEN** the validation record marks the uncompleted milestone and the observed friction without fabricating completion

### Requirement: Voluntary return is distinguished from a guided demonstration
The validation SHALL treat the first loop as successful only when at least one participant subsequently creates or joins a second Decision Space without a facilitator directing that action at that time. The evidence SHALL state whether the return happened and SHALL distinguish a voluntary return from a scheduled demonstration.

#### Scenario: A participant returns voluntarily
- **WHEN** a participant creates or joins a second Decision Space after the first loop has an observed outcome
- **THEN** the validation record links the return to the pseudonymized participant role and the second Space evidence reference
- **AND** it marks the return as voluntary only when no facilitator prompted that action at the time

#### Scenario: No voluntary return occurs in the validation window
- **WHEN** no participant creates or joins a second Decision Space before the agreed validation window closes
- **THEN** the validation record records no voluntary return
- **AND** the pilot SHALL NOT be reported as repeated product use

### Requirement: Validation findings create a disposition
The pilot debrief SHALL list material product frictions separately from feature requests and SHALL give each friction a disposition: a follow-up OpenSpec change, an explicitly deferred decision, or a documented reason it was not reproduced. The debrief SHALL state the boundary between observed pilot evidence and simulated test evidence.

#### Scenario: Material friction is found
- **WHEN** the pilot identifies a friction that blocks, delays, or confuses completion of a decision-loop milestone
- **THEN** the debrief records the affected milestone and a disposition
- **AND** a proposed product change is not presented as delivered evidence

#### Scenario: The pilot has no material friction
- **WHEN** the pilot debrief identifies no material friction
- **THEN** it states the participants, milestones, and evidence boundaries that support that conclusion

