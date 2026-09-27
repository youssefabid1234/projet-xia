"""Tests du parcours réellement branché, remplaçant le prototype Agent."""
import json
import tempfile
import unittest
from pathlib import Path
from app.colle import Colle, charger_banque
from app.chapitres import CHAPITRE_SERIES, COLLES
from app.profil import Profil
from app.moteur_colle import note_bilan, element_actif
from app.test_colle import BANQUE, EXERCICES
from app.test_moteur_colle import evaluation, PLAN
from app.catalogue_pedagogique import notions_cours


class ParcoursTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.path = Path(d.name) / "profil.json"

    def test_notion_fragile_prioritaire_apres_reconnexion(self):
        notion = next(iter(notions_cours()))
        banque = [dict(source="a", nature="definition", question="Q1", reponse_attendue="R1", priorite=1, notions=[notion]),
                  dict(source="b", nature="definition", question="Q2", reponse_attendue="R2", priorite=3, notions=[notion]),
                  dict(source="c", nature="definition", question="Q3", reponse_attendue="R3", priorite=1, notions=[])]
        c = Colle(self.path, CHAPITRE_SERIES, EXERCICES, banque)
        c.ouvrir_question_cours()
        for _ in range(2):
            c.appliquer("erreur", "reponse", evaluation("incorrecte", notions=[notion]))
        self.assertEqual(Profil.charger(self.path).notions_fragiles(chapitre=CHAPITRE_SERIES), [notion])
        reprise = Colle.from_dict(json.loads(json.dumps(c.to_dict())), self.path, EXERCICES, banque)
        reprise.ouvrir_question_cours()
        self.assertIsNone(reprise.tache)
        self.assertEqual(reprise.etape, "exercices")

    def test_toutes_les_phases_epuisees_sont_traversees(self):
        c = Colle(self.path, CHAPITRE_SERIES, EXERCICES, [])
        self.assertFalse(c.ouvrir_question_cours())
        self.assertEqual(c.etape, "exercices")
        self.assertTrue(c.candidats_exercices())

    def test_plan_prive_apres_reprise_et_tentative_non_doublee(self):
        c = Colle(self.path, CHAPITRE_SERIES, EXERCICES, BANQUE)
        c.ouvrir_exercice(EXERCICES[0], {"enonce": "ENTIER", "corrige": "CORRIGE_PRIVE"}, PLAN)
        c.appliquer("blocage", "blocage", None)
        c.appliquer("premier essai", "reponse", evaluation("incorrecte"))
        reprise = Colle.from_dict(json.loads(json.dumps(c.to_dict())), self.path, EXERCICES, BANQUE)
        self.assertEqual(element_actif(reprise.tache)["tentatives"], 1)
        self.assertNotIn("Conclusion ?", json.dumps(reprise.etat()))
        reprise.appliquer("second essai", "reponse", evaluation("incorrecte"))
        self.assertEqual(reprise.tache["etape_active"], 1)
        self.assertEqual(element_actif(reprise.tache)["tentatives"], 0)
        reprise.appliquer("4", "reponse", evaluation())
        archive = reprise.taches[0]
        profil = Profil.charger(self.path)
        avant = profil.to_dict()
        self.assertFalse(profil.marquer(archive, CHAPITRE_SERIES))
        self.assertEqual(profil.to_dict(), avant)
        self.assertFalse(archive["acquise"])

    def test_note_determinee_et_taches_non_notees_ignorees(self):
        self.assertIsNone(note_bilan([]))
        self.assertEqual(note_bilan([dict(etape="cours", score=.5)]), 10)
        self.assertEqual(note_bilan([dict(etape="cours", score=1), dict(etape="demonstration", score=0)]), 12)
        self.assertEqual(note_bilan([dict(etape="cours", score=1), dict(etape="exercices", score=None)]), 20)

    def test_toutes_les_questions_reelles_ont_des_notions_canoniques(self):
        config = COLLES[CHAPITRE_SERIES]
        for q in charger_banque(config["questions"], config["index"]):
            self.assertTrue(q["notions"], q["source"])
            self.assertLessEqual(set(q["notions"]), notions_cours().keys())

    def test_interruption_conserve_fragilite_sans_note_ni_baisse_de_niveau(self):
        notion = next(iter(notions_cours()))
        c = Colle(self.path, CHAPITRE_SERIES, EXERCICES, BANQUE)
        c.ouvrir_question_cours()
        c.appliquer("essai faux", "reponse", evaluation("incorrecte", notions=[notion]))
        c.terminer("Sans note")
        profil = Profil.charger(self.path)
        self.assertEqual(profil.fragilites(CHAPITRE_SERIES), {notion: 1})
        self.assertEqual(profil.niveau(CHAPITRE_SERIES), 1.5)
        self.assertIsNone(next(iter(profil.taches.values()))["score"])
        self.assertFalse(profil.acquises())
