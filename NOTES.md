# Comprendre le projet

Le projet est une première base de tuteur de maths pour les élèves de prépa scientifique. Il contient déjà une méthode pour évaluer une réponse d’élève et un programme pour l’essayer. L’application destinée aux élèves reste à construire.

## Le rôle de chaque fichier

### README.md — La présentation du projet

Ce fichier explique l’objectif général et l’organisation des dossiers. Il est légèrement en retard sur le contenu actuel : il annonce une structure initiale sans code applicatif, alors qu’un programme d’essai existe désormais.

### methods/evaluation_maths_prepa/main.mthds — Les instructions de correction

C’est le cœur pédagogique du projet. Il contient les instructions de correction destinées à l’intelligence artificielle. Il reçoit deux textes : l’énoncé de l’exercice et la réponse de l’élève.

La correction se déroule en deux étapes :

1. **Préparer une référence de correction**, uniquement à partir de l’énoncé, sans regarder la réponse de l’élève. Elle précise les résultats attendus, les justifications nécessaires, les points à vérifier et les éventuelles ambiguïtés.
2. **Examiner la réponse de l’élève**, en la confrontant à l’énoncé et à cette référence. Les consignes demandent d’accepter les méthodes alternatives et de reconnaître les situations où une conclusion fiable est impossible. La référence elle-même peut être remise en question si elle contient une erreur.

Le résultat comprend trois éléments :

- Un verdict : **correcte, incorrecte, incomplète ou indéterminable**.
- La nature de l’erreur principale : calcul, raisonnement, notion mal comprise, justification manquante, etc.
- Une explication en français de une à trois phrases, avec un maximum de 80 mots, qui indique le problème et propose une piste de correction.

La méthode ne donne ni note chiffrée ni corrigé intégral. Elle demande aussi de ne pas inventer le raisonnement de l’élève lorsque celui-ci fournit seulement un résultat.

### test_methode.py — Le programme d’essai

Ce programme contient un exercice sur la dérivée de la fonction f(x) = x × exp(x), accompagné d’une réponse volontairement fausse : l’élève affirme que la dérivée d’un produit est le produit des dérivées.

Le programme lit les fichiers de méthode présents dans `methods/evaluation_maths_prepa/`, les envoie avec cet exemple au service Pipelex, attend la correction et affiche le résultat ainsi que l’identifiant de l’exécution.

Malgré son nom, il ne vérifie pas automatiquement que la correction obtenue est juste : il permet de l’observer. Il vérifie toutefois qu’une clé d’accès Pipelex a été fournie et que des fichiers de méthode sont présents avant de poursuivre.

### .env.example — Le modèle pour les clés d’accès

Ce fichier prévoit deux emplacements vides : `OPENAI_API_KEY` et `PIPELEX_API_KEY`. Ces clés servent à accéder aux services correspondants.

Le programme actuel utilise uniquement la clé Pipelex. Il ne lit pas automatiquement un fichier `.env` : copier ce modèle ne suffit donc pas, à lui seul, à lui transmettre la clé. Celle-ci doit être fournie dans les paramètres de l’environnement où le programme est lancé.

### .gitignore — Les fichiers à garder hors de l’historique partagé

Ce fichier indique quels fichiers et dossiers ne pas inclure dans l’historique partagé du projet :

- `.env`, qui peut contenir les clés privées ;
- `__pycache__/`, qui contient des fichiers de travail produits par Python ;
- `.venv/`, qui peut contenir les outils Python installés spécialement pour ce projet.

### NOTES.md — Cette explication

Ce document décrit les fichiers du projet et leurs liens en français simple. Il sert de guide de lecture et ne participe pas à la correction des exercices.

## Le rôle des dossiers

- **`methods/`** contient la méthode de correction, rangée dans le sous-dossier `evaluation_maths_prepa/`.
- **`app/`** est actuellement vide et réservé à la future application destinée aux utilisateurs.
- **`.git/`** conserve l’historique des versions du projet et les informations nécessaires à son suivi. Il ne contient pas les consignes pédagogiques.

## Comment tout s’articule

```text
Programme d’essai : test_methode.py
  → lit les instructions de main.mthds
  → transmet l’exercice et la réponse à Pipelex
      → préparation de la référence de correction
      → évaluation de la réponse de l’élève
  → affiche le verdict et l’explication
```

La clé Pipelex permet au programme d’accéder au service. Le fichier `main.mthds` définit la manière de corriger, tandis que `test_methode.py` fournit l’exemple et déclenche le travail. Les fichiers de présentation expliquent le projet, mais n’interviennent pas dans son exécution.

## Ce qui a été vérifié

Les fichiers ont été lus et la vérification de structure par Pipelex a réussi : toutes les étapes de la méthode sont définies et elle est reconnue comme exécutable.

Aucune correction réelle n’a été lancée pendant cette lecture. Cette vérification ne mesure donc pas la qualité des réponses pédagogiques. Le présent document est le seul fichier créé pour consigner cette explication ; les fichiers existants n’ont pas été modifiés.
