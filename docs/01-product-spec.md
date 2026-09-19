# 01 — Spécification produit

Kollio n'est plus un gestionnaire d'idées. C'est un espace de décision pour une équipe privée : une équipe y cadre une décision, choisit un chemin avec ses raisons, puis enregistre ce qui s'est réellement passé. L'idéation reste possible, mais elle n'est plus le produit : elle vit à l'intérieur du premier moment.

## Audience

Équipes marketing, growth, produit, innovation et stratégie de 3 à 15 personnes qui utilisent déjà l'IA au quotidien et prennent des décisions à plusieurs. Le pilote privé tourne sur un cas réel de ce segment.

## Les trois moments visibles

C'est tout ce qu'un nouveau lecteur doit apprendre pour démarrer.

1. **Ce qu'il faut décider.** La question de décision, son propriétaire, les personnes qui y participent, et le matériau que chacun apporte.
2. **Ce qu'on choisit et pourquoi.** Les options en présence, les preuves et les hypothèses qui les portent, ce qui pourrait faire regretter un choix, puis la décision enregistrée avec ses raisons et ses conditions de réexamen.
3. **Ce qui s'est passé.** L'expérience montée pour vérifier la décision, le résultat observé face à ce qui était attendu, et la leçon qu'un humain confirme.

Branches, contributions, relations, clusters et scénarios sont des mécaniques de support. Elles servent ces trois moments et ne sont jamais un vocabulaire que tout nouvel utilisateur doit apprendre.

## Le cycle sous les moments

`Explore -> Converge -> Challenge -> Decide -> Test -> Learn`, pour un objet central qui est le **Decision Space**, pas l'Idea.

- **Decision Space.** La décision vivante : question, propriétaire, statut, échéance, participants. Statuts fermés `OPEN`, `EXPLORING`, `CONVERGING`, `READY_TO_DECIDE`, `DECIDED`, `TESTING`, `LEARNED`, avec `REOPENED` possible. Historique versionné et append-only.
- **Branch et Contribution.** Un participant explore dans sa branche privée ou partagée ; « proposer à l'espace » convertit le matériau en Contribution canonique, avec sa provenance, en attente de confirmation humaine.
- **Converge.** La carte du raisonnement collectif : accords, conflits, alternatives, inconnues, hypothèses fortes et peu étayées, doublons. Un désaccord ne se dissout jamais dans un résumé fade : compatible se relie, incompatible se sépare, et l'humain corrige la carte.
- **Option et preuve.** Une option a une proposition, un mécanisme, un bénéfice attendu, un coût, des risques, ses hypothèses critiques, ses preuves pour et contre, ses indicateurs de succès. Aucun score universel : le regard critique cherche ce qui ferait regretter le choix.
- **Decision record.** L'option retenue, les alternatives écartées, les arguments pour et contre, l'incertitude qui reste, le propriétaire, les critères de succès et les déclencheurs de réexamen. Versionné.
- **Experiment, Outcome, Learning.** Une expérience vérifie la décision, un résultat observé se compare à l'attendu, et l'IA propose une leçon qu'un humain confirme. Une leçon confirmée est ce qui rend la décision suivante meilleure.

## Rôles

- **Participation** dans un Decision Space : `owner`, `decision_maker`, `contributor`, `observer`.
- **Fonction métier** de la personne : une valeur parmi la liste fermée du produit (marketing, ventes, finance, produit, ingénierie, succès client, opérations, juridique, RH, données, direction, autre).
- **Rôles métier** de la personne : ses savoir-faire, une liste distincte de sa fonction et de sa participation.
- Par espace de travail : **membre** et **administrateur**.

## État des capacités

**Livré.** Les espaces de décision et leurs six sections, l'exploration et la promotion des contributions, la convergence manuelle, les options et le regard critique, le registre de décision, les expériences, les apprentissages confirmés, les membres et les réglages, et l'écran d'accueil qui dit ce qui demande votre attention. Les écrans existent en français et en anglais, avec les tokens du design system.

**En validation.** Une vraie décision prise par deux personnes avec leurs propres mots, un résultat observé dans les jours qui suivent, puis un retour volontaire pour une seconde décision. C'est le jalon en cours, et il ne demande aucune nouvelle intégration ni élargissement de fonctionnalités.

**Différé, et décrit comme tel.** La structuration automatique du matériau et le retriever de mémoire derrière la cinquième question de l'écran d'accueil (mémoire antérieure pertinente) : la carte de convergence d'aujourd'hui est construite et corrigée par des humains, et l'écran avoue lui-même que cette cinquième question n'a pas encore de réponse. Les intégrations (extension navigateur, Slack, Notion, Drive, exports Decision Brief, Experiment Brief, Learning Memo), la récupération sémantique à l'échelle, la couche publique et grand public, et la couche investisseurs (régulée, hors V1).

## Flux clés (V1)

1. **Cadrer.** Créer un Decision Space, écrire la question, inviter les participants, apporter son matériau dans sa branche, proposer à l'espace.
2. **Converger.** Corriger la carte du raisonnement collectif : relier, séparer, retirer un doublon.
3. **Choisir avec des raisons.** Construire les options, les passer au regard critique, committer la décision avec ses raisons, ses incertitudes et ses déclencheurs de réexamen.
4. **Enregistrer ce qui s'est passé.** Monter l'expérience, saisir le résultat, comparer à l'attendu, confirmer la leçon.

## Modèle de confiance

Les sorties d'IA traversent une frontière de validation avant tout effet : schéma strict, champs non déclarés refusés, identifiants de preuve limités à ce qui a été fourni, locale du texte vérifiée. La promotion d'un contenu canonique, une décision et une leçon restent des actes humains. La provenance prime sur le résumé poli.

## Qualité, au 2026-09-19 (commit `710a707`)

- 322 tests navigateur dans 21 fichiers, sur réponses d'API simulées : ils prouvent ce que le navigateur rend, pas l'authentification, la persistance ni la qualité fournisseur.
- 798 tests d'API collectés : 796 sans le marqueur live, dont 557 qui tournent sans base et 239 tests d'intégration qui exigent un PostgreSQL jetable migré ; 2 tests fournisseur live restent optionnels, budgétés et déclenchés à la main.
- Catalogues FR/EN à parité à 1013 clés, la garde vérifiant les deux sens (chaque clé utilisée existe, chaque clé du catalogue est atteinte par du code ou par une preuve).

## Hors V1 (différé, explicitement)

- **Couche investisseurs** (financer une idée ou une personne) : régulée (AMF/SEC) et hors périmètre, Phase 3 avec cadre juridique.
- Grand public et réseau ouvert massif : Phase 2, après validation de la boucle privée.

## Références

Stratégie et moat : `02-strategy-and-moat.md`. Jalon et phases : `09-roadmap.md`. Architecture, modèle de données, design system et i18n : `03`, `05`, `06`, `07`.
