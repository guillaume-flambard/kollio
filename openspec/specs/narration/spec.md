# narration Specification

## Purpose

While a constraint analysis is running, narrate the real inputs it is weighing rather than generic stage labels, without changing the verdict that replaces it.

## Requirements

### Requirement: The running screen narrates the real inputs (NL-01)
When the analysis is running, the screen SHALL read `analysis.progress` and show the actual company name, the active objective titles, the active constraint titles, the reused learning texts and the evidence sources, each group headed by a localized, count-aware sentence.

#### Scenario: Real inputs shown
- **WHEN** the analysis is running
- **THEN** the screen reads `analysis.progress`
- **AND** shows the company name, the active objective titles, the active constraint titles, the reused learning texts and the evidence sources
- **AND** each group is headed by a localized, count-aware sentence

### Requirement: The narration never overstates (NL-02)
A group with no real data SHALL be omitted; a long list SHALL be capped and the overflow shown as "+N more", so the narration never overstates.

#### Scenario: Empty group omitted
- **WHEN** a group has no real data
- **THEN** it is omitted

#### Scenario: Long list capped
- **WHEN** a group's list is long
- **THEN** it is capped and the overflow is shown as "+N more"

### Requirement: The narration derives from the frozen snapshot (NL-03)
The `running` read SHALL derive `progress` from the frozen launch snapshot and the effective evidence (which already carries the reused learnings), so nothing is invented.

#### Scenario: Progress derived, not invented
- **WHEN** the `running` read builds `progress`
- **THEN** it derives it from the frozen launch snapshot and the effective evidence
- **AND** invents nothing

### Requirement: The verdict is unchanged (NL-04)
The verdict that replaces the narration SHALL be the same resolved/abstained state as before; the narration SHALL never block or fabricate it.

#### Scenario: Verdict unaffected
- **WHEN** the analysis completes
- **THEN** the verdict is the same resolved/abstained state as before
- **AND** the narration neither blocked nor fabricated it

### Requirement: Reduced motion settles every group at once (NL-05)
`prefers-reduced-motion: reduce` SHALL render every group settled at once; the real data, not the animation, is what shows.

#### Scenario: Reduced motion
- **WHEN** the member prefers reduced motion
- **THEN** every group renders settled at once
- **AND** the real data is shown

### Requirement: FR and EN narrate the same real data (NL-06)
FR and EN SHALL show the same localized sentences over the same real data, with no technical jargon and canonical tokens only.

#### Scenario: French and English
- **WHEN** the narration runs in French, then in English
- **THEN** the same real data is shown under localized sentences
- **AND** no technical jargon appears
- **AND** only canonical tokens are used
