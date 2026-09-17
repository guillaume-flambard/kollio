## Context

`docs/00-project-overview.md` §9 describes two levels and one output.

- Level 1: optimistic, base, pessimistic and failure scenarios, with explicit Assumptions.
- Level 2: editable quantitative ranges. Its example is a marketing chain (budget, CPM, CTR, CPC, conversion, CAC, order value, revenue, margin).
- The useful output is not "Campaign B will make €42,183" but "Campaign B becomes preferable if CTR exceeds X while conversion remains above Y; conversion is the highest-impact variable with the weakest Evidence".

§9 also defers, explicitly, "probabilistic models, Monte Carlo where justified, workspace priors and validated narrow predictive models".

The hard part is the third bullet. A product that computes a number has to own a model of the business, and §9 forbids pretending it has one. This design therefore computes only what declared scenarios already imply, and says so.

## Domain model

`ScenarioVariable` belongs to a Decision Space: the quantities a decision turns on, with their editable ranges.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the privacy boundary |
| `name` | text, required | trimmed, non-empty; unique per Space, so a metric cannot be defined twice |
| `unit` | text, optional | `€`, `%`, `visits`; free text, informational |
| `low`, `base`, `high` | numeric, required | the editable range; `low <= base <= high` |
| `lang` | code, required | language of the last write, as everywhere |
| `created_at`, `updated_at` | timestamps | platform convention |

`ScenarioRun` belongs to an Option, because §20 step 7 puts simulation under Options and an Option is the thing a scenario compares.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `option_id` | reference, required | stays inside the Option's Space |
| `level` | closed value | `optimistic`, `base`, `pessimistic`, `failure` |
| `assumptions` | text, required | trimmed, non-empty: §9 says explicit Assumptions, and a scenario without them is a guess |
| `lang` | code, required | |
| `created_by` | reference, required | |
| `created_at`, `updated_at` | timestamps | |

`ScenarioRunValue` declares one variable's value in one run: `(run_id, variable_id)` unique, `value` numeric.

One `base` run per Option is enforced, because the base case is the reference point the others are read against; the other three levels may repeat or be absent.

## The sensitivity read

This is the whole point of the slice, so the algorithm is stated exactly.

Inputs: an Option, one of its runs designated by the caller as the criterion's carrier — actually the criterion is supplied by the caller: a `metric` (a variable of the Space), a `direction` (`above` or `below`) and a `threshold` (a number). All runs of the Option must declare a value for that metric; runs that do not are reported as `incomplete` and excluded from the computation, never silently averaged.

Per every other variable `V` of the Space:

1. Take the pairs of runs of this Option that declare both `V` and the metric, ordered by `V`'s value.
2. For each adjacent pair `(a, b)`, the criterion is `m - threshold` for `above`, `threshold - m` for `below`. If the sign changes between `a` and `b`, the criterion flips inside that interval: interpolate linearly and report `[v_a, v_b]` **as an interval, plus the interpolated crossing point**.
3. If more than one adjacent pair flips, report the narrowest interval and how many pairs flipped — more than one crossing means the declared points do not describe a single threshold, which the reader must know.
4. If no pair flips, report `beyond_declared_range` with the direction the metric travels as `V` grows. Reporting "no crossing in the declared range" is a real answer and is more useful than a fabricated one.
5. With fewer than two declaring runs, report `insufficient_points`.

Then:

- **Impact** per variable: the implied slope over each adjacent pair, `(Δmetric) / (ΔV)`, reported as a range (min, max). Variables are ranked by the largest absolute slope. This is the documented meaning of "highest-impact variable": a declared-points slope, not a fitted model.
- **Evidence** on the Option: counts of confirmed Contributions linked as `for` and as `against`, plainly reported. The design does **not** attribute Evidence to a variable: nothing in the data model says which variable a Contribution is about, and inventing that link would be exactly the kind of unsupported claim §21 forbids. §9's pairing of "highest impact" with "weakest Evidence" becomes answerable to a reader who sees both, and becomes attributable only in a later slice that lets a Contribution name a variable. That limitation is stated in the response rather than hidden.

The read returns no single predicted number, and the response schema has no field that could carry one.

## Permissions

Inherited from the Space, exactly as Options and Challenge do: any member reads, owner and participants write, everyone else receives the workspace-not-found treatment.

## Boundary

A new vertical module `apps/api/src/modules/scenarios/` following the platform's lightweight hexagonal seam:

- `domain/` — the pure range rule (`low <= base <= high`, non-blank names), the run rule (known level, non-blank assumptions, at most one `base` per Option) and the sensitivity computation itself. No I/O, under strict Mypy, unit-tested with no database. The computation is pure and decimal, so the tests are exact rather than tolerant.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/` — orchestration: variables, runs, values and the sensitivity read.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints.

## Persistence

One Alembic migration adding three tables:

- `scenario_variables` — cascade from the Space, unique `(space_id, name)`, a range check `low <= base <= high`, closed `lang`.
- `scenario_runs` — cascade from the Option, closed `level`, a `btrim` assumptions check, and a partial unique index enforcing one `base` run per Option.
- `scenario_run_values` — unique `(run_id, variable_id)`, cascade from the run and from the variable, numeric values.

Facts proved on disposable PostgreSQL, not in the browser: cross-workspace and cross-Space isolation by identifier, the non-member refusal on every operation, that a refused run writes nothing, and that a value must belong to the run's Space.

## Deliberately out of scope

- Probabilistic models, Monte Carlo, workspace priors and validated predictive models — §9 defers all four explicitly.
- Any LLM: the Scenario Analyst (§13) and the Critic remain declared debts. This slice is deterministic.
- The Option's own numbered fields already ship; nothing here re-reads them.
- Any user interface.
- Attributing Evidence to a variable, for the reason stated in the sensitivity section.

## Open questions

- Should a variable be Option-scoped rather than Space-scoped? Space scope was chosen because two Options compared on the same metric must share its definition; if Options ever need private variables, that is a separate decision.
- Should `failure` scenarios participate in the sensitivity read? They do today, because a failure case is a declared point like any other; if a failure scenario means "the plan is void" rather than "the metric moved", it should be excluded, and that is a product call worth making when the first real use appears.
