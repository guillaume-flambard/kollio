# 05 — Modèle de données

Postgres. `lang` (locale d'origine) sur tout contenu utilisateur. Embeddings multilingues dans pgvector. Multi-tenant (workspace) pour le B2B privé.

## Entités principales

### User
`id, handle, email, display_name, roles[] (skills/rôles réels : designer, dev, commercial…), bio, created_at`

### Workspace (B2B privé) + Membership
- `Workspace(id, name, plan, created_at)`
- `WorkspaceMembership(workspace_id, user_id, role: admin|member)`
- Une idée publique n'a pas de workspace ; une idée privée appartient à un workspace.

### Idea (le "dépôt")
`id, slug, title, pitch, owner_id, workspace_id?(null=public), stage(seed|iterating|team_formed), lang, visibility(public|workspace), created_at`

### Iteration (le "commit") — append-only
`id, idea_id, parent_id(null=init), author_id, message, payload(jsonb: l'état de l'idée à ce point), branch(default "main"), short_hash, created_at`
- **Append-only** : jamais d'update destructif → historique + rollback (créer une nouvelle itération pointant sur un parent antérieur).
- **Branches / propositions (PR)** : une proposition = une itération sur une branche + un statut `pending|accepted|rejected` ; l'acceptation par le porteur fusionne (nouvelle itération sur `main`) et peut créer une `Membership` d'idée.

### ConstraintAnalysis (le tueur de contraintes)
`id, idea_id, iteration_id, realism_score(0-100), constraints(jsonb: [{key: concurrence|cout|temps|defendabilite|acquisition, score, note}]), model, created_at`
- Recalculé par un agent à chaque itération majeure. Historisé (lié à l'itération).

### IdeaMembership (l'équipe qui se forme) — **le flux du moat**
`idea_id, user_id, role(porteur|designer|dev|commercial|growth|…), joined_via_iteration_id, joined_at`
- `sought_roles` sur l'idée : rôles recherchés (affichés dans l'explorer).

### Contribution / Outcome (le flux du moat)
`id, idea_id, user_id, iteration_id, kind, impact_note, created_at`
- **Outcome** (résultat mesurable, quand il existe) : `Outcome(id, idea_id, type, value, measured_at)` — c'est le signal rare et précieux (voir `02`).

### CompanyContext (contexte entreprise, par workspace)
- `CompanyProfile(workspace_id PK, name, description, business_model, products_services, customer_segments, markets, structure, created_at, updated_at)` — une seule fiche par workspace.
- `CompanyObjective(id, workspace_id, title, state(active|archived), priority, created_at, updated_at)` — objectifs évolutifs.
- `CompanyConstraint(id, workspace_id, title, detail?, state(active|archived), created_at, updated_at)` — contraintes réelles de l'entreprise ; à ne pas confondre avec les cinq dimensions d'une `ConstraintAnalysis`.
- Lus et écrits par tout membre du workspace ; jamais visibles hors du workspace.
- `lang` n'est pas stocké ici : ce sont des libellés courts, pas du contenu rédactionnel (voir `acceptance.md` du change `add-company-context`).

### Embedding (matching multilingue)
`id, subject_type(idea|user|contribution), subject_id, vector(pgvector), model, lang, updated_at`
- Modèle **multilingue** → cross-lingual (idée FR ↔ profil EN).

### Follow / Activity
`Follow(user_id, idea_id)` ; `ActivityEvent(idea_id, user_id, type, created_at)` (alimente le graphe d'élan).

## Notes
- **Traduction du contenu** : jamais stockée en base par défaut ; générée à la lecture (agent) selon la locale du lecteur. On stocke l'original + `lang`. Voir `07-i18n.md`.
- **État LangGraph** : tables du checkpointer Postgres (séparées du domaine).
- Le cœur "itérations/commits" et le "matching" méritent le **DDD tactique** ; le reste reste simple.
