# Proposition de rangement pour le rendu hackathon

?tat audit? : branche `modalites-integrees`, commit `5dbc1c8`, le 27 septembre 2026.
**Proposition uniquement : aucune suppression, aucun retrait de suivi Git effectu?.**

Le classement porte sur tous les fichiers suivis au d?but de l?audit. Les fichiers ignor?s (`.env`, environnements virtuels, comptes et profils locaux, caches Python) restent intacts. Le pr?sent document est ? conserver.

M?thode : lecture du point d?entr?e `python -m app.web`, des imports Python (analyse AST et recherche textuelle), des routes et des donn?es charg?es, puis inspection des scripts et de leurs consommateurs. ? Non branch? au parcours ? n?implique pas ? inutile ? : les outils de reconstruction et de v?rification r?utilisables sont conserv?s. Cette analyse statique devra ?tre confirm?e par les tests apr?s rangement.

## ? supprimer apr?s validation

Les chemins ci-dessous sont explicites et constituent le p?rim?tre propos?. Les changements associ?s font partie du rangement : adapter `app/test_pedagogie.py` pour conserver le test des notions invent?es avec un import direct de `app.evaluation.valider`, et retirer le test qui v?rifie uniquement les alias supprim?s ; remplacer l?ancien point d?entr?e d?extraction dans `scripts/EXTRACTION.md`. Conserver `app/test_parcours.py` : malgr? son nom, il teste le moteur actuel.

18 fichiers :

| Chemin | Motif |
|---|---|
| `NOTES.md` | Description du prototype initial, d?sormais contredite par le README et le parcours web. |
| `app/chronometrage.py` | Ancienne instrumentation sans appel dans le parcours actuel ; uniquement import?e par son test. |
| `app/generated/__init__.py` | Types et m?tadonn?es de progression_colle sans import applicatif ; comprend les fichiers d?initialisation devenus inutiles. |
| `app/generated/progression_colle/__init__.py` | Types et m?tadonn?es de progression_colle sans import applicatif ; comprend les fichiers d?initialisation devenus inutiles. |
| `app/generated/progression_colle/codegen.lock` | Types et m?tadonn?es de progression_colle sans import applicatif ; comprend les fichiers d?initialisation devenus inutiles. |
| `app/generated/progression_colle/models.py` | Types et m?tadonn?es de progression_colle sans import applicatif ; comprend les fichiers d?initialisation devenus inutiles. |
| `app/generated/progression_colle/sources.json` | Types et m?tadonn?es de progression_colle sans import applicatif ; comprend les fichiers d?initialisation devenus inutiles. |
| `app/parcours.py` | Fa?ade de compatibilit? sans import ; le parcours est int?gr? ? Colle et Examinateur. |
| `app/pedagogie.py` | Alias de compatibilit? utilis?s uniquement par app/test_pedagogie.py ; conserver son contr?le de validation en important directement app.evaluation. |
| `app/questions_cours.py` | Ancien dictionnaire QUESTIONS sans import ni utilisation ; les banques JSON sont utilis?es. |
| `app/test_chronometrage.py` | Tests exclusifs de cette instrumentation d?branch?e. |
| `app/tuteur.py` | Ancien terminal de s?lection d?exercices, distinct de la kh?lle actuelle ; remplac? pour la d?monstration par scripts/simuler_colle.py. |
| `methods/progression_colle/main.mthds` | Ancienne d?cision de progression Pipelex ; aucune invocation actuelle, remplac?e par moteur_colle.py. |
| `scripts/codegen_check.py` | V?rification des seuls types g?n?r?s du prototype de progression abandonn?. |
| `scripts/extract_topologie.py` | Alias historique de extract_chapitre.py ; mettre ? jour les deux commandes et l?explication dans scripts/EXTRACTION.md. |
| `test_methode.py` | Script manuel historique ; les tests d??valuation et verifier_evaluation_orale.py assurent la couverture actuelle. |
| `test_progression.md` | R?sultat g?n?r? de cette ancienne simulation. |
| `test_progression.py` | Simulation de l?ancien choix d?exercices par profil, hors moteur actuel. |

## ? retirer du suivi Git mais garder en local

Ajouter des r?gles cibl?es ? `.gitignore`, puis retirer uniquement ces fichiers de l?index Git en conservant leur contenu sur disque. Les anciennes traces ne certifient pas le rendu final ; un nouveau compte rendu de validation sera ?crit apr?s les essais. Cela ne retire pas les versions d?j? pr?sentes dans l?historique Git.

166 fichiers, liste exacte :

| Chemin | Motif |
|---|---|
| `data/apercu_topologie/extraction_brute.json` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/apercu_topologie/page_203.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/apercu_topologie/page_52.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_10.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_100.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_101.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_102.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_103.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_104.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_105.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_106.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_11.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_12.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/chapitre_2_sources/page_99.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/cours/page_139_apercu.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/cours/page_140_apercu.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/cours/page_141_apercu.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/cours_apercu.md` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/cours_edl_apercu.md` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/enonces_a_verifier.md` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/etoiles_verification.png` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/exercices.apercu.md` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/extraction_chapitre_14.audit.json` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/extraction_chapitre_17.audit.json` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/extraction_chapitre_2.audit.json` | Aper?u, contr?le visuel ou audit de pr?paration ; garder localement pour la relecture et la tra?abilit?. |
| `data/profil.json` | Profil produit par l?ancien tuteur ; donn?e locale, diff?rente des banques et des profils de tests synth?tiques. |
| `reports/architecture-pedagogique-20260927.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/.gitignore` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/bilan-faible.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-protocole.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-1-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-1-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-1.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-1.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-2-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-2-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-2.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-2.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-3-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-3-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-3.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-3.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-4-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-4-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-4.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/faible-session-4.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/mesures.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-protocole.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-1-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-1-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-1.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-1.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-2-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-2-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-2.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-2.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-3-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-3-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-3.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/moyen-session-3.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/observations-relues.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/profils/audit-longitudinal.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/releve-factuel.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927-reel/source-page49.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/.gitignore` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/faible-protocole.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/faible-serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/faible-session-1-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/faible-session-1-avant.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/faible-session-1.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/faible-session-1.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/audit-pedagogie-20260927/profils/audit-longitudinal.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/chronometrage-20260927.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/chronometrage-20260927.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/corrections-deroule-colle-20260927.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/diagnostic-profil/README.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/diagnostic-profil/profil-apres.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/diagnostic-profil/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/evaluation-orale-architecture.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/integration-moteur-colle-20260927.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/optimisation-pipelex-20260927.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/optimisation-pipelex-20260927.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-133841/conversations.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-133841/conversations.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-133841/profil-cours.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-133841/profil-exercice.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-133841/resultat.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-134142/conversations.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-134142/conversations.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-134142/profil-cours.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-134142/resultat.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141317/conversations.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141317/conversations.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141317/profil-cours.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141317/profil-exercice.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141317/resultat.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141807/conversations.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141807/conversations.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141807/profil-cours.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141807/profil-exercice.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/parcours-borne-reel-20260927-141807/resultat.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-105231/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-105231/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-105231/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-105333/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-105333/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-105333/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110251/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110251/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110251/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110424/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110424/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110424/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110517/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110517/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110517/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110747/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110747/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110747/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110947/README.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110947/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110947/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-110947/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113735/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113735/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113735/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113735/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113834/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113834/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113834/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-113834/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-114527/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-114527/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-114527/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-114527/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115146/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115146/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115146/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115146/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115207/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115207/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115207/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115207/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115502/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115502/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115502/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115502/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115519/profils/verification-profil.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115519/serveur.log` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115519/session.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/session-reelle-20260927-115519/utilisateurs.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/guide-nom-0.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/guide-nom-1.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/manuscrit-mobile.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/manuscrit-test.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/resultats.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/verification.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-modalites/vision-reelle.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-parcours-borne-20260927.md` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-rendu-katex/chat-1280.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-rendu-katex/chat-390.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-rendu-katex/classique-1280.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-rendu-katex/classique-390.png` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |
| `reports/verification-rendu-katex/resultats.json` | Archive de diagnostic : conserver les preuves, traces, captures et profils en local ; aucun usage au d?marrage. |

## ? conserver

- Le moteur actuel, l?interface, les modalit?s de communication et leurs tests. `app/notation.py` est utilis? par les plans : il ne faut pas le confondre avec une ancienne notation abandonn?e.
- La m?thode d??valuation Pipelex, utilis?e aussi par le mode OpenAI direct.
- Les sources PDF, attributions, banques JSON, index avec embeddings, cache d??nonc?s, plans et liens de notions. Les fac-simil?s `data/extraits/` restent associ?s au catalogue.
- Les scripts de reconstruction et leurs transcriptions relues, m?me s?ils ne sont pas import?s par le serveur.
- Les outils de v?rification, fixtures visuelles et audits rejouables : `simuler_colle`, `session_reelle_profil`, `audit_sessions_reelles`, `bilan_sessions_reelles`, `verifier_parcours_reel`, `verifier_evaluation_orale`, `verifier_recherche_cours`, `verifier_enonces`, `verifier_manuscrit_reel`, les contr?les JavaScript des modalit?s et de KaTeX. Leurs r?sultats historiques peuvent rester locaux sans supprimer l?outil qui les produit.
- Les guides, leurs sources, logos et mentions d?origine ; les droits signal?s dans le README restent ? clarifier, sans retirer de contenu ? ce stade.

116 fichiers suivis ? conserver :

- `.env.example`
- `.gitignore`
- `README.md`
- `app/catalogue_pedagogique.py`
- `app/chapitres.py`
- `app/colle.py`
- `app/config.py`
- `app/cours.py`
- `app/enonces.py`
- `app/evaluation.py`
- `app/examinateur.py`
- `app/faux.py`
- `app/modalites.py`
- `app/moteur_colle.py`
- `app/notation.py`
- `app/plans.py`
- `app/profil.py`
- `app/services.py`
- `app/test_catalogue_pedagogique.py`
- `app/test_chapitres.py`
- `app/test_colle.py`
- `app/test_corrections_colle.py`
- `app/test_cours.py`
- `app/test_edl.py`
- `app/test_enonces.py`
- `app/test_evaluation.py`
- `app/test_examinateur.py`
- `app/test_moteur_colle.py`
- `app/test_notation.py`
- `app/test_parcours.py`
- `app/test_pedagogie.py`
- `app/test_plans_moteur.py`
- `app/test_profil_moteur.py`
- `app/test_selection_moteur.py`
- `app/texte_eleve.py`
- `app/web/__init__.py`
- `app/web/__main__.py`
- `app/web/auth.py`
- `app/web/modalites.py`
- `app/web/requirements.txt`
- `app/web/static/branding/SOURCES.md`
- `app/web/static/branding/ens-psl.png`
- `app/web/static/branding/polytechnique.png`
- `app/web/static/colle.css`
- `app/web/static/colle.js`
- `app/web/static/guides.css`
- `app/web/static/guides/10-reflexes-oral-kholle.pdf`
- `app/web/static/guides/10-reflexes-oral-kholle.tex`
- `app/web/static/guides/guide-concours-oraux-2026.pdf`
- `app/web/static/guides/guide-concours-oraux-2026.tex`
- `app/web/static/micro-worklet.js`
- `app/web/static/modalites.js`
- `app/web/static/style.css`
- `app/web/static/tableau.js`
- `app/web/templates/auth.html`
- `app/web/templates/chat.html`
- `app/web/templates/compte.html`
- `app/web/templates/guide_concours.html`
- `app/web/templates/guide_kholle.html`
- `app/web/templates/guides_navigation.html`
- `app/web/test_auth.py`
- `app/web/test_chat.py`
- `app/web/test_modalites.py`
- `data/ATTRIBUTION.md`
- `data/cours/analyse.pdf`
- `data/cours_edl_index.json`
- `data/cours_edl_passages.json`
- `data/cours_index.json`
- `data/cours_passages.json`
- `data/cours_recherche_tests.json`
- `data/enonces_verifies.json`
- `data/enonces_verifies.plans.json`
- `data/exercices.json`
- `data/extraits/2.10_corrige_101.png`
- `data/extraits/2.10_corrige_102.png`
- `data/extraits/2.13_corrige_102.png`
- `data/extraits/2.20_corrige_104.png`
- `data/extraits/2.9_corrige_100.png`
- `data/extraits/2.9_corrige_101.png`
- `data/notions_exercices.json`
- `data/notions_questions.json`
- `data/poly.pdf`
- `data/questions_cours.json`
- `data/questions_cours_edl.json`
- `docs/integration-modalites.md`
- `docs/modalites-communication.md`
- `methods/evaluation_maths_prepa/main.mthds`
- `requirements.txt`
- `scripts/COURS.md`
- `scripts/EXTRACTION.md`
- `scripts/annoter_notions_colle.py`
- `scripts/audit_sessions_reelles.py`
- `scripts/bilan_sessions_reelles.py`
- `scripts/extract_chapitre.py`
- `scripts/fixture_modalites.py`
- `scripts/fixture_rendu_katex.py`
- `scripts/index_cours.py`
- `scripts/lister_formules_coupees.py`
- `scripts/preparer_catalogue.py`
- `scripts/preparer_cours_edl.py`
- `scripts/requirements-cours.txt`
- `scripts/session_reelle_profil.py`
- `scripts/simuler_colle.py`
- `scripts/test_extract_chapitre.py`
- `scripts/test_index_cours.py`
- `scripts/test_lister_formules_coupees.py`
- `scripts/transcriptions/chapitre_2.json`
- `scripts/transcriptions/cours_edl.json`
- `scripts/transcriptions/cours_series.json`
- `scripts/verifier_enonces.py`
- `scripts/verifier_evaluation_orale.py`
- `scripts/verifier_manuscrit_reel.py`
- `scripts/verifier_modalites.cjs`
- `scripts/verifier_parcours_reel.py`
- `scripts/verifier_recherche_cours.py`
- `scripts/verifier_rendu_katex.cjs`

## V?rification pr?vue apr?s accord

1. Appliquer seulement le p?rim?tre valid? et les adaptations associ?es, puis v?rifier les r?f?rences restantes.
2. Ex?cuter les tests hors ligne du moteur, des donn?es, de l?interface et des scripts.
3. Pr?parer un clone de validation contenant exactement la version candidate, avec un environnement Python neuf, sans r?utiliser `.venv` ni les profils locaux. Installer les d?pendances et contr?ler le lancement HTTP.
4. Fournir les cl?s par l?environnement local de test, sans les versionner. Parcourir une kh?lle compl?te au clavier avec les vraies API, jusqu?au bilan : cours, d?monstration, application, exercices, note, sauvegarde et rechargement. Tester aussi une demande d?aide et une r?ponse ? compl?ter. Aucun raccourci `/juste` ne remplacera l?essai de l?interface.
5. Consigner les commandes, la version test?e, le syst?me, les r?sultats et les limites. V?rifier Linux r?ellement si un environnement Linux est disponible ; sinon signaler explicitement que seules les instructions Linux ont ?t? relues.

L?int?gration dans `main` n?a pas ?t? faite : le travail demand? reste sur `modalites-integrees`.
