import unittest
from app.pedagogie import score_pondere, decider, valider_evaluation
from app.moteur_colle import calculer_score, decision
from app.test_moteur_colle import evaluation


class PedagogieTests(unittest.TestCase):
    def test_regles_uniques(self):
        self.assertIs(score_pondere, calculer_score)
        self.assertIs(decider, decision)

    def test_notion_inventee_refusee(self):
        with self.assertRaises(ValueError):
            valider_evaluation(evaluation("incorrecte", notions=["notion inventée"]))
