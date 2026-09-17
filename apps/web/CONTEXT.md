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

**Converge**:
The section at `/workspace/decision-spaces/[spaceId]/converge` where the map of the Space's confirmed Contributions is read and corrected by a human: the Relations between them, the Clusters a human decided, and the unclustered material. What the map shows is what a human last asserted; nothing is inferred.
_Avoid_: AI clustering, auto-aggregation, whiteboard, canvas

**Relation**:
A typed link a human asserts between two confirmed Contributions, one of SUPPORTS, CONTRADICTS, DUPLICATES, ALTERNATIVE_TO, DERIVED_FROM, SUPERSEDES, EVIDENCE_FOR or EVIDENCE_AGAINST. A directed pair carries at most one Relation, and a Contribution never relates to itself.
_Avoid_: Edge, link (alone), similarity

**Cluster**:
A group of confirmed Contributions whose grouping a human decided. A Contribution belongs to one Cluster at a time: assigning it moves it. Deleting a Cluster keeps its members.
_Avoid_: Category, theme, folder, bucket

**Options**:
The section at `/workspace/decision-spaces/[spaceId]/options` where the viable paths the team is considering are listed, written and edited, each carrying its proposal, its mechanism, its cost, its risks, its critical assumptions and its success metrics, and linking the Space's confirmed Contributions as evidence for or against. Nothing here scores, ranks or rates an Option.
_Avoid_: Shortlist, candidates, scoring matrix, comparison table

**Option**:
One viable path a member wrote for a Decision Space: a title and a proposal that are required, and six narrative fields (mechanism, upside, cost, risks, critical assumptions, success metrics) that are optional and stay absent when left out rather than becoming an empty answer.
_Avoid_: Idea, proposal, variant, hypothesis

**Option evidence**:
A confirmed Contribution of the same Space, linked to an Option on the `for` or `against` side by a member. Linking asserts nothing new about the Contribution: it says which Option that Contribution speaks to, and on which side.
_Avoid_: RATING, score, weight, confidence
