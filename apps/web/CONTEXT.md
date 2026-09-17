# Web

The Nuxt application. The product surface where owners deposit ideas, contributors join the loop, and observers browse progress. Renders domain concepts owned by the API; invents none.

## Language

**Explorer**:
The discovery feed of ideas, filterable by stage, sought role, and domain. Where a contributor finds an idea to join.
_Avoid_: Feed alone, marketplace, directory

**IdeaDetail**:
The screen that tells an idea's full story at a glance: current state, constraints, timeline, and team.
_Avoid_: Idea page, profile (for an idea)

**Initiative**:
The user-facing B2B word for an Idea, with its InitiativeType. The API glossary is canonical: the web never invents a second meaning.
_Avoid_: Idea (in user-facing B2B text)

**Deposit**:
The act of submitting a new idea through the form. The constraint killer runs live during it.
_Avoid_: Creation, submission (as a cold form), post

**Timeline**:
The visible, append-only history of an idea's iterations, including branches and proposal states.
_Avoid_: Changelog, log, history (as a vague noun)

**Companion**:
The AI surface that clarifies, compares, and structures decisions next to an idea. Its outputs stay inspectable.
_Avoid_: Chatbot, assistant (as a generic chat), agent (in user-facing text)

**WorkspaceArea**:
The private section of the app showing ideas belonging to the member's workspace, isolated by default.
_Avoid_: Dashboard, admin panel

**Observer**:
A signed-in user who follows or comments without team membership.
_Avoid_: Visitor, lurker, fan

**DecisionSpaces**:
The list at `/workspace`: the questions the workspace must settle, each with its owner, status, deadline and participants, plus the form that opens a new one. The idea Explorer lives one level below at `/workspace/ideas`.
_Avoid_: Home, dashboard, feed

**SpaceShell**:
The frame of one Decision Space at `/workspace/decision-spaces/[spaceId]`: the question, its facts and its status, the six section routes (Explore, Converge, Options, Decision, Experiment, Learning) and the transitions the lifecycle permits from the current status. A section whose capability has not shipped says what will live there.
_Avoid_: Tabs (the sections are routes, each addressable), detail page, workspace

**Branch**:
A container of raw exploration material inside one Decision Space, private to its creator or shared with the Space. Nothing in a Branch counts as the Space's reasoning until a Contribution is proposed from it and a human confirms it.
_Avoid_: Thread, draft, note, document

**Contribution**:
An atomic piece of reasoning promoted from Branch material into the Space's shared reasoning: an idea, a claim, evidence, an objection or a constraint. It carries its author, Branch, source, tool/model and timestamp.
_Avoid_: Post, comment, card, item

**Explore**:
The section at `/workspace/decision-spaces/[spaceId]/explore` where each participant explores independently, proposes Contributions from their Branch, and sees which Contributions are confirmed and which wait for a human.
_Avoid_: Brainstorm, ideation, feed
