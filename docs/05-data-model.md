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
`Option(id, space_id, title, proposal, mechanism?, upside?, cost?, risks?, critical_assumptions?, success_metrics?, created_by, lang, created_at, updated_at)` — une alternative qu'un Decision Space peut choisir, portant les champs du §7. Titre et proposition non vides (contraintes `btrim`), `lang` fermé. Aucun score, aucun rang, aucun verdict calculé : c'est le Critic qui porte le challenge machine, et il propose sans jamais décider.
- `OptionEvidence(option_id, contribution_id, side(for|against), created_at)` — clé primaire composite, ce qui interdit le même lien deux fois. Seules les Contributions **confirmées** du **même espace** sont liables (`suggested` et contributions étrangères refusées) : l'évidence est *liée*, jamais *affirmée*, donc une Option ne peut pas revendiquer un support qu'aucune Contribution ne porte. Une même Contribution peut soutenir une Option et en contredire une autre.
- Écriture (créer, éditer, supprimer, lier, délier) = propriétaire + participants ; lecture = membres de l'espace.
- Voir `openspec/changes/add-options/` et l'issue #112. Hors périmètre : le choix d'une Option et le Decision Record (étape 6), les scénarios (étape 7), tout écran.

### ChallengeRun + ChallengeFinding (le challenge — étape 5, seconde moitié)
`ChallengeRun(id, space_id, option_id, status(OPEN|RUNNING|COMPLETED|FAILED), opened_by, model?, failure_reason?, lang, created_at, updated_at)` — une tentative de challenger une Option contre les six contrôles du §7. `model` reste null tant que le Critic n'a pas tourné ; `failure_reason` ne porte une valeur que sur un run `FAILED`.
- `ChallengeFinding(id, run_id, kind, severity(low|medium|high), detail, origin(human|critic), status(proposed|confirmed|dismissed), contribution_id?, lang, created_at, updated_at)` — un constat. `kind` est l'ensemble fermé des six contrôles : `unsupported_assumption`, `contradictory_evidence`, `hidden_dependency`, `failure_mode`, `causal_claim`, `missing_success_criteria`.
- Un constat humain est `confirmed` d'emblée ; un constat du Critic reste `proposed` jusqu'à confirmation ou rejet humain. Le rejet conserve la ligne : c'est une donnée de convergence, pas une suppression.
- La couverture (quels contrôles portent au moins un constat non rejeté) est **informative** : elle ne bloque aucune transition, ne bloque aucune décision et ne produit aucun score.
- **Le Critic tourne à l'ouverture.** Ouvrir un challenge écrit le run puis le dispatche sur la tâche `challenge.execute`. Le worker assemble un brief (la question de l'espace, les champs présents de l'Option, les Contributions confirmées liées), fait **un** appel sur le tier visible, valide chaque constat contre les six `kind` et contre les citations envoyées, puis les écrit `proposed` avec `origin: critic` et complète le run.
- **Rien n'est écrit avant validation, et rien n'est inventé.** Un appel qui échoue, un résultat en partie invalide, un résultat vide ou un dispatch impossible terminent le run `FAILED` avec un `failure_reason` lisible et **zéro** constat ; le run raté et sa raison restent lisibles, et rouvrir un challenge sur la même Option est le seul chemin de reprise. L'API n'accepte toujours jamais un `origin: critic` venant d'un client.
- Voir `openspec/changes/add-challenge/`, `openspec/changes/add-critic/` et l'issue #113. Hors périmètre : le Decision Record (étape 6), tout écran.

### Decision + alternatives + arguments (le Decision Record — étape 6)
`Decision(id, space_id, version, selected_option_id, rationale, critical_assumptions?, uncertainty?, success_criteria?, revisit_triggers?, reviewer_ids, decided_by, lang, created_at)` — la trace versionnée et append-only de l'engagement d'un Decision Space. `(space_id, version)` est unique ; `version` démarre à 1. `rationale` non vide (contrainte `btrim`), `lang` fermé. Aucun update, aucun delete : le record d'un espace est sa version la plus haute, et son historique est entier.
- **Committer est le seul chemin vers `DECIDED`** : l'opération exige que l'espace soit `READY_TO_DECIDE`, écrit le record et ajoute l'événement `READY_TO_DECIDE → DECIDED` via l'adaptateur de l'étape 2, dans la même transaction. Tout autre statut est refusé sans rien écrire (ni record, ni événement). Réouvrir puis re-décider écrit la version suivante.
- `DecisionRejectedAlternative(decision_id, option_id)` — clé primaire composite : les Options explicitement écartées. C'est pourquoi une Option ne porte pas de statut propre.
- `DecisionArgument(decision_id, contribution_id, side(for|against))` — clé primaire composite `(decision_id, contribution_id)` : les Contributions **confirmées** du **même espace** sur lesquelles le record repose. `side` est une colonne, pas une partie de la clé, donc la même Contribution ne peut pas argumenter dans les deux sens sur une même décision (contradiction refusée, pas stockée deux fois).
- `reviewer_ids` est un **instantané** des participants au moment du commit, pas une jointure vive : un record doit garder son sens quand l'appartenance change ensuite.
- `revisit_triggers` est une liste structurée : `{metric (requis, non vide), direction?(above|below), threshold?, note?}`. Un métrique seul est un déclencheur légitime (un rappel de regarder). **Informatif** : aucun déclenchement automatique, aucun score.
- Écriture (committer) = propriétaire + participants ; lecture = membres de l'espace.
- Voir `openspec/changes/add-decision-record/` et l'issue #114. Hors périmètre : le Critic, les scénarios (étape 7), Outcome/Learning (étape 8), la Decision Inbox (étape 9), tout écran. Question laissée ouverte par l'étape 2 et tranchée ici : `READY_TO_DECIDE → CONVERGING` reste non modélisé, la réouverture est le chemin de retour déclaré.

### ScenarioVariable + ScenarioRun + ScenarioRunValue (la simulation — étape 7)
`ScenarioVariable(id, space_id, name, unit?, low, base, high, lang, created_at, updated_at)` — une grandeur **à l'échelle de l'espace**, pas de l'Option : deux Options comparées sur le même métrique doivent partager sa définition. `(space_id, name)` unique, `low <= base <= high` (contrainte `low <= base AND base <= high`), `Numeric(18, 6)`.
- `ScenarioRun(id, option_id, level(optimistic|base|pessimistic|failure), assumptions, created_by, lang, created_at, updated_at)` — un niveau de simulation d'une Option. `assumptions` non vide (contrainte `btrim`) parce que §9 exige des hypothèses explicites. **Au plus un run `base` par Option**, garanti par un index unique partiel (`level = 'base'`).
- `ScenarioRunValue(run_id, variable_id, value)` — clé primaire composite, `Numeric(18, 6)`. Les valeurs d'un run sont écrites en bloc (suppression puis réinsertion), et seulement pour les variables de l'espace.
- **Sensibilité déterministe** (aucun modèle, aucun chiffre prédit) : la lecture prend un critère (`metric_variable_id`, `direction above|below`, `threshold`) et renvoie, par variable, l'intervalle de bascule par interpolation linéaire entre points déclarés, le croisement interpolé et le nombre de croisements (plusieurs croisements → l'intervalle le plus étroit, jamais présenté comme un seuil net) ; sinon `beyond_declared_range` avec le sens de déplacement du métrique, ou `insufficient_points` (moins de deux points déclarant la variable et le métrique). Les variables sont **classées par pente implicite absolue** la plus forte. Les runs omettant le métrique sont signalés `incomplete_run_ids` et **jamais moyennés**. Le nombre de Contributions confirmées pour/contre l'Option est rapporté, mais **l'Evidence n'est pas attribuée à une variable** (rien dans le modèle ne le dit, et §21 interdit d'inventer ce lien). La réponse **n'a aucun champ pouvant porter une valeur prédite**.
- Écriture (variables + runs) = propriétaire + participants ; lecture = membres de l'espace.
- Voir `openspec/changes/add-scenario-analysis/` et l'issue #115. Hors périmètre : modèles probabilistes, Monte Carlo, priors d'espace, modèles prédictifs, tout écran.

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

### Experiment ⇄ Decision Space (le lien additif — étape 8)
`Experiment` gagne deux colonnes nullables : `decision_space_id` (FK `decision_spaces`, `ON DELETE SET NULL`, indexée) et `option_id` (FK `options`, `ON DELETE SET NULL`, indexée). Le rattachement à l'`Idea` reste en place : rien n'est migré, rien n'est cassé.
- Un `option_id` n'est posé qu'avec un `decision_space_id` ; l'option doit appartenir à cet espace, et l'espace au workspace de l'idée. Une idée publique (sans workspace) ne peut donc jamais rejoindre un espace.
- Supprimer l'espace ou l'option met le lien à `NULL` au lieu de détruire l'historique d'expérience.
- Deux lectures membres : `GET /workspaces/{w}/decision-spaces/{s}/experiments` et `.../learnings`. Le `Learning` est atteint par son expérience (jointure), jamais rattaché directement à l'espace.
- Aucun backfill : deviner un espace pour une expérience existante inventerait une décision que personne n'a prise.
- Voir `openspec/changes/link-experiments-to-spaces/` et l'issue #116.

### Decision inbox (lecture agrégée — étape 9)
Pas de table : l'inbox est une **projection en lecture** de lignes qui existent déjà, assemblée à la demande. Quatre sections : `needs_convergence` (Decision Space en `CONVERGING`, périmètre = les workspaces du lecteur), `needs_my_input` (Contribution `suggested` ou ChallengeFinding `proposed`, périmètre = les espaces où le lecteur est propriétaire ou participant), `ready_to_decide` (Decision Space en `READY_TO_DECIDE` qui ne porte encore aucune Decision), `needs_learning` (Experiment `completed` sans Outcome enregistré, ou Learning `draft`). Chaque section trie du plus ancien au plus récent et rend son propre `total`. Un `limit` optionnel (1..50, défaut 20) borne les entrées, jamais le total.
- La cinquième section du §4, la mémoire pertinente, est **volontairement absente** tant que le Memory Retriever (§11) n'existe pas : une liste vide sous cette clé affirmerait qu'aucune mémoire pertinente n'existe, ce que rien ne soutient.
- Voir `openspec/changes/add-decision-inbox/` et l'issue #117.

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
