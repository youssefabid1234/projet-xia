# Retravailler mes erreurs

Fonction issue de `gregory/retravailler-mes-erreurs`, basée sur le bilan de fin de khôlle (PR #2, `c1a0df1`). La branche `gregory/integration-site` réunit aussi les guides et le profil déclaratif de la PR #3. Voir `INTEGRATION.md` pour tester la version réunie.

## Parcours

1. Terminer une khôlle et ouvrir son bilan.
2. Cliquer sur **Retravailler mes erreurs**, ou sur une question évaluée incorrecte/incomplète. Un point non évalué ou indéterminable n'est jamais présenté comme une erreur.
3. Expliquer ce que l'on change dans son raisonnement (jusqu'à 2 000 caractères). Ce texte guide les relances, mais ne constitue pas une preuve de compréhension.
4. Recevoir un exercice du même chapitre et le résoudre en justifiant les hypothèses et le lien au cours. Le colleur doit poser une relance ciblée et attendre la réaction de l'élève.
5. Terminer la reprise et enregistrer un nouveau bilan. L'ancien bilan reste inchangé et affiche un lien vers le résultat de la reprise.

Une séance déjà en cours doit être terminée avant d'en lancer une autre. Les reprises et les bilans sont accessibles uniquement au compte connecté. Le démarrage est protégé par CSRF et par un jeton à usage unique ; un double clic ne multiplie pas les appels API.

## Choix et validation de la question

La sélection utilise les notions et la question du bilan, la proximité lexicale des énoncés et une difficulté au plus égale à celle de l'exercice d'origine (ou au niveau plafonné à 2 pour une question de cours). Elle exclut les exercices déjà proposés dans le profil, même restés sans évaluation. La proximité est une heuristique ; elle ne garantit pas une équivalence pédagogique.

Au plus trois candidats sont vérifiés avec le vérificateur d'énoncés existant et leur corrigé privé. Si aucun ne convient, la question d'origine est reprise explicitement, avec son corrigé du catalogue ou un passage de cours relu et identifié. Sans référence exploitable, le site explique l'indisponibilité ; il n'invente pas une variante.

Chaque nouvelle réponse de reprise est évaluée avec Pipelex. Seul un verdict correct clôt et valide cette question. Les verdicts incorrect, incomplet et indéterminable la laissent ouverte. La reprise ne change pas le niveau chiffré, les exercices vus ni les acquis précédents et ne valide pas les étapes d'une khôlle normale. Elle ajoute une preuve séparée dans `taches`, reliée à son bilan d'origine par `reprise_de`.

Le contexte de reprise est fourni comme un message de données utilisateur, séparément des instructions, conformément à la [documentation OpenAI sur les rôles](https://developers.openai.com/api/docs/guides/text). Il n'est pas accumulé à chaque tour dans l'historique. Le corrigé de référence reste réservé au vérificateur et à l'évaluateur.

## Tests

```sh
python -m unittest app.test_revision app.web.test_revision app.test_bilan app.web.test_bilans app.test_colle app.test_agent app.test_enonces app.test_evaluation app.test_cours app.web.test_web app.web.test_chat app.web.test_auth scripts.test_lister_formules_coupees -q
```

Résultat local du 27 septembre 2026 : **104 tests réussis**, dont **17 nouveaux**. Les tests incluent le trajet erreur → relance → réponse corrigée → nouveau bilan, la relecture après redémarrage, la référence privée, l'isolement des comptes, le repli sur la question d'origine, les doubles clics et les pannes de préparation. Le module `app.test_chapitres`, dont un test d'alias échoue déjà sur la base, n'est pas inclus dans cette commande.

Les services IA sont simulés dans ces tests. Le comportement et la pertinence des relances avec un modèle réel restent à vérifier avec les clés du serveur. La préparation utilise des appels OpenAI et les échanges de reprise utilisent OpenAI/Pipelex ; ils consomment des crédits. Le catalogue actuel reste limité aux séries numériques.

Pour un essai manuel : démarrer l'application, créer un compte de test, produire une réponse incorrecte puis terminer la khôlle. Depuis son bilan, lancer une reprise, vérifier l'énoncé présenté, répondre, enregistrer le nouveau bilan et revenir au premier pour vérifier le lien. Tester aussi le cas sans exercice proche et une question non évaluée (aucun bouton de reprise).
