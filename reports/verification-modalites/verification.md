# Vérification des modalités — 27 septembre 2026

Branche : `modalites-integrees`, base `5aa5fd7`. Référence extraite :
`origin/kholle-live` au commit `0ff5f59`.

## Résultats

| Vérification | Résultat |
|---|---|
| `python -m unittest discover -s app -p 'test_*.py'` | 118 tests réussis, dont 10 nouveaux tests de modalités |
| `node scripts/verifier_modalites.cjs <playwright>` | 11 scénarios Chrome réussis, aucune erreur JavaScript |
| `node scripts/verifier_rendu_katex.cjs <playwright>` | 5 formules, polices chargées, aucun débordement à 390 et 1280 px ; repli CDN vérifié |
| `python -m scripts.verifier_manuscrit_reel` | Un appel vision réel réussi ; erreur mathématique volontaire conservée |
| `node --check` sur les quatre scripts de production | Réussi |
| `git diff --check` | Réussi |
| Comparaison des fichiers pédagogiques avec HEAD | Aucun changement |

Le parcours Chrome utilise le vrai formulaire, le canvas, l'AudioWorklet et le
microphone simulé de Chrome. Seuls les fournisseurs de conversion et les réponses
du moteur sont simulés dans cette suite. La suite Python couvre le moteur et les
routes réelles, avec fournisseurs simulés. Le test vision appelle réellement OpenAI.

Scénarios détaillés : [resultats.json](resultats.json).
Sortie vision réelle : [vision-reelle.json](vision-reelle.json).
Capture mobile : [manuscrit-mobile.png](manuscrit-mobile.png) (CDN désactivé
volontairement dans cette suite, rendu KaTeX contrôlé séparément).

## Invariants vérifiés

- Aucun envoi pendant le dessin ou l'enregistrement ; transcription dans le
  brouillon, puis un seul POST textuel au moteur, y compris après un double clic.
- Aucun changement des profils ou de la colle lors des conversions seules.
- Authentification, CSRF, isolation des élèves, formats/dimensions/durée et
  limites HTTP ; maintien de la limite globale de 64 Kio.
- Lecture limitée à la consigne publique active, y compris côté serveur ; aucune
  lecture du corrigé, du bilan ou des étapes futures.
- Annulation, résultat tardif, changement de brouillon/question, refus du micro,
  erreur réseau, expiration et rechargement sans relecture automatique.
- Fonctionnement au clavier sans disponibilité des services de modalités.

Fichiers pédagogiques comparés sans différence : `colle.py`, `moteur_colle.py`,
`examinateur.py`, `evaluation.py`, `notation.py`, `chronometrage.py`, `profil.py`,
`parcours.py`, `plans.py`, `pedagogie.py`, `texte_eleve.py` et `methods/`.

## Limites attestées

- Pas de clé `GRADIUM_API_KEY` dans cet environnement : STT/TTS testés avec le SDK
  et un fournisseur simulé, sans essai sonore réel. La clé doit être renseignée
  dans `.env` puis le serveur redémarré pour activer ces deux commandes.
- Microphone physique, stylet physique et autres navigateurs non testés.
- La reconnaissance n'est pas infaillible ; relecture du brouillon prévue.
- La prononciation des formules complexes reste approximative.

Configuration et liste des fichiers : [documentation](../../docs/modalites-communication.md).
