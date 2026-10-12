# Contrat produit V3 — Draft à valider par les maquettes

## Une seule définition

Kollio est un espace de travail vivant. On crée un **Espace** à partir d'un besoin, on y ajoute des **objets** (contenu, sources, propositions, décisions), et on les manipule dans des **vues** adaptées. Les résultats sont durables et vérifiables ; la représentation peut changer.

**Invariant principal :** les données ont une identité stable et une provenance, indépendamment du rendu Web, Mac ou de l'agent qui les a proposées.

## Vocabulaire visible (FR / EN)

| Concept | Sens | Ne pas confondre |
|---|---|---|
| Workspace / Espace de travail | Limite personnelle ou d'équipe avec droits | Organisation du code |
| Space / Espace | Une unité de travail avec objectif et objets associés | Unique Decision Space |
| Artifact / Objet | Une information durable (note, source, option, résultat, décision) | Composant graphique |
| View / Vue | Présentation d'objets existants | Copie de données |
| Proposal / Proposition | Ensemble de changements suggérés et non validés | Mutation automatique |
| Evidence / Preuve | Référence et observation avec degré de vérification | Affirmation du modèle |
| Decision / Décision | Choix humain avec raisons et alternatives | Réponse IA |
| Activity / Activité | Historique intelligible des actions | Transcript de conversation |
| Capability / Capacité | Action déclarée, permissionnée, éventuellement externe | Plugin obligatoire |

**À résoudre avant code :** le `.kollio` actuel et les tables Web ne partagent pas ces identifiants ni ces frontières. Ne pas promettre de sérialisation compatible avant preuve round-trip.

## Architecture UX — navigation commune

- **Accueil** : reprise d'espaces, création rapide à partir de texte, espaces récents / partagés si activés.
- **Espace** : titre, contexte, contenu principal et barre d'intention ; vues `Document`, `Canvas`, `Comparer`.
- **Inspecteur** : source, état de vérification, proposition, historique ou propriétés de l'objet sélectionné.
- **Décisions** : accessibles comme objets de l'espace et dans l'historique, pas six pages obligatoires.
- **Préférences** : thèmes, langue, fournisseur intelligence si disponible, droits et mode local/synchronisé explicites.

Pas de dépendance à la voix ni à un agent pour effectuer les gestes principaux.

## Parcours canonique Web + Mac (dataset commun à construire)

1. **Créer** un espace depuis une phrase ; conserver exactement l'original avant génération.
2. **Ajouter** une source et deux options.
3. **Recevoir** une proposition ; afficher un avant/après et ses sources ; refuser une opération invalide.
4. **Accepter** une partie autorisée, rejeter le reste, tracer la décision.
5. **Changer de vue** Document → Canvas → Comparer sans duplication sémantique.
6. **Fermer et reprendre** : retrouver objets, décisions et historique.
7. **Échanger** le contenu entre clients au moyen d'un contrat versionné validé — synchronisation live hors première tranche.

Critère de réussite : les mêmes actions, statuts et résultats sont compréhensibles depuis les deux interfaces. Les gestes natifs peuvent différer.

## Contrat d'exécution (cible, pas implémentation)

```text
intention humaine
   → commande ou demande bornée
   → candidate/proposal (non autorisée)
   → validation schéma + règles + version + permission
   → diff et conséquences visibles
   → décision humaine
   → mutation atomique sur la source de vérité
   → journal + projections Document / Canvas / Comparer
```

La génération de `View` libre avec code exécutable est **hors tranche initiale**. Le modèle ne configure que des représentations déclaratives autorisées.

## Contraintes de sécurité et de qualité

- Aucun contenu externe n'est une instruction exécutable.
- Les données sensibles et permissions sont contrôlées avant une requête à un fournisseur.
- Offline = édition et reprise possibles ; aucune prétention d'IA locale si le modèle est indisponible.
- Un espace a une source de vérité définie (local ou partagé), et un protocole explicite de conflits.
- Contrats versionnés, migrations réversibles ou export de secours, invariants testés sur Web et Mac.
- Les états « simulé », « testé », « approuvé par un humain » et « vérifié par une source » restent distincts.

## Place des autres projets

- **Drop** : transport/découverte de capacités distantes ; dépendance facultative.
- **Harness agentique** : orchestration et vérification des travaux ; dépendance facultative.
- **Kollio** : UX, état d'espace et décisions humaines ; autonome en mode local.

L'intégration à ces projets est une extension de capacités, pas la définition de Kollio.
