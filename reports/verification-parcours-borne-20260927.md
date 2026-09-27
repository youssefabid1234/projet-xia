# Vérification du parcours limité à deux tentatives

Le serveur impose désormais la limite par question de cours et par étape d'exercice. Après deux réponses insuffisantes, il fournit la réponse, demande une courte reformulation, puis enchaîne. Le cours est accompagné de sa référence. Les exercices sont décomposés avant affichage à partir du corrigé du catalogue.

Chaque étape conserve ses tentatives, ses indices, ses évaluations et son mode de franchissement : `trouvee_seul`, `trouvee_avec_indice`, `donnee_par_agent`. Une réponse donnée reste non acquise, même si l'élève la recopie ensuite. Les acquisitions partielles restent enregistrées ; un exercice contenant une solution donnée ne procure pas de gain de niveau. Les compteurs et l'attente de reformulation sont conservés après reconnexion.

Les nouvelles transitions ne dépendent plus de la méthode de décision Pipelex. L'évaluation mathématique utilise toujours la vraie méthode d'évaluation. Les indices et réponses des étapes proviennent du plan privé ; les réponses futures ne sont pas transmises au modèle de dialogue. La prochaine tâche est affichée directement, sans demande de préférence.

## Vérifications

- **83 tests automatiques réussis**, dont les transitions, les deux tentatives, les trois modes de franchissement, la confidentialité des solutions futures, les échecs API, l'idempotence, la reconnexion, la sélection des exercices et les routes HTTP.
- **Exercice avec vraies APIs** : [conversation, échanges 5 à 8](parcours-borne-reel-20260927-133841/conversations.md). L'exercice du catalogue 17.6 est décomposé en six étapes. Après deux erreurs sur l'étape 1, sa solution est fournie. Sa copie par l'élève ouvre l'étape 2 avec zéro tentative ; l'étape 1 reste `donnee_par_agent`, non acquise. Ce scénario initialise directement l'agent au catalogue pour tester cette transition ; ce n'est pas une colle complète.
- **Cours avec vraies APIs, après correction de la préparation des questions** : [conversation complète](parcours-borne-reel-20260927-134142/conversations.md). Question sur la convergence absolue, deux erreurs, réponse issue de la définition 16.2.3 (page PDF 143), reformulation, puis question sur le théorème liant convergence absolue et convergence. La définition demeure non acquise.

Le premier essai réel avait révélé une question de cours qui récitait déjà sa réponse. Le contrôle de préparation a été renforcé pour rejeter ce cas et un test de non-régression a été ajouté. La seconde conversation vérifie ce correctif.

Ces vérifications portent sur les limites et l'enregistrement du parcours. Elles ne constituent pas une validation exhaustive de la justesse de tous les corrigés extraits du PDF ni des plans produits par le modèle.

## Audit longitudinal précédent

L'audit a été interrompu à la demande de modification du comportement : les quatre sessions du profil faible et les échanges déjà réalisés pour le profil moyen restent dans [le dossier de l'audit](audit-pedagogie-20260927-reel/bilan-faible.md). Le profil fort n'avait pas été lancé. Ces résultats concernent l'ancienne version et ne sont pas mélangés aux vérifications du nouveau parcours.
