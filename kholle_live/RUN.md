# Lancer la khôlle

```
cd kholle_live
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

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
| `SILENCE_TIMEOUT_S` | `10` | `.env` | relance après un silence de l'étudiant |
| Fin de tour | horizon 2 s, seuil 0,8 | codé en dur dans gradbot 0.2.0 | voir ci-dessous |
| `flush_duration_s` | `0.5` (défaut) | `STT__FLUSH_DURATION_S` | silence envoyé pour vider la transcription |

### Fin de tour

gradbot décide seul de la fin de tour : dès que le VAD sémantique de Gradium donne une
probabilité de silence > 0,8 sur les 2 s à venir (`gradbot_lib/src/speech_to_text.rs`).
Ni gradbot 0.2.0 ni Gradium n'exposent ce seuil. Mesuré : après « Donc je développe »,
la fin de tour tombe 1,3 s après le début de la pause.

Filet de sécurité dans `prompts/kholleur_system.md` (STYLE) : sur une phrase inachevée, le khôlleur
dit seulement « Je vous écoute. » (0,4 s), puis se tait. Si l'étudiant reprend pendant qu'il parle,
gradbot coupe le khôlleur.

Pour une vraie patience : rendre le seuil réglable dans gradbot et recompiler (Rust), ou
passer par un proxy LLM qui retient les phrases inachevées.

### Transcription affichée

`static/index.html` corrige l'affichage des répliques de l'étudiant (« elle haine » → ln,
« petit taux » → petit o, « ix cube » → x cube…). Le LLM reçoit le texte brut.

## Proxy de patience

`kholle/llm_proxy.py` se place entre gradbot et OpenAI et retient la réponse du khôlleur quand
l'étudiant s'arrête au milieu d'une phrase (« Donc je développe… »). Tout le reste passe tel quel.

```
cd kholle_live
uv run uvicorn kholle.llm_proxy:app --port 8001
```

Puis, dans `kholle_live/.env` : `LLM_BASE_URL=http://127.0.0.1:8001/v1`, et relancer le serveur (8000).
Le proxy doit tourner avant la khôlle : `LLM_BASE_URL` réglée sans proxy = khôlleur muet.

**Interrupteur** : remettre l'ancienne valeur (`# LLM_BASE_URL=`, commentée : gradbot parle directement
à OpenAI) et relancer le serveur. Sans relancer le serveur : relancer le proxy avec `PROXY_HOLD=0` (simple relais).

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
