"""État persistant de la colle ; décisions déléguées au moteur pédagogique."""
import json
import time
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from app.chapitres import nom_chapitre, chapitre_catalogue
from app.profil import Profil
from app.texte_eleve import texte_eleve
from app.catalogue_pedagogique import BanqueCours, Catalogue, notions_cours, DATA
from app.moteur_colle import (PHASES, NATURES_PAR_PHASE, appliquer_tour, choisir_phase,
                              difficulte_suivante, element_actif, installer_tache, phase_terminee)

ETAPES = PHASES
LIBELLES = {"cours": "Questions de cours", "demonstration": "Démonstration",
            "applications": "Application du cours", "exercices": "Exercices", "fin": "Colle terminée"}
INTENTIONS = ("reponse", "demande_indice", "blocage", "demande_correction", "question", "demande_saut", "hors_sujet")
VALIDER = "valider"
COMPLETER = "demander_complement"
INDICE = "donner_indice"
DONNER_CORRECTION = "donner_reponse"
REPONDRE_QUESTION = "repondre_question"
RECADRER = "recadrer"

def charger_banque(chemin_questions, chemin_index):
    """Questions de cours préparées, complétées par les passages de l'index."""
    questions = json.loads(Path(chemin_questions).read_text(encoding="utf-8"))["questions"]
    index = json.loads(Path(chemin_index).read_text(encoding="utf-8"))
    passages = {p["identifiant"]: p for p in index["passages"]}
    liens = json.loads((DATA / "notions_questions.json").read_text(encoding="utf-8"))
    canoniques = {p["identifiant"]: titre for titre, p in notions_cours().items()}
    banque = []
    for q in questions:
        passage = passages.get(q["source"])
        if passage is None:
            continue
        notions = [canoniques[r] for r in liens.get(q["source"], [q["source"]]) if r in canoniques]
        banque.append({**q, "notions": q.get("notions", notions), "titre": passage.get("titre", ""), "page_source": passage.get("page_source"),
                       "texte_source": passage.get("texte", "")})
    return banque



class Colle:
    def __init__(self, chemin_profil, chapitre, exercices, banque, duree_minutes=30, maintenant=None):
        self.chemin_profil = Path(chemin_profil)
        self.id = uuid4().hex
        self.chapitre = chapitre_catalogue(chapitre)
        self.catalogue = Catalogue([ex for ex in exercices if chapitre_catalogue(ex.get("chapitre", "")) == self.chapitre])
        self.exercices = self.catalogue.exercices
        self.banque = banque
        self.banque_cours = BanqueCours(banque, self.chapitre)
        self.debut = time.time() if maintenant is None else maintenant
        self.duree = duree_minutes * 60
        self.etape = "cours"
        self.tache = None
        self.taches = []
        self.messages = []
        self.posees = []
        self.ecartes = []
        self.difficulte_cible = None
        self.terminee = False
        self.bilan = None
        self.version = 2
        self.reprise_id = self.choisir_reprise()

    CHAMPS = ("version", "id", "chapitre", "debut", "duree", "etape", "tache", "taches",
              "messages", "posees", "ecartes", "difficulte_cible", "terminee", "bilan", "reprise_id")

    def to_dict(self):
        return {champ: getattr(self, champ) for champ in self.CHAMPS}

    @classmethod
    def from_dict(cls, donnees, chemin_profil, exercices, banque):
        colle = cls(chemin_profil, donnees["chapitre"], exercices, banque)
        for champ in cls.CHAMPS:
            if champ in donnees:
                setattr(colle, champ, deepcopy(donnees[champ]))
        if "reprise_id" not in donnees:
            colle.reprise_id = colle.choisir_reprise()
        colle.version = 2
        if colle.etape == "application":
            colle.etape = "applications"
        t = colle.tache
        if t and not t.get("version_moteur"):
            reponses = list(t.get("reponses", []))
            installer_tache(t)
            t["contenu_id"] = f"{t['nature']}:{t['source']}"
            t.setdefault("notions", [])
            t["autonome"].update(reponses=reponses, tentatives=len(reponses), indices=t.get("indices", 0))
            t["tentatives_totales"] = len(reponses)
            # Les anciens jugements restent archivés, sans inventer leur intuition.
        return colle

    def sauvegarder(self, chemin):
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
        temporaire.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        temporaire.replace(chemin)

    def temps_restant(self, maintenant=None):
        return max(0, int(self.debut + self.duree - (time.time() if maintenant is None else maintenant)))

    def etat(self):
        t = self.tache
        publique = None
        if t:
            active = element_actif(t)
            publique = {k: t.get(k) for k in ("etape", "nature", "question", "difficulte", "indices")}
            publique.update(etape_resolution=None if t["etape_active"] < 0 else t["etape_active"] + 1,
                            question_active=active.get("question", t["question"]),
                            tentatives=active["tentatives"], demandes_aide=active["demandes_aide"])
            for cle in ("question", "question_active"):
                publique[cle] = texte_eleve(publique[cle])
        return {"chapitre": nom_chapitre(self.chapitre), "etape": self.etape, "libelle_etape": LIBELLES[self.etape],
                "etapes": [{"cle": e, "libelle": LIBELLES[e]} for e in ETAPES],
                "debut": self.debut, "duree": self.duree, "temps_restant": self.temps_restant(),
                "terminee": self.terminee, "bilan": texte_eleve(self.bilan) if self.bilan else self.bilan, "tache": publique,
                "resultats": [{k: t.get(k) for k in ("etape", "nature", "statut", "score", "acquise")} for t in self.taches]}

    def profil(self):
        return Profil.charger(self.chemin_profil, self.chemin_profil.stem)

    def candidats_cours(self, natures):
        if isinstance(natures, str):
            natures = (natures,)
        profil = self.profil()
        candidats = self.banque_cours.candidats(natures, self.chapitre, exclure=set(self.posees))
        return self.selection_memoire(candidats, profil)

    def anciennes_taches(self, profil):
        return [t for t in profil.taches.values()
                if t.get("chapitre") == self.chapitre and t.get("session") != self.id]

    @staticmethod
    def identite(tache):
        return tache.get("contenu_id", f"{tache.get('nature')}:{tache.get('source', tache.get('id'))}")

    def choisir_reprise(self):
        """Une reprise réservée, stable après reconnexion ; très faible = score < 0,4."""
        profil = self.profil()
        disponibles = {q["contenu_id"] for q in self.banque_cours.questions}
        disponibles.update(f"exercice:{e['id']}" for e in self.exercices)
        acquises = profil.acquises(self.chapitre)
        anciennes = [t for t in self.anciennes_taches(profil)
                     if t.get("score") is not None and t["score"] < .4
                     and self.identite(t) in disponibles - acquises]
        pire = min(anciennes, key=lambda t: (t["score"], self.identite(t)), default=None)
        return self.identite(pire) if pire else None

    def selection_memoire(self, candidats, profil, exercices=False):
        anciennes = self.anciennes_taches(profil)
        vus = {self.identite(t) for t in anciennes}
        if exercices:
            vus.update(f"exercice:{identifiant}" for identifiant in profil.vus())
        notions_vues = {n for t in anciennes + self.taches for n in t.get("notions", [])}
        def identite(q):
            return f"exercice:{q['id']}" if exercices else q["contenu_id"]
        deja_reprise = any(self.identite(t) == self.reprise_id for t in self.taches)
        reprise = [q for q in candidats if identite(q) == self.reprise_id and not deja_reprise]
        neuves = [q for q in candidats if identite(q) not in vus]
        # La place réservée à la reprise est l'unique exception à la priorité au neuf.
        neuves.sort(key=lambda q: bool(set(q.get("notions", [])) & notions_vues))
        return reprise + neuves

    def ouvrir_question_cours(self):
        if self.terminee or self.temps_restant() == 0:
            return False
        if self.tache:
            return True
        def choisir(phase):
            if phase == "exercices":
                return None
            return next(iter(self.candidats_cours(NATURES_PAR_PHASE[phase])), None)
        self.etape, q = choisir_phase(self.etape, self.taches, choisir)
        if q is None:
            return False
        self.posees.append(q["contenu_id"])
        self.tache = self.nouvelle_tache(self.etape, q["nature"], q["source"], q["question"],
            q["reponse_attendue"], page_source=q.get("page_source"), notions=q["notions"])
        return True

    def candidats_exercices(self):
        if self.terminee or self.temps_restant() == 0 or phase_terminee("exercices", self.taches):
            return []
        profil = self.profil()
        self.difficulte_cible = difficulte_suivante(self.taches, profil.niveau(self.chapitre))
        candidats = self.catalogue.candidats(self.difficulte_cible, self.chapitre,
            exclure=set(self.posees) | set(self.ecartes),
            fragiles=profil.notions_fragiles(chapitre=self.chapitre))
        return self.selection_memoire(candidats, profil, exercices=True)

    def ouvrir_exercice(self, exercice, verifie, plan):
        from app.plans import valider_plan
        if self.terminee or self.temps_restant() == 0 or phase_terminee("exercices", self.taches):
            return False
        plan = valider_plan(plan)
        self.etape = "exercices"
        self.posees.append(exercice["id"])
        self.tache = self.nouvelle_tache("exercices", "exercice", exercice["id"], verifie["enonce"],
            verifie["corrige"], difficulte=exercice.get("difficulte") or 1,
            page_source=exercice.get("page_source"), notions=exercice.get("notions", []), plan=plan)
        return True

    def ecarter(self, exercice):
        if exercice["id"] not in self.ecartes:
            self.ecartes.append(exercice["id"])

    def nouvelle_tache(self, etape, nature, source, question, reference, plan=(), **extra):
        return installer_tache({"id": uuid4().hex, "contenu_id": f"{nature}:{source}",
            "etape": etape, "nature": nature, "source": source, "question": question, "reference": reference,
            "debut": time.time(), "reponses": [], "evaluations": [], "indices": 0, "echecs": 0,
            "blocages": 0, "statut": "active", "notions": [], **extra}, plan)

    def reponse_cumulee(self, message=None):
        reponses = element_actif(self.tache)["reponses"] + ([message] if message else [])
        if len(reponses) == 1:
            return reponses[0]
        return "\n\n".join(f"Intervention {i} : {texte}" for i, texte in enumerate(reponses, 1))

    def contexte_evaluation(self):
        t = self.tache
        actif = element_actif(t)
        precedentes = t["etapes_resolution"][:max(0, t["etape_active"])]
        return {"retour_attendu": "Dans explication, adressez-vous à l'élève : identifiez précisément ce qui manque ou est faux dans sa réponse et expliquez pourquoi, avant toute piste de correction. Ne donnez pas la réponse attendue ni de référence documentaire.",
                "reponses_precedentes": actif["reponses"], "aides": actif["aides"],
                "tentatives": actif["tentatives"], "indices": actif["indices"],
                "etape_active": t["etape_active"],
                "resultats_precedents": [{"resultat": s["reponse"], "donne_par_agent": s["reponse_donnee"]}
                                        for s in precedentes]}

    def appliquer(self, message, intention, evaluation):
        if self.tache is None:
            raise ValueError("Aucune tâche active.")
        action = appliquer_tour(self.tache, message, intention, evaluation)
        if self.tache["statut"] == "terminee":
            self.clore()
        return action

    def clore(self):
        t = self.tache
        t["statut"] = "acquise" if t["acquise"] else "corrigee"
        t["duree"] = int(time.time() - t["debut"])
        profil = self.profil()
        profil.marquer(t, self.chapitre, self.id)
        profil.sauvegarder(self.chemin_profil)
        if not any(x["id"] == t["id"] for x in self.taches):
            self.taches.append(deepcopy(t))
        self.difficulte_cible = difficulte_suivante(self.taches, profil.niveau(self.chapitre))
        self.tache = None

    def terminer(self, bilan):
        self.terminee = True
        self.etape = "fin"
        self.bilan = bilan
        profil = self.profil()
        if self.tache and (self.tache.get("evaluations") or self.tache.get("blocages")):
            # Garder les difficultés observées même si le temps interrompt la tâche.
            # L'absence de score empêche de la traiter comme un échec.
            interrompue = deepcopy(self.tache)
            interrompue.update(statut="interrompue", score=None, acquise=False, interrompue=True)
            profil.marquer(interrompue, self.chapitre, self.id)
        self.tache = None
        if not any(c["id"] == self.id for c in profil.colles):
            profil.colles.append({"id": self.id, "chapitre": self.chapitre, "debut": self.debut,
                "duree": int(time.time() - self.debut), "bilan": bilan,
                "taches": [{k: t.get(k) for k in ("etape", "nature", "source", "statut", "indices", "score", "acquise")}
                           for t in self.taches]})
            profil.sauvegarder(self.chemin_profil)
