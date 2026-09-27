import unittest
from app.catalogue_pedagogique import BanqueCours, Catalogue, notions_cours
from app.profil import charger_exercices
from app.chapitres import CHAPITRE_SERIES


class SelectionTests(unittest.TestCase):
    def test_priorite_notion_avant_difficulte_exclusions_et_chapitre(self):
        c = Catalogue([dict(id="a", chapitre="c", difficulte=1, notions=[]),
                       dict(id="b", chapitre="c", difficulte=4, notions=["N"]),
                       dict(id="x", chapitre="d", difficulte=1, notions=["N"])])
        self.assertEqual([e["id"] for e in c.candidats(1, "c", fragiles=["N"])], ["b", "a"])
        self.assertEqual(c.exercice_sur_notion("N", "c")["id"], "b")
        self.assertIsNone(c.exercice_sur_notion("N", "c", exclure=["b"]))
        self.assertEqual(c.exercice_proche(1, "c", ["b"])["id"], "a")

    def test_banque_ciblee_et_repli(self):
        b = BanqueCours([dict(source="1", nature="definition", notions=["N"], priorite=3),
                        dict(source="2", nature="theoreme", notions=["M"], priorite=1)], "c")
        self.assertEqual(b.candidats(("definition", "theoreme"), "c", fragiles=["N"])[0]["source"], "1")
        self.assertIsNone(b.question_sur("N", ("demonstration",), "c"))
        self.assertIsNone(b.prochaine(("definition",), "c", ["definition:1"]))
        self.assertIsNone(b.prochaine(("definition",), "d"))

    def test_catalogue_reel_annote_et_alias_chapitre(self):
        c = Catalogue(charger_exercices())
        series = c.candidats(2, "16 — Séries numériques")
        self.assertEqual(len(series), 31)
        for ex in series:
            self.assertTrue(ex["notions"])
            self.assertLessEqual(set(ex["notions"]), notions_cours().keys())
        self.assertEqual(len(c.candidats(2, CHAPITRE_SERIES)), 31)
