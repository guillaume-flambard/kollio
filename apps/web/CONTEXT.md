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
