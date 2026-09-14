# API

The FastAPI backend. Owns all Kollio domain state: ideas, their versioned history, constraint analyses, teams, and the private-workspace boundary. The agent graphs (LangGraph) also live here.

## Language

### The idea as a repository

**Idea**:
The living deposit of a project: title, pitch, owner, stage, and original language.
_Avoid_: Project, startup, repo (in user-facing text)

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

### The constraint killer

**ConstraintAnalysis**:
The agent-produced verdict on an idea at one iteration: a realism score plus five scored constraints with short notes. Recomputed on every major iteration, historized per iteration.
_Avoid_: Score alone, audit, review

**RealismScore**:
A 0-100 number summarizing how grounded an idea is. Always explained evidence, never a decorative number.
_Avoid_: Rating, grade

**Constraint**:
One of five fixed dimensions: `concurrence`, `cout`, `temps`, `defendabilite`, `acquisition`. Each carries a score and a short note.
_Avoid_: Criterion, metric, custom dimensions

### Team and moat flow

**IdeaMembership**:
One user's place on an idea's team, with a real-world role. An accepted proposal can create one.
_Avoid_: Assignment, seat

**TeamRole**:
What a member actually does: `designer`, `dev`, `commercial`, `growth`, and other everyday roles. The owner accepts members into the loop.
_Avoid_: Title, job, skill (as a job label)

**SoughtRole**:
A team role the idea is still looking for, shown in the explorer.
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
