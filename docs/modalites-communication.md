# Modalités de communication

Implémentation sur `modalites-integrees`, à partir de `5aa5fd7`. Extraction sélective
de `origin/kholle-live` (`0ff5f59`), sans fusion de son moteur.

## Utilisation

- **Clavier** reste le mode initial et fonctionne sans les services de conversion.
- **Manuscrit** ouvre un tableau au stylet, doigt ou à la souris. « Transcrire le
  tableau » ajoute la transcription au brouillon. Relire puis cliquer sur « Envoyer ».
- **Dicter** ouvre le microphone sur demande. « Arrêter et transcrire » ferme le
  micro et ajoute le texte au brouillon. Relire puis cliquer sur « Envoyer ».
- **Activer la lecture audio** lit la consigne publique actuelle, puis les nouvelles
  consignes révélées. « Relire la consigne » et « Arrêter la lecture » sont disponibles.
  L'audio est désactivé au chargement de la page. Le démarrage du micro arrête la lecture.

Les boutons de conversion ne soumettent rien au colleur. Le brouillon reste modifiable.
Les transcriptions sont ajoutées au texte déjà tapé ; elles ne le remplacent pas.
Un changement de brouillon, une annulation, un changement de question ou la fin de la
colle invalide les résultats en attente. Aucun POST pédagogique n'est rejoué automatiquement.
La durée passée à écrire, écouter ou transcrire compte dans le chronomètre existant.

## Configuration

Installer `app/web/requirements.txt` dans l'environnement Python existant.

```dotenv
OPENAI_API_KEY=...
VISION_MODEL=gpt-4.1-mini
GRADIUM_API_KEY=...
# Facultatif : Gaspard (iEu63s1rhn_kegTr) par défaut, comme kholle-live.
KHOLLEUR_VOICE_ID=
```

Les clés restent côté serveur. Aucune clé Gradium n'est nécessaire pour le clavier
ou le manuscrit. Le microphone exige HTTPS ou localhost et l'autorisation du navigateur.
Les médias sont envoyés au fournisseur seulement après une demande explicite de
transcription ; ils ne sont pas enregistrés par l'application dans les profils ou sur disque.
La synthèse envoie seulement la consigne autorisée à Gradium.

## Frontières techniques

`#message → envoyer() → POST /api/message → Examinateur.tour(message)` reste le
seul chemin de soumission. Ni les routes de conversion ni leurs adaptateurs ne
peuvent évaluer, faire avancer la colle ou sauvegarder un profil.

| Route | Entrée | Sortie |
|---|---|---|
| `GET /api/modalites` | Session authentifiée | Disponibilité des trois conversions |
| `POST /api/modalites/manuscrit` | PNG, 2 Mio et 4 millions de pixels maximum | `{"texte":"…"}` |
| `POST /api/modalites/dictee` | WAV mono 24 kHz / 16 bits, 0,1–120 s, 6 Mio maximum | `{"texte":"…"}` |
| `POST /api/modalites/lecture` | `{"question":"consigne publique active exacte"}` | WAV |

Toutes les nouvelles routes utilisent l'authentification existante. Les POST
exigent `X-CSRF-Token`. Leurs réponses portent `Cache-Control: no-store` et
`X-Content-Type-Options: nosniff`. Les limites média sont locales à leurs routes :
les autres requêtes restent limitées à 64 Kio et les messages à 6 000 caractères.
Les requêtes simultanées d'une même conversion et d'un même élève sont refusées.
La disponibilité de la colle est revérifiée après chaque conversion.

La lecture utilise une liste blanche **côté serveur** : `etat.tache.question_active`
de la colle authentifiée. Les textes génériques du dialogue, les corrigés, les étapes
futures et les bilans n'alimentent jamais la synthèse. La normalisation des formules
est déterministe et n'affecte pas le texte source, le DOM ou KaTeX.

Réutilisation de `kholle-live` : dessin, priorité au stylet et export recadré du
tableau ; principe d'appel vision et transcription fidèle ; appel TTS Gradium direct.
Adaptations : export sur clic, transcription sans SymPy, STT isolé, capture PCM via
AudioWorklet et WAV final, liste blanche de lecture. Aucun import de Gradbot, de
`kholle/state.py`, des outils de progression ou des panneaux d'évaluation.

L'adaptateur vocal suit les interfaces `speech.stt` / `speech.tts` du
[SDK officiel Gradium](https://github.com/gradium-ai/gradium-py/blob/main/gradium/speech.py).

## Fichiers

- `app/modalites.py` : validation des médias, reconnaissance et synthèse isolées.
- `app/web/modalites.py`, `app/web/__init__.py` : routes protégées et raccordement en lecture seule à l'état public.
- `app/web/static/tableau.js` : dessin et export local.
- `app/web/static/micro-worklet.js` : capture locale, sans envoi de fragments.
- `app/web/static/modalites.js` : commandes, brouillon, annulation et lecture.
- `app/web/static/colle.js` : raccordements à l'état, à l'occupation et à la soumission existante.
- `app/web/templates/chat.html`, `app/web/static/colle.css` : commandes des modalités.
- `app/web/requirements.txt`, `.env.example` : dépendances et configuration.
- `app/web/test_modalites.py` : tests des adaptateurs, routes et invariants.
- `scripts/fixture_modalites.py`, `scripts/verifier_modalites.cjs` : parcours Chrome.
- `scripts/verifier_rendu_katex.cjs` : sert aussi les nouveaux assets pendant les vérifications existantes.
- `scripts/verifier_manuscrit_reel.py` : essai vision réel explicite, sur image synthétique.
- `reports/verification-modalites/` : résultats et image de démonstration.
- `reports/verification-rendu-katex/chat-1280.png` et `chat-390.png` : captures actualisées du contrôle KaTeX.
- `docs/modalites-communication.md` : cette documentation.

## Vérifications et limites

Résultat de la vérification du 27 septembre 2026 : **118 tests Python**, **11
scénarios Chrome**, rendu KaTeX à deux largeurs et un appel vision réel réussis.
Voir le [compte rendu](../reports/verification-modalites/verification.md).

Commandes hors fournisseurs :

```powershell
.venv/Scripts/python.exe -m unittest discover -s app -p 'test_*.py'
node scripts/verifier_modalites.cjs <chemin-du-module-playwright>
node scripts/verifier_rendu_katex.cjs <chemin-du-module-playwright>
```

Essai réel facultatif (un appel vision payant, police Segoe Print sous Windows) :

```powershell
.venv/Scripts/python.exe -m scripts.verifier_manuscrit_reel
```

La reconnaissance peut mal lire une écriture ou une formule dictée : le brouillon
est toujours relisible et modifiable. La synthèse normalise les notations courantes ;
les formules complexes restent plus fiables à l'écrit. Un navigateur peut bloquer
la lecture automatique : le bouton « Relire » reste disponible.

La capture microphone a été vérifiée dans Chrome avec un périphérique simulé.
L'API Gradium a été simulée pendant les tests : `GRADIUM_API_KEY` n'était pas
configurée dans cet environnement. La qualité sonore réelle et les navigateurs
autres que Chrome ne sont donc pas attestés par ces tests.

L'essai vision réel a conservé l'erreur volontaire « 1 + 1 = 3 » et la phrase
« Je ne sais pas justifier. », sans correction mathématique.
