"""Règles déterministes de colle, sans réseau ni persistance."""
from copy import deepcopy

PHASES = ("cours", "demonstration", "applications", "exercices")
NATURES_PAR_PHASE = {"cours": ("definition", "theoreme"), "demonstration": ("demonstration",),
                     "applications": ("applications",), "exercices": ("exercice",)}
OBJECTIFS_PHASE = {"cours": (1, 1), "demonstration": (1, 1), "applications": (1, 1), "exercices": (3, 3)}
LIMITE_TENTATIVES = 2
SEUIL_NOTION_FRAGILE = 2
BAREME = (("cours", "Question de cours", 3), ("demonstration", "Démonstration", 4),
          ("applications", "Application du cours", 5), ("exercices", "Exercice 1", 3),
          ("exercices", "Exercice 2", 3), ("exercices", "Exercice 3", 2))
ERREURS = {"calcul", "raisonnement", "concept", "hypothese_ou_domaine", "notation",
           "justification_insuffisante", "reponse_incomplete", "hors_sujet", "aucune", "non_determinable"}


def valider_evaluation(ev, notions=None):
    champs = {"verdict", "type_erreur", "intuition", "progression", "notions_fragiles", "explication"}
    if (not isinstance(ev, dict) or set(ev) != champs
            or any(not isinstance(ev[k], str) for k in ("verdict", "type_erreur", "intuition", "progression"))
            or ev["verdict"] not in {"correcte", "incomplete", "incorrecte", "indeterminable"}
            or ev["type_erreur"] not in ERREURS
            or ev["intuition"] not in {"solide", "partielle", "absente"}
            or ev["progression"] not in {"avance", "stagne", "recule"}
            or not isinstance(ev["explication"], str) or not ev["explication"].strip()
            or not isinstance(ev["notions_fragiles"], list)
            or any(not isinstance(n, str) or not n.strip() or (notions is not None and n not in notions)
                   for n in ev["notions_fragiles"])):
        raise ValueError("Format d'évaluation invalide (six champs attendus).")
    if ((ev["verdict"] == "correcte") != (ev["type_erreur"] == "aucune")
            or ev["verdict"] == "indeterminable" and ev["type_erreur"] != "non_determinable"):
        raise ValueError("Verdict et type d'erreur incohérents.")
    return deepcopy(ev)


def postes_bilan(taches):
    """Les six postes fixes ; un score absent ne décale pas les exercices suivants."""
    par_phase = {p: iter([t for t in taches if t["etape"] == p]) for p in PHASES}
    return [(libelle, points, next(par_phase[phase], None)) for phase, libelle, points in BAREME]


def note_bilan(taches):
    """Somme sur 20, sans redistribution des points des tâches non traitées."""
    return round(sum(points * (t.get("score") or 0) for _, points, t in postes_bilan(taches)
                     if t is not None), 1)


def calculer_score(ev, indices=0, tentatives=1, reponse_donnee=False):
    if ev is None:
        return 0.0 if reponse_donnee else None
    if ev["verdict"] == "indeterminable":
        return None
    base = .7 * {"correcte": 1, "incomplete": .6, "incorrecte": .2}[ev["verdict"]]
    base += .3 * {"solide": 1, "partielle": .5, "absente": 0}[ev["intuition"]]
    score = base * .9 ** indices
    return round(min(.25 if reponse_donnee else 1, score), 4)


def element(**contenu):
    return {**contenu, "tentatives": 0, "demandes_aide": 0, "indices": 0,
            "reponses": [], "evaluations": [], "aides": [], "score": None,
            "terminee": False, "acquise": False, "reponse_donnee": False}


def installer_tache(tache, plan=()):
    tache.update(version_moteur=1, etape_active=-1, autonome=element(),
                 etapes_resolution=[element(**deepcopy(s)) for s in plan],
                 tentatives_totales=0, score=None, acquise=False, reussie=False,
                 reponse_donnee_par_agent=False, contexte_action=None)
    return tache


def element_actif(tache):
    i = tache["etape_active"]
    return tache["autonome"] if i < 0 else tache["etapes_resolution"][i]


def phase_terminee(phase, taches):
    reussites, plafond = OBJECTIFS_PHASE[phase]
    faites = [t for t in taches if t["etape"] == phase]
    return sum(bool(t.get("acquise", t.get("statut") == "acquise")) for t in faites) >= reussites or len(faites) >= plafond


def choisir_phase(phase, taches, choisir):
    """Saute les phases atteintes OU épuisées ; choisir ne modifie pas la séance."""
    for candidate in PHASES[PHASES.index(phase):]:
        if phase_terminee(candidate, taches):
            continue
        tache = choisir(candidate)
        if tache is not None:
            return candidate, tache
    return "exercices", None


def difficulte_suivante(taches, niveau):
    exercices = [t for t in taches if t["nature"] == "exercice"]
    if not exercices:
        return max(1, min(5, round(niveau)))
    dernier = exercices[-1]
    cible = dernier.get("difficulte") or round(niveau)
    score = dernier.get("score")
    if score is not None:
        cible += 1 if score >= .8 else (-1 if score < .4 else 0)
    return max(1, min(5, cible))


def decision(tache, intention, ev):
    """Compteurs déjà mis à jour ; (action, clôturer l'élément)."""
    actif = element_actif(tache)
    if intention == "question":
        return "repondre_question", False
    if intention == "hors_sujet":
        return "recadrer", False
    if ev and ev["verdict"] == "indeterminable":
        return "reformuler_demande", False
    if ev and ev["verdict"] == "correcte":
        return "valider", True
    bloque = actif["tentatives"] + actif["demandes_aide"] >= LIMITE_TENTATIVES
    correction = intention in {"demande_correction", "demande_saut"}
    if tache["etape_active"] < 0 and tache["etapes_resolution"] and (
            bloque or correction or intention in {"blocage", "demande_indice"}
            or ev and ev["progression"] == "stagne" and actif["indices"] >= 1):
        return "reveler_etape", False
    if bloque or correction:
        return "donner_reponse", True
    if ev and ev["type_erreur"] in {"concept", "hypothese_ou_domaine"}:
        return "renvoyer_au_cours", False
    if ev and ev["verdict"] == "incomplete" and actif["indices"] == 0:
        return "demander_complement", False
    return "donner_indice", False


def appliquer_tour(tache, message, intention, ev=None):
    """Applique un tour validé, capture l'ancien élément avant toute transition."""
    if intention not in {"reponse", "demande_indice", "blocage", "demande_correction", "question", "demande_saut", "hors_sujet"}:
        raise ValueError("Intention inconnue.")
    ev = valider_evaluation(ev) if intention == "reponse" else None
    actif = element_actif(tache)
    if ev and ev["verdict"] != "indeterminable":
        actif["tentatives"] += 1
        tache["tentatives_totales"] += 1
        actif["reponses"].append(message)
        tache["reponses"].append(message)
        item = {**ev, "message": message, "element": tache["etape_active"]}
        actif["evaluations"].append(item)
        tache["evaluations"].append(item)
        if ev["verdict"] != "correcte":
            tache["echecs"] += 1
    elif intention in {"demande_indice", "blocage"}:
        actif["demandes_aide"] += 1
        tache["blocages"] += 1
    action, clore = decision(tache, intention, ev)
    contexte = {"element": tache["etape_active"],
                "question": actif.get("question", tache["question"]),
                "reference": actif.get("reponse", tache["reference"]),
                "notions": ev["notions_fragiles"] if ev else []}
    derniere = ev or next(iter(reversed(actif["evaluations"])), None)
    contexte["explication"] = (derniere["explication"] if derniere else
        "Vous n'avez pas encore proposé de réponse à cet élément ; le raisonnement attendu reste à construire.")
    if action in {"donner_indice", "renvoyer_au_cours", "repondre_question", "reveler_etape"}:
        actif["indices"] += 1
        tache["indices"] += 1
    if action == "reveler_etape":
        tache["etape_active"] = 0
        contexte["suivante"] = tache["etapes_resolution"][0]["question"]
    if clore:
        donnee = action == "donner_reponse"
        derniere = ev or next(iter(reversed(actif["evaluations"])), None)
        actif.update(terminee=True, acquise=not donnee, reponse_donnee=donnee,
                     score=calculer_score(derniere, actif["indices"], actif["tentatives"], donnee))
        tache["reponse_donnee_par_agent"] |= donnee
        if tache["etape_active"] >= 0 and tache["etape_active"] + 1 < len(tache["etapes_resolution"]):
            tache["etape_active"] += 1
            contexte["suivante"] = element_actif(tache)["question"]
            action = "donner_reponse_etape" if donnee else "valider_etape"
        else:
            elements = tache["etapes_resolution"] if tache["etape_active"] >= 0 else [actif]
            scores = [s["score"] for s in elements if s["score"] is not None]
            score = sum(scores) / len(scores) if scores else None
            if score is not None and tache["etape_active"] >= 0:
                score *= .9 ** tache["autonome"]["indices"]
            if score is not None and tache["reponse_donnee_par_agent"]:
                score = min(.25, score)
            tache.update(score=round(score, 4) if score is not None else None,
                         acquise=all(s["acquise"] for s in elements) and not tache["reponse_donnee_par_agent"],
                         reussie=all(s["acquise"] for s in elements), statut="terminee")
    tache["contexte_action"] = contexte
    return action
