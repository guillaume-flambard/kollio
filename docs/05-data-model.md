# 05 — Modèle de données

Postgres. `lang` (locale d'origine) sur tout contenu utilisateur. Embeddings multilingues dans pgvector. Multi-tenant (workspace) pour le B2B privé.

## Entités principales

### User
`id, handle, email, display_name, roles[] (skills/rôles réels : designer, dev, commercial…), bio, created_at`

### Workspace (B2B privé) + Membership
- `Workspace(id, name, plan, created_at)`
- `WorkspaceMembership(workspace_id, user_id, role: admin|member)`
- Une idée publique n'a pas de workspace ; une idée privée appartient à un workspace.

### DecisionSpace (l'objet parent — pivot « Collaborative Decision Intelligence »)
`id, workspace_id (requis, jamais null), question (non vide), description?, owner_id, status, deadline?, lang, created_at, updated_at`
- `status` est un ensemble fermé : `OPEN|EXPLORING|CONVERGING|READY_TO_DECIDE|DECIDED|TESTING|LEARNED|REOPENED`.
- `DecisionSpaceParticipant(space_id, user_id, created_at)` — clé primaire composite, ce qui rend idempotent l'ajout du même participant. Le propriétaire est participant par construction et ne peut pas être retiré.
- `DecisionSpaceStatusEvent(id, seq, space_id, from_status?, to_status, actor_id, reason?, created_at)` — append-only, jamais modifié ni supprimé. `seq` (identité monotone) porte l'ordre, `now()` étant constant par transaction ; le `status` de l'espace est une projection du dernier événement.
- Cycle de vie fermé : seules les arêtes déclarées sont acceptées (`OPEN`→`EXPLORING`→`CONVERGING`→`READY_TO_DECIDE`→`DECIDED`→`TESTING`→`LEARNED`), plus la réouverture (`DECIDED`/`TESTING`/`LEARNED`→`REOPENED`, motif obligatoire) et la reprise (`REOPENED`→`EXPLORING`). Toute autre transition est refusée sans rien écrire.
- `deadline` est informatif : aucune transition n'est refusée parce qu'une date est passée.
- Le statut est écrit par le propriétaire et les participants ; la gestion des participants est réservée au propriétaire.
- Voir `openspec/changes/add-decision-space/` (étape 2 de la séquence de migration §20) et l'issue #109.

### Branch + Contribution (l'exploration — étape 3 de la migration §20)
`Branch(id, space_id, title, summary?, source_idea_id?, visibility(private|shared), created_by, lang, created_at, updated_at)` — conteneur d'exploration sous un Decision Space. Le contenu est une matière première non canonique. Une Idea mappée devient une Branch partagée (titre + pitch repris, historique accessible via `source_idea_id` sans duplication) ; le mapping est idempotent et les idées publiques (sans workspace) sont exclues.
- `Contribution(id, space_id, branch_id, kind(idea|claim|evidence|objection|constraint), title, body?, author_id, source?, tool_model?, transformation_history?, status(suggested|confirmed), lang, created_at, updated_at)` — unité canonique proposée depuis une Branch. Une proposition humaine est `confirmed` d'emblée ; une suggestion IA reste `suggested` jusqu'à confirmation humaine (qui devient alors l'auteur). Seules les `confirmed` alimenteront Converge (étape 4).
- Lecture : Branch privée = créateur seul ; partagée = lecteurs de l'espace. Écriture (proposer/confirmer) = propriétaire + participants.
- Voir `openspec/changes/map-ideas-to-branches/` et l'issue #110. Ne pas confondre avec `branch` (ligne d'itérations) ni `Contribution` (acte de participation) du vocabulaire historique.

### Converge map (la carte du raisonnement — étape 4, premier slice)
`ContributionRelation(id, space_id, from_contribution_id, to_contribution_id, relation_type(SUPPORTS|CONTRADICTS|DUPLICATES|ALTERNATIVE_TO|DERIVED_FROM|SUPERSEDES|EVIDENCE_FOR|EVIDENCE_AGAINST), created_by, created_at)` — lien explicite dirigé entre deux Contributions confirmées du même espace. Une relation par paire ordonnée, pas d'auto-relation, paires inter-espaces refusées.
- `Cluster(id, space_id, title, created_by, created_at)` — regroupement titré pour la carte. L'appartenance passe par `contributions.cluster_id` (nullable, `ON DELETE SET NULL`) : une Contribution est dans au plus un Cluster ; assigner déplace ; supprimer un Cluster désassigne sans rien supprimer.
- Lecture de la carte : Contributions confirmées (les `suggested` restent dehors), relations, Clusters avec leurs membres. Écriture = propriétaire + participants.
- Voir `openspec/changes/add-converge-map/` et l'issue #111. Le proposeur IA (relations `suggested` à confirmer) est le slice suivant.

### Option + OptionEvidence (les alternatives — étape 5, slice humain)
`Option(id, space_id, title, proposal, mechanism?, upside?, cost?, risks?, critical_assumptions?, success_metrics?, created_by, lang, created_at, updated_at)` — une alternative qu'un Decision Space peut choisir, portant les champs du §7. Titre et proposition non vides (contraintes `btrim`), `lang` fermé. Aucun score, aucun rang, aucun verdict calculé : c'est le Critic (slice suivant, premier à nécessiter un modèle) qui portera le challenge machine.
- `OptionEvidence(option_id, contribution_id, side(for|against), created_at)` — clé primaire composite, ce qui interdit le même lien deux fois. Seules les Contributions **confirmées** du **même espace** sont liables (`suggested` et contributions étrangères refusées) : l'évidence est *liée*, jamais *affirmée*, donc une Option ne peut pas revendiquer un support qu'aucune Contribution ne porte. Une même Contribution peut soutenir une Option et en contredire une autre.
- Écriture (créer, éditer, supprimer, lier, délier) = propriétaire + participants ; lecture = membres de l'espace.
- Voir `openspec/changes/add-options/` et l'issue #112. Hors périmètre : le Critic, le choix d'une Option et le Decision Record (étape 6), les scénarios (étape 7), tout écran.

### Idea (le "dépôt")
`id, slug, title, pitch, owner_id, workspace_id?(null=public), stage(seed|iterating|team_formed), lang, visibility(public|workspace), created_at`

### Iteration (le "commit") — append-only
`id, idea_id, parent_id(null=init), author_id, message, payload(jsonb: l'état de l'idée à ce point), branch(default "main"), short_hash, created_at`
- **Append-only** : jamais d'update destructif → historique + rollback (créer une nouvelle itération pointant sur un parent antérieur).
- **Branches / propositions (PR)** : une proposition = une itération sur une branche + un statut `pending|accepted|rejected` ; l'acceptation par le porteur fusionne (nouvelle itération sur `main`) et peut créer une `Membership` d'idée.

### ConstraintAnalysis (le tueur de contraintes)
`id, idea_id, iteration_id, realism_score(0-100), constraints(jsonb: [{key: concurrence|cout|temps|defendabilite|acquisition, score, note}]), steps(jsonb), model, created_at`
- Recalculé par un agent à chaque itération majeure. Historisé (lié à l'itération).
- `steps` persiste le pipeline de raisonnement adversarial (#76) derrière une seule analyse : `[{name, tier, model, output}]` dans l'ordre analyste → challenger → critique de preuves → company fit → synthétiseur. Le membre ne voit qu'un résultat ; les étapes restent rejouables et auditées. La colonne `draft_steps` sur l'`AnalysisWorkflow` porte les mêmes étapes avant revue humaine.

### IdeaMembership (l'équipe qui se forme) — **le flux du moat**
- `participation(owner|decision_maker|contributor|observer)` + `business_function` (12 fonctions métier) : deux axes,cf. décision #48.
`idea_id, user_id, role(porteur|designer|dev|commercial|growth|…), joined_via_iteration_id, joined_at`
- `sought_roles` sur l'idée : rôles recherchés (affichés dans l'explorer).

### Contribution / Outcome (le flux du moat)
`id, idea_id, user_id, iteration_id, kind, impact_note, created_at`
- **Outcome** (résultat mesurable, quand il existe) : `Outcome(id, idea_id, type, value, measured_at)` — c'est le signal rare et précieux (voir `02`).

### CompanyContext (contexte entreprise, par workspace)
- `CompanyProfile(workspace_id PK, name, description, business_model, products_services, customer_segments, markets, structure, created_at, updated_at)` — une seule fiche par workspace.
- `CompanyObjective(id, workspace_id, title, state(active|archived), priority, created_at, updated_at)` — objectifs évolutifs.
- `CompanyConstraint(id, workspace_id, title, detail?, state(active|archived), created_at, updated_at)` — contraintes réelles de l'entreprise ; à ne pas confondre avec les cinq dimensions d'une `ConstraintAnalysis`.
- `CompanyPrinciple(id, workspace_id, title, detail?, state(active|archived), lang, created_at, updated_at)` — principes et non-négociables déclarés (vision, positionnement, refus explicites).
- `CompanyMetric(id, workspace_id, name, value?, unit?, observed_at?, source?, state(active|archived), lang, created_at, updated_at)` — indicateurs clés simples ; la valeur, l'unité, la date et la source sont optionnelles pour autoriser une réponse partielle.
- Lus et écrits par tout membre du workspace ; jamais visibles hors du workspace.
- `lang` (fr|en) est stocké sur les cinq tables : il enregistre la langue de la dernière écriture, comme pour `Idea` et `Iteration`.

### Embedding (matching multilingue)
`id, subject_type(idea|user|contribution), subject_id, vector(pgvector), model, lang, updated_at`
- Modèle **multilingue** → cross-lingual (idée FR ↔ profil EN).

### Follow / Activity
`Follow(user_id, idea_id)` ; `ActivityEvent(idea_id, user_id, type, created_at)` (alimente le graphe d'élan).

## Notes
- **Traduction du contenu** : jamais stockée en base par défaut ; générée à la lecture (agent) selon la locale du lecteur. On stocke l'original + `lang`. Voir `07-i18n.md`.
- **État LangGraph** : tables du checkpointer Postgres (séparées du domaine).
- Le cœur "itérations/commits" et le "matching" méritent le **DDD tactique** ; le reste reste simple.
