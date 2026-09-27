import tempfile
import unittest
from pathlib import Path
from app.profil import Profil
from app.test_moteur_colle import evaluation, tache


class ProfilMoteurTests(unittest.TestCase):
    def test_ancien_profil_et_persistance(self):
        p = Profil.from_dict({"nom": "A", "niveaux": {"c": 2}})
        self.assertEqual(p.notions_fragiles(chapitre="c"), [])
        for _ in range(2):
            p.signaler_notion_fragile("N", "c")
        p.signaler_notion_fragile("Autre", "d")
        self.assertEqual(p.notions_fragiles(chapitre="c"), ["N"])
        with tempfile.TemporaryDirectory() as d:
            fichier = Path(d) / "profil.json"
            p.sauvegarder(fichier)
            self.assertEqual(Profil.charger(fichier).to_dict(), p.to_dict())
        p.consolider_notion("N", "c")
        self.assertEqual(p.notions_fragiles(chapitre="c"), [])

    def test_cloture_unique_et_erreurs_intermediaires(self):
        p = Profil("A")
        t = tache()
        t.update(source="x", notions=["N"], score=.7, acquise=True, indices=1,
                 evaluations=[evaluation("incorrecte", notions=["N"]), evaluation("incomplete", notions=["N"]), evaluation()])
        self.assertTrue(p.marquer(t, "c", "session"))
        self.assertFalse(p.marquer(t, "c", "session"))
        self.assertAlmostEqual(p.niveau("c"), 1.58)
        self.assertEqual(p.fragilites("c"), {"N": 2})
        self.assertEqual(p.vus(), {"x"})
        self.assertIn(t["contenu_id"], p.acquises("c"))

    def test_solution_donnee_ne_consolide_jamais(self):
        p = Profil("A")
        p.signaler_notion_fragile("N", "c")
        t = tache()
        t.update(source="x", notions=["N"], score=.25, acquise=True, reponse_donnee_par_agent=True,
                 evaluations=[evaluation()])
        p.marquer(t, "c")
        self.assertFalse(p.acquises())
        self.assertEqual(p.fragilites("c"), {"N": 1})

    def test_reussite_autonome_consolide_et_niveau_borne(self):
        p = Profil("A")
        p.fixer_niveau("c", 5)
        p.signaler_notion_fragile("N", "c")
        t = tache()
        t.update(source="x", notions=["N"], score=1, acquise=True, evaluations=[evaluation()])
        p.marquer(t, "c")
        self.assertEqual(p.niveau("c"), 5)
        self.assertEqual(p.fragilites("c"), {"N": 0})
