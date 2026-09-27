# Lancer la khôlle

```
cd kholle_live
bash scripts/start_demo.sh
```

Lance le proxy de patience (8001) puis le serveur (8000) qui passe par lui ; Ctrl-C arrête les deux
(voir « Proxy de patience »). Serveur seul, sans proxy : `uv run uvicorn main:app --host 0.0.0.0 --port 8000`.

Ouvrir http://localhost:8000/, cliquer « Démo ». Clés dans `kholle_live/.env` (modèle : `.env.example`).
La clé Gradium n'accepte que 2 sessions à la fois, et une khôlle les prend toutes les deux (transcription + voix) :
une seule khôlle ouverte à la fois.

## Avant la démo

Depuis `kholle_live`, serveur arrêté :

1. Remettre le profil à zéro : `data/profile.json` doit contenir exactement
   `{"eleve": null, "faiblesses": {}, "historique": []}` (c'est la version du dépôt) :
   ```
   git checkout -- data/profile.json
   ```
2. Vider `data/reports/` en gardant son `.gitignore` (PowerShell) :
   ```
   Get-ChildItem data\reports\* -Exclude .gitignore -Force | Remove-Item
   ```
3. Aucune autre khôlle ouverte (onglet, test) : la clé Gradium n'accepte que 2 sessions.

## Réglages de la voix

| Réglage | Valeur | Où | Effet |
|---|---|---|---|
| Langue de la transcription | `fr` | gradbot, d'après `language` | |
| Vocabulaire favorisé | `main.VOCABULAIRE` (+ majuscule initiale) | `stt_extra_config.keywords` | ln, logarithme, sinus, cube, petit… |
| `STT_KEYWORDS_BOOST` | `3` | `.env` | poids du vocabulaire (Gradium : -6 à 6, 3 recommandé) |
| `STT_DELAY_FRAMES` | vide = `10` (0,8 s) | `.env` | contexte de la transcription avant d'écrire un mot |
| `SILENCE_TIMEOUT_S` | `600` | `.env` | relance après un silence de l'étudiant : 10 min, il écrit, il réfléchit |
| `SILENCE_ALERTE_S` | `60` | `.env` | relance quand une nouvelle ligne fausse attend ; dès que l'étudiant parle (« Voilà. »), la question vient tout de suite |
| Fin de tour | horizon 2 s, seuil 0,8 | codé en dur dans gradbot 0.2.0 | voir ci-dessous |
| `flush_duration_s` | `0.5` (défaut) | `STT__FLUSH_DURATION_S` | silence envoyé pour vider la transcription |

### Silences

Un étudiant qui écrit en silence réfléchit : le khôlleur ne le relance pas avant 10 min
(`SILENCE_TIMEOUT_S`), et le prompt (STYLE) lui interdit de relancer tant que l'étudiant ne parle pas,
sauf pour une ligne fausse restée sans réponse : elle est signalée après 60 s de silence
(`SILENCE_ALERTE_S`), ou dès que l'étudiant parle.

Le silence se compte depuis la fin de la voix du khôlleur, pas depuis la ligne rouge : une ligne
fausse écrite après 50 s de silence est signalée ~10 s plus tard. Vérifié dans le source de gradbot
(`gradbot_lib/src/multiplex.rs`, gradbot_py 0.2.0) :
- `silence_timeout_s` est un flottant sans borne, relu à chaque pas : 600 est pris tel quel ;
- relance = `...` quand `temps STT - fin de la voix du khôlleur > silence_timeout_s`, au plus 5 fois
  de suite (le compteur repart quand l'étudiant parle) ;
- rien d'autre ne fait parler le khôlleur : une nouvelle config (tableau) ne déclenche rien, la voix
  ouvre un flux par réplique, la transcription se reconnecte seule toutes les 5 min (limite Gradium)
  sans rien dire, les résultats d'outils ne suivent que les appels du LLM lui-même.

Conséquence pour le proxy de patience : une phrase inachevée retenue (« Donc je développe »)
suivie d'un silence n'est plus relancée au bout de ~9 s (test (e) plus bas, mesuré avec l'ancien
réglage de 12 s) ; le khôlleur attend que l'étudiant reprenne.

### Fin de tour

gradbot décide seul de la fin de tour : dès que le VAD sémantique de Gradium donne une
probabilité de silence > 0,8 sur les 2 s à venir (`gradbot_lib/src/speech_to_text.rs`).
Ni gradbot 0.2.0 ni Gradium n'exposent ce seuil. Mesuré : après « Donc je développe »,
la fin de tour tombe 1,3 s après le début de la pause.

Filet de sécurité dans `prompts/kholleur_system.md` (STYLE) : sur une phrase inachevée, le khôlleur
dit seulement « Je vous écoute. » (0,4 s), puis se tait. Si l'étudiant reprend pendant qu'il parle,
gradbot coupe le khôlleur.

La vraie patience vient du proxy (section « Proxy de patience ») : il retient la réponse du
khôlleur à une phrase inachevée.

### Tableau et compte-rendu : délais

| Réglage | Valeur | Où | Pourquoi |
|---|---|---|---|
| Envoi après le stylet levé | `1500` ms | `ATTENTE_MS`, `static/board.html` | gardé : plus court, une ligne à moitié écrite part et sa lecture retarde celle de la ligne finie |
| Seconde lecture (confirme les ✗) | lancée avec la première | `kholle/board_reader.py` | ligne fausse lue en ~3 s au lieu de 5,6 s |
| Panneau du tableau (portable) | `500` ms | `PERIODE_MS`, `static/board_panel.js` | |
| Panneau du compte-rendu | `500` ms | `PERIODE_MS`, `static/report_panel.js` | le compte-rendu s'affiche dès qu'il est prêt |
| `PIPELEX_TIMEOUT_S` | `19` | `.env` | au-delà, le repli OpenAI (lancé en même temps) est pris |

Fin de khôlle : si le khôlleur dit « … je rédige votre compte-rendu » sans appeler `terminer_colle`
(vu en test avec gpt-4.1), le serveur termine lui-même : compte-rendu et fin de page.

## Scénario de démo, de bout en bout

```
bash scripts/start_demo.sh                       # autre terminal
SERVEUR=127.0.0.1:8000 uv run python scripts/live_tests/scenario_demo.py 2
```

Élève synthétique (voix Gradium) et tableau tapé, pas manuscrit : « Démo » -> prénom -> énoncé ->
trois lignes écrites en parlant (ligne 3 fausse) -> l'étudiant attend la ligne rouge et dit « Voilà. » ->
question sur l'ordre ou le reste -> ligne 3 barrée, résultat juste ✓ -> `question_suivante` (tangente) ->
« je suis bloqué » -> `donner_indice` niveau 1 -> bonne réponse -> `terminer_colle` -> compte-rendu,
ligne 3 « corrigée après question ». Écrit un compte-rendu dans `data/` : remise à zéro avant la démo.

Deux passages de suite, 27/09 21:51, proxy de patience actif, silences 600 s / 60 s :

| Mesure | Passage 1 | Passage 2 |
|---|---|---|
| Scénario complet | réussi | réussi |
| Stylet levé -> ligne rouge sur le portable | 4,6 s | 4,5 s |
| Fin de « Voilà. » -> question sur la ligne 3 | 1,7 s | 1,6 s |
| Fin de parole de l'étudiant -> voix du khôlleur (médiane / max sur 9 répliques) | 2,0 / 2,9 s | 2,0 / 2,6 s |
| `terminer_colle` -> compte-rendu prêt (moteur) | 14,0 s (Pipelex) | 19,1 s (repli OpenAI) |

Stylet -> ligne rouge = 1,5 s d'attente + ~3 s de lecture (deux en parallèle) + 0,25 s de sondage
en moyenne. Sur la vraie tablette, l'écriture manuscrite reste à chronométrer.

## Relances après un silence

```
SERVEUR=127.0.0.1:8000 uv run python scripts/live_tests/silences.py
```

Une khôlle, élève synthétique, pas de compte-rendu. Deux exécutions le 27/09 ; la seconde, après
le correctif du numéro de ligne (voir (iii)), réussit les quatre :

| Test | Attendu | 1re exécution | 2e exécution |
|---|---|---|---|
| (i) deux lignes justes écrites en silence, 90 s | aucune relance | rien (ni voix ni appel LLM) | rien (ni voix ni appel LLM) |
| (ii) ligne fausse écrite en silence (rouge à ~8 s) | question vers 60 s, pas avant | question à 60,2 s | question à 60,5 s |
| (iii) nouvelle ligne fausse (L4, sous L3 barrée), rouge, « Voilà. » | question sur cette ligne en ~2 s | 1,8 s, mais « troisième ligne » | 2,3 s, « votre quatrième ligne » |
| (iv) « Je ne vois pas. » | `donner_indice` | appelé (niveau 1) | appelé (niveau 1) |

Silence de (ii) compté de la dernière voix du khôlleur au début de sa question, appel LLM et
synthèse compris. (iii) : l'alerte citait « votre troisième ligne » en
exemple quel que soit le numéro ; elle nomme maintenant la ligne fausse (`prompts.designation`).

### Transcription affichée

`static/index.html` corrige l'affichage des répliques de l'étudiant (« elle haine » → ln,
« petit taux » → petit o, « ix cube » → x cube…). Le LLM reçoit le texte brut.

## Proxy de patience

`kholle/llm_proxy.py` se place entre gradbot et OpenAI et retient la réponse du khôlleur quand
l'étudiant s'arrête au milieu d'une phrase (« Donc je développe… »). Tout le reste passe tel quel.

La démo se lance avec `bash scripts/start_demo.sh` (Git Bash sous Windows), depuis `kholle_live` :
1. démarre le proxy sur 8001 (relancé s'il s'arrête ; journal dans `$TMPDIR/kholle_proxy.log`) ;
2. attend qu'il réponde, 10 s au plus ;
3. démarre le serveur sur 8000 avec `LLM_BASE_URL=http://127.0.0.1:8001/v1` pour ce seul processus.

Si le proxy ne répond pas, un grand avertissement s'affiche et le serveur part en direct sur OpenAI :
le khôlleur n'est jamais muet. Ctrl-C arrête les deux. Ne pas mettre `LLM_BASE_URL` dans `.env`.

**Interrupteur** : `PROXY_HOLD=0 bash scripts/start_demo.sh` (le proxy relaie tout), ou lancer le serveur
seul : `uv run uvicorn main:app --host 0.0.0.0 --port 8000` (gradbot parle directement à OpenAI).

Tests en direct (élève synthétique, port 8011) : `scripts/live_tests/README.md`.

Ce que fait gradbot (mesuré) : uniquement `POST /v1/chat/completions`, toujours en `stream: true`.
Relance après `SILENCE_TIMEOUT_S` : un message utilisateur `...`, collé au précédent s'il est de l'étudiant.

Règle (sans appel LLM), sur le dernier message s'il vient de l'étudiant :
- retenu s'il finit par `…`, `...` ou `,`, ou si son dernier mot est un mot de liaison (donc, et, de, égal,
  plus, moins, euh…), une élision (j', l'…) ou un verbe qui attend son complément (développe, pose, obtiens…) ;
- jamais retenu s'il contient « voilà », « j'ai fini », « c'est tout », « je réfléchis », ou finit par `?` ;
- toujours transmis : relance après silence, appels et résultats d'outils.

Retenir = répondre une complétion vide (un morceau SSE vide, `finish_reason: stop`, `[DONE]`). gradbot
se tait, se remet à écouter, et colle la suite au même message : le LLM reçoit
« Donc, je développe, à l'ordre 3, en posant u égale sinus de x. » en une fois.

| Élève synthétique (port 8011), 2 passages | Résultat |
|---|---|
| (a) « Donc je développe » + 4 s + « à l'ordre trois… » | aucun audio pendant la pause ; réponse à la phrase entière, 1er audio 1,54 / 1,46 s |
| (b) « Voilà. » | 1er audio 1,61 / 1,58 s (1,56 s sans proxy) |
| (c) ligne 3 fausse + « Voilà. » | « Sur votre troisième ligne… terme en x au cube » (2/2) |
| (e) fragment retenu puis silence | relance à 9,0 / 9,4 s (« Je vous écoute… ») |
| (f) « Je ne vois pas » | `donner_indice` appelé (2/2) |
| Surcoût du proxy | 0,3 à 1 ms d'analyse ; +7 ms médian (p95 20 ms) sur un amont local |

Réglages (variables d'environnement du proxy) : `PROXY_UPSTREAM_URL` (défaut `https://api.openai.com/v1`),
`PROXY_HOLD=0` (ne rien retenir), `PROXY_HOLD_TEXT` (texte d'une réponse retenue, vide par défaut),
`PROXY_LOG=chemin.jsonl` (journal des requêtes : derniers messages, décision, raison).
