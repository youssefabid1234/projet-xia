# Version réunie des contributions de Gregory

La branche `gregory/integration-site` part de `main` au commit `63b44bb` et réunit :

- le bilan de fin de khôlle (PR #2) ;
- « Comment réussir sa khôlle », ses conseils, PDF et logos ;
- le guide des concours et le profil élève (PR #3) ;
- « Retravailler mes erreurs », avec une nouvelle question ciblée, une relance et un nouveau bilan.

Les conflits du profil et du contexte transmis au colleur sont résolus : les objectifs déclarés, les tâches et les bilans sont conservés ensemble. La navigation donne accès aux guides, au profil et aux bilans. Cette branche peut être relue puis fusionnée seule pour ces contributions ; il n'est pas nécessaire de fusionner séparément les PR #2 et #3. Elle ne comprend pas les branches de travail `kholle-live`, `refonte-colle` ou `fond-pedagogique` des autres contributeurs.

## Essai local

Après avoir sauvegardé d'éventuelles modifications locales :

```sh
git fetch origin
git switch gregory/integration-site
```

Utiliser Python 3.12 et les dépendances du `README.md`, puis démarrer `python -m app.web` avec les clés OpenAI et Pipelex configurées localement. Le port par défaut est 5000.

1. Consulter les deux guides et télécharger leurs PDF.
2. Créer un compte de test avec une filière, un classement et un objectif ; les modifier dans « Mon profil ».
3. Faire une courte khôlle, donner une réponse incorrecte puis terminer la séance.
4. Ouvrir le bilan, cliquer sur « Retravailler mes erreurs » et expliquer ce qui doit changer dans le raisonnement.
5. Répondre à la nouvelle question, réagir à la relance, terminer et retrouver le nouveau bilan depuis l'ancien.
6. Vérifier que le profil et le bilan d'origine sont conservés. Une question non évaluée ne doit pas être traitée comme une erreur.

## Validation

```sh
python -m unittest app.test_revision app.web.test_revision app.test_bilan app.web.test_bilans app.test_colle app.test_agent app.test_enonces app.test_evaluation app.test_cours app.web.test_web app.web.test_chat app.web.test_auth app.web.test_projet_eleve scripts.test_lister_formules_coupees -q
```

110 tests réussis le 27 septembre 2026, avec services IA simulés. Le test d'intégration vérifie notamment que les contextes « projet élève » et « reprise » arrivent ensemble comme données et que l'archivage préserve les objectifs et l'ancien bilan. Le module `app.test_chapitres` est exclu de cette commande : un test d'alias échoue déjà sur la version de base.

La pertinence pédagogique doit encore être testée avec les modèles réels. Le catalogue actuel concerne les séries numériques. La sélection d'une reprise repose sur la proximité des énoncés et ne garantit pas une équivalence pédagogique. Les appels réels consomment les crédits API du serveur. Voir `RETRAVAILLER.md` pour les limites et `docs/guide-concours-profil-eleve.md` pour les guides.
