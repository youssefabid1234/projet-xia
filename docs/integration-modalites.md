# Raccorder les modalités au colleur

Référence : branche `fond-pedagogique`, code au commit `cf9efc6` (27 septembre 2026).
Périmètre : raccorder une synthèse vocale, une saisie manuscrite et une réponse orale **déjà réalisées**. Le contrat du colleur reste textuel ; aucun endpoint audio/image ni bus de modalités n'existe actuellement.

## 1. Déroulé et décisions

Sources : [Colle](../app/colle.py), [Examinateur](../app/examinateur.py), [moteur](../app/moteur_colle.py).
Ordre : `cours` (une définition ou un théorème), `demonstration` (une), `applications` (une), `exercices` (trois maximum), puis `fin`. Une tâche close compte même si elle n'est pas acquise ; une phase sans candidat est sautée. Les exercices sont vérifiés et dotés d'un plan interne avant ouverture. Leur difficulté s'adapte aux résultats et au profil.

`Colle.temps_restant(self, maintenant=None)` calcule les secondes restantes depuis `debut + duree`, sans pause. Durée par défaut : 30 minutes (`COLLE_DUREE_MINUTES`, bornée à 5–120). Préparation, transcription, écoute et appels réseau consomment ce temps. Le navigateur extrapole `etat.temps_restant` et appelle le bilan à zéro dès qu'aucun tour n'est occupé ; le serveur vérifie aussi l'expiration avant/après un tour et avant une nouvelle tâche. Un tour engagé peut donc finir après l'échéance.

Clôture : programme épuisé, temps écoulé ou bouton « Terminer ». `Examinateur.bilan(self)` produit le bilan déterministe, appelle `Colle.terminer(self, bilan)` et publie l'état final. Une tâche interrompue n'est pas un échec ; les difficultés déjà observées sont conservées dans le profil. Une tâche close passe par `Colle.clore(self)` ; le serveur ouvre ensuite la suivante. Ne jamais déclencher cette progression depuis une modalité.

Chaque `Examinateur.tour(self, message)` classe l'intention ; seule `reponse` est évaluée. `Colle.appliquer(self, message, intention, evaluation)` délègue à `appliquer_tour(tache, message, intention, ev=None)`. Les règles, dans leur ordre, sont :

- `question` → réponse de compréhension ; `hors_sujet` → recadrage ; jugement `indeterminable` → précision, sans tentative consommée. On reste sur l'élément.
- `correcte` → validation de l'élément. Sinon, blocage à **deux tentatives + demandes d'aide cumulées par élément** ; seules les réponses déterminables incrémentent les tentatives, et `blocage`/`demande_indice` les demandes d'aide.
- Exercice encore autonome (`etape_active = -1`) : blocage, correction/saut demandé, aide demandée, ou stagnation après indice → révélation de la première étape, sans terminer la tâche.
- Sinon, limite atteinte ou correction/saut demandé → réponse donnée, élément clos. Avant cette limite : erreur de concept/domaine → rappel de cours ; réponse incomplète sans indice → complément ; sinon → indice.

Les étapes guidées sont révélées une par une, chacune avec ses compteurs. Validation/correction passe à la suivante ; la dernière clôt la tâche. Une réussite autonome clôt directement l'exercice. Les questions de compréhension ne consomment pas de tentative mais comptent comme aides (`indices`), tout comme les indices, rappels de cours et révélations. `progression` n'est pas une permission de passer à la suite.

## 2. Évaluation et note

Source unique des consignes : [méthode d'évaluation](../methods/evaluation_maths_prepa/). Entrée via `Examinateur.evaluer(self, client, message)` puis `app.evaluation.evaluer(enonce, reponse, corrige, *, openai=None, pipelex=None, moteur=None, contexte=None)` (coroutines).

L'évaluateur reçoit la question de l'élément actif, le corrigé vérifié correspondant, les interventions textuelles cumulées de la tâche (nouveau message compris), et un contexte : réponses/aides de l'élément, compteurs, interventions rattachées aux éléments, résultats antérieurs avec indication des réponses données par l'agent, notions autorisées. Dans la méthode, les quatre entrées sont `enonce`, `reponse_eleve`, `corrige`, `contexte` (ce dernier est une chaîne JSON). Il juge la compréhension, accepte le langage oral et les rectifications ; il n'attribue pas les réponses du colleur à l'élève. Le moteur local par défaut et Pipelex utilisent la même méthode.

Sortie validée, exactement six champs, sans note ni action :

| Champ | Format / valeurs |
|---|---|
| `verdict` | `correcte`, `incorrecte`, `incomplete`, `indeterminable` |
| `type_erreur` | `aucune`, `calcul`, `raisonnement`, `concept`, `hypothese_ou_domaine`, `notation`, `justification_insuffisante`, `reponse_incomplete`, `hors_sujet`, `non_determinable` |
| `intuition` | `solide`, `partielle`, `absente` |
| `progression` | `avance`, `stagne`, `recule` |
| `notions_fragiles` | Liste de chaînes du vocabulaire autorisé ; vide si correcte/indéterminable selon les consignes |
| `explication` | Chaîne non vide ; consigne : français, 1–3 phrases, 80 mots maximum |

`aucune` équivaut à `correcte` ; `indeterminable` exige `non_determinable`.
`calculer_score(ev, indices=0, tentatives=1, reponse_donnee=False)` calcule `(0,7 × V + 0,3 × I) × 0,9^indices`, avec V = 1 / 0,6 / 0,2 pour correcte/incomplète/incorrecte, I = 1 / 0,5 / 0 pour solide/partielle/absente. `tentatives` n'ajoute aucune pénalité. Réponse donnée : plafond 0,25 (zéro sans évaluation) ; indéterminable : score absent. En guidage : moyenne des scores présents des étapes, multipliée par `0,9^indices_autonomes` ; toute réponse révélée plafonne aussi la tâche à 0,25. Scores arrondis à quatre décimales.

`note_bilan(taches)` : cours **3**, démonstration **4**, application **5**, exercices **3 + 3 + 2**. Somme des points × scores, arrondie à une décimale sur 20, sans redistribution. Non traité/interrompu/non évaluable : zéro point, sans diagnostic d'échec.

## 3. Interface et contrat de transport

[Flask](../app/web/__init__.py) sert `/` avec [chat.html](../app/web/templates/chat.html) : JSON initial `#donnees`, formulaire `#saisie`, textarea `#message`, aperçu `#apercu`, dialogue `#fil`. [colle.js](../app/web/static/colle.js) gère les échanges et KaTeX. `auth.html`/`compte.html` concernent les comptes ; `guide_kholle.html`/`guide_concours.html` les routes publiques `/reussir-sa-kholle` et `/guide-concours`.

| Route | Entrée → sortie |
|---|---|
| `GET /api/etat` | État public JSON : `chapitres`, `duree` (minutes), `anciennes`, `messages`, `etat` |
| `POST /api/colle` | `{"chapitre": index_entier}` issu de `chapitres` → même JSON, première question dans `messages[].question` |
| `POST /api/message` | `{"message": "texte élève"}` → événements NDJSON |
| `POST /api/bilan` | `{}` → NDJSON de clôture |
| `POST /api/nouvelle` | `{}` → efface la séance courante, conserve le profil, renvoie l'état d'accueil ; ce n'est pas un bilan |

Session authentifiée et en-tête `X-CSRF-Token` de la meta `csrf` pour les POST ; `Content-Type: application/json`. Message non blanc, chaîne de 6 000 caractères maximum ; corps HTTP limité à 64 Kio. Erreurs HTTP JSON `{"erreur":"…"}` : notamment 400, 401, 409 (tour occupé), 503. Aucun média binaire/base64 dans `message`.

`api_message()` appelle `diffuser(examinateur, examinateur.tour(message))`. Les coroutines `demarrer()` et générateurs asynchrones `tour(message)`/`bilan()` de l'examinateur sont orchestrés par les services partagés. Un seul tour par élève ; sauvegarde et libération dans `finally`, même après déconnexion du navigateur.

`flux(url, corps, surEvenement)` décode une ligne JSON par événement, indépendamment des paquets réseau : `statut`/`texte`/`erreur` portent `texte` ; `action` porte `action` et `verdict` (éventuellement null) ; `question` porte `{etape, libelle, texte}` ; `etat` porte `etat`. `suivreColleur(url, corps, {apresErreur} = {})` concatène les textes, rend via `requestAnimationFrame`, ajoute la question puis actualise l'état ; il ignore actuellement `action`. **Ce n'est pas du SSE ni du texte token par token** : le serveur assemble les fragments du modèle puis applique `texte_eleve` avant émission. Plusieurs événements `texte` restent possibles, notamment avec le bilan.

## 4. Raccordements autorisés et invariants

**Manuscrit et oral → texte.** À la sortie de vos composants existants, placer la transcription finale dans `#message`, appeler `majApercu()`, puis soumettre via `envoyer(evenement)` (événement facultatif). C'est le chemin commun : bulle élève, `occupe`, POST, récupération du brouillon après erreur. Une saisie = une intervention finale ; ne pas envoyer chaque hypothèse de reconnaissance, ni enrichir/corriger mathématiquement la réponse. Conserver le texte et le LaTeX (`$…$`) ; `JSON.stringify` assure l'échappement. Adapter les contrôles de modalité à `occuper(etat)` et à `etat.terminee`. Aucun accès direct à l'évaluateur : il perdrait la classification, l'historique et les compteurs.

**Texte public → synthèse vocale.** Brancher la lecture de l'énoncé sur `question.texte` : après `demarrer(index, bouton)` pour la première question, puis dans le traitement de l'événement `question` de `suivreColleur`. `ajouterQuestion(article, question)` est le point de rendu commun, mais il est aussi appelé au rechargement : ne pas y lancer automatiquement toutes les lectures. Pour lire la consigne guidée actuelle, utiliser `etat.tache.question_active` reçu par `majEtat(etat)` ; `etape_resolution` vaut null en autonomie puis 1, 2… Les transitions guidées arrivent en `texte` puis `etat`, pas nécessairement en `question`. Ne pas lire deux fois la même consigne. La sortie audio reste locale à la modalité ; elle ne renvoie aucun message élève et ne modifie pas le chronomètre.

**À préserver.** `rendre(element, texte)` échappe le HTML, préserve les formules puis appelle KaTeX (`trust:false`, `throwOnError:false` ; `$…$`, `$$…$$`, `\(…\)`, `\[…\]`). Fournir le texte source à la synthèse, pas le DOM KaTeX. Ne pas modifier ce rendu ni les filtres publics pour une adaptation vocale. Ne jamais exposer `reference`, le plan complet, les prompts ou les fichiers de séance. Ne pas modifier méthode d'évaluation, règles/scoring, profils, sélection, persistance ou verrous : ils garantissent équité et continuité. Après une coupure, resynchroniser via `/api/etat` ; ne pas rejouer automatiquement un POST, car le serveur peut avoir terminé le tour.

Validation du raccordement : même transcription → même parcours que le clavier ; première question et étapes guidées lisibles sans doublon ; aucune soumission intermédiaire ; erreur réseau, tour occupé, expiration et reprise gérés. Régressions existantes : `python -m unittest app.test_moteur_colle app.test_evaluation app.test_examinateur app.web.test_chat` ; contrôle navigateur du rendu : `node scripts/verifier_rendu_katex.cjs`.
