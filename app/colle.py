"""État d'une colle et règles de progression, décidées par le serveur.

Aucun appel réseau ici : le modèle de langage classe le message de l'élève et
l'évaluateur donne un verdict ; ce module décide seul de la suite (indice,
correction, validation, question suivante) et tient le profil à jour.

Déroulé d'une colle (comme à l'oral) :
1. cours : une définition puis un énoncé de théorème ;
2. démonstration courte d'un résultat du cours ;
3. application directe d'un exemple du cours ;
4. exercices du catalogue, jusqu'à la fin du temps.
Une question non réussie est corrigée par le colleur puis remplacée par une autre
de même nature : on ne passe pas à la suite sans acquisition. Après trois
questions corrigées sur la même étape, le colleur avance et le note au bilan.
"""

import json
import random
import time
from pathlib import Path
from uuid import uuid4

from app.chapitres import nom_chapitre
from app.profil import Profil, choisir_exercice

ETAPES = ("cours", "demonstration", "applications", "exercices")
LIBELLES = {"cours": "Questions de cours", "demonstration": "Démonstration",
            "applications": "Application du cours", "exercices": "Exercices", "fin": "Colle terminée"}
# Étapes du cours, dans l'ordre : (étape, nature de la question).
PROGRAMME = (("cours", "definition"), ("cours", "theoreme"),
             ("demonstration", "demonstration"), ("applications", "applications"))
ESSAIS_PAR_ETAPE = 3

INTENTIONS = ("reponse", "demande_indice", "blocage", "demande_correction",
              "question", "demande_saut", "hors_sujet")

# Actions décidées par le serveur pour le tour.
VALIDER = "valider"
CORRIGER_ERREUR = "corriger_erreur"
COMPLETER = "completer"
INDICE = "indice"
DONNER_CORRECTION = "donner_correction"
REPONDRE_QUESTION = "repondre_question"
RECADRER = "recadrer"
ACTIONS_CLOTURE = (VALIDER, DONNER_CORRECTION)

# Au-delà, le colleur donne la correction : erreurs (ou réponses incomplètes
# au cours) et indices déjà donnés.
SEUILS = {"cours": (3, 3), "demonstration": (3, 3), "applications": (3, 3), "exercices": (4, 4)}
# Étapes où une réponse partielle sans erreur est une étape normale du travail
# (preuve ou calcul en plusieurs messages), et non un échec.
PROGRESSIVES = ("demonstration", "applications", "exercices")


def charger_banque(chemin_questions, chemin_index):
    """Questions de cours préparées, complétées par les passages de l'index."""
    questions = json.loads(Path(chemin_questions).read_text(encoding="utf-8"))["questions"]
    index = json.loads(Path(chemin_index).read_text(encoding="utf-8"))
    passages = {p["identifiant"]: p for p in index["passages"]}
    banque = []
    for q in questions:
        passage = passages.get(q["source"])
        if passage is None:
            continue
        banque.append({**q, "titre": passage.get("titre", ""), "page_source": passage.get("page_source"),
                       "texte_source": passage.get("texte", "")})
    return banque


def decider(tache, intention, evaluation):
    """Action du colleur pour ce tour, à partir de l'intention et du verdict."""
    max_echecs, max_indices = SEUILS[tache["etape"]]
    if intention == "demande_correction":
        return DONNER_CORRECTION
    if intention == "demande_saut":
        return DONNER_CORRECTION if tache["etape"] == "exercices" else RECADRER
    if intention in ("demande_indice", "blocage"):
        return DONNER_CORRECTION if tache["indices"] >= max_indices else INDICE
    if intention == "question":
        return REPONDRE_QUESTION
    if intention != "reponse" or evaluation is None:
        return RECADRER
    verdict = evaluation["verdict"]
    if verdict == "correcte":
        return VALIDER
    echec = verdict == "incorrecte" or tache["etape"] not in PROGRESSIVES
    if echec and tache["echecs"] + 1 >= max_echecs:
        return DONNER_CORRECTION
    return CORRIGER_ERREUR if verdict == "incorrecte" else COMPLETER


class Colle:
    def __init__(self, chemin_profil, chapitre, exercices, banque, duree_minutes=30, maintenant=None):
        self.chemin_profil = Path(chemin_profil)
        self.id = uuid4().hex
        self.chapitre = chapitre
        self.exercices = [ex for ex in exercices if ex.get("chapitre") == chapitre]
        self.banque = banque
        self.debut = maintenant or time.time()
        self.duree = duree_minutes * 60
        self.etape = "cours"
        self.programme = 0          # position dans PROGRAMME
        self.essais_etape = 0       # questions posées pour la position courante
        self.tache = None
        self.taches = []            # tâches closes de cette colle
        self.messages = []          # dialogue affiché
        self.posees = []            # sources et exercices déjà proposés dans cette colle
        self.ecartes = []           # exercices illisibles, écartés
        self.difficulte_cible = None
        self.terminee = False
        self.bilan = None

    # ----- Persistance -------------------------------------------------------

    CHAMPS = ("id", "chapitre", "debut", "duree", "etape", "programme", "essais_etape", "tache",
              "taches", "messages", "posees", "ecartes", "difficulte_cible", "terminee", "bilan")

    def to_dict(self):
        return {champ: getattr(self, champ) for champ in self.CHAMPS}

    @classmethod
    def from_dict(cls, donnees, chemin_profil, exercices, banque):
        colle = cls(chemin_profil, donnees["chapitre"], exercices, banque)
        for champ in cls.CHAMPS:
            if champ in donnees:
                setattr(colle, champ, donnees[champ])
        return colle

    def sauvegarder(self, chemin):
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
        temporaire.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        temporaire.replace(chemin)

    # ----- Temps et état public ---------------------------------------------

    def temps_restant(self, maintenant=None):
        return max(0, int(self.debut + self.duree - (maintenant or time.time())))

    def etat(self):
        tache = self.tache
        return {
            "chapitre": nom_chapitre(self.chapitre), "etape": self.etape, "libelle_etape": LIBELLES[self.etape],
            "etapes": [{"cle": e, "libelle": LIBELLES[e]} for e in ETAPES],
            "debut": self.debut, "duree": self.duree, "temps_restant": self.temps_restant(),
            "terminee": self.terminee, "bilan": self.bilan,
            "tache": None if tache is None else {
                "etape": tache["etape"], "nature": tache["nature"], "question": tache["question"],
                "difficulte": tache.get("difficulte"), "indices": tache["indices"]},
            "resultats": [{"etape": t["etape"], "nature": t["nature"], "statut": t["statut"]} for t in self.taches],
        }

    # ----- Acquis durables ----------------------------------------------------

    def profil(self):
        return Profil.charger(self.chemin_profil, self.chemin_profil.stem)

    def acquis(self, profil=None):
        """(nature, source) déjà réussies pour ce chapitre, toutes sessions confondues."""
        profil = profil or self.profil()
        return {(t.get("nature"), t.get("source")) for t in profil.taches.values()
                if t.get("chapitre") == self.chapitre and t.get("acquise")}

    # ----- Choix des tâches ---------------------------------------------------

    def candidats_cours(self, nature):
        acquis = self.acquis()
        candidats = [q for q in self.banque if q["nature"] == nature
                     and (nature, q["source"]) not in acquis and f"{nature}:{q['source']}" not in self.posees]
        if not candidats:
            # Tout est acquis : on réinterroge, sans reposer une question de cette colle.
            candidats = [q for q in self.banque if q["nature"] == nature
                         and f"{nature}:{q['source']}" not in self.posees]
        if not candidats:
            return []
        meilleure = min(q.get("priorite", 2) for q in candidats)
        candidats = [q for q in candidats if q.get("priorite", 2) == meilleure]
        random.shuffle(candidats)
        return candidats

    def ouvrir_question_cours(self):
        """Ouvre la prochaine question de cours ; renvoie False si le cours est terminé."""
        while self.programme < len(PROGRAMME):
            etape, nature = PROGRAMME[self.programme]
            candidats = self.candidats_cours(nature) if self.essais_etape < ESSAIS_PAR_ETAPE else []
            if candidats:
                q = candidats[0]
                self.etape = etape
                self.essais_etape += 1
                self.posees.append(f"{nature}:{q['source']}")
                self.tache = self.nouvelle_tache(etape, nature, q["source"], q["question"],
                                                 q["reponse_attendue"], page_source=q.get("page_source"))
                return True
            self.programme += 1
            self.essais_etape = 0
        self.etape = "exercices"
        return False

    def candidats_exercices(self):
        """Exercices non vus, du plus proche au plus éloigné de la difficulté visée."""
        profil = self.profil()
        exclus = set(self.posees) | set(self.ecartes)
        restants = [ex for ex in self.exercices if ex["id"] not in exclus]
        if self.difficulte_cible is not None:
            profil.niveaux[self.chapitre] = self.difficulte_cible
        ordre = []
        while True:
            exercice = choisir_exercice(profil, self.chapitre, restants, [e["id"] for e in ordre])
            if exercice is None:
                break
            ordre.append(exercice)
        return ordre

    def ouvrir_exercice(self, exercice, verifie):
        self.etape = "exercices"
        self.posees.append(exercice["id"])
        question = verifie["enonce"]
        self.tache = self.nouvelle_tache("exercices", "exercice", exercice["id"], question,
                                         verifie["corrige"], difficulte=exercice.get("difficulte"),
                                         page_source=exercice.get("page_source"))

    def ecarter(self, exercice):
        self.ecartes.append(exercice["id"])

    def nouvelle_tache(self, etape, nature, source, question, reference, **extra):
        return {"id": uuid4().hex, "etape": etape, "nature": nature, "source": source,
                "question": question, "reference": reference, "debut": time.time(),
                "reponses": [], "evaluations": [], "indices": 0, "echecs": 0, "blocages": 0,
                "statut": "active", **extra}

    # ----- Un tour de dialogue ------------------------------------------------

    def reponse_cumulee(self, message=None):
        """Interventions de l'élève sur la tâche, dans l'ordre, pour l'évaluateur."""
        reponses = self.tache["reponses"] + ([message] if message else [])
        if len(reponses) == 1:
            return reponses[0]
        return "\n\n".join(f"Intervention {i} : {texte}" for i, texte in enumerate(reponses, 1))

    def appliquer(self, message, intention, evaluation):
        """Enregistre le tour et renvoie l'action décidée. Ne crée pas la tâche suivante."""
        tache = self.tache
        action = decider(tache, intention, evaluation)
        if intention == "reponse":
            tache["reponses"].append(message)
            if evaluation is not None:
                tache["evaluations"].append({"reponse": self.reponse_cumulee(), **evaluation})
        if intention == "blocage":
            tache["blocages"] += 1
        if action == INDICE:
            tache["indices"] += 1
        if action == CORRIGER_ERREUR or (action == COMPLETER and tache["etape"] not in PROGRESSIVES):
            tache["echecs"] += 1
        if action in ACTIONS_CLOTURE:
            self.clore(acquise=action == VALIDER)
        return action

    def clore(self, acquise):
        tache = self.tache
        tache["statut"] = "acquise" if acquise else "corrigee"
        tache["duree"] = int(time.time() - tache["debut"])
        derniere = tache["evaluations"][-1] if tache["evaluations"] else None
        profil = self.profil()
        profil.taches[tache["id"]] = {
            "id": tache["id"], "session": self.id, "chapitre": self.chapitre, "etape": tache["etape"],
            "nature": tache["nature"], "source": tache["source"], "enonce": tache["question"],
            "page_source": tache.get("page_source"), "evaluations": tache["evaluations"],
            "indices_donnes": tache["indices"], "tentatives": len(tache["reponses"]),
            "blocages": tache["blocages"], "acquise": acquise, "cloturee": True,
            "correction_donnee": not acquise,
        }
        if tache["etape"] == "exercices":
            verdict = derniere["verdict"] if acquise and derniere else "incorrecte"
            if tache["source"] not in profil.exercices_vus:
                profil.enregistrer(tache["source"], self.chapitre, verdict,
                                   derniere["type_erreur"] if derniere else "non_determinable")
            difficulte = tache.get("difficulte") or profil.niveau(self.chapitre)
            # Réussite autonome : plus difficile ; correction donnée : plus facile.
            ajustement = 1 if acquise and tache["indices"] <= 1 else (0 if acquise else -1)
            self.difficulte_cible = max(1, min(5, difficulte + ajustement))
        elif acquise or self.essais_etape >= ESSAIS_PAR_ETAPE:
            self.programme += 1
            self.essais_etape = 0
        profil.sauvegarder(self.chemin_profil)
        self.taches.append({k: tache[k] for k in (
            "id", "etape", "nature", "source", "question", "statut", "indices", "echecs",
            "blocages", "duree", "evaluations")} | {"difficulte": tache.get("difficulte")})
        self.tache = None

    def terminer(self, bilan):
        self.terminee = True
        self.etape = "fin"
        self.bilan = bilan
        profil = self.profil()
        profil.colles.append({"id": self.id, "chapitre": self.chapitre, "debut": self.debut,
                              "duree": int(time.time() - self.debut), "bilan": bilan,
                              "taches": [{k: t[k] for k in ("etape", "nature", "source", "statut", "indices")}
                                         for t in self.taches]})
        profil.sauvegarder(self.chemin_profil)
