# R0 — État des lieux comparatif

**Statut des preuves : audit source et documentation uniquement.** Aucun test ni parcours manuel n'a été rejoué pour ce chantier ; aucune capture runtime du Mac n'est présente sur sa branche `main`. Ne pas confondre visuel approuvé et screenshot de l'app en marche.

## Ce qui existe réellement

| Dimension | Kollio Web (`kollio`) | Kollio Mac (`kollio-mac`) | Écart V3 |
|---|---|---|---|
| Point d'entrée | Decision Inbox / espaces / idées | Saisie initiale et document local | Repenser accueil et création identiques |
| Objet principal | Decision Space, branches, contributions, options | `.kollio`, objets, relations, décisions | Nouveau contrat `Space` + `Artifact` |
| Rendu | Nuxt, pages, six sections de décision | SwiftUI, canvas + propositions | Ajouter les mêmes modes Document/Canvas/Comparer |
| IA | LangGraph/LiteLLM, backend spécialisé | `SuggestionService`, Foundation Models et Vapor en option | Contrat de propositions, pas orchestration dupliquée |
| Validation | Revues/confirmation dans flux collectif | `ProposalValidator` + commande atomique | Statuts et retours utilisateur compatibles |
| Provenance | contributions, décisions, apprentissages | SourceLedger, révisions, citations | Schéma canonique de sources à rapprocher |
| Collaboration | membres, rôles, Logto, PostgreSQL | Solo local ; partage non construit | Capacité progressive, sans bloquer le mode Solo |
| Identité | Aubergine / porcelain ; Geist | Paper/Ink/Branch ; accent bleu ; système Apple | Tokens, typographie et composants harmonisés |
| Qualité déclarée | CI GitHub ; large corpus tests backend et navigateur | suites Swift et évaluations locales décrites | Relancer puis capturer, sans supposer qualité UX |

## Références vérifiées dans le code

**Web**
- [Design système](../../DESIGN.md), [tokens web](../../packages/ui/src/tokens.css), [theme](../../packages/ui/src/theme.ts).
- [Présentation produit](../../docs/00-project-overview.md), [Decision Spaces](../../apps/web/app/pages/workspace/decision-spaces/index.vue), [Converge](../../apps/web/app/pages/workspace/decision-spaces/[spaceId]/converge.vue).
- [Relations typées](../../apps/api/src/modules/converge/domain/relations.py), [enregistrements de décisions](../../apps/api/src/modules/decisions/domain/record.py), [réutilisation d'apprentissages](../../apps/api/src/modules/experiments/service/reuse.py).
- [Maquette approuvée : bibliothèque](../../docs/assets/design/approved-ideas-library.png), [maquette approuvée : détail](../../docs/assets/design/approved-idea-detail.png) — **références de design, pas preuve runtime**.

**Mac**
- [Product blueprint](https://github.com/guillaume-flambard/kollio-mac/blob/main/docs/PRODUCT_BLUEPRINT.md), [limites connues](https://github.com/guillaume-flambard/kollio-mac/blob/main/docs/known-limitations.md), [preuves](https://github.com/guillaume-flambard/kollio-mac/blob/main/openspec/specs/evidence.md).
- [Tokens Swift](https://github.com/guillaume-flambard/kollio-mac/blob/main/packages/KollioApp/Sources/KollioApp/DesignSystem/DesignTokens.swift).
- [DocumentCodec](https://github.com/guillaume-flambard/kollio-mac/blob/main/packages/KollioCore/Sources/KollioCore/Serialization/DocumentCodec.swift), [ProposalValidator](https://github.com/guillaume-flambard/kollio-mac/blob/main/packages/KollioCore/Sources/KollioCore/Validation/ProposalValidator.swift).
- [Atlas des 44 interactions](https://github.com/guillaume-flambard/kollio-mac/blob/main/docs/design/06-interaction-atlas.md).

## Matrice de captures R0 — **NON PRODUITES**

| Scène | Web runtime | Mac runtime | Maquette V3 |
|---|---|---|---|
| Accueil / espace récent | À capturer | À capturer | À concevoir |
| Création d'espace | À capturer | À capturer | À concevoir |
| Document ou contenu ouvert | À capturer | À capturer | À concevoir |
| Proposition IA en attente | À capturer | À capturer | À concevoir |
| Comparer / décider / historique | À capturer | À capturer | À concevoir |

Protocole : taille desktop documentée, mêmes données de référence, thème clair, langue FR, captures sans données personnelles. Sur Mac, le script `run-app.sh --shot` est documenté comme peu fiable : obtenir l'identifiant de fenêtre, capturer la fenêtre Kollio uniquement, **ouvrir et inspecter** l'image. Les captures absentes sont signalées, jamais remplacées par une illustration générée.

## Critères de sortie R0

- [x] Branches, versions et sources des deux repos identifiées.
- [x] Écarts de vocabulaire, palette, navigation et données recensés.
- [ ] Web lancé et les cinq scènes réelles capturées.
- [ ] Mac lancé et les cinq scènes réelles capturées.
- [ ] Échecs, écrans manquants et limites documentés.
- [ ] Tests et parcours humains rejoués à des SHA précis.

**Remarque** : les suites de tests détaillées dans les READMEs sont de la documentation historique, pas des vérifications du 12/10/2026.
