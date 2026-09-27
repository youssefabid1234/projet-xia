# Intégration du moteur pédagogique — 27 septembre 2026

Le parcours web utilise désormais les règles de app/moteur_colle.py.
Colle conserve la séance et le profil ; Examinateur organise les services et
le dialogue. Les anciens prototypes pedagogie.py et parcours.py réexportent
le moteur commun, sans règles concurrentes.

## Validation étape par étape

| Étape | Résultat | Validation au passage de l'étape |
|---|---|---|
| 1. Règles pures | Score, borne de deux essais, étapes intermédiaires, indétermination neutre, phases épuisées | 6 tests |
| 2. Profil | Fragilités par chapitre, consolidation, clôture idempotente, anciens profils lisibles | 10 tests cumulés |
| 3. Sélection | Recherche par notion, difficulté de repli, exclusions, alias des chapitres | 15 tests cumulés |
| 4. Plans | Plan privé, cache persistant, invalidation, compteurs et historiques séparés | 18 tests cumulés |
| 5. Évaluation | Six champs, contexte pédagogique, tolérance à la forme, transports local/Pipelex | 26 tests cumulés et validation Pipelex |
| 6. Parcours actif | Branchement de Colle/Examinateur, transitions rendues par le serveur, pannes réessayables | 47 tests cumulés |
| 7. Web et bilan | Reconnexion HTTP, confidentialité, note déterministe, migration et interruption sans pénalité | 97 tests réussis, suite complète de l'application |

Commande de vérification hors ligne :

    .venv/Scripts/python.exe -m unittest discover -s app -q

La validation Pipelex de methods/evaluation_maths_prepa/main.mthds a retourné
is_valid: true, is_runnable: true, pending_signatures: [].
La compétence utilisée pour ce contrat est pipelex-design.

Flux de la méthode : énoncé + réponse + corrigé + contexte → un jugement à six
champs. Son gabarit d'entrée est :

    {
      "enonce": "texte de l'élément actif",
      "reponse_eleve": "nouvelle réponse",
      "corrige": "référence de cet élément",
      "contexte": "JSON sérialisé des réponses précédentes, aides et notions autorisées"
    }

## Choix de conception

- Score : 70 % verdict (1 / 0,6 / 0,2) + 30 % intuition (1 / 0,5 / 0),
  moins 0,15 par aide et 0,05 par tentative supplémentaire sur l'élément.
  Une réponse incomplète avec une intuition solide vaut 0,72 avant pénalités.
- En exercice guidé, le score agrège à poids égal les scores des étapes,
  puis retire le coût des aides de la recherche autonome. Le nombre d'étapes
  nécessaire à la résolution n'est pas en lui-même une pénalité.
- Dès qu'une réponse d'élément est donnée par l'agent, la tâche entière reste
  non acquise et son score est plafonné à 0,25. Une réussite avec seulement
  des indices peut être acquise, mais rapporte moins.
- Les demandes d'indice ou blocages partagent la borne de deux avec les essais.
  Une question de compréhension n'utilise pas d'essai, mais sa réponse compte
  comme aide. Une demande de correction/saut termine l'élément ; pendant
  la recherche autonome d'un exercice, elle ouvre d'abord le guidage.
- L'énoncé entier est affiché au départ. Un blocage explicite révèle la première
  étape ; deux réponses non concluantes à l'ensemble font de même. Chaque étape
  révélée dispose ensuite de son propre compteur. Réussir une étape intermédiaire
  fait avancer d'une étape, sans clôturer tout l'exercice.
- L'indétermination n'ajoute ni tentative, ni pénalité, ni fragilité ; les
  messages restent dans le dialogue, mais pas dans l'historique évalué.
- Chaque tentative problématique peut signaler une notion une fois. Les
  erreurs intermédiaires restent mémorisées même après une réussite finale.
  Une réussite autonome sans erreur préalable consolide d'un point.
- Le seuil de priorité reste deux signalements. Les notions les plus fragiles
  passent en premier ; les départages sont déterministes. Les contenus acquis
  et ceux déjà posés sont exclus des questions ; les exercices vus sont exclus.
- Niveau : variation de 0,4 × (score − 0,5), bornée à l'intervalle [1, 5].
  Une clôture répétée n'ajoute aucun gain ni signalement.
- Phases : cours 3 réussites / 5 tâches, démonstration 1 / 2, application 1 / 3.
  Une phase épuisée est traversée ; les exercices n'ont pas de plafond artificiel.
  La clé historique applications est conservée pour la compatibilité.
- Le classificateur d'intention est conservé. Une réponse mathématique déclenche
  un seul jugement ; une demande d'aide n'en déclenche aucun. Les décisions
  pédagogiques ne sont jamais confiées au classificateur ou au rédacteur.
- Les corrections et les transitions d'étapes sont rendues par le serveur.
  Le rédacteur ne reçoit que la référence de l'élément actif, pas le plan futur.
- Le bilan utilise une note calculée : cours 6, démonstration 4, application 5,
  exercices 5, avec renormalisation sur les phases effectivement notées.
  Le modèle rédige les commentaires. Une tâche interrompue n'est pas notée ;
  ses difficultés observées restent toutefois archivées dans le profil.
- Après expiration, un nouveau message n'est pas évalué. Une préparation qui
  échoue temporairement reste réessayable ; un ancien exercice définitivement
  non décomposable est écarté sans baisse de niveau.

## Données et portée de la validation

Les 31 exercices de séries disposent d'annotations dans
data/notions_exercices.json, liées à l'empreinte des sources.
Les 50 questions de cours sont reliées au vocabulaire canonique, y compris
les applications dont la source est un exemple.

Les textes des exercices/corrigés extraits ne sont pas réécrits. Les plans sont
générés au premier besoin à partir de la référence vérifiée, puis cachés.
Les anciens niveaux et historiques sont conservés ; aucune intuition ou
progression n'est inventée pour les anciens jugements à trois champs.

Les tests utilisent des services simulés. Ils vérifient les décisions, contrats,
transports, sauvegardes et réponses HTTP, mais ne mesurent pas la qualité
mathématique des réponses d'un modèle réel. Aucun lot de générations réelles
de plans ni aucune colle payante n'a été exécuté pour cette validation.
L'interface classique conserve son API historique ; cette migration vise
le parcours de colle.
