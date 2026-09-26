# 100 cas pour un khôlleur qui fait réagir

But : vérifier qu'après une proposition, le khôlleur pose un défi utile, écoute
la réaction et adapte la suite. Il évalue en interne sans commencer par « tu as
raison / tort ». Une justification suffisante doit permettre de progresser ; le
challenge ne doit pas devenir une boucle.

## Ce qui est fourni

- `banque.py` : 100 situations rédigées, 10 familles de 10, sur les séries.
- `donnees/cas_100.json` : export exploitable par un autre programme.
- `donnees/scenarios_100.md` : fiches à lire et discuter avec Abid.
- `consigne.md` : proposition de consigne pour le khôlleur, activable lors des essais.
- `banc.py` : validation, export, lancement du véritable `app.agent.Agent` et traces.
- `test_banc.py` : tests hors ligne du banc, avec appels réseau simulés.

Chaque cas possède une question, une référence mathématique privée, une réponse
initiale, un objectif, un exemple de relance et trois réactions distinctes :
justification, erreur persistante, blocage. Les exemples sont des possibilités,
pas des phrases à reproduire. Les références et catégories ne sont pas envoyées
au khôlleur comme messages de l'élève ; la référence sert de corrigé privé au
mécanisme d'évaluation existant.

Les familles : définitions, comparaisons, calculs exacts, Riemann/intégrales,
alternance, développements, restes, paramètres, raisonnements et interaction.
Le niveau va des bases aux relances de prépa ; le lot ne prétend pas que les 100
questions sont toutes du niveau d'un oral Mines-Ponts ou Centrale. Aucun énoncé
n'est attribué à une annale officielle. Une relecture mathématique par enseignant
reste utile avant d'en faire une référence définitive.

## Démarrer sans dépenser de crédits

Depuis la racine de `projet-xia`, avec Python 3.12 :

```bash
.venv/bin/python -m evals_kholleur verifier
.venv/bin/python -m evals_kholleur exporter
.venv/bin/python -m unittest evals_kholleur.test_banc -v
.venv/bin/python -m evals_kholleur executer --tous --phase tout --simuler
```

Sur Windows remplacer `.venv/bin/python` par `.venv\Scripts\python.exe`.
La dernière commande prépare 400 sondes : 100 premières relances et 300 réactions.
Elle n'appelle aucun modèle. La vérification de structure des 100 cas et les tests
du banc ne signifient jamais que le tuteur a réussi 100 scénarios réels.

## Essayer le vrai tuteur

Il faut les dépendances du dépôt, `OPENAI_API_KEY` et `PIPELEX_API_KEY` dans
l'environnement du terminal. Le banc n'utilise pas les clés gardées uniquement
dans le processus du serveur web. `OPENAI_MODEL` reste le réglage habituel du
dépôt. Ne pas stocker de clé dans les fichiers de ce dossier.

Un premier cas avec la consigne actuelle :

```bash
.venv/bin/python -m evals_kholleur executer --ids K001 --phase initiale --sortie evals_kholleur/resultats/actuelle-k001.jsonl
```

Puis comparer le même cas avec la proposition de consigne :

```bash
.venv/bin/python -m evals_kholleur executer --ids K001 --phase initiale --consigne defi --sortie evals_kholleur/resultats/defi-k001.jsonl
```

Le complément est appliqué seulement pendant l'essai. Le prompt de production,
le serveur en cours et les profils d'élèves restent inchangés.

Pour vérifier spécifiquement la réponse à une justification et à une erreur :

```bash
.venv/bin/python -m evals_kholleur executer --ids K002 K045 K096 K100 --phase reactions --branche toutes --consigne defi --sortie evals_kholleur/resultats/reactions.jsonl
```

Un lancement réel consomme les crédits des appels OpenAI et éventuellement
Pipelex : une sonde peut effectuer plusieurs appels, dont recherche dans le cours,
évaluation et décision. Le banc exige une sélection explicite : `--ids` ou
`--tous`. Pour le lot complet, `--tous --phase tout` produit jusqu'à 400 sondes ;
commencer par quelques cas pour mesurer les coûts et repérer les défauts. Une
erreur fournisseur est enregistrée comme erreur d'exécution, jamais comme faute
de l'élève. Le fichier de sortie ne doit pas déjà exister.

## Protocole : ce que mesure ce banc

**Sonde initiale** : une tâche synthétique est enregistrée côté serveur et la
première réponse de l'élève est envoyée au vrai tuteur. On observe sa relance.

**Sonde de réaction** : une nouvelle tâche isolée est créée avec l'historique
« question → première réponse → relance de référence ». On envoie ensuite la
réaction choisie et on observe la réponse du tuteur. Les trois branches partent
de cet historique commun. On ne donne jamais à l'agent une réponse préécrite qui
prétendrait répondre à une relance différente qu'il vient de produire librement.

Ce protocole contrôle la pertinence d'une relance et la prise en compte du tour
précédent. Il **ne mesure pas** la réussite d'une khôlle libre de bout en bout,
l'inscription, la sélection initiale du chapitre, ni les transitions complètes
cours → démonstration → applications → exercices. Les tâches sont initialisées
au stade exercices pour isoler le dialogue. Les autres compteurs ne simulent pas
des évaluations déjà faites. Un bon résultat ici ne suffit donc pas à valider
l'ensemble de la plateforme.

Chaque sonde utilise un profil temporaire différent, puis conserve la réponse,
la tâche testée avant/après, les évaluations et la décision dans la trace. Même si
le tuteur ouvre une autre tâche, la tâche initiale reste celle inspectée. Les
profils temporaires sont supprimés après récupération des traces.

## Grille de relecture

Chaque trace contient six notes initialement `null` :

| Critère | 0 : insuffisant | 1 : acceptable | 2 : solide |
|---|---|---|---|
| Exactitude mathématique | Assertion ou objection fausse | Mathématiques justes avec imprécision mineure | Hypothèses et raisonnement précis |
| Défi ciblé sans verdict initial | Verdict seul, réponse donnée ou faux piège | Question pertinente mais peu ciblée | Une relance précise sur l'idée de l'élève |
| Indice proportionné | Solution dévoilée sans demande ou aide inutilisable | Aide utilisable | Le plus petit pas adapté au blocage |
| Prise en compte de la réaction | Ignore la réponse ou l'auto-correction | Répond au contenu principal | Distingue justification, erreur et blocage, et ajuste |
| Progression sans boucle | Répète le même défi après justification | Poursuit avec quelques répétitions | Accepte ce qui est établi et choisit la suite utile |
| Ton et clarté | Humiliation, pression arbitraire ou confusion | Respectueux et compréhensible | Bref, précis, une demande à la fois |

Pour la sonde initiale, « prise en compte » porte sur la première réponse et son
éventuel historique. Un indice ou une nouvelle question n'est pas exigé quand
ce serait inutile. Une correction complète explicitement demandée (K095) est
compatible avec la règle, à condition de vérifier ensuite la compréhension.
Une réponse déjà justifiée peut être suivie d'une extension, pas d'une objection
fabriquée. Le critère de progression combine dialogue et état sauvegardé :
observer notamment si une justification est évaluée, si une erreur a été
reformulée, et si une autorisation de poursuivre est cohérente.

Le script ne réduit pas ces critères à une recherche de mots ou à la présence
d'un point d'interrogation. Ses drapeaux lexicaux sont seulement des invitations
à relire. Une phrase contenant « faux » dans une question mathématique n'est pas
automatiquement un échec. Aucune note pédagogique n'est inventée par le banc.

Pour conclure une relecture, renseigner dans la trace `relecture.relecteur`,
`relecture.statut` à `relue`, les six notes entières 0/1/2 et un commentaire qui
cite le passage concerné. Une sonde est réussie seulement si elle est relue et
que tous les critères atteignent au moins 1. Un seul 0 suffit à signaler un échec ;
une trace incomplètement notée reste « à relire ».

```bash
.venv/bin/python -m evals_kholleur resumer evals_kholleur/resultats/reactions.jsonl
```

## Réactivité de l'élève

Le banc stocke séparément `latence_execution_secondes` (temps du programme/API)
et `temps_reaction_eleve_secondes` (laissé à `null` ici). Des réponses synthétiques
préécrites ne permettent pas de mesurer un élève qui réagit vite. Pour cela, il
faudra une séance réelle et mesurer le délai entre la fin de la question et le
début de sa réponse, avec pauses et contexte. Une réponse rapide et fausse ne
vaut pas une réponse réfléchie et argumentée ; aucun seuil universel de vitesse
n'est utilisé pour attribuer la maîtrise.

## Modifier un cas et contribuer

Modifier le cas correspondant dans `banque.py`, puis régénérer les deux exports
avec `exporter`. Vérifier le lot et lancer les tests. Les fichiers de résultats
sont ignorés par Git pour garder les traces personnelles hors de la contribution.
Ce dossier peut faire l'objet d'une pull request distincte ; aucune modification
n'est publiée automatiquement.
