"""Références canoniques et préparation persistée, sans appel réseau en session."""
import hashlib
import json
from pathlib import Path
from app.chapitres import COLLES, chapitre_catalogue

DATA = Path(__file__).resolve().parents[1] / "data"


def passages_cours():
    return [p for config in COLLES.values()
            for p in json.loads(config["index"].read_text(encoding="utf-8"))["passages"]]


def notions_cours():
    return {p["titre"]: p for p in passages_cours()
            if p.get("titre") and p["type"] not in {"exemple", "remarque"}}


def empreinte(exercice):
    texte = json.dumps([exercice.get("enonce"), exercice.get("corrige")], ensure_ascii=False)
    return hashlib.sha256(texte.encode()).hexdigest()


def preparation_valide(exercice):
    cache = exercice.get("preparation", {})
    return cache.get("empreinte") == empreinte(exercice) and cache.get("exploitable") is True


def annoter_exercice(exercice, annotations=None, par_id=None):
    """Annotations éditoriales liées aux sources ; aucun diagnostic inventé en session."""
    ex = dict(exercice)
    chemin = DATA / "notions_exercices.json"
    if annotations is None:
        annotations = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
    annotation = annotations.get(ex.get("id", ex.get("identifiant")), {})
    if annotation.get("empreinte") == empreinte(ex):
        if par_id is None:
            par_id = {p["identifiant"]: nom for nom, p in notions_cours().items()}
        ex["notions"] = [par_id[r] for r in annotation["references"]]
    else:
        ex.setdefault("notions", [])
    return ex


class Catalogue:
    def __init__(self, exercices):
        chemin = DATA / "notions_exercices.json"
        annotations = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
        par_id = {p["identifiant"]: nom for nom, p in notions_cours().items()}
        self.exercices = [annoter_exercice(ex, annotations, par_id) for ex in exercices]

    def candidats(self, cible, chapitre, exclure=(), fragiles=()):
        exclus = set(exclure)
        def ordre(ex):
            priorite = next((i for i, n in enumerate(fragiles) if n in ex.get("notions", [])), len(fragiles))
            d = ex.get("difficulte") or 1
            return priorite, abs(d - cible), d < cible, ex["id"]
        return sorted((ex for ex in self.exercices if chapitre_catalogue(ex["chapitre"]) == chapitre_catalogue(chapitre)
                       and ex["id"] not in exclus), key=ordre)

    def exercice_sur_notion(self, notion, chapitre, exclure=(), cible=1):
        return next((ex for ex in self.candidats(cible, chapitre, exclure)
                     if notion in ex.get("notions", [])), None)

    def exercice_proche(self, cible, chapitre, exclure=()):
        return next(iter(self.candidats(cible, chapitre, exclure)), None)


class BanqueCours:
    def __init__(self, questions, chapitre):
        self.chapitre = chapitre_catalogue(chapitre)
        self.questions = []
        for q in questions:
            nature = "applications" if q["nature"] == "application" else q["nature"]
            self.questions.append({**q, "nature": nature, "contenu_id": f"{nature}:{q['source']}",
                "notions": q.get("notions", [q["titre"]] if q.get("titre") else [])})

    def candidats(self, natures, chapitre, exclure=(), fragiles=()):
        if chapitre_catalogue(chapitre) != self.chapitre:
            return []
        def ordre(q):
            priorite = next((i for i, n in enumerate(fragiles) if n in q["notions"]), len(fragiles))
            return priorite, q.get("priorite", 2), q["contenu_id"]
        return sorted((q for q in self.questions if q["nature"] in natures
                       and q["contenu_id"] not in exclure), key=ordre)

    def question_sur(self, notion, natures, chapitre, exclure=()):
        return next((q for q in self.candidats(natures, chapitre, exclure) if notion in q["notions"]), None)

    def prochaine(self, natures, chapitre, exclure=()):
        return next(iter(self.candidats(natures, chapitre, exclure)), None)
