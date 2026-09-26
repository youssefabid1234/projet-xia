# Agent tuteur pour la prépa scientifique

Projet Python d’agent tuteur destiné aux élèves de classes préparatoires scientifiques.
Il vise à accompagner les élèves dans la compréhension des cours et la résolution d’exercices.

- `methods/` : méthodes Pipelex.
- `app/` : profil élève, tuteur en terminal et interface web.
- `.env.example` : variables d’environnement à renseigner dans un fichier `.env` local.

## Interface web

Depuis la racine du projet, dans PowerShell :

```powershell
python -m venv --system-site-packages .venv
.venv/Scripts/python.exe -m pip install -r app/web/requirements.txt
$env:PIPELEX_API_KEY = "votre-cle"
$env:OPENAI_API_KEY = "votre-cle-openai"
# Facultatif : modèle utilisé par le dialogue et la vérification des tentatives.
$env:OPENAI_MODEL = "gpt-4.1-mini"
.venv/Scripts/python.exe -m app.web
```

Ouvrir http://127.0.0.1:5000 pour discuter en français avec le tuteur.
Demander un exercice dans un chapitre, partager une piste, demander un indice
ou consulter son niveau. Le tuteur encourage la recherche avant de donner des
indices progressifs. Les messages d’aide ou d’abandon ne sont pas des copies à
corriger ; les réponses mathématiques courtes et les raisonnements partiels le sont.

L’ancienne interface reste accessible sur http://127.0.0.1:5000/classique,
avec le même formulaire, les mêmes corrections et la même progression.
Le tuteur en terminal (`python -m app.tuteur`) reste également disponible.

L’interface Flask se trouve dans `app/web/`. L’agent dans `app/agent.py` utilise
l’API Responses OpenAI et ses trois outils : `proposer_exercice(chapitre)`,
`consulter_niveau(chapitre)` et `chercher_dans_cours(question)`.
La recherche utilise les 80 passages de séries numériques dans
`data/cours_index.json` et renvoie leurs pages sources. Elle combine embeddings
OpenAI et recherche lexicale ; voir [les commandes et tests du cours](scripts/COURS.md).
Les instructions du tuteur imposent cette recherche avant toute réponse sur une
notion, définition, méthode ou théorème, avec citation du passage et de sa page PDF.
Tout complément absent des extraits doit porter la mention « Hors du cours extrait : ».
Avant chaque proposition dans le chat, `app/enonces.py` vérifie l'énoncé avec le
corrigé du catalogue dans un appel OpenAI privé. Il remet les formules en LaTeX
uniquement si leur lecture est certaine ; sinon l'agent passe silencieusement au
candidat suivant, selon le même ordre de niveau. La vérification par modèle reste
probabiliste, avec consigne de refuser au moindre doute.
Les exercices écartés restent exclus pour cette conversation sans être comptés
comme vus. Le catalogue n'est pas modifié et le corrigé n'entre pas dans
l'historique du dialogue. Une panne de vérification laisse le candidat réessayable.
L'énoncé validé est conservé dans l'exercice actif : la correction utilise ce
texte exact et ne relance jamais la vérification ou la reconstruction.
Cette préparation consomme un appel OpenAI par candidat examiné.
Le choix et la lecture du niveau utilisent `app/profil.py`, l’évaluation réutilise
la méthode existante via `app/evaluation.py`. Le function calling suit la
[documentation officielle OpenAI](https://developers.openai.com/api/docs/guides/function-calling).
L'évaluation reçoit `enonce`, `reponse_eleve` et le champ `corrige` du catalogue,
réservé aux appels privés de vérification et d'évaluation. Elle compare la copie à ce corrigé vérifié ; elle ne
reconstruit plus de référence. Un corrigé absent ou vide bloque l'appel ; une
ambiguïté empêchant la comparaison doit produire `indeterminable`.
Avant une correction, une vérification indépendante par le modèle contrôle que
le message constitue une tentative. Cette classification reste probabiliste.
Le serveur exige aussi l’énoncé actif et le message exact de l’élève.

Chaque échange consomme du crédit OpenAI ; seules les tentatives évaluées
consomment aussi du crédit Pipelex. Les clés restent côté serveur ; le fichier
`.env` n’est pas chargé automatiquement. Sans clé OpenAI, l’ancienne interface
reste utilisable avec la clé Pipelex seule.

Les conversations sont isolées par session de navigateur et conservées en mémoire
(au plus 100 discussions, 60 échanges par discussion). Un redémarrage les efface.
« Nouvelle discussion » efface le dialogue courant, sans effacer le profil.

L’interface web demande une inscription ou une connexion. Les comptes sont dans
`data/utilisateurs.json`, avec des mots de passe hachés par Werkzeug. Chaque élève
a son profil dans `data/profils/<identifiant>.json`. Ces données sont ignorées par Git.
La session Flask conserve la connexion ; « Se déconnecter » la termine.
Définir `FLASK_SECRET_KEY` avec une valeur secrète stable pour conserver les sessions
au redémarrage (sinon une clé aléatoire est créée à chaque lancement).
Utiliser un seul processus serveur pour ce stockage JSON local.
Le tuteur en terminal conserve son fichier `data/profil.json` indépendant.
Le profil web est sauvegardé après chaque correction
valide ; les exercices déjà traités ne sont plus proposés. Dans le chat,
retravailler un exercice déjà enregistré ne modifie pas à nouveau le niveau.

Les formules des énoncés et explications sont rendues avec
[KaTeX auto-render](https://katex.org/docs/autorender), chargé depuis un CDN
(connexion Internet nécessaire). Les délimiteurs `$…$`, `$$…$$`, `\(…\)`
et `\[…\]` sont pris en charge. Le texte reste lisible si le CDN est inaccessible.

Tests hors ligne, avec Pipelex simulé et un profil temporaire :

```powershell
.venv/Scripts/python.exe -m unittest app.test_agent app.test_enonces app.test_evaluation app.web.test_web app.web.test_chat app.web.test_auth scripts.test_lister_formules_coupees
```

## Repérer les formules coupées dans les énoncés

```powershell
python scripts/lister_formules_coupees.py --sortie data/enonces_a_verifier.md
```

Le rapport contient les identifiants, pages sources, lignes suspectes et énoncés
complets numérotés. Le script ne modifie pas `data/exercices.json` : corriger son
champ `enonce` à la main en consultant le PDF. La détection est heuristique et peut
signaler une formule multiligne valide. Ajouter `--tous-multilignes` pour inclure
tous les énoncés multilignes, ou `--format json` pour un rapport exploitable en code.
