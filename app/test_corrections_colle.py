"""Régressions : format court, mémoire, restitution et clôture automatique."""
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from app.colle import Colle
from app.chapitres import CHAPITRE_SERIES
from app.examinateur import Examinateur
from app.faux import FauxOpenAI, ServicesSimples
from app.profil import Profil
from app.test_colle import BANQUE, EXERCICES, CORRECT
from app.test_moteur_colle import PLAN, evaluation
from app.test_examinateur import CacheSimule, evenements
from app.texte_eleve import texte_eleve, compte_rendu


class CorrectionsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.path = Path(dossier.name) / "profil.json"

    def colle(self, banque=BANQUE):
        return Colle(self.path, CHAPITRE_SERIES, EXERCICES, banque)

    def ancien(self, source, nature, score, acquise=False, notions=()):
        p = Profil.charger(self.path)
        identifiant = f"{nature}:{source}"
        p.taches[identifiant] = dict(id=identifiant, contenu_id=identifiant, source=source,
            nature=nature, chapitre=CHAPITRE_SERIES, session="ancienne", score=score,
            acquise=acquise, notions=list(notions))
        p.sauvegarder(self.path)

    def test_une_seule_reprise_pire_score_et_reconnexion(self):
        self.ancien("d1", "definition", .2)
        self.ancien("t1", "demonstration", .1)
        self.ancien("e1", "applications", .3)
        c = self.colle()
        self.assertEqual(c.reprise_id, "demonstration:t1")
        c.ouvrir_question_cours()
        self.assertNotEqual(c.tache["source"], "d1")
        c.appliquer("oui", "reponse", CORRECT)
        c = Colle.from_dict(json.loads(json.dumps(c.to_dict())), self.path, EXERCICES, BANQUE)
        c.ouvrir_question_cours()
        self.assertEqual(c.tache["contenu_id"], "demonstration:t1")
        c.appliquer("oui", "reponse", CORRECT)
        self.assertFalse(c.ouvrir_question_cours())  # application ancienne non réservée
        self.assertEqual(sum(t["contenu_id"] in {"definition:d1", "demonstration:t1", "applications:e1"}
                             for t in c.taches), 1)

    def test_notion_neuve_avant_question_neuve_sur_notion_vue(self):
        self.ancien("d1", "definition", 1, True, ["N"])
        banque = [{**q, "notions": ["M" if q["source"] == "d3" else "N"]} for q in BANQUE]
        c = self.colle(banque)
        c.ouvrir_question_cours()
        self.assertEqual(c.tache["source"], "d3")
        self.assertIsNone(c.reprise_id)

    def test_reprise_exercice_et_plafond_meme_en_echec(self):
        self.ancien("x1", "exercice", .1)
        self.ancien("d1", "definition", .3)
        c = self.colle()
        self.assertEqual(c.candidats_exercices()[0]["id"], "x1")
        for _ in range(3):
            ex = c.candidats_exercices()[0]
            c.ouvrir_exercice(ex, {"enonce": "Q", "corrige": "R"}, PLAN)
            while c.tache:
                c.appliquer("abandon", "demande_correction", None)
        self.assertEqual(c.candidats_exercices(), [])
        self.assertFalse(c.ouvrir_exercice(EXERCICES[-1], {"enonce": "Q", "corrige": "R"}, PLAN))

    async def test_fin_apres_trois_exercices_et_bilan_sans_modele(self):
        c = self.colle()
        c.etape = "exercices"
        for ex in EXERCICES[:3]:
            c.ouvrir_exercice(ex, {"enonce": "Q", "corrige": "R"}, PLAN)
            c.appliquer("juste", "reponse", CORRECT)
        client = FauxOpenAI()
        exam = Examinateur(c, ServicesSimples(client), CacheSimule({}))
        evts = await evenements(exam.tour("suite"))
        self.assertTrue(c.terminee)
        self.assertIn("au revoir", c.bilan)
        self.assertIn("8/20", c.bilan)
        self.assertFalse(client.appels)
        self.assertNotIn("question", [e["type"] for e in evts])

    def test_correction_explique_avant_reponse_meme_apres_indice(self):
        c = self.colle()
        c.ouvrir_question_cours()
        ev = evaluation("incorrecte")
        ev["explication"] = "Vous confondez terme et somme : la convergence porte sur les sommes partielles."
        c.appliquer("faux", "reponse", ev)
        t = c.tache
        action = c.appliquer("corrigez", "demande_correction", None)
        exam = Examinateur(c, ServicesSimples(FauxOpenAI()), CacheSimule({}))
        texte = exam.texte_impose(action, t)
        self.assertLess(texte.index(ev["explication"]), texte.index(t["reference"]))

    def test_references_privees_et_bilan_determine(self):
        texte = texte_eleve("Reprenez Définition 16.1.13, page PDF 142 et Théorème 16.2.4, page PDF 143.")
        self.assertNotIn("16.", texte)
        self.assertNotIn("PDF", texte)
        taches = [dict(etape="cours", question="Q", score=.2, evaluations=[{"explication": "Tout est parfait"}])]
        bilan = compte_rendu(taches, {"cours": "Cours"})
        self.assertIn("20 %", bilan)
        self.assertNotIn("Tout est parfait", bilan)
        self.assertIn("aucune tâche à ce seuil", bilan)

    @patch.dict("os.environ", {"COLLE_EVALUATEUR": "local"})
    async def test_reference_fragmente_pas_diffusee(self):
        c = self.colle()
        c.ouvrir_question_cours()
        client = FauxOpenAI(intentions=["demande_indice"],
                            textes=["Reprenez la Définition 16.1.13, page PDF 142 : les sommes partielles."])
        exam = Examinateur(c, ServicesSimples(client), CacheSimule({}))
        evts = await evenements(exam.tour("Un indice"))
        for ev in evts:
            public = json.dumps(ev, ensure_ascii=False)
            self.assertNotIn("16.1.13", public)
            self.assertNotIn("PDF 142", public)
        self.assertIn("sommes partielles", c.messages[-1]["texte"])

    @patch.dict("os.environ", {"COLLE_EVALUATEUR": "local"})
    async def test_parcours_complet_six_taches_et_fin_sans_clic(self):
        c = self.colle()
        client = FauxOpenAI(intentions=["reponse"] * 6, evaluations=[CORRECT] * 6)
        cache = CacheSimule({ex["id"]: {"enonce": "Q", "corrige": "R"} for ex in EXERCICES})
        exam = Examinateur(c, ServicesSimples(client), cache)
        await exam.demarrer()
        for _ in range(6):
            self.assertFalse(c.terminee)
            await evenements(exam.tour("juste"))
        self.assertTrue(c.terminee)
        self.assertEqual([t["etape"] for t in c.taches],
                         ["cours", "demonstration", "applications", "exercices", "exercices", "exercices"])
        self.assertEqual(len(Profil.charger(self.path).colles), 1)
        self.assertIn("20/20", c.bilan)
