# Décision R1 — Spatial Ink est retenu

**Décision prise le 12/10/2026 :** adopter la direction visuelle **Spatial Ink** pour Kollio V3. Elle prime désormais sur l'option de tableau de bord permanent comme expérience centrale.

## Intention

Créer un **document spatial vivant** où l'humain comprend rapidement l'ensemble d'un problème et fait apparaître les éléments qui lui servent au bon moment. L'inspiration n8n concerne la visualisation claire des relations et la manipulation directe, **pas l'orchestration de workflows ni un DAG d'exécution**.

### Invariants

1. Après création ou ouverture d'un espace, **Canvas/Spatial** est le mode d'entrée proposé. Document et Comparer présentent le même état.
2. L'espace montre d'abord peu de choses ; **Explorer** révèle progressivement d'autres objets. Replier ne supprime aucune information.
3. Les objets ont une forme selon leur signification : intention ancrée, idée typographique, source inspectable, question visible, proposition provisoire, décision durable.
4. Les relations ont un type explicite (soutient, contredit, dépend, propose, etc.), ne signifient pas « exécuter » par défaut et sont accessibles sans couleur seule.
5. Une proposition reste **provisoire** et ne devient jamais une mutation par le seul effet d'une animation.
6. Les commandes, références, sources et historiques restent accessibles par clavier et interactions natives même hors réseau et sans LLM.
7. Les contrôles apparaissent dans le contexte, sans panneaux permanents envahissant le document.

## Composants prioritaires

`SpatialStage`, `MeaningNode`, `BranchEdge`, `ExpansionHandle`, `ProposalGhost`, `FocusReader`, `DecisionAnchor`, `SpatialControls`.

Le contrat est commun ; l'implémentation reste native en Vue/Nuxt et SwiftUI.

## État d'exécution vérifié

Un workspace local V3 contient les deux applications dans des Git worktrees isolés ainsi qu'un prototype HTML et des tokens CSS/Swift générés. **Le prototype, non connecté à un moteur IA**, ouvre désormais un espace en vue spatiale, permet Explorer/Replier, de sélectionner un objet et d'inspecter sa signification. Dix captures WebKit du prototype ont été régénérées, le JavaScript passe le contrôle syntaxique, le contrôle statique des tokens/scènes/actions passe. Commit local du workspace design : `4fe21ea`.

**Non fait :** portage du nouveau canvas dans les véritables clients Nuxt/SwiftUI, tests d'interaction humains, persistance ou interopérabilité effective des deux modèles de données, zoom/pan performant.

## Étape suivante

Transformer le prototype en contrats précis, puis intégrer une première tranche verticale dans les deux applications : `SpatialStage + MeaningNode + BranchEdge + ExpansionHandle`, sur une fixture partagée. Valider le rendu et l'interaction réels, puis ajouter `ProposalGhost` et `FocusReader`. Ne pas importer des bibliothèques de composants visuels génériques simplement pour obtenir une parité superficielle.

**Le canvas est une surface d'exploration sémantique, pas un moteur d'automatisation.**
