# Lancer la khôlle

```
cd kholle_live
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Ouvrir http://localhost:8000/, cliquer « Démo ». Clés dans `kholle_live/.env` (modèle : `.env.example`).
La clé Gradium n'accepte que 2 sessions à la fois, et une khôlle les prend toutes les deux (transcription + voix) :
une seule khôlle ouverte à la fois.

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
