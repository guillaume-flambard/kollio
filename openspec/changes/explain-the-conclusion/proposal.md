# Explain the conclusion: basis, missing evidence, contradictions

## Why

#58 made the engine separate Known, Assumed and Unknown and state
contradictions, and the API exposes both. Nothing in the product showed
them: a member read a score and five notes with no way to tell what the
analysis knew from what it guessed, and a conflict with a stated
objective or constraint stayed invisible.

## What changes

- The verdict panel names each factor's basis and, when the basis is
  unknown, the missing evidence it names.
- A contradictions block lists each conflict with its target (objective
  or constraint) and the engine's prose.
- Both French and English label the vocabulary and the contradiction
  targets.

## Out of scope

- The idea detail and the iteration timeline still show only the analysis
  label; they have no constraint panel to extend today. Carrying the
  explanation there is a separate slice.
