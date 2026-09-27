# Évaluation unique et décisions pédagogiques déterministes

## Architecture livrée

- `methods/evaluation_maths_prepa/main.mthds` : un seul PipeLLM, modèle `gpt-5.4`, méthode validée comme exécutable par l'API Pipelex. `gpt-4.1` a été refusé par le catalogue Pipelex ; il reste utilisé uniquement pour la préparation hors session via OpenAI.
- Entrées : énoncé, corrigé intégral du catalogue (ou passage source du cours), réponse actuelle et déroulé JSON textuel contenant question active, réponse attendue de l'étape, tentatives, indices reçus, réponses précédentes et vocabulaire exact du cours.
- Sorties : verdict, type_erreur, notions_fragiles, intuition, explication. Les formulations orales justes sont acceptées. La référence incohérente impose indeterminable.
- `app/pedagogie.py` : score et décision, sans réseau. `app/profil.py` : historique, niveau et choix d'exercice. `app/parcours.py` : deux tentatives, correction, reformulation, franchissement et persistance.
- `app/agent.py` : préparation locale des questions et lecture des plans persistés. Aucun appel de dialogue, de reconstruction ou d'embedding pendant une réponse. Un appel d'évaluation pour une tentative mathématique ; zéro pour afficher une tâche, demander un indice ou reformuler après une réponse donnée.
- Ancienne méthode de progression, types générés et chemins d'appel supprimés. Les catégories de chronométrage historiques restent lisibles.

## Score et règles

Score brut = 0,7 × verdict + 0,3 × intuition.

| Entrée | Valeurs |
|---|---|
| Verdict | correcte 1 ; incomplete 0,45 ; incorrecte 0,05 |
| Intuition | solide 1 ; partielle 0,5 ; absente 0 |
| Indices | facteur max(0,5 ; 1 − 0,12 × nombre) |
| Tentatives | facteur max(0,7 ; 1 − 0,1 × (tentatives − 1)) |
| Réponse donnée | plafond 0,2 ; acquise toujours faux |
| Indéterminable | aucun score, tentative, évaluation ni échange ajouté au profil pédagogique |

Une réponse correcte permet d'avancer. Une réponse insuffisante à la deuxième tentative entraîne la solution et une reformulation courte ; celle-ci ne provoque pas une troisième évaluation. Au premier échec, le type d'erreur, les notions fragiles, leur historique et le score déterminent indice, référence précise ou reformulation de l'énoncé. Chaque échec déterminé reçoit un indice ou un renvoi au cours.

À la clôture d'un exercice, le niveau reçoit une fois `0,3 × max(0, (score_moyen − 0,2) / 0,8)`. Les étapes autonomes ou aidées peuvent ainsi produire un gain partiel même si une autre étape a été donnée. Une reformulation d'une réponse donnée ne crée pas un acquis. Les interfaces classique et terminal utilisent aussi le score pondéré.

Après au moins deux échecs enregistrés sur une notion, priorité à un exercice inédit qui la mobilise, choisi au plus près du niveau. Cette priorité s'applique aussi après une question de cours. À défaut, sélection normale par niveau hors exercices vus. Sans remédiation prioritaire, une définition et un théorème précèdent le catalogue : exercice à l'échange 7 dans le test avec deux échecs et une reformulation à chaque question.

## Catalogue

Les appels réels de `scripts/preparer_catalogue.py` ont annoté les 54 exercices munis d'un corrigé et enregistré leurs plans dans `data/exercices.json`. Les 58 entrées portent un champ notions et un statut de préparation. Les noms des notions des séries sont contraints au vocabulaire du cours indexé. Les autres chapitres n'ont pas de références indexées inventées.

Les quatre corrigés absents (2.4, 2.6, 2.8, 2.24) sont explicitement non exploitables. L'exercice 17.4 est écarté après relecture de la trace réelle : la source autorise un terme initial réel quelconque, mais affirme la positivité dès le rang zéro. Les sources originales n'ont pas été réécrites. Il reste 53 préparations utilisables, dont 30 exercices de séries.

Chaque préparation conserve une empreinte des sources, la date et le modèle. Modifier l'énoncé ou le corrigé invalide le cache. Le script reprend uniquement les entrées non préparées ou périmées. Les plans générés restent probabilistes : cette validation ciblée ne constitue pas une relecture mathématique exhaustive des 54 corrigés.

## Vérifications

- 63 tests ciblés réussis : score, borne, remédiation, exclusion des vus, cache périmé, confidentialité, reprise, absence de mutation pour indeterminable, un appel même lors du changement de tâche, HTTP et authentification.
- Six cas d'évaluation réels réussis avec le prompt final : définition orale, fausse condition suffisante, critère de Riemann formulé oralement, preuve amorcée mais incomplète, référence illisible et référence contradictoire. Entrées, attendus et sorties complets : [evaluation-orale-architecture.json](evaluation-orale-architecture.json).
- Huit échanges avec le vrai agent et Pipelex : [conversation complète](parcours-borne-reel-20260927-141807/conversations.md), [résultat](parcours-borne-reel-20260927-141807/resultat.json). Deux échecs au cours, correction référencée, reformulation et nouvelle tâche ; deux échecs sur une étape d'exercice, réponse donnée puis étape suivante sans acquisition fictive. Ce test ciblé initialise séparément le cours et le catalogue ; ce n'est pas une session longitudinale complète.
- La trace précédente [141317](parcours-borne-reel-20260927-141317/conversations.md) a permis de repérer le défaut du corrigé 17.4. Elle ne valide pas la qualité mathématique de ce corrigé.
- La découverte générale des tests révèle un échec préexistant dans `app/test_chapitres.py`, sur huit variantes d'alias. Ni ce test ni `app/chapitres.py` n'ont été modifiés par cette refonte. Les 63 tests ciblés passent ; la suite générale n'est donc pas entièrement verte.

Les anciennes conversations longitudinales restent dans leurs rapports d'origine. Les douze sessions ne sont pas présentées ici comme rejouées avec cette nouvelle architecture.
