# 00 — KOLLIO · PRD / PRODUCT BLUEPRINT v1.0 — Pivot: Collaborative Decision Intelligence — September 2026

## 1. NORTH STAR

Kollio turns fragmented human + AI work into shared, traceable, testable decisions, then learns from what actually happened.

Core loop: Explore -> Converge -> Challenge -> Decide -> Test -> Learn.

Visible journey: three moments, and only three, are what a new team member is asked to learn.

1. Frame the decision. The question, its owner, the participants and the material they bring. Explore and Converge serve this moment: Branches hold raw material, promoting a Contribution makes it canonical, and the convergence map shows where people agree, conflict, or still need evidence.
2. Choose with reasons. Options, the evidence and assumptions behind them, what would make the team regret the choice, and the Decision Record that keeps the rejected alternatives and the revisit triggers.
3. Record what happened. The Experiment, the observed Outcome against what was expected, and the Learning a human confirms.

Branches, Contributions, relations, clusters and scenario variables are support mechanics. They stay available on demand, and they are never a vocabulary a beginner has to learn before starting.

Kollio is no longer primarily an idea manager. Existing ideation becomes the Explore layer of a broader decision-intelligence product.

Product definition:
- Transform scattered human and AI thinking into clear team decisions.
- Make options, disagreements, assumptions and reasons visible instead of accumulating chats and files.
- Connect decisions to outcomes so the organization builds reusable memory of what worked, failed and why.

Kollio is NOT a ChatGPT/Claude replacement, generic shared chat, brainstorming whiteboard, universal idea scorer, project-management suite or prediction oracle.

## 2. PROBLEM

AI accelerates individual work but fragments collective thinking. People explore the same problem in ChatGPT, Claude, documents, Slack or Notion. Teams then pay a convergence tax: reconstructing state, reconciling versions, finding duplicate work, exposing contradictions and assumptions, comparing alternatives, recording why a decision was made and learning from its result.

Initial wedge: marketing, growth, product, innovation and strategy teams of roughly 3–15 people already using AI heavily.

## 3. CORE DOMAIN MODEL

The central object is a Decision Space, not an Idea.

Workspace: team boundary. Decision Space: one question requiring convergence. Branch: private/shared exploration. Contribution: atomic idea, claim, evidence, objection or constraint promoted into shared reasoning. Option: viable path. Assumption: something that must be true. Evidence: support or contradiction. Decision: committed choice + rationale + uncertainty + revisit triggers. Experiment: real-world validation. Outcome: observed result. Learning: human-confirmed reusable knowledge.

State: OPEN -> EXPLORING -> CONVERGING -> READY_TO_DECIDE -> DECIDED -> TESTING -> LEARNED. A Decision can be REOPENED by new evidence, outcomes or predefined triggers. Committed history is versioned and append-only.

## 4. UX

HOME = Decision Inbox. It answers “What needs my attention?”

Sections:
- Needs convergence.
- Needs my input.
- Ready to decide.
- Needs learning.
- Relevant prior memory.

The first four have answers today. The fifth does not yet: the convergence map is built and corrected by hand, no retriever surfaces past lessons, and the inbox itself says that this question has no answer today.

DECISION SPACE: Header: question, owner, status, deadline, participants. Navigation: Explore / Converge / Options / Decision / Experiment / Learning. Main canvas: structured work, never merely a giant chat transcript. Intelligence rail: contradictions, assumptions, missing evidence, related past Decisions. Collaboration layer: comments, proposals, reviews, provenance and history.

## 5. EXPLORE

Preserve current Kollio ideation here. Users create private/shared Branches containing notes, AI outputs, URLs, documents, research and artifacts. They may continue using ChatGPT, Claude and other tools.

Raw Branch content is not canonical. “Propose to shared space” converts selected material into Contributions. AI can suggest promotion; a human confirms it. Preserve author, Branch, original source, tool/model when known, timestamp and transformation history.

## 6. CONVERGE — FLAGSHIP DIFFERENTIATOR

Converge creates a live map of collective reasoning.

Detect:
- Agreements: independent contributions reinforcing each other.
- Conflicts: incompatible claims/assumptions.
- Alternatives: distinct approaches that should remain separate.
- Unknowns: missing information capable of changing the Decision.
- Assumption hotspots: high-impact beliefs with weak Evidence.
- Duplicate work.

Critical rule: NEVER collapse meaningful disagreement into one bland AI summary. Compatible thinking may MERGE. Incompatible thinking should FORK.

Humans can correct clusters, merge/split Contributions, mark false contradictions, request Evidence, challenge Assumptions and promote Alternatives into Options. AI suggests structure; human-corrected structure becomes canonical.

## 7. OPTIONS + CHALLENGE

Every Option contains: Proposal; Mechanism; Upside; Cost; Risks; Critical Assumptions; Evidence For; Evidence Against; Success Metrics.

Do not create a fake universal AI score. Make trade-offs inspectable.

Before commitment, Critic checks unsupported assumptions, contradictory evidence, hidden dependencies, failure modes, causal claims and missing success criteria. Core question: “What could make us regret this Decision?”

## 8. DECIDE

Decision Record:
- selected Option;
- rejected Alternatives;
- strongest arguments for/against;
- critical Assumptions;
- unresolved uncertainty;
- owner/reviewers;
- success criteria;
- revisit triggers.

A Decision Record must make sense six months later without reopening original AI chats.

## 9. SIMULATION / SCENARIOS

Initial promise = scenario analysis, NOT prediction.

Level 1: optimistic/base/pessimistic/failure scenarios with explicit Assumptions. Level 2: editable quantitative ranges. Marketing example: budget, CPM, CTR, CPC, conversion, CAC, order value, revenue, margin.

The useful output is not “Campaign B will make €42,183.” It is “Campaign B becomes preferable if CTR exceeds X while conversion remains above Y; conversion is the highest-impact variable with the weakest Evidence.”

Later only: probabilistic models, Monte Carlo where justified, workspace priors and validated narrow predictive models.

## 10. TEST -> OUTCOME -> LEARN

Experiment fields: hypothesis, selected Option, owner, budget, duration, baseline, primary metric, guardrails, expected range, success threshold, stop condition.

After execution compare Expected vs Observed. Identify which Assumptions were right/wrong and why. AI proposes a Learning; human confirms it.

Long-term loop: Decision -> Experiment -> Outcome -> Learning -> Future Decision.

## 11. ORGANIZATIONAL MEMORY

Memory units are Decisions, Assumptions, Outcomes, confirmed Learnings and reusable Evidence — not generic chat history.

When a new Decision appears, the ambition is that Kollio surfaces relevant past lessons and explains WHY they are relevant, with provenance. That retriever is not built yet: today a confirmed Learning lives with its Decision Space, and a person has to bring it forward by hand.

## 12. COLLABORATION

Personal Branch: private exploration. Shared Branch: subgroup exploration. Proposal: submit to canonical reasoning. Review: support/challenge/comment/request Evidence. Merge: combine compatible Contributions with provenance. Fork: preserve incompatible interpretations. Approval: optional governance.

Kollio supports individual divergence + collective convergence.

## 13. AI ARCHITECTURE

AI = facilitator + structurer + critic, not oracle.

Structurer: extract Contributions/Assumptions/Evidence/Options. Convergence Engine: detect duplicates/agreements/alternatives/contradictions. Critic: find weak assumptions and failure modes. Decision Editor: concise briefs preserving dissent. Scenario Analyst: scenario/sensitivity modeling. Memory Retriever: relevant prior Decisions/Learnings. Learning Analyst: compare expectations with Outcomes.

Trust:
- trace AI structure to sources;
- never fabricate consensus;
- never silently modify committed Decisions;
- expose uncertainty;
- human confirmation for canonical promotion, Decisions and Learnings;
- remain model/provider independent.

## 14. INTEGRATIONS

MVP: text, URLs, documents, AI-chat exports. Next: browser capture, Slack, Notion, Google Drive with backlinks. Later: native AI-workspace connectors where APIs permit. Exports: Decision Brief, Experiment Brief, Learning Memo, read-only Decision page.

## 15. MVP

Shipped (the canonical behaviours live in `openspec/specs`):
- [x] Decision Space
- [x] Multiple contributors
- [x] Independent Branches
- [x] AI/imported exploration
- [x] Contribution promotion + provenance
- [x] Converge: agreements/conflicts/alternatives/unknowns/assumptions/duplicates
- [x] Human correction of convergence
- [x] Structured Options
- [x] Challenge
- [x] Versioned Decision Record
- [x] Revisit triggers
- [x] Editable Scenario comparison
- [x] Experiment
- [x] Outcome
- [x] Confirmed Learning
- [x] End-to-end history
- [x] The decision inbox that says what needs attention
- [x] Members, business functions and participation roles
- [x] French and English, on the Living Canvas tokens

In validation, and the only milestone that matters now: one real Decision taken by two people in their own words, an observed Outcome within the following days, and a voluntary return for a second Decision. This milestone requires no new integration and no feature expansion, only real use of the loop that already ships.

Quality, measured 2026-09-19 on commit `710a707` whose CI passes: 322 browser tests in 21 files run against simulated API responses, so they prove rendering and not authentication, persistence or provider quality; 557 API tests pass without a database, 239 integration tests need a migrated throwaway PostgreSQL, and 2 provider tests are live, opt-in and budgeted; the FR/EN catalogs match at 1013 keys and the guard checks both directions.

Deferred: browser extension; Slack/Notion/Drive; semantic Decision/Learning retrieval; templates; notifications; revisit alerts; analytics. Automatic structuring of raw material and the memory retriever behind the inbox's fifth question belong here too: today the convergence map is built and corrected by hand, and the inbox itself says that question has no answer yet.

Out of scope now: generic PM, full AI-chat replacement, social feed, marketplace, autonomous campaign execution, predictive-accuracy claims, complex enterprise governance, vanity scoring.

## 16. JULIE / FAKTUS VALIDATION

Use one REAL marketing Decision, not “Do you like Kollio?”

17. Pick a live Decision with >=2 plausible paths.
18. Julie + another participant explore independently using normal AI tools.
19. Bring useful outputs into separate Branches.
20. Promote Contributions.
21. Run Converge.
22. Inspect/correct Agreements, Conflicts, Assumptions and missing Evidence.
23. Create + Challenge Options.
24. Make the real Decision in Kollio.
25. Record Scenario ranges + success criteria.
26. Execute.
27. Capture Outcome + Learning.

Strong signals: missed conflict discovered; implicit Assumption exposed; less manual recap; real Decision committed in Kollio; team returns for second Decision; prior Learning later affects another Decision. Warning: generic summary, administrative overhead, Decision happens elsewhere, no repeat use.

## 17. SUCCESS METRICS

North-star candidate: Decision Spaces completing Decide -> Outcome/Learning whose Learning is later reused by another Decision Space.

Supporting: activation with >=2 contributors; convergence completion; time to Decision; Decisions with Assumptions/revisit triggers; Outcome capture; repeat Decision Spaces; Learning reuse; human correction rate of AI convergence.

## 18. TECHNICAL MODEL

Entities: Workspace, User, Membership, DecisionSpace, Branch, Contribution, ContributionRelation, Cluster, Option, Assumption, Evidence, DecisionVersion, Experiment, ScenarioVariable, ScenarioRun, Outcome, Learning, Source, Comment, Review.

Relations: SUPPORTS, CONTRADICTS, DUPLICATES, ALTERNATIVE_TO, DERIVED_FROM, SUPERSEDES, EVIDENCE_FOR, EVIDENCE_AGAINST.

Rules:
- structured canonical objects separate from raw content;
- version Decisions;
- relationships stored explicitly, not only embeddings;
- embeddings discover candidate relationships;
- human corrections become durable data;
- expensive AI runs asynchronously/incrementally;
- cache convergence artifacts;
- observe model/provider/prompt/latency/cost;
- provenance and permissions are first-class.

## 19. AI PIPELINE / COST

Branch content -> Structurer -> Contributions -> embeddings/candidate neighbors -> relationship classifier -> incremental clusters -> Critic -> human corrections -> Options -> Decision -> Scenario/Experiment -> Outcome -> Learning Analyst -> confirmed Learning.

Control cost with cheap routine extraction, embeddings for context narrowing, incremental analysis, cached structured state, and stronger models only at high-value moments: Converge, Challenge, Decide, Learn.

## 20. MIGRATION FROM CURRENT KOLLIO

Do NOT rewrite everything.

Current Idea -> Branch or Contribution. Idea board -> Explore. AI generation -> Branch assistant/Structurer. Collaboration -> Proposal + Review + Merge/Fork. Memory -> Decision + Learning memory. Scoring -> Evidence/Assumption support. Simulation -> Scenario analysis attached to Options/Experiment.

Sequence:
1. Freeze new generic ideation features.
2. Introduce DecisionSpace as parent domain.
3. Map existing Ideas into Branches/Contributions.
4. Build Converge first.
5. Add Options + Challenge.
6. Add Decision Record.
7. Move simulation under Options/Experiment.
8. Add Outcome/Learning.
9. Redesign Home into Decision Inbox.
10. Add integrations after core loop validation.

## 21. PRODUCT PRINCIPLES

Decisions over documents. Convergence over generation. Branches before premature consensus. Provenance over polished hallucination. Explicit assumptions over hidden reasoning. Scenarios over fake certainty. Outcomes over vanity scores. Organizational learning over infinite chat history. Integrate with users’ AI tools rather than replace them.

Feature filter: If a feature does not materially help Explore, Converge, Challenge, Decide, Test or Learn, it is peripheral.

## 22. CODING-AGENT ACCEPTANCE CRITERIA

The pivot is functionally real when:
- two people independently explore the same real Decision;
- their work converges without losing provenance or disagreement;
- Kollio exposes agreements, conflicts, alternatives and assumptions;
- humans can correct the AI map;
- the team creates structured Options;
- a Decision is committed with rationale and revisit triggers;
- a Scenario becomes an Experiment;
- an Outcome creates a confirmed Learning;
- that Learning can later be retrieved for another Decision.

Status, measured 2026-09-19: the first eight hold in the shipped product, and the ninth does not. Nothing surfaces a past Learning today, so a person brings it forward by hand, which is also why the inbox's fifth question has no answer yet. The milestone that would prove the first eight in real use is one Decision taken by two people in their own words, an observed Outcome within days, and a voluntary return for a second Decision.

END OF PRD / BLUEPRINT
