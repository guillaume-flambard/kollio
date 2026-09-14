# Kollio, état d'avancement du pilote Faktus

Date : 2026-09-14. Branche de référence : `main` (`0a5a899`). Ce rapport est un instantané, il n'est pas committé.

---

## 1. En une page

En une journée, le "mémoire collective de décisions" du pilote a été construit de bout en bout, en sept tranches verticales mergées. Ce qui existait avant : landing B2B, historique d'idées versionné (itérations), analyse par contraintes avec workflow durable et revue humaine. Ce qui a été ajouté : le contexte entreprise, le cadrage d'initiative, les deux axes d'équipe, la boucle expérience vers apprentissage, la séparation Connu / Supposé / Inconnu avec contradictions explicites, la réutilisation des apprentissages d'un lancement à l'autre, et la surface qui explique une conclusion.

- 7 PR mergées (#63 à #72), 1 PR ouverte (#73, verte).
- 149 tests API, 59 tests navigateur, 32 tests Vitest, plus les evals enregistrées hors ligne. Tous verts.
- 12 révisions Alembic, head `3d9a1f4c7b20`, sans dérive (`alembic check`).
- 34 opérations d'API exposées, contrat OpenAPI et client TypeScript régénérés à chaque tranche.
- 8 dossiers de changement OpenSpec, chacun avec `proposal`, `design`, `tasks` et `acceptance` (les limites y sont écrites noir sur blanc).

Le pilote n'est pas encore démontrable de bout en bout : il manque le seed Faktus et le parcours de démo (#62), l'écran qui montre les expériences et les apprentissages, et le formulaire d'ajout de participant (#66). Le moteur et les données, eux, sont prêts.

---

## 2. Ce qui est livré, par capacité

### 2.1 Contexte entreprise (#63)
Le workspace porte un profil (nom, description, modèle économique, produits, segments, marchés, structure), des objectifs (état actif ou archivé, priorité) et des contraintes (titre, détail, état). Écran de réglages dans le workspace. Migration `5a7c1e9d3b48`.
Preuve : tests d'intégration du module `company_context`, test navigateur `company-context.spec.ts`.
Limite : les principes et métriques du brief ne sont pas modélisés (seuls profil, objectifs, contraintes).

### 2.2 Cadrage d'initiative (#64)
Type d'initiative fermé (10 valeurs) et copie orientée B2B. Migration `7b1f0c2e9a55`.
Preuve : `initiative-type.spec.ts` et tests API.

### 2.3 Équipe : deux axes (#65)
Chaque participant est décrit par une **participation** (`owner`, `decision_maker`, `contributor`, `observer` ; `owner` réservé, jamais attribuable) et une **fonction métier** (12 valeurs). L'owner ajoute un membre du workspace directement, effectif immédiatement (`POST /ideas/{idea_id}/members`) ; la candidature spontanée reste possible et nomme la fonction apportée. Migration `9f3c7a2b6e14`, mapping sans perte des rôles historiques (dev vers engineering, commercial vers sales, growth vers marketing, designer/product vers product, data vers data, owner vers direction).
Preuve : 25 cas unitaires sur les règles, intégration (ajout owner-only, refus d'une fonction inconnue, boucle candidature vers acceptation), navigateur `team.spec.ts`.
Limite : l'UI de sélection de membre n'existe pas (voir #66). `ideas.sought_roles` garde son nom de colonne alors que ses valeurs ont changé d'axe.

### 2.4 Analyse par contraintes : Connu / Supposé / Inconnu, contradictions, contexte (#68)
Chaque facteur porte une **base** : `known` (score et au moins une preuve citée), `assumed` (score, sans source), `unknown` (aucun score, `gap` nommant la preuve manquante). Un verdict `unknown` ne porte aucun score global et rend tous les facteurs inconnus. Le résultat porte une liste de **contradictions** structurées (cible objectif ou contrainte, identifiant exact, conflit en prose) ; le validateur refuse toute référence non fournie au lancement. Le lancement gèle le **contexte entreprise actif** (profil, objectifs, contraintes) sous des identifiants `objective:<uuid>` et `constraint:<uuid>` ; le snapshot voyage avec le run, le worker le porte au graphe, la passerelle l'envoie comme donnée non fiable. Une correction est une nouvelle preuve sur un nouveau run : le premier résultat reste intact.
Preuve : 7 cas unitaires sur les règles de base, intégration (contexte injecté sans l'objectif archivé, correction sur second run, premier résultat inchangé), fixtures d'eval enregistrées (abstention et contradiction), `alembic check` sans dérive.
Aucune migration : résultat et snapshot sont en JSONB.
Limite : les preuves citées ne sont pas listées côté UI (l'API expose les `source_ids` du facteur, pas les textes).

### 2.5 Boucle d'apprentissage (#67)
Expériences avec hypothèse, métrique de succès, base de référence, cible et cycle de vie `proposed -> running -> completed | cancelled` (les deux derniers sont terminaux). Tout membre lecteur enregistre des résultats ; la complétion rédige un **brouillon d'apprentissage** (hypothèse, métrique, cible, résultats épinglés par identifiant) qu'un membre édite et confirme. Un apprentissage confirmé ne redevient jamais brouillon. Lisible par expérience et par idée. Migration `2c8e5b1f7a93`.
Preuve : 7 cas unitaires sur le cycle de vie, test d'intégration du parcours complet, `experiments` sans écran.
Limite : le brouillon est **déterministe**, pas écrit par un modèle. Aucun écran ne montre expériences et apprentissages (l'API seule).

### 2.6 Réutilisation des apprentissages (#71)
Un apprentissage confirmé est **embeddé** comme une idée (même modèle, mêmes dimensions), sa provenance portant le workspace, l'idée et l'expérience. Au lancement d'une analyse, les apprentissages les plus proches, **restreints aux workspaces du lecteur**, entrent en preuves `learning:<uuid>` et le snapshot trace `reused_learning_ids`. La **fuite inter-workspace** de la recherche de similarité est fermée : `similar_idea_ids` prend désormais les workspaces du lecteur et filtre via `ideas.workspace_id`. Migration `3d9a1f4c7b20` (table `learning_embeddings` plus alignement JSON vers JSONB sur `learnings.outcome_ids`).
Preuve : intégration (provenance du vecteur, isolation inter-workspace prouvée dans les deux sens, injection au lancement, extérieur refusé), fixture d'eval enregistrée.
Limites : les deux accroches sont **best-effort** (un fournisseur absent est journalisé et le run continue sur les preuves fournies) ; **aucun chemin de production n'embedde les idées**, donc la recherche d'idées similaires est scopée et prouvée mais non alimentée ; pas de seuil de similarité ni d'exclusion de l'initiative elle-même.

### 2.7 Surface d'explication (#72)
Dans le panneau de verdict du dépôt : la base de chaque facteur, la **preuve manquante** quand la base est inconnue, et un bloc **contradictions** (libellé de cible traduit plus la prose du moteur). Catalogues FR et EN, styles sur le token canonique `--ui-text-muted`.
Preuve : contrôle navigateur DEPOSIT-05 dans les deux locales, sur une analyse portant base, `gap` et contradiction.
Limite : seule la **page de dépôt** explique la conclusion ; le détail d'idée et la timeline n'affichent qu'un libellé.

### 2.8 Membres du workspace (PR #73, ouverte)
`GET /workspaces/{workspace_id}/members` rend les membres (id, nom, rôle) à un membre du workspace, triés par nom ; un non-membre reçoit 404 `workspace_not_found`. C'est l'activateur du formulaire d'ajout de participant.
Preuve : intégration (membre voit les deux membres et leurs rôles, extérieur refuse).
Limite : aucune UI ne le consomme encore (#66).

---

## 3. État technique

### Modules API (81 fichiers Python sous `src/modules`)
`company_context`, `constraint_analysis`, `experiments`, `ideas`, `iterations`, `profiles`, `workspaces`, plus la plateforme (`auth`, `db`, `embeddings`, `worker`, `seed_demo`, `evaluation`).

### Migrations (12 révisions, head `3d9a1f4c7b20`)
bootstrap postgres et vector, snapshots d'import legacy, profils de démo, workflows d'analyse, itérations versionnées, réconciliation (proposal, sought roles, candidatures), contexte entreprise, type d'initiative, deux axes d'équipe, expériences et apprentissages, embeddings d'apprentissage. `alembic check` ne signale aucune dérive.

### Opérations d'API (34)
Dépôt et lecture d'idée, itérations (créer, accepter, rejeter, rollback), candidatures et membres (demander, accepter, rejeter, ajouter, retirer, quitter), analyses (lancer, lire, revoir), contexte entreprise (lire, profil, objectifs, contraintes), expériences (créer, lister, lire, statut, résultat, apprentissage), workspaces (lister, membres), profil.

### Tests et CI
- 149 tests API (`uv run pytest -m 'not live'`), dont unitaires sur les règles de domaine et intégration Postgres.
- 59 tests navigateur Playwright (9 fichiers, FR et EN), **non exécutés en CI**.
- 32 tests Vitest, exécutés en CI.
- Evals DeepEval enregistrées (abstention, contradiction, réutilisation) sans appel fournisseur ; variante live sur déclenchement manuel.
- CI "Foundations" : ruff, format, mypy strict, pytest, eslint, typecheck Nuxt, parité FR/EN, build, budget de performance.

### Contrats
Huit dossiers OpenSpec sous `openspec/changes/` : `add-company-context`, `add-initiative-framing`, `add-participant-axes`, `add-learning-loop`, `analysis-basis-and-contradictions`, `reuse-confirmed-learnings`, `explain-the-conclusion`, `workspace-members-endpoint`. Chacun porte ses scénarios, ses preuves et ses limites.

---

## 4. Ce qui reste

| # | Sujet | Nature | Dépend de |
| --- | --- | --- | --- |
| #73 | Endpoint des membres du workspace | PR ouverte, verte, à merger | rien |
| #66 | Formulaire d'ajout de participant (owner) | UI plus test navigateur, consomme #73 | #73 et #65 |
| #57 | Wizard d'onboarding Faktus | UI plus parcours | contexte entreprise |
| #62 | Parcours E2E de démo pilote, seed Faktus, acceptance | clôture de #52 | tout le reste |
| #69 | Aligner 5 valeurs de l'UI sur les tokens canoniques | petite correction de design | rien |
| #70 | Garde-fou tokens inconnus et couleurs littérales | script plus CI | #69 |

Ordre recommandé vers une démo : #73, puis #66, puis le seed et le parcours (#62), avec #57 en parallèle. #69 puis #70 ferment la cohérence visuelle.

### Absent de l'application aujourd'hui
- Aucun écran pour les expériences, résultats et apprentissages : l'API existe, la boucle se pilote en API ou en tests.
- Aucun chemin de production n'embedde les idées : le matching idée vers idée n'est pas alimenté.
- L'analyse ne consomme que le contexte entreprise et les apprentissages ; elle n'utilise pas encore les itérations passées comme preuves.
- Pas de couche investisseurs, hors périmètre V1 assumé.

---

## 5. Limites et dettes assumées, consolidées

1. **Apprentissages non écrits par un modèle** : le brouillon est un gabarit déterministe que le membre édite.
2. **Repli silencieux** : les accroches d'embedding avalent l'échec fournisseur avec un avertissement ; seul le snapshot (`reused_learning_ids`) le rend observable.
3. **Idées non embeddées en production** : la recherche d'idées similaires est correctement scopée et testée, mais aucune donnée ne l'alimente.
4. **Migration non testée sur données historiques** : #65 mappe les rôles par constante partagée et un test unitaire, le schéma par `alembic check`, mais aucun test n'exécute la migration sur des lignes legacy réelles.
5. **Preuves non affichées** : la surface d'explication montre la base et le manque, pas les preuves citées.
6. **Dérive de design** : 5 valeurs de l'UI workspace utilisent des noms de tokens inexistants avec repli hexadécimal (#69), sans garde-fou automatique (#70).
7. **Playwright hors CI** : les 59 tests navigateur ne tournent qu'en local ; les fixtures simulent les réponses d'API.
8. **Contradictions figées au lancement** : un identifiant de contexte n'est pas revérifié après coup, le run garde le sens qu'il avait.
9. **Ranking non réglé** : pas de seuil de similarité, pas de re-classement, pas de pondération entre contexte et apprentissages.

---

## 6. Comment vérifier soi-même

Prérequis : Postgres local `memo@localhost`, base `kollio_test_faktus`, Redis sur `63799`.

```
export DATABASE_URL="postgresql+asyncpg://memo@localhost/kollio_test_faktus"
export TEST_DATABASE_URL="$DATABASE_URL"
export REDIS_URL="redis://localhost:63799/0"
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"

make verify                                        # lint, types, 149 tests API, parité FR/EN
cd apps/api && uv run pytest -m 'not live' -q      # API seule
cd apps/api && uv run alembic check               # zéro dérive de schéma
pnpm --dir apps/web test:ui                       # 32 tests Vitest
pnpm --dir apps/web exec playwright test          # 59 tests navigateur (hors CI)
```

---

## 7. Points d'attention

- **Empilement de branches** : deux fois déjà, une PR construite sur une autre a dû être rejouée après un squash merge. Repartir de `main` à jour avant chaque tranche évite le conflit.
- **La valeur du pilote repose sur #62** : sans seed Faktus ni parcours de démo, ce qui est livré reste une API. C'est le prochain jalon qui transforme le travail en démonstration.
- **Le moteur est en avance sur la surface** : beaucoup de capacités (expériences, apprentissages, réutilisation) n'ont pas d'écran. Décider vite si le pilote se montre par l'interface ou par des données préparées.
