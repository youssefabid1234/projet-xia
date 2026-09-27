"""Intégration état/profil/sélection, sans réseau."""
import json
import tempfile
import unittest
from pathlib import Path
from app.chapitres import CHAPITRE_SERIES, COLLES
from app.colle import Colle, charger_banque
from app.profil import Profil
from app.test_moteur_colle import evaluation, PLAN

CORRECT = evaluation()
FAUX = evaluation("incorrecte", intuition="absente")
PARTIEL = evaluation("incomplete")

def question(source, nature, priorite=1):
    return {"source": source, "nature": nature, "priorite": priorite,
            "question": f"Question {nature} {source} ?", "reponse_attendue": f"Réponse {source}"}

BANQUE = [question("d1", "definition"), question("d2", "definition"), question("d3", "definition"),
          question("d4", "definition"), question("d5", "definition", 3),
          question("t1", "theoreme"), question("t2", "theoreme"),
          question("t1", "demonstration"), question("e1", "applications")]
EXERCICES = [{"id": f"x{d}", "chapitre": CHAPITRE_SERIES, "difficulte": d, "enonce": f"Énoncé {d}",
              "corrige": f"Corrigé {d}"} for d in (1, 2, 3, 4)]


class ColleTests(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.chemin = Path(dossier.name) / "eleve.json"
        self.colle = Colle(self.chemin, CHAPITRE_SERIES, EXERCICES, BANQUE)

    def test_deroule_objectifs_phases(self):
        c = self.colle
        c.ouvrir_question_cours()
        for i in range(1):
            self.assertEqual(c.etape, "cours")
            c.appliquer("juste", "reponse", CORRECT)
            c.ouvrir_question_cours()
        self.assertEqual(c.etape, "demonstration")
        c.appliquer("juste", "reponse", CORRECT)
        c.ouvrir_question_cours()
        self.assertEqual(c.etape, "applications")
        c.appliquer("juste", "reponse", CORRECT)
        self.assertFalse(c.ouvrir_question_cours())
        self.assertEqual(c.etape, "exercices")
        p = Profil.charger(self.chemin)
        self.assertEqual(len(p.taches), 3)
        self.assertEqual(p.exercices_vus, [])
        self.assertAlmostEqual(p.niveau(CHAPITRE_SERIES), 2.1)

    def test_plafond_cours_et_pas_de_repetition(self):
        c = self.colle
        sources = []
        for _ in range(1):
            c.ouvrir_question_cours()
            self.assertEqual(c.etape, "cours")
            sources.append(c.tache["contenu_id"])
            c.appliquer("correction", "demande_correction", None)
        c.ouvrir_question_cours()
        self.assertEqual(c.etape, "demonstration")
        self.assertEqual(len(set(sources)), 1)
        self.assertFalse(Profil.charger(self.chemin).acquises())

    def test_acquis_exclus_nouvelle_session(self):
        self.colle.ouvrir_question_cours()
        premier = self.colle.tache["contenu_id"]
        self.colle.appliquer("juste", "reponse", CORRECT)
        autre = Colle(self.chemin, CHAPITRE_SERIES, EXERCICES, BANQUE)
        autre.ouvrir_question_cours()
        self.assertNotEqual(autre.tache["contenu_id"], premier)

    def test_exercice_entier_puis_etapes_et_niveau(self):
        c = self.colle
        ex = c.candidats_exercices()[0]
        self.assertEqual(ex["id"], "x2")
        c.ouvrir_exercice(ex, {"enonce": "Énoncé entier", "corrige": "Corrigé"}, PLAN)
        avant = json.dumps(c.etat(), ensure_ascii=False)
        self.assertNotIn("Conclusion ?", avant)
        c.appliquer("solution entière", "reponse", CORRECT)
        p = Profil.charger(self.chemin)
        self.assertAlmostEqual(p.niveau(CHAPITRE_SERIES), 1.7)
        self.assertEqual(c.difficulte_cible, 3)
        self.assertEqual(c.candidats_exercices()[0]["id"], "x3")
        self.assertEqual(p.vus(), {"x2"})

    def test_persistance_temps_et_ancienne_session(self):
        c = self.colle
        c.ouvrir_question_cours()
        c.appliquer("faux", "reponse", FAUX)
        chemin = self.chemin.with_suffix(".colle.json")
        c.sauvegarder(chemin)
        relue = Colle.from_dict(json.loads(chemin.read_text(encoding="utf-8")), self.chemin, EXERCICES, BANQUE)
        self.assertEqual(relue.to_dict(), c.to_dict())
        self.assertEqual(c.temps_restant(c.debut + 60), 29 * 60)
        ancien = c.to_dict()
        ancien["tache"] = {k: v for k, v in c.tache.items() if k not in
                           ("version_moteur", "autonome", "etapes_resolution", "etape_active")}
        relue = Colle.from_dict(ancien, self.chemin, EXERCICES, BANQUE)
        self.assertEqual(relue.tache["autonome"]["tentatives"], 1)
        self.assertEqual(relue.tache["autonome"]["reponses"], ["faux"])

    def test_bilan_archive_une_fois(self):
        self.colle.terminer("Bilan")
        self.colle.terminer("Bilan")
        self.assertEqual(len(Profil.charger(self.chemin).colles), 1)

    def test_banque_reelle(self):
        config = COLLES[CHAPITRE_SERIES]
        banque = charger_banque(config["questions"], config["index"])
        self.assertEqual({q["nature"] for q in banque}, {"definition", "theoreme", "demonstration", "applications"})
        for q in banque:
            self.assertTrue(q["question"].strip() and q["reponse_attendue"].strip())
