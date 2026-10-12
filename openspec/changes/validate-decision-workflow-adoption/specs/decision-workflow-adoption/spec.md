## Purpose

Establish whether private teams adopt Kollio's decision workflow at the right moment, use it to work through disagreement, and recognize its durable value without exposing their decision content.

## ADDED Requirements

### Requirement: The decision-start trigger is evidenced
The pilot SHALL record why the team started a Decision Space, what alternative workflow it would otherwise have used, and whether Kollio was introduced before or after the substantive decision discussion began. The finding SHALL be classified as a clear trigger, a late trigger, or an unclear trigger.

#### Scenario: Kollio is started before substantive discussion
- **WHEN** a team creates a Decision Space before it begins substantive decision discussion elsewhere
- **THEN** the pilot record identifies the triggering event and classifies the trigger as clear

#### Scenario: Kollio is started after substantive discussion
- **WHEN** a team creates a Decision Space after the decision discussion has already begun elsewhere
- **THEN** the pilot record identifies what made the team start late and classifies the trigger as late or unclear

### Requirement: Coordination and disagreement are assessed separately
The pilot SHALL record whether the team could identify the next responsible action and whether an important disagreement became more legible, remained unresolved, or was resolved. It SHALL distinguish a factual disagreement, an assumption, and an authority decision when participants identify them.

#### Scenario: A disagreement becomes actionable
- **WHEN** participants encounter a material disagreement in a Decision Space
- **THEN** the pilot record states whether it was factual, assumption-based, or authority-based
- **AND** it states whether the next action or decision owner became clear

#### Scenario: No material disagreement occurs
- **WHEN** the pilot contains no material disagreement
- **THEN** the pilot record states that absence without claiming that disagreement support was validated

### Requirement: Value, memory, and portability trust are evidenced
The pilot debrief SHALL record participants' own account of the practical value they observed, whether they would expect past learning to help a later decision, and whether they understand how to retrieve their decision record. It SHALL not claim time saved, decision quality, or retention unless the participant evidence supports that conclusion.

#### Scenario: A participant identifies a concrete value signal
- **WHEN** a participant identifies a concrete outcome from using the workflow
- **THEN** the debrief records the outcome as the participant described it
- **AND** it distinguishes observed value from an unverified estimate

#### Scenario: A participant questions memory or portability
- **WHEN** a participant expresses uncertainty about finding or taking out past decision material
- **THEN** the debrief records the concern and its impact on trust or reuse
- **AND** it does not propose an implementation without a disposition decision

### Requirement: Follow-up scope is evidence-led
Every adoption finding SHALL receive one of three dispositions: a follow-up OpenSpec change when it blocks a milestone or recurs, an explicit deferral with rationale, or no change when the finding is not reproduced. A requested feature alone SHALL NOT be treated as validation.

#### Scenario: A recurring adoption blocker is observed
- **WHEN** the same friction blocks a milestone for more than one participant or recurs in the same pilot path
- **THEN** the debrief creates or names a follow-up OpenSpec change

#### Scenario: An isolated preference is observed
- **WHEN** one participant requests a feature without a repeated or milestone-blocking friction
- **THEN** the debrief records the request as an isolated preference or defers it with rationale
