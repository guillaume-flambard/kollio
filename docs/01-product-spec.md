# 01 — Spécification produit

## Concepts cœur (la métaphore GitHub)
- **Idea (dépôt).** Une idée = un "repo" : titre, pitch, porteur, stade, langue d'origine. Peut être publique (B2C) ou privée à un workspace (B2B).
- **Iteration (commit).** Chaque évolution de l'idée est une itération tracée : auteur, horodatage, message, `parent_id`, hash court. **Append-only** → historique complet, **retour arrière** possible. Des **branches** et des **propositions** (façon pull request) permettent d'explorer sans casser la version principale.
- **Le tueur de contraintes.** Un agent analyse l'idée et produit un **score de réalisme** (0–100) + des contraintes notées : *concurrence, coût de build, temps au marché, défendabilité, acquisition*. Chaque contrainte a une barre + une note courte. C'est ce qui rend l'idée réaliste au lieu de rêvée. Recalculé à chaque itération majeure.
- **Team / contributeurs.** Une équipe se forme autour d'une idée. Le porteur **accepte** un collaborateur dans la boucle (une proposition acceptée = un membre). Chaque membre a un **rôle réel** (designer, dev, commercial, growth…). L'idée affiche l'équipe et les rôles **recherchés**.
- **Explorer (feed).** Découverte des idées : filtres par stade (graine / en itération / équipe formée), par profil recherché, par score de réalisme, par domaine. C'est là qu'un collaborateur trouve une idée à rejoindre.
- **Profil.** Un utilisateur a des compétences/rôles (issus de sa "vie de tous les jours"), ses idées, ses contributions, son historique.
- **Élan.** Signal d'activité d'une idée (graphe de contributions type "contribution graph", nb d'itérations, abonnés).

## Rôles utilisateur
- **Porteur** d'une idée (owner du repo).
- **Contributeur** (accepté dans la boucle).
- **Observateur** (suit, commente, propose).
- (B2B) **Membre de workspace** ; **admin de workspace**.

## Flux clés (V1)
1. **Déposer une idée** → formulaire ; le tueur de contraintes tourne en direct (l'IA seule apporte de la valeur dès le 1er user → règle le cold-start jour 1).
2. **Itérer** → ajouter un commit / ouvrir une branche / proposer une modification ; le porteur accepte ou non.
3. **Rejoindre la boucle** → un utilisateur propose sa contribution/son rôle ; le porteur l'accepte → l'équipe grandit.
4. **Explorer** → parcourir/filtrer les idées, en suivre, en rejoindre.

## Périmètre V1 (in)
Dépôt d'idée · tueur de contraintes · itération versionnée (commits/branches/PR/rollback) · formation d'équipe · explorer · profils. Variante **B2B privée** : même ossature, espace d'équipe privé, connecté aux outils de l'équipe.

## Hors V1 (différé, explicitement)
- **Couche investisseurs** ("un investisseur finance une idée/personne via crédits"). Séduisant mais **régulé** (AMF/SEC — crowdfunding/equity) et re-introduit un marketplace à 3 faces + un métier de relation. → **Phase 3, avec cadre juridique.** Dans l'UI V1 : la montrer *verrouillée* ("plus tard").
- Le grand public / réseau ouvert massif : Phase 2.

## Maquettes de référence
Design system + écrans publiés comme artefacts (voir `06-design-system.md` pour les liens).
