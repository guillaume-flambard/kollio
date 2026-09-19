# Kollio

**Kollio** est un espace de décision pour équipes privées : des équipes marketing, growth, produit, innovation et stratégie de 3 à 15 personnes qui utilisent déjà l'IA au quotidien. Le parcours visible a trois moments : cadrer la décision, choisir avec ses raisons, puis enregistrer ce qui s'est passé. On y dépose une idée que l'IA confronte au réel, l'équipe explore et converge, tranche en gardant la trace des options écartées et des hypothèses, éprouve la décision par une expérience et en tire un apprentissage confirmé par un humain. Le flux privé, c'est-à-dire qui résout quoi avec qui et ce que ça a donné, est la vraie matière du produit.

Ce dépôt est la **source de vérité** du projet : documentation produit, décisions d'architecture, spécifications et roadmap. Il est écrit pour être lu par des humains et par des agents de code (voir `AGENTS.md`), et ses specs vivent sous `openspec/`.

## Ordre de lecture
1. `AGENTS.md` — instructions pour les agents de code (à lire en premier)
2. `docs/00-project-overview.md` — ce qu'est Kollio, la vision
3. `docs/01-product-spec.md` — le produit, les concepts, le périmètre V1
4. `docs/02-strategy-and-moat.md` — la défendabilité (le moat) et la stratégie B2B-first
5. `docs/03-architecture.md` — l'architecture back-end / agentique
6. `docs/04-tech-stack.md` — la stack et les décisions
7. `docs/05-data-model.md` — le modèle de données
8. `docs/06-design-system.md` — le design system
9. `docs/07-i18n.md` — le multilingue FR/EN (dès le départ)
10. `docs/08-conventions-and-testing.md` — conventions, monorepo, tests
11. `docs/09-roadmap.md` — les phases
12. `docs/10-project-init.md` — **bootstrap** : commandes d'initialisation (CLIs officiels, dernières versions) — à lire avant d'écrire du code
13. `docs/11-bootstrap-status.md` — versions résolues, preuves de bootstrap et critères Phase 0 restants
14. `docs/12-agentic-stack-2026.md` — décision agentique vérifiée en 2026 et responsabilités de chaque brique

## Statut
Pré-PMF, en pilote privé. Le pivot vers la décision collaborative est livré de bout en bout côté écrans : espaces de décision et leurs six sections, explore, converge, options, décision, expérience, apprentissage, membres et inbox. Les specs correspondantes ont rejoint le registre canonique (`openspec/specs`), et les documents de fondation restent la référence pour l'architecture, le modèle de données et la stratégie. Le jalon en cours, et le seul qui compte maintenant, est une vraie décision prise par deux personnes avec leurs propres mots, suivie d'un résultat observé dans les jours qui suivent et d'un retour volontaire pour une seconde décision : il ne demande aucune nouvelle intégration, seulement l'usage réel de la boucle déjà livrée. Mesuré le 2026-09-19 sur le commit `710a707`, dont la CI passe : 322 tests navigateur dans 21 fichiers tournent sur des réponses d'API simulées et prouvent donc le rendu, pas l'authentification, la persistance ni la qualité fournisseur ; 557 tests d'API passent sans base, 239 tests d'intégration exigent un PostgreSQL jetable migré, et 2 tests fournisseur sont live, optionnels et budgétés ; les catalogues FR/EN sont à parité à 1013 clés, la garde vérifiant les deux sens. Restent ouverts la couche investisseurs (hors V1) et l'extension du corpus d'évaluation aux surfaces du pivot.

## Principe directeur
Bâtir du **solide sans sur-ingénierie**. Chaque brique se remplace individuellement quand une métrique le réclame, jamais "au cas où".

## Contribuer
- `CONTRIBUTING.md` dit comment lancer le projet et comment une modification est livrée.
- `CODE_OF_CONDUCT.md` et `SECURITY.md` couvrent la conduite attendue et la divulgation privée d'une faille.
- Les issues et les pull requests passent par les modèles de `.github/`.

Kollio est distribué sous **licence Apache-2.0** : voir `LICENSE`.

## Local foundations

Use the runtimes recorded in `.nvmrc` and `.python-version`. Copy `.env.example`
to `.env`, generate a local Postgres password and LiteLLM master key, and set the
local database URL. Provider credentials remain outside Git.

```bash
make install
make services
make migrate
make build
make up
make verify
```

Integration tests require `TEST_DATABASE_URL` pointing to a separate Postgres
database with the Alembic migrations applied. Never point tests at imported data.
Provider calls require `KOLLIO_RUN_LIVE_EVALS=1`; ordinary checks use recordings.

See `docs/11-bootstrap-status.md` for resolved versions, evidence and unfinished
Phase 0 acceptance criteria.
