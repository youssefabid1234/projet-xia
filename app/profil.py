"""Suivi du niveau d'un eleve et selection d'exercices adaptes."""

import json
from pathlib import Path

CHEMIN_EXERCICES = Path(__file__).parent.parent / "data" / "exercices.json"

# Variation du niveau selon le verdict rendu par la methode Pipelex.
# La montee est plus rapide que la descente : un echec isole ne doit
# pas faire degringoler un eleve qui progresse.
GAINS = {
    "correcte": 0.3,
    "incomplete": 0.1,
    "incorrecte": -0.2,
    "indeterminable": 0.0,
}

NIVEAU_MIN = 1.0
NIVEAU_MAX = 5.0
NIVEAU_DEPART = 1.5


class Profil:
    """Niveau d'un eleve par chapitre et historique des exercices vus."""

    def __init__(self, nom):
        self.nom = nom
        self.niveaux = {}
        self.exercices_vus = []
        self.historique = []
        self.taches = {}
        self.colles = []
        self.notions = {}

    def niveau(self, chapitre):
        return self.niveaux.get(chapitre, NIVEAU_DEPART)

    def fixer_niveau(self, chapitre, niveau):
        self.niveaux[chapitre] = max(NIVEAU_MIN, min(NIVEAU_MAX, niveau))

    def fragilites(self, chapitre):
        return dict(self.notions.get(chapitre, {}))

    def notions_fragiles(self, seuil=2, chapitre=None):
        compte = self.fragilites(chapitre) if chapitre is not None else {}
        if chapitre is None:
            for notions in self.notions.values():
                for notion, nombre in notions.items():
                    compte[notion] = compte.get(notion, 0) + nombre
        return sorted((n for n in compte if compte[n] >= seuil), key=lambda n: (-compte[n], n))

    def signaler_notion_fragile(self, notion, chapitre):
        compte = self.notions.setdefault(chapitre, {})
        compte[notion] = compte.get(notion, 0) + 1

    def consolider_notion(self, notion, chapitre):
        compte = self.notions.setdefault(chapitre, {})
        compte[notion] = max(0, compte.get(notion, 0) - 1)

    def acquises(self, chapitre=None):
        return {t.get("contenu_id", f"{t.get('nature')}:{t.get('source')}") for t in self.taches.values()
                if t.get("acquise") and (chapitre is None or t.get("chapitre") == chapitre)}

    def vus(self):
        return set(self.exercices_vus)

    def marquer(self, tache, chapitre, session=None):
        """Clôture idempotente : un identifiant de tentative ne compte qu'une fois."""
        from copy import deepcopy
        if tache["id"] in self.taches:
            return False
        enregistrement = deepcopy(tache)
        enregistrement.update(chapitre=chapitre, session=session, cloturee=True)
        if tache.get("reponse_donnee_par_agent"):
            enregistrement["acquise"] = False
        self.taches[tache["id"]] = enregistrement
        evaluations = [e for e in tache.get("evaluations", []) if e["verdict"] != "indeterminable"]
        erreurs = [e for e in evaluations if e["verdict"] != "correcte"]
        for ev in erreurs:
            for notion in set(ev.get("notions_fragiles", [])):
                self.signaler_notion_fragile(notion, chapitre)
        if enregistrement.get("acquise") and not tache.get("indices", 0) and not erreurs:
            for notion in set(tache.get("notions", [])):
                self.consolider_notion(notion, chapitre)
        score = tache.get("score")
        if score is not None:
            self.fixer_niveau(chapitre, self.niveau(chapitre) + .4 * (score - .5))
        if tache["nature"] == "exercice":
            source = tache["source"]
            if source not in self.exercices_vus:
                self.exercices_vus.append(source)
            dernier = evaluations[-1] if evaluations else {}
            self.historique.append({"exercice": source, "chapitre": chapitre, "score": score,
                "verdict": dernier.get("verdict", "indeterminable"),
                "type_erreur": dernier.get("type_erreur", "non_determinable")})
        return True

    def enregistrer(self, id_exercice, chapitre, verdict, type_erreur):
        if verdict == "indeterminable":
            return
        actuel = self.niveau(chapitre)
        nouveau = actuel + GAINS.get(verdict, 0.0)
        self.niveaux[chapitre] = max(NIVEAU_MIN, min(NIVEAU_MAX, nouveau))

        if id_exercice not in self.exercices_vus:
            self.exercices_vus.append(id_exercice)

        self.historique.append({
            "exercice": id_exercice,
            "chapitre": chapitre,
            "verdict": verdict,
            "type_erreur": type_erreur,
        })

    def erreurs_frequentes(self):
        """Compte les types d'erreur rencontres, du plus frequent au moins."""
        compte = {}
        for entree in self.historique:
            t = entree["type_erreur"]
            if t not in ("aucune", "non_determinable"):
                compte[t] = compte.get(t, 0) + 1
        return sorted(compte.items(), key=lambda x: x[1], reverse=True)

    def to_dict(self):
        return {
            "nom": self.nom,
            "niveaux": self.niveaux,
            "exercices_vus": self.exercices_vus,
            "historique": self.historique,
            "taches": self.taches,
            "colles": self.colles,
            "notions": self.notions,
        }

    @classmethod
    def from_dict(cls, donnees):
        profil = cls(donnees["nom"])
        profil.niveaux = donnees.get("niveaux", {})
        profil.exercices_vus = donnees.get("exercices_vus", [])
        profil.historique = donnees.get("historique", [])
        profil.taches = donnees.get("taches", {})
        profil.colles = donnees.get("colles", [])
        profil.notions = donnees.get("notions", {})
        return profil

    def sauvegarder(self, chemin):
        # Écriture atomique : un arrêt pendant la sauvegarde ne corrompt pas le profil.
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
        temporaire.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        temporaire.replace(chemin)

    @classmethod
    def charger(cls, chemin, nom_defaut="eleve"):
        chemin = Path(chemin)
        if not chemin.exists():
            return cls(nom_defaut)
        return cls.from_dict(json.loads(chemin.read_text(encoding="utf-8")))


def charger_exercices(chemin=CHEMIN_EXERCICES):
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if isinstance(donnees, dict):
        donnees = donnees.get("exercices", [])
    # Un exercice sans etoile est traite comme une application directe.
    for ex in donnees:
        # Le JSON extrait utilise « identifiant » ; la logique du profil utilise « id ».
        if "id" not in ex:
            ex["id"] = ex["identifiant"]
        if not ex.get("difficulte"):
            ex["difficulte"] = 1
    return donnees


def choisir_exercice(profil, chapitre, exercices, exercices_presentes=()):
    """Retourne l'exercice non vu dont la difficulte colle le mieux au niveau."""
    candidats = [
        ex for ex in exercices
        if ex.get("chapitre") == chapitre
        and ex.get("id") not in profil.exercices_vus
        and ex.get("id") not in exercices_presentes
    ]
    if not candidats:
        return None

    cible = profil.niveau(chapitre)
    return min(candidats, key=lambda ex: (
        abs(ex["difficulte"] - cible), ex["difficulte"] < cible,
    ))
