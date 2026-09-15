# Pilot demo path

The pilot SHALL be demonstrated on a seeded Faktus workspace by walking the loop
entirely through the interface, and the acceptance checklist SHALL be verified
with evidence. Each step below names the interface action and the executable
that already proves it.

## Steps

- **A** On the seeded workspace, open the company context and confirm the
  profile, objectives, constraints, principles and indicators are present.
  Seed proven by `test_seed_faktus`; editing proven by the settings checks.
- **B** Deposit an initiative with a closed type; the initial iteration lands on
  the timeline. `test_deposit` plus the deposit and initiative-type browser
  checks.
- **C** Launch an analysis; the active company context (objectives, constraints)
  is injected without any pasting. `test_analysis_context` and the reuse fixture.
- **D** Read the verdict: each factor carries its basis (Known, Assumed,
  Unknown), unknowns name the missing evidence, and a contradiction block names
  the objective or constraint it collides with. The recorded abstention and
  contradiction evals plus the explanation browser check DEPOSIT-05.
- **E** A second member challenges the initiative with a proposal; the owner
  accepts it and the append-only history keeps both steps. `test_iterations` plus
  the proposal, owner-actions and timeline browser checks.
- **F** Define an experiment from the initiative (hypothesis, metric, baseline,
  target). EXPERIMENT-02.
- **G** Launch it and record real outcomes. EXPERIMENT-03 and EXPERIMENT-04.
- **H** Complete it and confirm the drafted learning. EXPERIMENT-05 and
  EXPERIMENT-06; the loop round-trip in `test_the_learning_loop_records_outcomes_and_confirms_a_learning`.
- **I** Launch a later analysis and see the confirmed learning reused as
  evidence, scoped to the workspace. `test_confirmed_learnings_are_embedded_and_reused_within_the_workspace`.

## Boundaries

- Interface steps are proven on simulated responses; authentication, backend
  authorization and persistence are proven by the integration tests named above.
- A live analysis verdict is the operator's demo act; its shape is pinned by the
  recorded evals, and its quality by the comparative evals tracked in #77.
