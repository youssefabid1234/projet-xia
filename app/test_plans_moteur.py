import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from app.plans import CachePlans, preparer_plan
from app.test_moteur_colle import PLAN, tache, evaluation
from app.moteur_colle import appliquer_tour, element_actif


class PlansTests(unittest.IsolatedAsyncioTestCase):
    async def test_preparation_privee_et_sortie_invalide(self):
        client = SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(
            status="completed", output_text=json.dumps({"exploitable": True, "etapes": PLAN})))))
        self.assertEqual(await preparer_plan("E", "CORRIGE_PRIVE", client), PLAN)
        self.assertIn("CORRIGE_PRIVE", client.responses.create.call_args.kwargs["input"])
        client.responses.create.return_value.output_text = '{"exploitable": true, "etapes": []}'
        with self.assertRaises(ValueError):
            await preparer_plan("E", "C", client)

    async def test_cache_persistant_invalidation_et_panne_reessayable(self):
        with tempfile.TemporaryDirectory() as d:
            chemin = Path(d) / "plans.json"
            cache = CachePlans(chemin)
            with patch("app.plans.preparer_plan", new=AsyncMock(return_value=PLAN)) as preparer:
                await cache.obtenir({"id": "x"}, {"enonce": "E", "corrige": "C"}, None)
                await CachePlans(chemin).obtenir({"id": "x"}, {"enonce": "E", "corrige": "C"}, None)
                self.assertEqual(preparer.await_count, 1)
                preparer.side_effect = ValueError("panne")
                with self.assertRaises(ValueError):
                    await cache.obtenir({"id": "x"}, {"enonce": "E", "corrige": "nouveau"}, None)
                preparer.side_effect = None
                await cache.obtenir({"id": "x"}, {"enonce": "E", "corrige": "nouveau"}, None)
                self.assertEqual(preparer.await_count, 3)

    async def test_reprise_et_historique_propre_a_chaque_etape(self):
        t = tache(PLAN)
        appliquer_tour(t, "aide", "blocage")
        appliquer_tour(t, "premier essai faux", "reponse", evaluation("incorrecte"))
        reprise = json.loads(json.dumps(t))
        self.assertEqual(element_actif(reprise)["tentatives"], 1)
        appliquer_tour(reprise, "encore faux", "reponse", evaluation("incorrecte"))
        self.assertEqual(element_actif(reprise)["reponses"], [])
        self.assertEqual(reprise["contexte_action"]["reference"], PLAN[0]["reponse"])
        self.assertEqual(reprise["contexte_action"]["suivante"], PLAN[1]["question"])

    async def test_cache_corrompu_regenere(self):
        from app.catalogue_pedagogique import empreinte
        verifie = {"enonce": "E", "corrige": "C"}
        cache = CachePlans()
        cache.memoire = {"x": {"empreinte": empreinte(verifie), "etapes": []}}
        with patch("app.plans.preparer_plan", new=AsyncMock(return_value=PLAN)) as preparer:
            self.assertEqual(await cache.obtenir({"id": "x"}, verifie, None), PLAN)
            preparer.assert_awaited_once()
