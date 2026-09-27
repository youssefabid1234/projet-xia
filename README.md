# Colle de maths : simulateur de khôlle pour la prépa scientifique

Application web qui fait passer une colle orale de mathématiques : le colleur
interroge l’élève sur le cours, lui fait démontrer un résultat, puis lui donne
des exercices adaptés à son niveau. Il fait chercher, donne des indices gradués,
corrige si besoin et termine par une note indicative sur 20 et un bilan.

Le barème reste fixe : question de cours sur 3, démonstration sur 4,
application du cours sur 5, puis exercices sur 3, 3 et 2 points.
Chaque tâche rapporte son barème multiplié par son score ; les tâches non
atteintes rapportent zéro sans être présentées comme des échecs.
L'évaluation cumule les réponses et précisions de l'élève sur la tâche.
Chaque indice multiplie le score par 0,9, sans pénalité supplémentaire de reprise.

- `app/` : moteur de colle, colleur (LLM), évaluation, profils, interface web, tuteur en terminal.
- `methods/` : méthodes Pipelex (évaluation d’une réponse, ancienne décision de progression).
- `data/` : cours indexé, banque de questions de cours, catalogue d’exercices et leur vérification.
- `scripts/` : extraction et indexation du cours, préparation des données, simulation en terminal.

## Installation sur Windows

Prérequis : Git et Python **3.12 64 bits** avec le lanceur `py`, une clé API
OpenAI (indispensable) et une clé Pipelex (interface classique et mode d’évaluation Pipelex).

```powershell
git clone https://github.com/youssefabid1234/projet-xia.git
cd projet-xia
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configuration

Copier `.env.example` en `.env` à la racine et y renseigner les clés. Le fichier
`.env` est **chargé automatiquement** au lancement (les variables déjà définies
dans l’environnement restent prioritaires). Il est ignoré par Git : ne jamais
mettre de vraie clé dans `.env.example`, qui est versionné.

| Variable | Rôle |
|---|---|
| `OPENAI_API_KEY` | Colleur, analyse des messages, évaluation locale, recherche dans le cours. |
| `PIPELEX_API_KEY` | Interface classique, tuteur en terminal, mode `COLLE_EVALUATEUR=pipelex`. |
| `OPENAI_MODEL` | Modèle utilisé (défaut `gpt-4.1-mini`). |
| `FLASK_SECRET_KEY` | Valeur secrète stable pour garder les sessions après un redémarrage. |
| `COLLE_EVALUATEUR` | `local` (défaut) ou `pipelex` : voir « Évaluation » ci-dessous. |
| `COLLE_DUREE_MINUTES` | Durée d’une colle (défaut 30). |

## Lancement

```powershell
.\.venv\Scripts\python.exe -m app.web
```

Ouvrir http://127.0.0.1:5000, créer un compte, puis cliquer sur « Commencer ».
Au démarrage, le serveur préchauffe les connexions OpenAI en arrière-plan
(5 à 15 s dans un processus neuf) : le premier élève n’attend donc pas.
Un seul processus serveur à la fois (stockage JSON local, port 5000).

Autres points d’entrée :

```powershell
# Colle en terminal, avec mesure de la latence de chaque tour (profil temporaire).
.\.venv\Scripts\python.exe -m scripts.simuler_colle
# Tuteur minimal en terminal, par l'API Pipelex.
.\.venv\Scripts\python.exe -m app.tuteur
```

Dans `simuler_colle`, `/juste` envoie la réponse attendue (pour parcourir toute
la colle rapidement) et `/bilan` termine la colle.

## Déroulé d’une colle

1. **Cours** : une définition, puis un énoncé de théorème.
2. **Démonstration** : la preuve courte d’un résultat du cours.
3. **Application** : un exemple du cours à traiter.
4. **Exercices** du catalogue, jusqu’à la fin du temps.

Règles, appliquées par le serveur (`app/colle.py`) et non par le modèle :

- une réponse juste clôt la question ; la suivante s’affiche aussitôt ;
- une erreur est signalée sans donner la réponse et l’élève doit corriger ;
- les indices sont gradués ; le colleur donne la correction sur demande, ou
  après 3 indices, ou après 3 réponses fausses ou incomplètes (en exercice :
  4 indices ou 4 erreurs, une réponse partielle sans erreur n’étant qu’une étape) ;
- une question corrigée est remplacée par une autre de même nature : on ne passe
  pas à l’étape suivante sans acquisition ; après 3 questions corrigées sur une
  étape, le colleur avance et le bilan le signale ;
- une demande de saut d’étape est refusée ; en exercice, elle vaut demande de correction ;
- les questions réussies (profil) ne sont jamais reposées, même dans une colle ultérieure ;
- aux exercices, une réussite autonome vise une difficulté supérieure, une
  correction donnée une difficulté inférieure ; le niveau du profil évolue comme avant.

La colle en cours est sauvegardée après chaque tour (`data/profils/<élève>.colle.json`)
et reprend après un rechargement de la page ou un redémarrage du serveur. Le
bilan est archivé dans le profil (`colles`) et affiché sur la page d’accueil.

## Fonctionnement d’un tour

Pour chaque message de l’élève (`app/examinateur.py`) :

1. **en parallèle**, un appel court classe l’intention (réponse, demande d’indice,
   blocage, demande de correction, question de cours, demande de saut, hors sujet)
   et l’évaluateur compare la réponse à la référence ; l’évaluation est abandonnée
   si le message n’est pas une réponse ;
2. le serveur décide de l’action (valider, signaler l’erreur, indice, correction…) ;
3. le colleur formule sa réaction, **diffusée mot à mot** (flux NDJSON) ; si la
   question est close, le serveur affiche lui-même la question suivante.

La référence (réponse attendue ou corrigé) est donnée au colleur en consigne
privée et ne doit être dévoilée qu’au moment de la correction. Pour une question
de cours posée par l’élève, le colleur interroge l’index du cours (embeddings +
BM25, `app/cours.py`) et cite la source (« Théorème 16.2.4, page PDF 143 ») ;
tout complément absent des extraits est précédé de « Hors du cours extrait : ».

Latence mesurée (gpt-4.1-mini, serveur préchauffé) : **1 à 4 s avant le premier
mot affiché**, 1,5 à 4,5 s pour le tour complet. L’ancien agent mettait environ
47 s par tour et échouait à chaque réponse d’élève (voir « Historique »).

## Données

- `data/questions_cours.json` : 50 questions de cours (12 définitions, 20 théorèmes,
  10 démonstrations, 8 applications) avec leur réponse attendue en LaTeX, vérifiée
  sur les pages du PDF. Chaque question renvoie à un passage de `data/cours_index.json`.
  Priorité 1 = grand classique de colle, posé en premier.
- `data/exercices.json` : catalogue brut extrait du PDF (non modifié).
- `data/enonces_verifies.json` : pour chaque exercice, résultat de la vérification
  privée (`app/enonces.py`) : énoncé et corrigé retranscrits en LaTeX propre, ou
  exercice écarté si une formule reste ambiguë. 20 exercices de séries sur 31 sont
  exploitables. Le cache est invalidé si le texte du catalogue change ; un
  exercice absent du cache est vérifié à la volée au moment de le proposer.

```powershell
# Vérifier d'avance les exercices (un appel OpenAI par exercice non encore vérifié).
.\.venv\Scripts\python.exe -m scripts.verifier_enonces --chapitre 17
# Retenter les exercices écartés avec un modèle plus fort.
.\.venv\Scripts\python.exe -m scripts.verifier_enonces --ecartes --modele gpt-4.1
```

Seul le chapitre des séries a un cours indexé et une banque de questions
(`app/chapitres.py`, dictionnaire `COLLES`). Pour ouvrir un autre chapitre :
indexer son cours (voir [scripts/COURS.md](scripts/COURS.md)), écrire sa banque de
questions au même format, vérifier ses exercices, puis l’ajouter à `COLLES`.

## Évaluation

La méthode `methods/evaluation_maths_prepa/main.mthds` reste la seule source des
consignes de correction. Elle s’exécute de deux façons (`app/evaluation.py`) :

- `COLLE_EVALUATEUR=local` (défaut) : le système, le prompt et le schéma de sortie
  sont lus dans le fichier `.mthds` et envoyés directement à OpenAI en sortie
  structurée : 1 à 3 s ;
- `COLLE_EVALUATEUR=pipelex` : exécution par l’API Pipelex hébergée, 7 à 22 s par
  réponse mesurées, quel que soit le modèle choisi. Dans ce mode, l’évaluation
  n’est lancée qu’après l’analyse du message, pour ne pas payer une évaluation
  Pipelex sur une demande d’indice.

L’interface classique (`/classique`) et le tuteur en terminal utilisent toujours
l’API Pipelex. Le client Pipelex est désormais partagé entre les requêtes et
interrogé toutes les 0,5 s au lieu de 2 s.

La méthode `methods/progression_colle` n’est plus appelée pendant la colle : sa
décision (15 à 26 s mesurées) était de toute façon contrainte par le serveur, et
les règles sont maintenant explicites dans `app/colle.py`. Elle et ses types
générés (`app/generated/progression_colle`) sont conservés.

## Interface web

`app/web/` : Flask, API JSON (`/api/colle`, `/api/message`, `/api/bilan`,
`/api/nouvelle`, `/api/etat`) et page unique (`templates/chat.html`,
`static/colle.js`, `static/colle.css`). Les requêtes Flask déposent leur travail
sur une boucle asyncio partagée (`app/services.py`) qui garde les clients OpenAI
et Pipelex ouverts ; un seul tour à la fois par élève, sans bloquer les autres.
Les formules sont rendues par [KaTeX](https://katex.org/docs/autorender) (CDN),
y compris en aperçu pendant la saisie. Thèmes clair et sombre, affichage mobile.

Les comptes sont dans `data/utilisateurs.json` (mots de passe hachés par
Werkzeug), les profils dans `data/profils/<identifiant>.json` ; ces données sont
ignorées par Git. L’ancienne interface d’exercices reste sur `/classique`.

## Tests

Tests hors ligne (services simulés par `app/faux.py`, aucun crédit consommé) :

```powershell
.venv/Scripts/python.exe -m unittest app.test_colle app.test_examinateur app.test_enonces app.test_evaluation app.test_cours app.test_chapitres app.web.test_web app.web.test_chat app.web.test_auth scripts.test_lister_formules_coupees
```

## Repérer les formules coupées dans les énoncés

```powershell
python scripts/lister_formules_coupees.py --sortie data/enonces_a_verifier.md
```

Le rapport contient les identifiants, pages sources, lignes suspectes et énoncés
complets numérotés. Le script ne modifie pas `data/exercices.json`. La détection
est heuristique. Ajouter `--tous-multilignes` pour inclure tous les énoncés
multilignes, ou `--format json` pour un rapport exploitable en code.

## Historique : pourquoi le moteur a été refait

Mesures faites sur l’ancien agent (`app/agent.py`, supprimé), avec les vraies API :

- l’outil `observer_tour` déclarait ses indicateurs comme texte libre ; le modèle
  y écrivait la phrase de l’élève au lieu de « oui »/« non », le serveur refusait,
  le modèle réessayait six fois puis le tour échouait : **toute réponse d’élève
  sur une question de cours finissait en erreur 502** ;
- chaque réponse enchaînait une évaluation Pipelex (8 à 19 s) puis une décision
  Pipelex (15 à 26 s), plus plusieurs appels OpenAI : environ 47 s par tour ;
- un verrou global sérialisait tous les élèves pendant ces appels ;
- un message renvoyé après une erreur était enregistré et évalué deux fois ;
- chaque énoncé d’exercice était revérifié par un appel OpenAI à chaque proposition.
