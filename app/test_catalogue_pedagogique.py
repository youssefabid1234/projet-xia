import unittest
from app.catalogue_pedagogique import empreinte, preparation_valide, notions_cours


class CatalogueTests(unittest.TestCase):
    def test_cache_invalide_si_source_change(self):
        ex = {"enonce": "Question", "corrige": "Réponse"}
        ex["preparation"] = {"empreinte": empreinte(ex), "exploitable": True}
        self.assertTrue(preparation_valide(ex))
        ex["corrige"] += " corrigée"
        self.assertFalse(preparation_valide(ex))

    def test_noms_et_references_proviennent_du_cours(self):
        notions = notions_cours()
        self.assertGreater(len(notions), 20)
        for nom, passage in notions.items():
            self.assertEqual(nom, passage["titre"])
            self.assertTrue(passage["identifiant"])
