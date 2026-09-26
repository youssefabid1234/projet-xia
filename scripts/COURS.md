# Séries numériques

Depuis la racine du projet (PowerShell), extraction locale sans appel API :

```powershell
.venv-extraction/Scripts/python.exe -X utf8 scripts/extract_chapitre.py --chapitre 17 --enonces 48 51 --corriges 191 202
.venv-extraction/Scripts/python.exe -X utf8 scripts/index_cours.py
```

Les pages sont celles du PDF, à partir de 1. Le cours occupe les pages PDF
139–157 (imprimées 137–155). Les 80 unités numérotées deviennent des passages :
définitions, résultats et leurs éléments de preuve, exemples, remarques,
avertissements et méthodes. Les introductions sont conservées séparément et
comme contexte du premier passage qui les suit. Les commentaires entre deux
unités restent dans la première. Les passages continuent au-delà des changements
de page. Une preuve absente de la source n'est pas inventée.

`data/cours_passages.json` contient les textes, titres, types, sections, pages,
coordonnées et empreinte du PDF. `data/cours_apercu.md` montre les dix premiers.
Les formules de ces dix passages ont été remises en forme dans
`scripts/transcriptions/cours_series.json` ; le texte brut reste conservé.
Les autres passages sont du texte PDF brut dont les formules sont à relire.
Les exercices sont également des extractions brutes, signalées dans leur audit.
La difficulté est le nombre d'étoiles pleines parmi cinq, zéro inclus.

Après vérification et corrections éventuelles de `data/cours_passages.json` :

```powershell
.venv-extraction/Scripts/python.exe -m pip install -r scripts/requirements-cours.txt
# OPENAI_API_KEY doit être définie dans l'environnement.
.venv-extraction/Scripts/python.exe -X utf8 scripts/index_cours.py --embed
```

Cette seconde commande lit les passages sauvegardés sans les réextraire,
appelle l'API OpenAI par lots et écrit `data/cours_index.json` uniquement quand
tous les vecteurs sont reçus et vérifiés. Le modèle par défaut est
`text-embedding-3-small` (option `--model`), conformément à la
[documentation OpenAI](https://developers.openai.com/api/docs/guides/embeddings).
Les entrées trop longues sont refusées avant tout appel ; une preuve n'est pas
coupée arbitrairement pour entrer dans la limite. Aucun appel payant n'est
effectué en mode aperçu. Le fichier `.env` n'est pas chargé automatiquement.

Tests sans réseau :

```powershell
.venv-extraction/Scripts/python.exe -X utf8 -m unittest discover -s scripts -p 'test_*.py'
```

## Recherche depuis l'agent

`app/cours.py` expose `chercher_dans_cours(question)` (fonction asynchrone).
L'agent déclare cet outil et l'appelle pour les questions de cours. La question
est vectorisée avec le modèle et les dimensions de l'index. Les cinq passages
retenus sont classés par recherche hybride : similarité cosinus + 0,25 × score
BM25 normalisé (titres et textes, accents et pluriels normalisés). Les mots
précis, comme « reste », complètent ainsi la recherche sémantique.
Le retour contient les textes, titres, types, identifiants, scores et pages
PDF/imprimées, sans les vecteurs. Le score hybride n'est pas une probabilité.
L'agent cite les passages utilisés. L'index est mis en cache en mémoire et
rechargé après modification du fichier.

Les 80 embeddings ont été calculés avec `text-embedding-3-small`, en 1 536
dimensions. La recherche utilise le SDK OpenAI déjà requis par l'application
web, sans base vectorielle supplémentaire. Chaque recherche effectue un appel
d'embedding pour la question. Les données de profil ne sont pas modifiées.

Contrôles locaux :

```powershell
.venv/Scripts/python.exe -X utf8 -m unittest app.test_cours app.test_agent
```

Test réel des trois questions (appels OpenAI payants, recherche directe puis
dialogue complet de l'agent) :

```powershell
.venv/Scripts/python.exe -X utf8 -m scripts.verifier_recherche_cours
```

Le rapport `data/cours_recherche_tests.json` conserve les questions, classements,
appels d'outil, réponses et empreinte de l'index testé. Les contrôles automatiques
vérifient la présence d'une référence attendue et l'appel réussi de l'outil ;
les réponses mathématiques demandent aussi une lecture qualitative.
