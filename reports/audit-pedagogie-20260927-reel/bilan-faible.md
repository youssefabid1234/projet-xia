# Premier lot — quatre sessions du profil faible

Les quatre conversations sont issues du vrai serveur HTTP, du vrai agent et de ses appels OpenAI/Pipelex. Aucun tuteur, outil ni évaluateur n'est simulé. L'élève est joué par un modèle. Le compte `audit-longitudinal` est conservé sans remise à zéro. Le code du tuteur n'a pas été modifié pendant l'audit.

| Session | Conversation | Premier exercice du catalogue visible | Premier exercice nouveau enregistré | Niveau avant → après |
|---|---|---:|---:|---|
| 1 | [Lire les 20 échanges](faible-session-1.md) | E14 | E14 | 1,5 → 2,4 |
| 2 | [Lire les 20 échanges](faible-session-2.md) | E1 | E1 | 2,4 → 2,9 |
| 3 | [Lire les 20 échanges](faible-session-3.md) | E1, répétition | E6 | 2,9 → 2,8 |
| 4 | [Lire les 20 échanges](faible-session-4.md) | E1, répétition | E5 | 2,8 → 3,0 |

E1 compte la sélection du chapitre et la première réponse. La session 2 inclut un HTTP 502 à E14 et une reconnexion à E15 après relance du serveur. Les sessions atteignent le plafond de 20 échanges ; cela ne signifie pas que toutes les tâches sont achevées.

Le seuil « avant E10 » n'est pas satisfait en session 1 pour un exercice exploitable du catalogue. Une application est annoncée à E9, sans préciser la série à étudier. Les sessions suivantes accèdent immédiatement aux exercices grâce au profil conservé, mais les sessions 3 et 4 commencent par une répétition indue.

## Questions et exercices

En S1 : définition d'une série convergente à E1 (acquise E4), énoncé « convergence absolue implique convergence » à E4 (acquis E5), démonstration à E5 (acquise E9), puis application à la convergence absolue/conditionnelle à E9 (acquise E13). En S2 E15, la définition déjà validée est redemandée. Aucune nouvelle tâche de cours n'est enregistrée en S2–S4 ; les questions sur le cours dans les exercices sont des demandes de justification, pas un nouveau diagnostic complet.

| Session | Exercices proposés, difficulté du catalogue |
|---|---|
| 1 | E14 : 17.6, somme de logarithmes et série inverse, **2/5** ; E16 : 17.9, produit de (1−εᵢ), **3/5** ; E18 : 17.20, suite complexe et sommes pondérées, **4/5**, énoncé altéré. |
| 2 | E1 : 17.12, comparaison de uₙ et uₙ/(1+uₙ), **2/5** ; E7 : 17.13, règle de Cauchy, **3/5**, application altérée ; E16 : 17.14, (nα)ⁿ / somme des k!, **3/5**. |
| 3 | E1 puis E11 : reprise de 17.6, **2/5**, déjà validé ; E6 : 17.11, combinaison de racines carrées, **3/5** ; E12 : 17.16, condensation de Cauchy et séries de Bertrand, **3/5**. |
| 4 | E1 : reprise de 17.6, **2/5**, déjà validé ; E5 : 17.15, suite décroissante sommable et n aₙ → 0, **3/5** ; E9 : 17.18, n^α / produit des (1+aᵏ), **3/5**. E18 annonce une reprise du 17.13 non clôturé, mais E19 lui attribue en fait la formule du 17.18. |

## Progression et fiabilité

Le score passe de **1,5 à 3,0** : gains successifs **+0,9 ; +0,5 ; −0,1 ; +0,2**. Ce score ne mesure pas directement l'apprentissage : il est modifié à la première évaluation d'un exercice (correcte +0,3, incomplète +0,1, incorrecte −0,2), puis ne reflète pas nécessairement les rectifications ultérieures. Les quatre acquisitions de cours/démonstration/application de S1 ne modifient pas ce score.

Les verdicts des évaluations, y compris les réévaluations, sont :

| Session | Correctes | Incomplètes | Incorrectes |
|---|---:|---:|---:|
| 1 | 7 | 4 | 4 |
| 2 | 2 | 4 | 0 |
| 3 | 2 | 1 | 3 |
| 4 | 3 | 3 | 1 |

Ils ne correspondent ni à un taux de réussite sur tous les messages, ni à une vérification indépendante de la correction mathématique. L'élève faible généré produit parfois des réponses trop élaborées ; la fidélité du profil est imparfaite.

Le tuteur sait donner des pistes et demander une reformulation, mais l'audit met en évidence :

1. Des questions/exercices acquis reposés, parfois hors de tout enregistrement de tâche.
2. Des corrections contradictoires avec la réponse de l'élève (S1 E11).
3. Des données mathématiques altérées lors de la reconstruction des énoncés (17.20 et 17.13, vérifiés sur le PDF).
4. Des preuves incomplètes ou injustifiées validées (S1 E20, S4 E8).
5. Des annonces de fin ou de passage à la suite ensuite contredites par un blocage serveur (S3 E9–E10, E18–E20 ; S4 E16–E17).

La comparaison avec le profil fort n'est pas encore disponible dans ce premier lot. Elle devra tenir compte du même compte partagé, de l'ordre de passage, des répétitions et des validations erronées. Voir les [observations avec références précises](observations-relues.md) et le [relevé automatique](releve-factuel.md).
