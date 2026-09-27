# Observations relues dans les conversations réelles

Ces observations complètent le relevé automatique : celui-ci ne voit que les tâches enregistrées, alors que le modèle peut afficher une question ou un exercice sans ouvrir de tâche.

## Profil faible

- **Session 1, E1–E4 :** définition d'une série convergente (source 16.1.5). L'élève confond initialement terme tendant vers zéro et convergence ; le tuteur demande une reformulation. Définition acquise à E4.
- **Session 1, E4–E5 :** énoncé « convergence absolue implique convergence » (16.2.4), acquis à E5.
- **Session 1, E5–E9 :** démonstration du même théorème. À E7, une preuve par le critère de Cauchy dans les réels est présentée ; le tuteur demande en plus la décomposition en parties positives/négatives, comme si elle était indispensable. À E8, l'« indice » contient presque toute cette seconde preuve.
- **Session 1, E9 :** première application, mais énoncé inexploitable seul : « Résoudre l'exercice d'application sur la convergence absolue d'une série. » Aucune série n'est précisée. L'élève choisit lui-même un exemple à E10 ; le tuteur ajoute ensuite une exigence de convergence non absolue.
- **Session 1, E11 :** l'élève distingue correctement série harmonique alternée et série harmonique. Le tuteur lui reproche pourtant de confondre convergence absolue et conditionnelle.
- **Session 1, E13/E14 :** l'état passe aux exercices à E13, mais le premier énoncé de catalogue apparaît seulement à E14 (17.6, 2/5). Le seuil strict avant E10 n'est pas respecté pour un exercice de catalogue.
- **Session 1, E18–E20 :** exercice 17.20 (4/5) altéré. Le PDF, page 49 (imprimée 43), donne une convergence absolue de la série des a_n/n et des sommes a_n/n^k nulles ; le dialogue donne une convergence absolue de la série des a_n et des sommes a_n n^k nulles. Vérification visuelle conservée dans [source-page49.png](source-page49.png). Le tuteur valide ensuite un argument d'analyticité au point z=1 sans établir l'analyticité au voisinage de ce point, situé sur le bord du disque garanti. Le gain de niveau associé ne prouve pas une résolution correcte du problème original.
- **Session 2, E1 :** exercice 17.12 (2/5) directement proposé après reconnexion. Le compte conserve bien les acquisitions de cours.
- **Session 2, E7–E13 :** exercice 17.13 (3/5), règle de Cauchy. L'application affichée et discutée comporte un facteur (n+1)/(2n+5) multipliant a_n, tandis que la page PDF 49 contient ((n+1)/(2n+5))^n. Le problème travaillé a changé.
- **Session 2, E14 :** HTTP 502, connexion à Pipelex interrompue lors de la récupération d'une évaluation. Aucune nouvelle réponse du tuteur. E15 reprend après redémarrage du serveur et reconnexion avec le même compte ; l'incident et la reprise comptent dans les 20 échanges.
- **Session 2, E15 :** « Commençons par le cours. Donnez-moi la définition d'une série convergente. » Cette question déjà acquise en S1 E4 est redemandée sans nouvelle tâche, alors que l'état affiche « Exercices du catalogue ».
- **Session 3, E1 et E11 :** l'exercice 17.6, validé en S1 E15, est reproposé dans le dialogue sans nouvelle tâche. Le premier exercice enregistré de S3 n'arrive qu'à E6 (17.11, 3/5). Le premier exercice *visible* est bien E1.
- **Session 3, E9/E10 :** le tuteur annonce « Fin de l'étude de cette série », propose de changer, puis refuse de passer à un nouvel exercice au tour suivant. E18/E19 répètent une contradiction similaire entre offre de nouvel exercice et blocage de transition.
- **Session 4, E1 :** nouvelle répétition de l'exercice 17.6, sans nouvelle tâche ; premier exercice enregistré à E5 (17.15, 3/5).
- **Session 4, E7–E8 :** pour montrer n a_n → 0, le dialogue établit n a_(2n) → 0 puis prétend disposer d'un encadrement suffisant de n a_n. La borne supérieure tendant vers zéro n'est pas obtenue dans la chaîne présentée ; le tuteur la déclare pourtant complète. Une preuve correcte peut séparer les indices pairs/impairs ou utiliser la somme entre floor(n/2) et n, mais ce passage manque dans la réponse validée.

## Limites du protocole

Le tuteur, le serveur HTTP et les APIs sont réels. L'élève est joué par un modèle à partir du dialogue visible. Les comportements demandés sont cycliques et consignés dans les fichiers *-protocole.json ; ils ne garantissent pas le taux de réussite réalisé. Certaines réponses du profil faible sont nettement plus développées qu'attendu. Les verdicts de l'évaluateur ne constituent pas une vérité mathématique, comme le montrent les contradictions ci-dessus.

Les sessions sont plafonnées à 20 échanges, et ne signifient pas que chaque exercice ou colle est achevé. Le même compte est conservé entre sessions et profils : l'ordre des profils influence l'accès aux exercices, les acquis et le niveau initial. Cela empêche d'attribuer causalement une différence de progression au seul profil.
