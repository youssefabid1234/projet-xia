"""Règles de la colle et persistance, sans appel réseau."""

import json
import tempfile
import unittest
from pathlib import Path

from app.chapitres import CHAPITRE_SERIES, COLLES
from app.colle import (COMPLETER, CORRIGER_ERREUR, DONNER_CORRECTION, ESSAIS_PAR_ETAPE, INDICE, RECADRER,
                       REPONDRE_QUESTION, VALIDER, Colle, charger_banque, decider)
from app.profil import Profil

CORRECT = {"verdict": "correcte", "type_erreur": "aucune", "explication": "Juste."}
FAUX = {"verdict": "incorrecte", "type_erreur": "concept", "explication": "Faux."}
PARTIEL = {"verdict": "incomplete", "type_erreur": "reponse_incomplete", "explication": "Partiel."}


def question(source, nature, priorite=1):
    return {"source": source, "nature": nature, "priorite": priorite,
            "question": f"Question {nature} {source} ?", "reponse_attendue": f"Réponse {source}"}


BANQUE = [question("d1", "definition"), question("d2", "definition"), question("d3", "definition"),
          question("d4", "definition"), question("d5", "definition", priorite=3),
          question("t1", "theoreme"), question("t2", "theoreme"),
          question("t1", "demonstration"), question("e1", "applications")]
EXERCICES = [{"id": f"x{d}", "chapitre": CHAPITRE_SERIES, "difficulte": d, "enonce": f"Énoncé {d}",
              "corrige": f"Corrigé {d}"} for d in (1, 2, 3, 4)]


def tache(etape="cours", indices=0, echecs=0):
    return {"etape": etape, "indices": indices, "echecs": echecs}


class DeciderTests(unittest.TestCase):
    def test_table_des_actions(self):
        cas = [
            (tache(), "reponse", CORRECT, VALIDER),
            (tache(), "reponse", FAUX, CORRIGER_ERREUR),
            (tache(), "reponse", PARTIEL, COMPLETER),
            (tache(echecs=2), "reponse", FAUX, DONNER_CORRECTION),
            (tache(echecs=2), "reponse", PARTIEL, DONNER_CORRECTION),
            # Une réponse partielle n'est pas un échec pendant une preuve ou un exercice.
            (tache("exercices", echecs=3), "reponse", PARTIEL, COMPLETER),
            (tache("demonstration", echecs=2), "reponse", PARTIEL, COMPLETER),
            (tache("exercices", echecs=3), "reponse", FAUX, DONNER_CORRECTION),
            (tache("exercices", echecs=2), "reponse", FAUX, CORRIGER_ERREUR),
            (tache(), "demande_indice", None, INDICE),
            (tache(), "blocage", None, INDICE),
            (tache(indices=3), "blocage", None, DONNER_CORRECTION),
            (tache(), "demande_correction", None, DONNER_CORRECTION),
            (tache(), "demande_saut", None, RECADRER),
            (tache("exercices"), "demande_saut", None, DONNER_CORRECTION),
            (tache(), "question", None, REPONDRE_QUESTION),
            (tache(), "hors_sujet", None, RECADRER),
            (tache(), "reponse", None, RECADRER),
        ]
        for t, intention, evaluation, attendu in cas:
            with self.subTest(etape=t["etape"], intention=intention, evaluation=evaluation and evaluation["verdict"]):
                self.assertEqual(decider(t, intention, evaluation), attendu)


class ColleTests(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.chemin = Path(dossier.name) / "eleve.json"
        self.colle = self.nouvelle()

    def nouvelle(self):
        return Colle(self.chemin, CHAPITRE_SERIES, EXERCICES + [{"id": "autre", "chapitre": "Topologie"}], BANQUE, 30)

    def repondre_juste(self, colle=None):
        colle = colle or self.colle
        action = colle.appliquer("ma réponse", "reponse", CORRECT)
        self.assertEqual(action, VALIDER)
        return colle.ouvrir_question_cours()

    def test_deroule_complet_du_cours(self):
        colle = self.colle
        self.assertTrue(colle.ouvrir_question_cours())
        self.assertEqual((colle.etape, colle.tache["nature"]), ("cours", "definition"))
        # La priorité 1 passe avant la priorité 3.
        self.assertNotEqual(colle.tache["source"], "d5")
        self.assertTrue(self.repondre_juste())
        self.assertEqual((colle.etape, colle.tache["nature"]), ("cours", "theoreme"))
        self.assertTrue(self.repondre_juste())
        self.assertEqual((colle.etape, colle.tache["nature"], colle.tache["source"]), ("demonstration", "demonstration", "t1"))
        self.assertTrue(self.repondre_juste())
        self.assertEqual(colle.etape, "applications")
        self.assertFalse(self.repondre_juste())
        self.assertEqual(colle.etape, "exercices")
        self.assertIsNone(colle.tache)
        self.assertEqual([t["statut"] for t in colle.taches], ["acquise"] * 4)
        profil = Profil.charger(self.chemin)
        self.assertEqual(len(profil.taches), 4)
        self.assertTrue(all(t["acquise"] and t["cloturee"] for t in profil.taches.values()))
        # Les questions de cours ne comptent pas comme exercices vus.
        self.assertEqual(profil.exercices_vus, [])

    def test_acquis_non_reposes_dans_une_nouvelle_colle(self):
        self.colle.ouvrir_question_cours()
        premiere = self.colle.tache["source"]
        self.repondre_juste()
        suivante = self.nouvelle()
        suivante.ouvrir_question_cours()
        self.assertEqual(suivante.tache["nature"], "definition")
        self.assertNotEqual(suivante.tache["source"], premiere)

    def test_correction_puis_autre_question_de_meme_nature_et_plafond(self):
        colle = self.colle
        colle.ouvrir_question_cours()
        vues = []
        for _ in range(ESSAIS_PAR_ETAPE):
            self.assertEqual(colle.tache["nature"], "definition")
            vues.append(colle.tache["source"])
            self.assertEqual(colle.appliquer("je ne sais pas", "demande_correction", None), DONNER_CORRECTION)
            colle.ouvrir_question_cours()
        self.assertEqual(len(set(vues)), ESSAIS_PAR_ETAPE)
        # Après trois corrections, le colleur avance : la question suivante est un théorème.
        self.assertEqual(colle.tache["nature"], "theoreme")
        self.assertEqual([t["statut"] for t in colle.taches], ["corrigee"] * ESSAIS_PAR_ETAPE)
        self.assertFalse(any(t["acquise"] for t in Profil.charger(self.chemin).taches.values()))

    def test_compteurs_et_reponse_cumulee(self):
        colle = self.colle
        colle.ouvrir_question_cours()
        self.assertEqual(colle.appliquer("un indice ?", "demande_indice", None), INDICE)
        self.assertEqual(colle.appliquer("je bloque", "blocage", None), INDICE)
        self.assertEqual(colle.appliquer("essai 1", "reponse", FAUX), CORRIGER_ERREUR)
        self.assertEqual(colle.appliquer("bonjour", "hors_sujet", None), RECADRER)
        t = colle.tache
        self.assertEqual((t["indices"], t["blocages"], t["echecs"]), (2, 1, 1))
        self.assertEqual(t["reponses"], ["essai 1"])
        self.assertEqual(colle.reponse_cumulee("essai 2"), "Intervention 1 : essai 1\n\nIntervention 2 : essai 2")
        self.assertEqual(t["evaluations"][-1]["verdict"], "incorrecte")

    def test_exercices_niveau_et_difficulte_adaptee(self):
        colle = self.colle
        colle.programme = 4
        self.assertFalse(colle.ouvrir_question_cours())
        ordre = [ex["id"] for ex in colle.candidats_exercices()]
        self.assertEqual(ordre[0], "x2")  # niveau de départ 1,5 : difficulté 2 d'abord
        self.assertNotIn("autre", ordre)
        colle.ouvrir_exercice(EXERCICES[1], {"enonce": "Énoncé propre", "corrige": "Corrigé propre"})
        self.assertEqual(colle.tache["question"], "Énoncé propre")
        self.assertEqual(colle.tache["reference"], "Corrigé propre")
        self.assertEqual(colle.appliquer("solution", "reponse", CORRECT), VALIDER)
        profil = Profil.charger(self.chemin)
        self.assertEqual(profil.exercices_vus, ["x2"])
        self.assertEqual(profil.historique[0]["verdict"], "correcte")
        self.assertAlmostEqual(profil.niveau(CHAPITRE_SERIES), 1.8)
        # Réussite autonome : on vise plus difficile.
        self.assertEqual(colle.difficulte_cible, 3)
        self.assertEqual(colle.candidats_exercices()[0]["id"], "x3")
        colle.ouvrir_exercice(EXERCICES[2], {"enonce": "E3", "corrige": "C3"})
        colle.appliquer("la correction", "demande_correction", None)
        self.assertEqual(colle.difficulte_cible, 2)
        self.assertEqual(Profil.charger(self.chemin).historique[-1]["verdict"], "incorrecte")
        colle.ecarter(EXERCICES[0])
        self.assertEqual([ex["id"] for ex in colle.candidats_exercices()], ["x4"])

    def test_persistance_et_temps(self):
        colle = self.colle
        colle.ouvrir_question_cours()
        colle.appliquer("essai", "reponse", FAUX)
        colle.messages.append({"role": "eleve", "texte": "essai"})
        chemin = self.chemin.with_suffix(".colle.json")
        colle.sauvegarder(chemin)
        relue = Colle.from_dict(json.loads(chemin.read_text(encoding="utf-8")), self.chemin, EXERCICES, BANQUE)
        self.assertEqual(relue.to_dict(), colle.to_dict())
        self.assertEqual(relue.etat()["chapitre"], "Séries numériques")
        self.assertEqual(colle.temps_restant(colle.debut + 60), 29 * 60)
        self.assertEqual(colle.temps_restant(colle.debut + 3600), 0)

    def test_terminer_archive_le_bilan(self):
        self.colle.ouvrir_question_cours()
        self.repondre_juste()
        self.colle.terminer("**Note : 15/20**")
        self.assertTrue(self.colle.terminee)
        self.assertEqual(self.colle.etat()["etape"], "fin")
        colles = Profil.charger(self.chemin).colles
        self.assertEqual(colles[0]["bilan"], "**Note : 15/20**")
        self.assertEqual(colles[0]["taches"][0]["statut"], "acquise")


class BanqueReelleTests(unittest.TestCase):
    def test_banque_du_depot_coherente(self):
        config = COLLES[CHAPITRE_SERIES]
        banque = charger_banque(config["questions"], config["index"])
        natures = {q["nature"] for q in banque}
        self.assertEqual(natures, {"definition", "theoreme", "demonstration", "applications"})
        for q in banque:
            with self.subTest(source=q["source"], nature=q["nature"]):
                self.assertTrue(q["question"].strip() and q["reponse_attendue"].strip())
                self.assertEqual(q["question"].count("$") % 2, 0)
                self.assertIn(q["priorite"], (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
