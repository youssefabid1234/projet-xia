# Ce que la v1 (khôlleur texte) peut apporter à kholle_live

Inventaire seulement : rien n'est porté. Chemins relatifs à la racine du dépôt.

**À savoir d'abord :** la v1 n'a ni SymPy, ni audio, ni lecture d'image, et **aucun exercice de DL**. Les exercices de `data/exercises.yaml` sont donc tous nouveaux.

## Données
- `data/exercices.json` : 58 exercices `{identifiant, chapitre, enonce, corrige, page_source, difficulte}`, chapitres Séries (17), Dérivation et intégration (2), Topologie (18). Le texte brut du chapitre 17 est abîmé par l'extraction PDF.
- `data/enonces_verifies.json` : les 31 exercices de séries transcrits proprement en LaTeX.
- `data/questions_cours.json` : 50 questions de cours sur les séries `{nature, priorite, question, reponse_attendue}`. Utile pour une phase « question de cours ».
- `data/profil.json` : exemple de profil élève (niveaux, historique des verdicts et types d'erreur).

## Prompts
- `app/examinateur.py` :
  - `COLLEUR` (l.48) : persona du colleur (vouvoiement, une question par tour).
  - `CONSIGNES` (l.71) : indices gradués n°1, 2, 3.
  - `BILAN` (l.106) : note /20, points forts, à retravailler. Base possible pour la lane C.
- `methods/evaluation_maths_prepa/main.mthds` :
  - verdicts `correcte / incorrecte / incomplete / indeterminable` ;
  - 10 types d'erreur (calcul, raisonnement, hypothese_ou_domaine, justification_insuffisante…) ;
  - style déjà sans LaTeX, adapté à l'oral.
- `methods/progression_colle/main.mthds` : décide `avancer / approfondir / revenir_au_cours / changer_exercice`.

## Code réutilisable
- `app/colle.py` : aucun appel réseau.
  - `decider()` (l.70) : fonction pure qui passe de (intention, verdict) à une action.
  - Classe `Colle` (l.92) : minuteur et persistance JSON atomique.
- `app/profil.py` : suivi des faiblesses. `Profil` (l.23), `erreurs_frequentes()` (l.52), `choisir_exercice()` (l.111).
- `app/examinateur.py` : `prechauffer()` (l.121) garde les connexions HTTP chaudes, ce qui réduit la latence à l'oral.
- `app/services.py` : client `AsyncOpenAI` partagé avec keepalive.
- `app/faux.py` : `FauxOpenAI`, une doublure hors ligne de `responses.create` pour tester sans crédit.

## Interface web
- `app/web/static/colle.css` : palette tableau et craie en variables `:root` (`--tableau`, `--craie`), avec mode sombre.
- `app/web/static/colle.js` : rendu Markdown + KaTeX (`rendre()`, l.41), minuteur (`tic()`, l.176).
- KaTeX 0.18.9 par CDN jsDelivr, repris dans `static/index.html`.

## Configuration
- La v1 utilise OpenAI (API Responses, sortie JSON stricte), modèle par défaut `gpt-4.1-mini`.
- Variables : `OPENAI_API_KEY`, `OPENAI_MODEL`, `PIPELEX_API_KEY`, `COLLE_EVALUATEUR`, `COLLE_DUREE_MINUTES`.

## Pièges du squelette kholle_live
- `gradbot.routes.setup` monte le dossier audio de gradbot sur `/static/js/` : ne mettez rien dans `kholle_live/static/js/`, ce serait masqué.
- `prompts/*.md` contiennent d'autres accolades que les champs à remplir (`{ligne: …}`, `{tag, conseil}`). Remplissez avec `str.replace`, pas `str.format`.
- `main.py` charge `.env` avant `gradbot.config.from_env()`, qui est mis en cache.
- Les `t` de `state` sont en secondes depuis `Session.started_at`.
- Les rappels de `on_board_change` peuvent être async. Ils sont alors planifiés, ce qui permet par exemple un `input_handle.send_config(...)` de gradbot.
- Tests : `uv run pytest`.
