# API

The FastAPI backend. Owns all Kollio domain state: ideas, their versioned history, constraint analyses, the company context, teams, and the private-workspace boundary. The agent graphs (LangGraph) and their Taskiq workers also live here.

## Vocabulary in transition

`docs/00-project-overview.md` §20 re-points this domain over several steps. The Idea, Iteration, Branch, Proposal, ConstraintAnalysis, RealismScore and Embedding sections below describe today's shipped product; the Decision spaces section describes the parent object that steps 3 to 8 attach them to or replace. Read them as a sequence, not as coexisting targets: step 3 mapped Ideas into Branches and Contributions (see Exploration branches below), step 4 added the converge map, step 5 added Options (see Options below), and its Challenge half added the structure the Critic writes into (see Challenge below), step 6 added the Decision Record (see Decision records below), step 7 added scenario analysis with a deterministic sensitivity read (see Scenario analysis below), step 8 linked experiments to spaces so a Space reaches its own Outcomes and Learnings while the initiative path stays intact (see Experiment loop and the space link below), and the matching vocabulary is frozen rather than extended.

## Language

### The idea as a repository

**Idea**:
The living deposit of a project: title, pitch, owner, stage, and original language.
_Avoid_: Project, startup, repo (in user-facing text)

**Initiative**:
What an Idea is called in user-facing B2B text. Same object as Idea; the split is deliberate: code, DB and API always say Idea, UX always says Initiative.
_Avoid_: Idea (in user-facing B2B text)

**InitiativeType**:
The closed kind of an Initiative, set by the owner at deposit and editable after: idea, hypothesis, campaign, opportunity, decision, experiment, pricing, market, partnership, internal improvement.
_Avoid_: Free-text type, tag, category

**Stage**:
Where an idea stands: `seed`, `iterating`, or `team_formed`.
_Avoid_: Status, phase

**Owner**:
The user who deposited the idea and accepts or rejects proposals.
_Avoid_: Founder, creator, porteur (in code and English prose)

### Versioned history

**Iteration**:
One traced change to an idea: author, timestamp, message, parent, short hash. History is append-only.
_Avoid_: Commit (in user-facing text), version, edit, update

**Branch**:
A named line of iterations diverging from `main`, used to explore without touching the main line.
_Avoid_: Fork, copy

**Proposal**:
An iteration on a branch awaiting the owner's decision: `pending`, `accepted`, or `rejected`. Accepting merges it onto `main`.
_Avoid_: Pull request (in user-facing text), suggestion, PR

**Rollback**:
A new iteration pointing back at an earlier parent, restoring a previous state without rewriting history.
_Avoid_: Undo, revert, restore

### Company context

**CompanyContext**:
The durable reality of a workspace: its profile, objectives, constraints, principles and key metrics. Analyses read profile, objectives and constraints today; principles and metrics are stored and edited but not yet injected.
_Avoid_: Company knowledge base, memory, company settings

**CompanyProfile**:
The company's identity: name, description, business model, products or services, customer segments, markets and structure (size and shape).
_Avoid_: About page, company card

**Objective**:
A stated company goal, `active` or `archived`, optionally marked priority.
_Avoid_: Goal (as a vague noun), KPI

**CompanyConstraint**:
A real limitation the company operates under: budget, team size, skills, deadlines, regulation, capacity, brand or product dependencies. `active` or `archived`.
_Avoid_: Constraint (reserved for the analysis dimensions below), blocker

**Principle**:
A stated intent or an explicitly refused item the company judges decisions against (vision, positioning, priorities, non-negotiables). `active` or `archived`.
_Avoid_: Value, rule (as an engine term), constraint

**KeyMetric**:
A simple tracked number the company references without a BI system: a name with optional value, unit, observed date and source.
_Avoid_: KPI, Outcome (the experiment result), measure

### The constraint killer

**ConstraintAnalysis**:
The agent-produced verdict on an idea at one iteration: a realism score plus five scored constraints with short notes. Recomputed on every major iteration, historized per iteration.
_Avoid_: Score alone, audit, review

**RealismScore**:
A 0-100 number summarizing how grounded an idea is. Always explained evidence, never a decorative number.
_Avoid_: Rating, grade

**Constraint**:
One of the five fixed analysis dimensions: `concurrence`, `cout`, `temps`, `defendabilite`, `acquisition`. Each carries a score and a short note.
_Avoid_: Criterion, metric, custom dimensions

### Team and moat flow

**IdeaMembership**:
One user's place on an idea's team, with a real-world role. An accepted proposal can create one.
_Avoid_: Assignment, seat

**Participation**:
How a person stands in an initiative's loop: `owner`, `decision_maker`, `contributor`, `observer`. The owner accepts members into the loop; `owner` is implicit and never granted.
_Avoid_: Seat, seniority

**BusinessFunction**:
What a person brings to an initiative, from a closed list: `marketing`, `sales`, `finance`, `product`, `engineering`, `customer_success`, `operations`, `legal`, `hr`, `data`, `direction`, `other`.
_Avoid_: Craft role, job title, skill (as a job label)

**SoughtFunction**:
A business function an initiative is still looking for, shown in the explorer.
_Avoid_: Open position, vacancy, hiring

**Contribution**:
A recorded act that moves an idea forward: evidence, a proposal, execution capacity.
_Avoid_: Comment alone, activity (as a generic event)

**Outcome**:
A measured result attached to an idea. Rare and precious: it is the moat's training signal.
_Avoid_: Result (as a vague noun), KPI

**Momentum**:
The visible activity signal of an idea: iteration count, contribution graph, followers.
_Avoid_: Élan (in code and English prose), hype, traction

### Visibility and matching

**Workspace**:
A private team area. An idea with a workspace is private to it; an idea without one is public.
_Avoid_: Organization, tenant (in user-facing text)

**Follow**:
An observer's subscription to an idea's progress. Following never grants edit rights.
_Avoid_: Subscribe, watch, like

**Embedding**:
The multilingual vector of an idea, user, or contribution, stored in pgvector. French content matches English profiles through it.
_Avoid_: Translation (as stored data), vector alone

### Decision spaces

**DecisionSpace**:
The central object of Kollio: one question a workspace commits to converging on, owned by a person and worked by participants through a fixed lifecycle. Workspace-scoped, never public.
_Avoid_: Idea (once step 3 lands), project, thread, discussion, ticket

**DecisionSpaceParticipant**:
A workspace member who works a decision space. The owner is a participant by construction and can never be removed from their own space.
_Avoid_: Member (the workspace role), assignee, watcher

**DecisionSpaceStatusEvent**:
One append-only status change on a decision space: from, to, actor, optional reason, timestamp. Ordered by an internal monotonic `seq`, never updated and never deleted; the stored status is a projection of the last event.
_Avoid_: Log entry, audit row, history item

**Decision space status**:
The closed lifecycle: `OPEN`, `EXPLORING`, `CONVERGING`, `READY_TO_DECIDE`, `DECIDED`, `TESTING`, `LEARNED`, `REOPENED`. Forward edges only, except reopening (`DECIDED`/`TESTING`/`LEARNED` → `REOPENED`, reason required) and resuming (`REOPENED` → `EXPLORING`). Anything else is refused and writes nothing.
_Avoid_: Stage (reserved for an Idea), phase, state

**Decision space deadline**:
An optional date carried on a space for information only. It gates no transition and skips no state.
_Avoid_: Due date (as a trigger), SLA, expiry

### Exploration branches

**Branch** (exploration container):
A private or shared container of raw material under a Decision Space: notes, AI outputs, URLs, documents, research and artifacts. Private reads only for its creator; shared reads for Space readers; writes follow the Space rule (owner plus participants). A mapped Idea's title, pitch and iteration history become a shared Branch's raw material through an explicit source link, without duplication. Raw material is never canonical.
_Avoid_: Branch (the iteration line under Versioned history) without qualification, folder, project

**Contribution** (canonical unit):
An atomic canonical unit proposed from Branch material: `idea`, `claim`, `evidence`, `objection` or `constraint`. `suggested` by AI until a human confirms it; `confirmed` by a human is canonical and will feed Converge. Carries author, Branch, source, tool/model when known, timestamp and transformation history.
_Avoid_: Contribution (the participation record under Team and moat flow), comment alone

### Challenge

**ChallengeRun**:
One attempt at challenging one Option against the six checks of §7. Carries a closed status - `OPEN`, `RUNNING`, `COMPLETED`, `FAILED` - and the model that produced its findings, null until the Critic runs. Every run belongs to an Option inside a Space, and is never reachable outside it.
_Avoid_: Review, audit, test run

**ChallengeFinding**:
One recorded objection on a run: a kind, a severity, the detail statement, an origin and a status.
_Avoid_: Comment, issue, critique note

**Challenge kind**:
The six checks of §7, a closed set: `unsupported_assumption`, `contradictory_evidence`, `hidden_dependency`, `failure_mode`, `causal_claim`, `missing_success_criteria`. A seventh check is a change to §7, not a runtime value.
_Avoid_: Category, type, label

**Finding origin and status**:
A finding a human records is `confirmed` on arrival (origin `human`); a finding the Critic proposes arrives `proposed` (origin `critic`) and waits for a human to confirm or dismiss it. Dismissal is permanent and keeps the record: "we looked at this and it does not hold" is convergence data, not a deletion.
_Avoid_: Approved/rejected (reserved for proposals), deleted

**Challenge coverage**:
Which of the six checks carry at least one non-dismissed finding. Information only: it gates no transition, blocks no Decision and produces no score.
_Avoid_: Score, completeness rating, gate

**Critic**:
The component that will propose Challenge findings automatically: unsupported assumptions, contradictory evidence, hidden dependencies, failure modes, causal claims and missing success criteria. **Not built.** `service/ports.py` declares the gateway it will implement; the API never lets a client declare a `critic` origin, and nothing ranks or scores an Option while it is absent.
_Avoid_: Reviewer, analyst, score, verdict, rating

### Converge map

**ContributionRelation**:
An explicit directed link between two confirmed Contributions of one Space, typed by the closed set `SUPPORTS`, `CONTRADICTS`, `DUPLICATES`, `ALTERNATIVE_TO`, `DERIVED_FROM`, `SUPERSEDES`, `EVIDENCE_FOR`, `EVIDENCE_AGAINST`. One relation per ordered pair; no self-relation; both ends must belong to the same Space. Asserted and removed by the Space's writers; human corrections are the map until the AI proposer arrives.
_Avoid_: Implicit similarity, tag, comment thread

**Cluster**:
A titled grouping of Contributions inside one Space for the map. A Contribution sits in at most one Cluster; assigning moves it; deleting a Cluster ungroups its members without deleting them.
_Avoid_: Folder, category, label

**Converge map**:
The read model of a Space's reasoning: its confirmed Contributions (suggested ones stay out), every relation between them, and every Cluster with its member ids. Readable by workspace members; writers build and correct it by hand.
_Avoid_: Report, summary, AI output

### Options

**Option**:
One alternative a Decision Space may choose between, built from the §7 fields: a title, the proposal, and mechanism, upside, cost, risks, critical assumptions and success metrics. Workspace-scoped, reachable only through its Decision Space. It carries no score, no rank and no computed verdict, by design.
_Avoid_: Alternative (the relation type), scenario (a simulated variant), plan, draft

**OptionEvidence**:
A link from an Option to a *confirmed* Contribution, on the `for` or `against` side. Evidence is linked rather than asserted, so an Option cannot claim support no Contribution backs. The same Contribution may support one Option and contradict another.
_Avoid_: Evidence (the Contribution kind), citation, note

### Decision records

**Decision** (record):
The committed choice of a Decision Space, committed from `READY_TO_DECIDE`: the selected Option, the rationale, the critical assumptions, the unresolved uncertainty, the success criteria and the revisit triggers. Append-only and versioned per Space; committing moves the Space to `DECIDED` through the existing lifecycle edge, and reopening then re-deciding writes the next version.
_Avoid_: DecisionSpace (the container), choice, plan

**Decision version**:
One row of a record's history, numbered from 1. Never updated and never deleted; a Space's current record is its highest version.
_Avoid_: Revision, edit, draft

**Decision alternative**:
An Option the record explicitly did not take. Recorded per decision, which is why an Option carries no status of its own.
_Avoid_: Runner-up, loser

**Decision argument**:
A link from a record to a *confirmed* Contribution of the same Space, on the `for` or `against` side. One Contribution argues one way on one decision: citing it both ways is refused.
_Avoid_: OptionEvidence (which argues about an Option), quote, citation

**Revisit trigger**:
A structured reason to come back: a required metric, with an optional direction (`above` or `below`), threshold and note. A metric alone is a legitimate reminder. Informational only: it gates nothing and produces no score.
_Avoid_: Alert, KPI, expiry

### Scenario analysis

**ScenarioVariable**:
A space-scoped quantity two Options can be compared on: a name (unique per space), an optional unit and a declared `low`/`base`/`high` range in that order. Space-scoped rather than Option-scoped, because two Options compared on the same metric must share its definition.
_Avoid_: Parameter, input, driver, assumption

**ScenarioRun**:
One level of an Option's simulation: `optimistic`, `base`, `pessimistic` or `failure`, carrying its explicit assumptions and one numeric value per variable. At most one `base` run per Option. A run that omits the metric is reported as incomplete and is never averaged in.
_Avoid_: Scenario (the level), case, variant, projection

**Sensitivity**:
The answer to what would change the preference, computed by scanning the declared points: per variable, the interval where the criterion flips plus the interpolated crossing, or `beyond_declared_range` with the direction the metric travels, or `insufficient_points`. Variables rank by the largest absolute implied slope. Informational: it gates nothing and never returns a predicted value.
_Avoid_: Forecast, prediction, projection, estimate

### Experiment loop and the space link

**Experiment**:
A real-world test run after a choice: a title, a hypothesis, a success metric and an optional baseline and target. An experiment belongs to an Idea (its original home) and MAY also carry a `decision_space_id` and an `option_id`, which is what lets a Decision Space reach its own Outcomes and Learnings. The link is additive: an unlinked experiment behaves exactly as before, and a linked one keeps its initiative path too.
_Avoid_: Test (too vague), trial, simulation (which is `ScenarioRun`)

**ExperimentOutcome**:
One recorded result of an experiment: a metric, a value, an optional unit and observed date, plus a comment or qualitative note.
_Avoid_: Result (as a vague noun), measurement, KPI

**Learning**:
The human-confirmed knowledge an experiment produced: a text a person confirms, and which never returns to draft. Confirmation embeds it for reuse and its provenance carries the workspace, the idea and the experiment. A Learning is reached through its experiment, never directly from a Space.
_Avoid_: Insight, takeaway, conclusion

**Experiment space link**:
The optional pair a Decision Space sees its tests through. An `option_id` is only ever set together with a `decision_space_id`, both ends belong to the idea's workspace, and the option must belong to that space. Deleting a Space or an Option nulls the link rather than destroying experiment history. No backfill: inferring a space for an existing experiment would invent a decision nobody made.
_Avoid_: Parent (the idea is still the parent), re-parent, migration link
