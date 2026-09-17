# API

The FastAPI backend. Owns all Kollio domain state: ideas, their versioned history, constraint analyses, the company context, teams, and the private-workspace boundary. The agent graphs (LangGraph) and their Taskiq workers also live here.

## Vocabulary in transition

`docs/00-project-overview.md` §20 re-points this domain over several steps. The Idea, Iteration, Branch, Proposal, ConstraintAnalysis, RealismScore and Embedding sections below describe today's shipped product; the Decision spaces section describes the parent object that steps 3 to 8 attach them to or replace. Read them as a sequence, not as coexisting targets: step 3 maps Ideas into Branches and Contributions, step 8 re-parents Outcome and Learning onto the Decision → Experiment → Outcome → Learning chain, and the matching vocabulary is frozen rather than extended.

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
