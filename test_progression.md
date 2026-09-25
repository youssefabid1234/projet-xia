# Simulation de progression

Chapitre : **2 — Dérivation et Intégration**. Niveau initial : **1,5**.

Le champ `chapitre` du JSON correspond exactement au filtre de `choisir_exercice` : aucune correction de ce champ n'est nécessaire.

Simulation exécutée avec `app/profil.py`, sans appel Pipelex. Les verdicts sont fixés dans le script : quatre réponses correctes, une incomplète (`incomplete`), puis une incorrecte.

Le chargeur associe `identifiant` à `id` en mémoire. Il traite une difficulté source de 0 comme une difficulté de 1 pour la sélection ; le JSON reste inchangé. À distance égale du niveau, le premier exercice dans l'ordre du JSON est retenu.

| Étape | Exercice proposé | Difficulté source | Difficulté utilisée | Verdict simulé | Niveau avant | Nouveau niveau |
|---|---|---:|---:|---|---:|---:|
| 1 | 2.1 | 0 | 1 | correcte | 1.5 | 1.8 |
| 2 | 2.2 | 2 | 2 | correcte | 1.8 | 2.1 |
| 3 | 2.19 | 2 | 2 | correcte | 2.1 | 2.4 |
| 4 | 2.7 | 3 | 3 | correcte | 2.4 | 2.7 |
| 5 | 2.9 | 3 | 3 | incomplete | 2.7 | 2.8 |
| 6 | 2.11 | 3 | 3 | incorrecte | 2.8 | 2.6 |

Les gains appliqués sont +0,3 pour `correcte`, +0,1 pour `incomplete` et −0,2 pour `incorrecte`. Le niveau final est **2,6**.

Vérifications réussies : six exercices distincts du bon chapitre, séquence et niveaux attendus, historique de six réponses, erreurs enregistrées, autre chapitre inchangé et fichier JSON non modifié.

Reproduction : `python test_progression.py`.
