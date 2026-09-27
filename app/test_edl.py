"""Intégrité des sources EDL et parcours avec les données livrées, sans réseau."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from app.catalogue_pedagogique import notions_cours, preparation_valide
from app.chapitres import CHAPITRE_EDL, COLLES, NOM_EDL, chapitre_catalogue, nom_chapitre
from app.colle import Colle, charger_banque
from app.cours import charger_index
from app.enonces import CacheEnonces
from app.examinateur import Examinateur
from app.faux import FauxOpenAI, ServicesSimples
from app.profil import charger_exercices
from app.test_colle import CORRECT
from scripts.index_cours import ROOT, extract


class EDLTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = COLLES[CHAPITRE_EDL]
        self.banque = charger_banque(self.config["questions"], self.config["index"])
        self.exercices = [e for e in charger_exercices() if e["chapitre"] == CHAPITRE_EDL]

    def test_sources_et_index(self):
        payload = extract(ROOT / "data/cours/analyse.pdf", 69, 76, "11 — " + NOM_EDL)
        expected = [f"11.{section}.{i}" for section, count in [(1, 3), (2, 10), (3, 10)] for i in range(1, count + 1)]
        self.assertEqual([p["identifiant"] for p in payload["passages"]], expected)
        path = self.config["index"]
        stat = path.stat()
        index, vectors = charger_index(str(path), stat.st_mtime_ns, stat.st_size)
        self.assertEqual(index["pdf_sha256"], payload["pdf_sha256"])
        self.assertEqual(len(vectors), 23)
        self.assertEqual(index["dimensions"], 1536)
        self.assertTrue(all(69 <= n <= 76 for p in index["passages"] for n in p["page_source"]["pdf"]))
        self.assertEqual(next(p for p in index["passages"] if p["identifiant"] == "11.3.8")["page_source"]["pdf"], [75, 76])

    def test_exercices_prepares(self):
        self.assertEqual([e["id"] for e in self.exercices], [f"14.{i}" for i in range(1, 15)])
        cache = CacheEnonces()
        for ex in self.exercices:
            self.assertTrue(preparation_valide(ex), ex["id"])
            self.assertTrue(cache.lire(ex)[1], ex["id"])
            self.assertIn(ex["difficulte"], range(6))
            self.assertTrue(ex["notions"])
            self.assertLessEqual(set(ex["notions"]), notions_cours().keys())
            self.assertTrue(all(r.startswith("11.") for r in ex["references_notions"].values()))
            for field, bounds in [("enonce", (41, 42)), ("corrige", (172, 178))]:
                pages = ex["page_source"][field]["pdf"]
                self.assertTrue(all(bounds[0] <= p <= bounds[1] for p in (pages if isinstance(pages, list) else [pages])))

    def test_banque_et_alias(self):
        for alias in [NOM_EDL, "edl", "equations differentielles lineaires", "11 — " + NOM_EDL, CHAPITRE_EDL]:
            self.assertEqual(chapitre_catalogue(alias), CHAPITRE_EDL)
            self.assertEqual(nom_chapitre(alias), NOM_EDL)
        self.assertEqual(len(self.banque), 25)
        self.assertEqual({q["nature"] for q in self.banque}, {"definition", "theoreme", "demonstration", "application"})
        self.assertTrue(all(q["notions"] and q["reponse_attendue"] for q in self.banque))
        self.assertEqual(len({(q["nature"], q["source"]) for q in self.banque}), 25)
        self.assertFalse(any(q["nature"] == "demonstration" and q["source"] in {"11.3.8", "11.3.10"} for q in self.banque))

    async def test_parcours_et_recherche_du_bon_chapitre(self):
        with tempfile.TemporaryDirectory() as folder:
            colle = Colle(Path(folder) / "profil.json", NOM_EDL, charger_exercices(), self.banque)
            client = FauxOpenAI()
            exam = Examinateur(colle, ServicesSimples(client), CacheEnonces())
            await exam.demarrer()
            client.intentions = ["question"]
            with patch("app.examinateur.chercher_dans_cours", new=AsyncMock(return_value={"passages": []})) as recherche:
                _ = [event async for event in exam.tour("Comment résoudre une équation homogène ?")]
                self.assertEqual(recherche.await_args.kwargs["chemin"], self.config["index"])
            for phase in ["cours", "demonstration", "applications"]:
                self.assertEqual(colle.etape, phase)
                self.assertTrue(colle.tache["source"].startswith("11."))
                colle.appliquer("Réponse juste", "reponse", CORRECT)
                colle.ouvrir_question_cours()
            self.assertEqual(colle.etape, "exercices")
            self.assertTrue(all(e["id"].startswith("14.") for e in colle.candidats_exercices()))


if __name__ == "__main__":
    unittest.main()
