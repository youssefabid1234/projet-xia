# X-khôlleur — s’entraîner à la khôlle de mathématiques

Le X-khôlleur simule une khôlle de mathématiques pour les élèves de prépa scientifique : il interroge sur le cours, demande une démonstration, puis propose une application et des exercices adaptés. L’élève répond au clavier, au tableau manuscrit ou par dictée ; le colleur accompagne le raisonnement et termine par une note indicative sur 20 et un bilan. Les chapitres disponibles sont les **séries numériques** et les **équations différentielles linéaires**.

La branche `main` contient la version finale intégrée et est sélectionnée par défaut lors du clonage du dépôt.

## Installation depuis un clone frais

Prérequis : Git, **Python 3.12 64 bits**, un navigateur récent et une connexion Internet. Les données et index nécessaires sont déjà versionnés : aucune extraction PDF ni reconstruction d’index n’est nécessaire au premier lancement. Node.js et LaTeX ne sont pas nécessaires pour utiliser l’application.

### Windows — PowerShell

Installer Python 3.12 avec le lanceur `py`, puis :

```powershell
git clone https://github.com/youssefabid1234/projet-xia.git
cd projet-xia
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Renseigner `.env` comme indiqué ci-dessous, puis lancer depuis la racine :

```powershell
.\.venv\Scripts\python.exe -m app.web
```

### Linux — bash

Installer Git, Python 3.12 et son module `venv` avec le gestionnaire de paquets de votre distribution (sur Ubuntu 24.04 : `sudo apt install git python3.12 python3.12-venv python3-pip`), puis :

```bash
git clone https://github.com/youssefabid1234/projet-xia.git
cd projet-xia
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Renseigner `.env`, puis :

```bash
.venv/bin/python -m app.web
```

L’activation de l’environnement virtuel n’est pas nécessaire avec ces commandes.

## Clés API et configuration

Créer les clés dans les consoles des fournisseurs et les copier dans `.env`. Ce fichier est chargé automatiquement ; les variables déjà définies dans l’environnement sont prioritaires. Il est ignoré par Git et doit rester local.

| Variable | Nécessaire pour | Où l’obtenir |
|---|---|---|
| `OPENAI_API_KEY` | Le dialogue, l’évaluation par défaut, la recherche dans le cours et la transcription manuscrite. Obligatoire pour une khôlle au clavier. | Créer une clé dans la [console OpenAI](https://platform.openai.com/api-keys), voir le [guide officiel](https://developers.openai.com/api/docs/quickstart). |
| `PIPELEX_API_KEY` | L’évaluation hébergée si `COLLE_EVALUATEUR=pipelex`. Facultative en mode `local`. | Créer une clé dans la [console Pipelex](https://app.pipelex.com), voir le [guide API](https://docs.pipelex.com/latest/get-started/quick-start/). |
| `GRADIUM_API_KEY` | La dictée et la lecture audio. Facultative pour le clavier et le manuscrit. | Créer une clé dans [Gradium Studio](https://studio.gradium.ai), voir la [documentation Gradium](https://docs.gradium.ai/). |

Les comptes API doivent disposer des accès et crédits nécessaires ; les échanges réels consomment des crédits chez les fournisseurs utilisés. Le mode `local` désigne un appel direct à OpenAI depuis le serveur, pas une exécution hors ligne.

Les autres réglages sont décrits dans [.env.example](.env.example) : `OPENAI_MODEL` et `VISION_MODEL` valent par défaut `gpt-4.1-mini`, `COLLE_EVALUATEUR` vaut `local` et `COLLE_DUREE_MINUTES` vaut `30`. Définir une `FLASK_SECRET_KEY` aléatoire et stable pour préserver les connexions après redémarrage. `KHOLLEUR_VOICE_ID` permet de choisir la voix Gradium.

## Première khôlle au clavier

Ouvrir **http://127.0.0.1:5000**, créer un compte local, choisir un chapitre et commencer. Saisir une réponse dans le champ de dialogue puis cliquer sur « Envoyer » ; le mode clavier est sélectionné initialement. On peut demander une précision, un indice ou une correction en langage naturel. Le bilan apparaît en fin de parcours ou à la fin du temps imparti.

Les comptes et profils sont stockés dans `data/utilisateurs.json` et `data/profils/`, hors Git. La séance est sauvegardée après chaque tour et peut reprendre après rechargement. Garder un seul processus serveur ; `Ctrl+C` l’arrête.

## Architecture

**Déroulé et interface.** Flask (`app/web/`) sert l’interface et les routes du dialogue. `Colle` (`app/colle.py`) conserve l’état de la séance, sélectionne les tâches et sauvegarde le profil. Le parcours comporte une question de cours (définition ou théorème), une démonstration, une application et jusqu’à trois exercices, sous réserve du temps et des contenus disponibles. `Examinateur` classe l’intention de l’élève, fait évaluer les réponses, puis formule la réaction du colleur. Les messages arrivent progressivement par un flux NDJSON ; KaTeX affiche les formules. `app/services.py` partage une boucle asynchrone et les clients API entre les requêtes.

**Moteur pédagogique et notation.** Les décisions appartiennent au moteur déterministe `app/moteur_colle.py` : validation, demande de complément, aide, correction et passage à la suite. Les plans de résolution (`app/plans.py`) permettent un accompagnement par étapes. Le catalogue et le profil orientent la sélection selon la difficulté, les acquis et les notions fragiles. Le barème fixe est de **3 + 4 + 5 + 3 + 3 + 2 = 20 points**. Le score combine le verdict et l’intuition mathématique ; chaque indice applique un facteur de 0,9, et une réponse révélée plafonne le score de l’élément concerné à 0,25. Les postes non traités ne rapportent pas de points et ne sont pas présentés comme des erreurs de l’élève.

**Évaluation.** `methods/evaluation_maths_prepa/main.mthds` contient les consignes et le contrat de sortie, lus par `app/evaluation.py`. En mode `local`, ils sont envoyés directement à OpenAI ; en mode `pipelex`, la méthode s’exécute via l’API hébergée Pipelex. L’évaluateur compare les réponses cumulées pour l’élément actif à la référence et renvoie six champs : verdict, type d’erreur, intuition, progression, notions fragiles et explication. Le serveur contrôle ce résultat avant de l’utiliser. Une référence inexploitable peut conduire à un verdict indéterminable.

**Index du cours.** Les fichiers `data/cours_index.json` et `data/cours_edl_index.json` contiennent les passages et leurs vecteurs. `app/cours.py` combine une recherche sémantique par embeddings et une recherche lexicale BM25 pour répondre aux questions de compréhension. Les références aux pages restent disponibles dans les données ; le dialogue masque leurs identifiants techniques. Les banques `questions_cours*.json`, les exercices, leurs vérifications et les liens de notions alimentent la sélection pédagogique. La reconstruction des contenus est documentée dans [scripts/COURS.md](scripts/COURS.md) et [scripts/EXTRACTION.md](scripts/EXTRACTION.md).

**Modalités de communication.** Le clavier est le parcours de référence. Le tableau manuscrit est transcrit par OpenAI ; Gradium assure la dictée et la synthèse vocale. Les transcriptions rejoignent un brouillon modifiable que l’élève relit avant envoi, puis empruntent le même parcours d’évaluation que le clavier. La lecture audio restitue les messages publics du colleur. Les conversions ne décident ni de la note ni de la progression. Voir [docs/modalites-communication.md](docs/modalites-communication.md).

## Sources de contenu et licences

- **Exercices :** *Exercices de mathématiques supérieures*, rédigé par **Quentin De Muynck**, d’après Monsieur **Éric Merle**, lycée Louis-le-Grand, MPSI 2, année 2019–2020, version du 12 juillet 2020. La préface crédite également les camarades de la promotion pour les corrections. Le [polycopié source](data/poly.pdf) est sous licence [Creative Commons Attribution — Pas d’Utilisation Commerciale — Partage dans les Mêmes Conditions 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/). **Nous avons extrait et restructuré les exercices et leurs corrigés**, en organisant les données, transcrivant les notations et conservant les références aux pages. Les extraits et cette restructuration sont partagés sous la même licence ; les vérifications et plans pédagogiques sont des traitements du projet, distincts du document original. Voir [data/ATTRIBUTION.md](data/ATTRIBUTION.md).
- **Cours :** **Alain Troesch**, *Cours de mathématiques — Partie II : Analyse*, MP2I, lycée Louis-le-Grand, année 2023–2024, version du 4 juillet 2024, conservé dans [data/cours/analyse.pdf](data/cours/analyse.pdf). Les chapitres sur les séries et les équations différentielles servent aux extraits, index et questions. Aucune licence explicite n’a été identifiée dans ce PDF ou dans le dépôt ; les conditions de redistribution de ce cours et de ses extraits restent à clarifier. La licence du recueil d’exercices ne leur est pas attribuée.
- **Guides de préparation :** les sources `.tex` et les PDF sont dans `app/web/static/guides/`. Aucune licence distincte n’est déclarée dans le dépôt.
- **Logos :** École polytechnique et ENS–PSL, provenant des sites officiels. Les sources et conditions d’utilisation sont indiquées dans [SOURCES.md](app/web/static/branding/SOURCES.md) ; ils ne sont pas couverts par la licence des exercices.

Le dépôt ne contient pas de licence générale pour le code. Les licences des contenus tiers ne constituent pas une licence du logiciel.

## Limites connues

- Prototype de démonstration locale : stockage JSON et serveur de développement Flask, sans déploiement de production ni stockage partagé entre processus.
- Deux chapitres préparés seulement. Le catalogue est fini et certaines extractions mathématiques restent ambiguës ou sont écartées.
- Les modèles peuvent mal interpréter une réponse, une preuve ou une notation. La note sert à l’entraînement et ne remplace pas une évaluation humaine.
- Internet, les services API et leurs quotas conditionnent le fonctionnement ; le rendu KaTeX utilise un CDN. Les délais varient selon les appels et les fournisseurs.
- Le manuscrit et la dictée nécessitent une relecture. La lecture orale de formules complexes est imparfaite ; le microphone nécessite localhost ou HTTPS et l’autorisation du navigateur. Écrire, transcrire et écouter consomme le temps de la séance.
- Les réponses et contextes nécessaires sont transmis aux fournisseurs utilisés. Les images et enregistrements de conversion ne sont pas conservés sur disque par l’application ; les échanges textuels sont sauvegardés dans le profil local.
- Les droits de redistribution du cours et la licence du code restent à préciser, comme indiqué ci-dessus.

## Vérifications et maintenance

Les tests hors ligne utilisent des services simulés et ne consomment pas de crédits. Depuis la racine, avec le Python de l’environnement virtuel (Windows : `.\.venv\Scripts\python.exe`, Linux : `.venv/bin/python`) :

```text
python -m unittest discover -s app -p "test_*.py"
python -m unittest discover -s app/web -p "test_*.py"
python -m unittest discover -s scripts -p "test_*.py"
```

Remplacer `python` par le chemin correspondant ci-dessus. Les tests web sont lancés séparément pour couvrir explicitement l’interface. `python -m scripts.simuler_colle` permet aussi un dialogue au clavier en terminal avec le moteur actuel ; `/juste` est un raccourci de diagnostic et `/bilan` termine la séance. Cette simulation utilise les vraies API et un profil temporaire.

La validation du rendu doit également couvrir une installation dans un environnement vierge et une khôlle complète au clavier dans le navigateur ; les seuls tests simulés ne prouvent pas le fonctionnement des services réels.
