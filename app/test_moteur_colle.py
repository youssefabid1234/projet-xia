import copy
import unittest
from app.moteur_colle import appliquer_tour, calculer_score, choisir_phase, element_actif, installer_tache, phase_terminee


def evaluation(verdict="correcte", intuition="solide", progression="avance", notions=()):
    return dict(verdict=verdict, intuition=intuition, progression=progression,
                type_erreur="aucune" if verdict == "correcte" else "non_determinable" if verdict == "indeterminable" else "calcul",
                notions_fragiles=list(notions), explication="Retour.")


def tache(plan=()):
    return installer_tache(dict(id="tentative", contenu_id="exercice:x", etape="exercices", nature="exercice",
        question="Énoncé entier", reference="Corrigé entier", reponses=[], evaluations=[], indices=0, echecs=0,
        blocages=0, statut="active"), plan)


PLAN = [dict(objectif="Calculer", question="Calcul ?", indice="Piste", reponse="2"),
        dict(objectif="Conclure", question="Conclusion ?", indice="Piste finale", reponse="4")]


class MoteurTests(unittest.TestCase):
    def test_score_comprehension_aide_et_indetermination(self):
        e = evaluation()
        self.assertEqual(calculer_score(e), 1)
        self.assertEqual(calculer_score(e, indices=1, tentatives=2), .9)
        self.assertEqual(calculer_score(e, indices=2), .81)
        self.assertEqual(calculer_score(e, tentatives=3), 1)
        self.assertAlmostEqual(calculer_score(evaluation("incomplete"), indices=1),
                               calculer_score(evaluation("incomplete")) * .9)
        self.assertGreater(calculer_score(evaluation("incomplete")), .5)
        self.assertLessEqual(calculer_score(e, reponse_donnee=True), .25)
        self.assertIsNone(calculer_score(evaluation("indeterminable")))

    def test_indeterminable_ne_consomme_rien(self):
        t = tache(PLAN)
        appliquer_tour(t, "essai", "reponse", evaluation("incorrecte"))
        avant = copy.deepcopy(t)
        self.assertEqual(appliquer_tour(t, "?", "reponse", evaluation("indeterminable")), "reformuler_demande")
        for cle in ("autonome", "evaluations", "reponses", "tentatives_totales", "indices", "echecs"):
            self.assertEqual(t[cle], avant[cle])

    def test_etape_correcte_ne_clot_pas_exercice(self):
        t = tache(PLAN)
        self.assertEqual(appliquer_tour(t, "aide", "blocage"), "reveler_etape")
        self.assertEqual(appliquer_tour(t, "2", "reponse", evaluation()), "valider_etape")
        self.assertEqual(t["statut"], "active")
        self.assertEqual(element_actif(t)["tentatives"], 0)
        appliquer_tour(t, "4", "reponse", evaluation())
        self.assertTrue(t["acquise"])
        self.assertEqual(t["score"], .9)

    def test_deux_essais_par_element_et_correction_non_acquise(self):
        t = tache(PLAN)
        for _ in range(2):
            appliquer_tour(t, "faux", "reponse", evaluation("incorrecte"))
        self.assertEqual(t["etape_active"], 0)
        for _ in range(2):
            action = appliquer_tour(t, "faux", "reponse", evaluation("incorrecte"))
        self.assertEqual(action, "donner_reponse_etape")
        self.assertEqual(t["contexte_action"]["reference"], "2")
        appliquer_tour(t, "4", "reponse", evaluation())
        self.assertFalse(t["acquise"])
        self.assertLessEqual(t["score"], .25)

    def test_aide_bornee_question_sans_essai(self):
        t = tache()
        appliquer_tour(t, "pourquoi", "question")
        self.assertEqual(element_actif(t)["tentatives"], 0)
        appliquer_tour(t, "aide", "demande_indice")
        self.assertEqual(appliquer_tour(t, "aide", "demande_indice"), "donner_reponse")
        self.assertFalse(t["acquise"])

    def test_phases_epuisees_et_objectifs(self):
        vues = []
        def choisir(phase):
            vues.append(phase)
            return {"id": "ex"} if phase == "exercices" else None
        self.assertEqual(choisir_phase("cours", [], choisir), ("exercices", {"id": "ex"}))
        self.assertEqual(len(vues), 4)
        self.assertTrue(phase_terminee("cours", [dict(etape="cours", acquise=True)] * 3))
        self.assertFalse(phase_terminee("cours", []))
        self.assertTrue(phase_terminee("cours", [dict(etape="cours", acquise=False)] * 5))
        self.assertTrue(phase_terminee("exercices", [dict(etape="exercices", acquise=False)] * 3))
