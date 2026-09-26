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
.venv/Scripts/python.exe -m app.web
```

Ouvrir http://127.0.0.1:5000. Choisir un chapitre, rédiger une réponse,
puis cliquer sur « Vérifier ma réponse ». Le verdict, l’explication et le
niveau actualisé s’affichent sur la même page. « Exercice suivant » choisit
un nouvel exercice adapté au niveau. Une réponse vide est acceptée comme
copie blanche.

L’interface Flask se trouve dans `app/web/`. Elle utilise `app/profil.py`
et partage l’appel Pipelex de `test_methode.py` via `app/evaluation.py`.
Chaque correction envoyée exécute la méthode hébergée et consomme du crédit
Pipelex. La clé reste côté serveur ; le fichier `.env` n’est pas chargé
automatiquement.

Cette version locale est mono-élève : elle partage `data/profil.json` avec
le tuteur en terminal. Utiliser un seul serveur et éviter de lancer le tuteur
terminal en même temps. Le profil est sauvegardé après chaque correction
valide ; les exercices déjà traités ne sont plus proposés.

Les formules des énoncés et explications sont rendues avec
[KaTeX auto-render](https://katex.org/docs/autorender), chargé depuis un CDN
(connexion Internet nécessaire). Les délimiteurs `$…$`, `$$…$$`, `\(…\)`
et `\[…\]` sont pris en charge. Le texte reste lisible si le CDN est inaccessible.

Tests hors ligne, avec Pipelex simulé et un profil temporaire :

```powershell
.venv/Scripts/python.exe -m unittest app.web.test_web
```
