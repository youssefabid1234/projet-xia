"""Validation hors ligne, export lisible et sondes réelles du tuteur.

Une sonde « réaction » rejoue une relance de référence dans un historique
contrôlé. Elle ne prétend pas simuler un élève répondant à une relance libre.
Les verdicts pédagogiques restent à renseigner par un relecteur.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import re
import tempfile
import time
from collections import Counter
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from .banque import CAS, CHAPITRE

RACINE = Path(__file__).resolve().parent
BRANCHES = ("justifiee", "erreur_persistante", "blocage")
STATUTS = {"correcte", "incorrecte", "incomplete", "hors_sujet", "aide", "correction"}
CRITERES = (
    "exactitude_mathematique", "defi_cible_sans_verdict_initial",
    "indice_proportionne", "prise_en_compte_reaction",
    "progression_sans_boucle", "ton_et_clarte",
)


def verifier(cas_liste=CAS):
    erreurs = []
    if len(cas_liste) != 100:
        erreurs.append(f"Attendu : 100 cas ; reçu : {len(cas_liste)}.")
    ids = [c.get("id") for c in cas_liste]
    if ids != [f"K{n:03d}" for n in range(1, 101)]:
        erreurs.append("Les identifiants doivent être uniques et aller de K001 à K100.")
    familles = Counter(c.get("famille") for c in cas_liste)
    if len(familles) != 10 or set(familles.values()) != {10}:
        erreurs.append("Attendu : 10 familles de 10 cas.")
    titres = [c.get("titre") for c in cas_liste]
    if len(set(titres)) != len(titres):
        erreurs.append("Titres dupliqués.")
    for c in cas_liste:
        identifiant = c.get("id", "?")
        for champ in ("titre", "enonce", "reference", "reponse_initiale",
                      "relance_exemple", "objectif_relance", "critere_specifique"):
            if not isinstance(c.get(champ), str) or not c[champ].strip():
                erreurs.append(f"{identifiant} : champ {champ} vide ou non textuel.")
        if c.get("statut_initial") not in STATUTS or c.get("chapitre") != CHAPITRE:
            erreurs.append(f"{identifiant} : statut ou chapitre invalide.")
        reactions = c.get("reactions", {})
        if not isinstance(reactions, dict) or set(reactions) != set(BRANCHES):
            erreurs.append(f"{identifiant} : les trois réactions sont requises.")
            continue
        for nom, reaction in reactions.items():
            if not isinstance(reaction, dict) or any(
                not isinstance(reaction.get(k), str) or not reaction[k].strip()
                for k in ("eleve", "attendu")
            ):
                erreurs.append(f"{identifiant}/{nom} : réaction incomplète.")
        if c.get("temps_eleve_secondes") is not None:
            erreurs.append(f"{identifiant} : ne pas inventer de temps de réaction élève.")
    if erreurs:
        raise ValueError("\n".join(erreurs))
    return {"cas": len(cas_liste), "reactions": sum(len(c["reactions"]) for c in cas_liste),
            "familles": dict(familles), "statut": "structure_validee_hors_ligne"}


def grille_vierge():
    return {"statut": "a_relire", "criteres": {c: None for c in CRITERES},
            "commentaire": "", "relecteur": None}


def fiche(c):
    lignes = [f"## {c['id']} — {c['titre']}", "", f"Famille : {c['famille']}", "",
              f"**Question / contexte :** {c['enonce']}", "",
              f"**Référence réservée à l'évaluateur :** {c['reference']}", "",
              f"**Première réponse de l'élève :** {c['reponse_initiale']}", "",
              f"**Statut interne :** {c['statut_initial']}", "",
              f"**Défi attendu :** {c['objectif_relance']}", "",
              f"**Exemple de relance, pas une phrase imposée :** {c['relance_exemple']}", ""]
    for nom, r in c["reactions"].items():
        lignes.extend([f"### Réaction : {nom}", "", f"Élève : {r['eleve']}", "",
                       f"Attendu : {r['attendu']}", ""])
    if c.get("historique_avant"):
        lignes.extend(["**Historique préalable injecté pour ce cas :**", ""])
        lignes.extend(f"- {m['role']} : {m['content']}" for m in c["historique_avant"])
        lignes.append("")
    if c.get("explication_avant_relance"):
        lignes.extend(["**Correction fournie avant la relance dans les sondes de réaction :**", "",
                       c["explication_avant_relance"], ""])
    lignes.extend(["Temps de réaction réel de l'élève : non mesuré dans ce scénario synthétique.", ""])
    return "\n".join(lignes)


def exporter(destination):
    verifier()
    destination.mkdir(parents=True, exist_ok=True)
    donnees = {"version": 1, "chapitre": CHAPITRE,
               "description": "100 cas, chacun avec trois réactions à une relance de référence.",
               "validation": "Structure vérifiée ; évaluation réelle du tuteur et relecture humaine distinctes.",
               "criteres": list(CRITERES), "cas": CAS}
    (destination / "cas_100.json").write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    introduction = ("# X-IA — 100 scénarios pour un khôlleur qui fait réagir\n\n"
                    "Chaque cas possède trois réactions : justification, erreur persistante, blocage. "
                    "Les exemples de relance sont indicatifs : on juge le sens et l'adaptation. "
                    "Les références sont synthétiques et ne constituent pas des annales officielles.\n\n"
                    "Statut : scénarios préparés ; aucun résultat de réussite du modèle n'est déduit "
                    "de la validation des fichiers. Voir ../README.md pour lancer des essais.\n\n")
    (destination / "scenarios_100.md").write_text(
        introduction + "\n".join(fiche(c) for c in CAS), encoding="utf-8")


def sondes(selection, phase, branche):
    for c in selection:
        if phase in ("initiale", "tout"):
            yield c, "initiale"
        if phase in ("reactions", "tout"):
            for nom in BRANCHES if branche == "toutes" else (branche,):
                yield c, nom


def preparer_agent(c, branche, chemin_profil):
    # Import différé : validation et exports n'ont besoin d'aucune dépendance API.
    from app.agent import Agent

    exercice = {"id": c["id"], "identifiant": c["id"], "chapitre": CHAPITRE,
                "enonce": c["enonce"], "corrige": c["reference"], "difficulte": 3}
    agent = Agent(chemin_profil, [exercice])
    # Une tâche d'exercice synthétique isole le comportement du khôlleur. Ce
    # montage ne prétend pas tester l'inscription ou toute la progression cours.
    agent.etape = "exercices"
    agent.chapitre = CHAPITRE
    agent.exercice = copy.deepcopy(exercice)
    agent.exercices_presentes.add(c["id"])
    agent.ouvrir_tache(agent.exercice)
    question = c["enonce"]
    # Pour ces deux cas le contexte fait partie de l'historique, pas d'une
    # instruction qui attribuerait une erreur ou une bonne réponse à l'élève.
    if c["id"] == "K096":
        question = "Étudier sum_{n>=1}(-1)^{n-1}/n."
    elif c["id"] == "K100":
        question = "Étudier sum_{n>=1}1/n^2."
    historique = [{"role": "assistant", "content": question}]
    historique.extend(copy.deepcopy(c.get("historique_avant", [])))
    if branche == "initiale":
        message = c["reponse_initiale"]
    else:
        relance = c["relance_exemple"]
        if c.get("explication_avant_relance"):
            relance = c["explication_avant_relance"] + "\n\n" + relance
        historique.extend([
            {"role": "user", "content": c["reponse_initiale"]},
            {"role": "assistant", "content": relance},
        ])
        message = c["reactions"][branche]["eleve"]
    agent.historique = historique
    agent.messages = copy.deepcopy(historique)
    agent.tache["echanges"] = [m["content"] for m in historique if m["role"] == "user"]
    agent.tache["tentatives"] = len(agent.tache["echanges"])
    # La branche n'invente aucun verdict d'un ancien évaluateur : seule la
    # conversation canonique est rejouée. Les autres compteurs restent vierges.
    agent.sauver_tache()
    return agent, message


def instantane(agent, id_tache):
    from app.profil import Profil
    profil = Profil.charger(agent.chemin_profil)
    return {"etape": agent.etape, "nouvelle_tache_autorisee": agent.nouvelle_tache_autorisee,
            "tache_active_id": agent.tache["id"] if agent.tache else None,
            "tache_testee": copy.deepcopy(profil.taches.get(id_tache)),
            "niveau": profil.niveau(CHAPITRE),
            "exercices_vus": list(profil.exercices_vus)}


def observations(texte, avant, apres, message):
    # Indices de relecture uniquement : ces heuristiques ne jugent ni la vérité
    # des mathématiques, ni la qualité d'une question, ni une réaction humaine.
    drapeaux = []
    if re.search(r"^\s*(?:oui[, !.]?\s*|non[, !.]?\s*)?(?:tu as|vous avez)\s+(?:tort|raison)\b|"
                 r"^\s*c['’]est\s+(?:faux|vrai|correct|incorrect)\b", texte, re.I):
        drapeaux.append("verdict_explicite_en_entree_a_relire")
    tache = apres.get("tache_testee")
    if tache is None:
        drapeaux.append("tache_testee_absente_du_profil")
    elif message not in tache.get("echanges", [])[len((avant.get("tache_testee") or {}).get("echanges", [])):]:
        drapeaux.append("dernier_message_non_enregistre_dans_la_tache")
    if not texte.strip():
        drapeaux.append("reponse_vide")
    return {"drapeaux_a_relire": drapeaux,
            "changement_etat": avant != apres,
            "evaluation_pedagogique": "non_automatisee"}


async def executer_sonde(c, branche, dossier, consigne="actuelle"):
    from app import agent as module_agent
    agent, message = preparer_agent(c, branche, dossier / "profil.json")
    id_tache = agent.tache["id"]
    avant = instantane(agent, id_tache)
    trace = {"cas": c["id"], "titre": c["titre"], "branche": branche,
             "protocole": "tache_isolee" if branche == "initiale" else "rejeu_relance_de_reference",
             "consigne": consigne, "modele_demande": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
             "date_utc": datetime.now(timezone.utc).isoformat(),
             "historique_fourni": copy.deepcopy(agent.historique), "message_eleve": message,
             "objectif": c["objectif_relance"], "reference_evaluateur": c["reference"],
             "attendu_reaction": c["reactions"][branche]["attendu"] if branche != "initiale" else None,
             "etat_avant": avant, "temps_reaction_eleve_secondes": None,
             "relecture": grille_vierge()}
    ajout = RACINE.joinpath("consigne.md").read_text(encoding="utf-8")
    contexte = patch.object(module_agent, "INSTRUCTIONS", module_agent.INSTRUCTIONS + "\n" + ajout) if consigne == "defi" else nullcontext()
    debut = time.perf_counter()
    try:
        with contexte:
            texte = await agent.repondre(message)
        trace.update(statut_execution="terminee", reponse_kholleur=texte)
    except Exception as erreur:
        # Ne pas enregistrer un message d'erreur fournisseur pouvant contenir
        # une clé, un en-tête ou une URL d'authentification.
        trace.update(statut_execution="erreur", type_erreur=type(erreur).__name__,
                     reponse_kholleur="")
    trace["latence_execution_secondes"] = round(time.perf_counter() - debut, 3)
    trace["etat_apres"] = instantane(agent, id_tache)
    trace["observations"] = observations(trace["reponse_kholleur"], avant, trace["etat_apres"], message)
    return trace


def selectionner(ids, tous=False):
    if tous:
        return CAS
    demandes = list(dict.fromkeys(ids or []))
    index = {c["id"]: c for c in CAS}
    inconnus = set(demandes) - index.keys()
    if inconnus:
        raise ValueError("Identifiants inconnus : " + ", ".join(sorted(inconnus)))
    if not demandes:
        raise ValueError("Choisir au moins un identifiant ou --tous.")
    return [index[i] for i in demandes]


async def lancer(args):
    verifier()
    selection = selectionner(args.ids, args.tous)
    programme = list(sondes(selection, args.phase, args.branche))
    if args.simuler:
        print(json.dumps({"statut": "simulation_sans_appel_api", "cas": len(selection),
                          "sondes": len(programme), "consigne": args.consigne,
                          "programme": [f"{c['id']}/{b}" for c, b in programme]},
                         ensure_ascii=False, indent=2))
        return 0
    if not args.sortie:
        raise ValueError("--sortie est requis pour conserver les traces d'une exécution réelle.")
    manquantes = [nom for nom in ("OPENAI_API_KEY", "PIPELEX_API_KEY") if not os.environ.get(nom, "").strip()]
    if manquantes:
        raise ValueError("Variables requises absentes : " + ", ".join(manquantes) + ". Ne pas coller les clés dans les fichiers de test.")
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    erreurs = 0
    # Mode exclusif : ne jamais remplacer silencieusement un résultat antérieur.
    with args.sortie.open("x", encoding="utf-8") as rapport:
        for numero, (c, branche) in enumerate(programme, 1):
            with tempfile.TemporaryDirectory(prefix="xia-eval-") as temporaire:
                trace = await executer_sonde(c, branche, Path(temporaire), args.consigne)
            rapport.write(json.dumps(trace, ensure_ascii=False) + "\n")
            rapport.flush()
            erreurs += trace["statut_execution"] == "erreur"
            print(f"{numero}/{len(programme)} {c['id']}/{branche} : {trace['statut_execution']} ; pédagogie à relire.")
    return 1 if erreurs else 0


def resumer(chemin):
    traces = [json.loads(ligne) for ligne in chemin.read_text(encoding="utf-8").splitlines() if ligne.strip()]
    bilan = {"sondes": len(traces), "executions_en_erreur": 0, "relues_reussies": 0,
             "relues_echouees": 0, "a_relire": 0}
    for t in traces:
        if t["statut_execution"] != "terminee":
            bilan["executions_en_erreur"] += 1
            continue
        grille = t.get("relecture", {})
        notes = grille.get("criteres", {})
        # Une note nulle signifie un échec ; None est non jugé ; bool est exclu.
        complet = (bool(grille.get("relecteur")) and grille.get("statut") == "relue"
                   and set(notes) == set(CRITERES)
                   and all(type(v) is int and v in (0, 1, 2) for v in notes.values()))
        if not complet:
            bilan["a_relire"] += 1
        elif any(v == 0 for v in notes.values()):
            bilan["relues_echouees"] += 1
        else:
            bilan["relues_reussies"] += 1
    return bilan


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commandes = parser.add_subparsers(dest="commande", required=True)
    commandes.add_parser("verifier", help="Valider les 100 cas sans API.")
    export = commandes.add_parser("exporter", help="Produire JSON et fiches Markdown.")
    export.add_argument("--dossier", type=Path, default=RACINE / "donnees")
    execution = commandes.add_parser("executer", help="Tester le vrai Agent ; appels API sauf --simuler.")
    choix = execution.add_mutually_exclusive_group(required=True)
    choix.add_argument("--ids", nargs="+")
    choix.add_argument("--tous", action="store_true")
    execution.add_argument("--phase", choices=("initiale", "reactions", "tout"), default="initiale")
    execution.add_argument("--branche", choices=(*BRANCHES, "toutes"), default="toutes")
    execution.add_argument("--consigne", choices=("actuelle", "defi"), default="actuelle")
    execution.add_argument("--simuler", action="store_true")
    execution.add_argument("--sortie", type=Path)
    synthese = commandes.add_parser("resumer")
    synthese.add_argument("rapport", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.commande == "verifier":
            print(json.dumps(verifier(), ensure_ascii=False, indent=2))
        elif args.commande == "exporter":
            exporter(args.dossier)
            print(f"Fichiers créés dans {args.dossier.resolve()}")
        elif args.commande == "executer":
            return asyncio.run(lancer(args))
        else:
            print(json.dumps(resumer(args.rapport), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as erreur:
        parser.exit(2, str(erreur) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
