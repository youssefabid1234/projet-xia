import unittest
from unittest.mock import AsyncMock

from app.evaluation import evaluer_reponse


class EvaluationTests(unittest.IsolatedAsyncioTestCase):
    async def test_corrige_transmis_sans_modification(self):
        client = AsyncMock()
        corrige = "Corrigé vérifié :\n$1+1=2$."
        await evaluer_reponse(client, "Calculer 1+1", "2", corrige)
        self.assertEqual(client.start_and_wait.call_args.kwargs["inputs"],
                         {"enonce": "Calculer 1+1", "reponse_eleve": "2", "corrige": corrige})

    async def test_corrige_manquant_ne_declenche_pas_evaluation(self):
        for corrige in (None, "", "  \n"):
            client = AsyncMock()
            with self.assertRaisesRegex(ValueError, "corrigé du catalogue"):
                await evaluer_reponse(client, "Calculer 1+1", "2", corrige)
            client.start_and_wait.assert_not_awaited()
