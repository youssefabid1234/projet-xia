import json
import unittest
from unittest.mock import AsyncMock

from app.evaluation import evaluer, methode_locale, rendre_prompt
from app.evaluation import evaluer_reponse
from app.faux import FauxOpenAI


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


class EvaluationLocaleTests(unittest.IsolatedAsyncioTestCase):
    def test_methode_lue_depuis_le_fichier_mthds(self):
        methode = methode_locale()
        self.assertIn("correcteur rigoureux", methode["systeme"])
        schema = methode["format"]["schema"]
        self.assertEqual(schema["properties"]["verdict"]["enum"], ["correcte", "incorrecte", "incomplete", "indeterminable"])
        self.assertIn("non_determinable", schema["properties"]["type_erreur"]["enum"])
        self.assertEqual(schema["properties"]["explication"]["type"], "string")
        self.assertEqual(sorted(schema["required"]), ["explication", "type_erreur", "verdict"])
        prompt = rendre_prompt(methode, {"enonce": "E1", "reponse_eleve": "R1", "corrige": "C1"})
        for valeur in ("E1", "R1", "C1"):
            self.assertIn(valeur, prompt)
        self.assertNotIn("@enonce", prompt)

    async def test_evaluation_locale_structuree(self):
        attendu = {"verdict": "correcte", "type_erreur": "aucune", "explication": "Juste."}
        client = FauxOpenAI(evaluations=[attendu])
        self.assertEqual(await evaluer("Calculer 1+1", "2", "2", openai=client, moteur="local"), attendu)
        appel = client.appels[0]
        self.assertTrue(appel["text"]["format"]["strict"])
        self.assertFalse(appel["store"])

    async def test_sortie_invalide_refusee(self):
        client = FauxOpenAI(evaluations=[{"verdict": "peut-etre", "type_erreur": "aucune", "explication": "?"}])
        with self.assertRaises(ValueError):
            await evaluer("E", "R", "C", openai=client, moteur="local")

    async def test_corrige_manquant_local(self):
        client = FauxOpenAI()
        with self.assertRaisesRegex(ValueError, "corrigé du catalogue"):
            await evaluer("E", "R", " ", openai=client, moteur="local")
        self.assertEqual(client.appels, [])


if __name__ == "__main__":
    unittest.main()
