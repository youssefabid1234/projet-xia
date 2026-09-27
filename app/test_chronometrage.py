"""Vérifie le cumul, les erreurs et l'isolation des échanges."""
import asyncio
import unittest
from unittest.mock import patch

from app.chronometrage import chronometrer, mesurer, mesurer_echange


class ChronometrageTests(unittest.TestCase):
    def test_cumul_et_erreur_sans_fuite_vers_echange_suivant(self):
        with self.assertLogs("app.chronometrage", level="INFO"):
            with patch("app.chronometrage.perf_counter", side_effect=[0, 1, 3, 4, 7, 10, 11, 12]):
                with self.assertRaisesRegex(ValueError, "échec"):
                    with mesurer_echange() as premier:
                        with mesurer("dialogue_openai"):
                            pass
                        with mesurer("dialogue_openai"):
                            raise ValueError("échec")
                with mesurer_echange() as suivant:
                    pass
        self.assertEqual(premier["total_secondes"], 10)
        self.assertEqual(premier["autres_secondes"], 5)
        self.assertEqual(premier["repartition"]["dialogue_openai"],
                         {"appels": 2, "secondes": 5, "pourcentage": 50})
        self.assertEqual(premier["statut"], "erreur")
        self.assertEqual(premier["appels"][-1]["statut"], "erreur")
        self.assertEqual(suivant["appels"], [])

    def test_contexte_transmis_a_asyncio_run(self):
        @chronometrer("progression")
        async def progression():
            return 42

        with self.assertLogs("app.chronometrage", level="INFO"):
            with mesurer_echange() as suivi:
                self.assertEqual(asyncio.run(progression()), 42)
        self.assertEqual(suivi["repartition"]["progression"]["appels"], 1)
