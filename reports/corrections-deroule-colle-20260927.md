# Déroulé et notation de la colle — 27 septembre 2026

## État constaté avant les corrections

Le moteur demandait trois acquisitions de cours (plafond cinq questions), une
démonstration (plafond deux), une application (plafond trois), puis des exercices
sans plafond. La fin du temps ou du catalogue invitait à cliquer sur « Terminer ».
Le renvoi au cours affichait des titres numérotés et des pages PDF ; le prompt de
recherche demandait aussi explicitement ces citations. Les corrections rendues par
le serveur donnaient directement la réponse attendue.

La mémoire excluait les questions acquises et les exercices vus, mais favorisait
les notions fragiles sans limiter les anciennes questions non acquises.

La note était déjà calculée par `note_bilan`, à partir des scores des tâches.
Le compte rendu était une génération du modèle : il recevait question, statut,
score, aides, erreurs, durée, difficulté, notions et dernier avis. La consigne lui
interdisait de changer la note, mais ses points forts et conseils n'étaient pas
déterminés par des seuils.

## Comportement corrigé

- Une question de cours, une démonstration, une application directe, trois exercices
  au maximum, même en cas d'échec. Une phase sans contenu admissible est sautée.
- Clôture, bilan et prise de congé automatiques à la fin du programme ou du temps.
  Le navigateur déclenche le bilan à zéro, après le tour courant s'il est occupé ;
  le serveur vérifie également le temps à chaque tour et avant une nouvelle tâche.
- Rappel du cours en langage naturel ; références conservées dans le contexte privé.
  Les textes publics sont filtrés, y compris les questions et les anciens messages
  du colleur. Les réponses générées sont assemblées avant diffusion pour éviter une
  fuite de référence répartie entre plusieurs fragments.
- Chaque correction imposée commence par l'explication enregistrée pour l'élément
  concerné, avant sa réponse attendue. Après une demande d'aide, le dernier diagnostic
  de cet élément est conservé. Sans tentative, le message constate l'absence de réponse
  sans inventer une erreur. L'évaluateur reçoit la demande explicite d'expliquer pourquoi.
- Une reprise réservée par colle : la tâche disponible du chapitre ayant le score
  historique minimum strictement inférieur à 40 %, jamais acquise depuis. Elle peut
  être le cours, la démonstration, l'application ou un exercice et occupe une place
  du format normal. Son identité est persistée pour les reconnexions. Les autres
  tâches sont inédites ; les notions jamais rencontrées passent avant les notions
  déjà rencontrées. Aucune autre ancienne question n'est sélectionnée.
  Sans antécédent admissible, il n'y a pas de reprise. Une clôture anticipée peut
  naturellement survenir avant la phase de la reprise.
- Compte rendu entièrement déterministe : scores par tâche, aides, tentatives,
  points forts à partir de 80 %, éléments à retravailler sous 80 %, conseil ciblé
  sur la tâche au score minimum. Aucun appel de génération pour le bilan.

## Calcul exact conservé

Pour chaque élément résolu (tâche autonome ou étape d'exercice) :

`score = max(0, 0,7 × verdict + 0,3 × intuition − 0,15 × aides − 0,05 × max(0, tentatives − 1))`

| Entrée | Valeur |
|---|---:|
| Verdict correcte / incomplète / incorrecte | 1 / 0,6 / 0,2 |
| Intuition solide / partielle / absente | 1 / 0,5 / 0 |

Le dernier avis exploitable de l'élément est utilisé. Une correction donnée plafonne
son score à 0,25 ; sans avis, une réponse donnée vaut zéro. Un avis indéterminable
ne reçoit pas de score. Les aides comprennent les indices, les rappels du cours,
les réponses aux questions de compréhension et l'entrée dans le guidage.

Pour un exercice guidé : moyenne des scores des étapes notées, moins 0,15 par aide
reçue pendant la tentative autonome, avec plancher à zéro. Si le colleur a donné
une réponse, le score de toute la tâche est plafonné à 0,25. Arrondi à quatre décimales.

La note sur 20 est la moyenne des scores par phase, pondérée ainsi :

| Phase | Poids sur 20 |
|---|---:|
| Cours | 6 |
| Démonstration | 4 |
| Application | 5 |
| Exercices (moyenne des exercices notés) | 5 |

`note = 20 × somme(poids × moyenne de phase) / somme(poids des phases notées)`

Arrondi au dixième. Une phase sans tâche notée est exclue et les poids sont
renormalisés. Une tâche interrompue ne compte pas comme zéro. Aucune tâche notée :
pas de note. La durée et la difficulté ne pondèrent pas directement la note.

Le modèle continue de juger le verdict et l'intuition des réponses : ces jugements
alimentent le score. Il ne choisit ni les coefficients, ni la note finale, ni les
catégories du compte rendu.

## Vérification

- `python -m unittest discover -s app` : 105 tests réussis, services externes simulés.
- `node --check app/web/static/colle.js` : syntaxe valide.
- Exécution isolée du minuteur et de la clôture JavaScript : à zéro, un seul appel
  au bilan, sans confirmation ; aucun second appel pendant le traitement.
- Régressions couvertes : six tâches et fin automatique, expiration du temps,
  trois exercices même en échec, pire résultat réservé après reconnexion,
  priorité aux notions nouvelles, explication avant réponse, références coupées
  entre fragments, bilan indépendant des commentaires du modèle.
