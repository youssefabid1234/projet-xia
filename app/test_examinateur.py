"""Tours de colle avec OpenAI simulé : événements, pannes et enchaînements."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from openai import APIConnectionError

from app.chapitres import CHAPITRE_SERIES
from app.colle import Colle
from app.examinateur import Examinateur
from app.faux import FauxOpenAI, ServicesSimples
from app.profil import Profil
from app.test_colle import BANQUE, CORRECT, EXERCICES, FAUX
from app.test_moteur_colle import PLAN, evaluation
from app.moteur_colle import element_actif


class CacheSimule:
    def __init__(self, resultats):
        self.resultats = resultats
        self.demandes = []

    async def exercice_verifie(self, exercice, client):
        self.demandes.append(exercice["id"])
        resultat = self.resultats.get(exercice["id"])
        if isinstance(resultat, BaseException):
            raise resultat
        return resultat


async def evenements(generateur):
    return [e async for e in generateur]


@patch.dict(os.environ, {"COLLE_EVALUATEUR": "local"})
class ExaminateurTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.chemin = Path(dossier.name) / "eleve.json"
        self.client = FauxOpenAI()
        self.cache = CacheSimule({})
        self.colle = Colle(self.chemin, CHAPITRE_SERIES, EXERCICES, BANQUE, 30)
        self.examinateur = Examinateur(self.colle, ServicesSimples(self.client), self.cache)
        self.ouverture = await self.examinateur.demarrer()

    def texte(self, evts):
        return "".join(e["texte"] for e in evts if e["type"] == "texte")

    async def test_ouverture_sans_appel_au_modele(self):
        self.assertIn("On commence par le cours", self.ouverture["texte"])
        self.assertEqual(self.ouverture["question"]["libelle"], "Questions de cours")
        self.assertEqual(self.ouverture["question"]["texte"], self.colle.tache["question"])
        self.assertEqual(self.client.appels, [])

    async def test_evaluation_cumulee_apres_relance_et_reconnexion(self):
        self.colle.appliquer("Les sommes partielles convergent", "reponse", evaluation("incomplete"))
        reprise = Colle.from_dict(self.colle.to_dict(), self.chemin, EXERCICES, BANQUE)
        exam = Examinateur(reprise, ServicesSimples(self.client), self.cache)
        self.client.evaluations = [CORRECT]
        await exam.evaluer(self.client, "Vers une limite finie")
        prompt = self.client.appels[-1]["input"][0]["content"]
        reponse = prompt.split('<reponse_eleve', 1)[1].split('</reponse_eleve>', 1)[0]
        self.assertIn("Les sommes partielles convergent", reponse)
        self.assertIn("Vers une limite finie", reponse)
        self.assertLess(reponse.index("sommes partielles"), reponse.index("limite finie"))
        reprise.appliquer("Vers une limite finie", "reponse", CORRECT)
        self.assertEqual(reprise.taches[0]["score"], 1)

    async def test_tentative_autonome_conservee_dans_evaluation_etape(self):
        self.colle.ouvrir_exercice(EXERCICES[0], {"enonce": "Q", "corrige": "R"}, PLAN)
        self.colle.appliquer("Mon idée initiale", "reponse", evaluation("incomplete"))
        self.colle.appliquer("Un indice", "demande_indice", None)
        self.client.evaluations = [CORRECT]
        await self.examinateur.evaluer(self.client, "Ma précision")
        prompt = self.client.appels[-1]["input"][0]["content"]
        self.assertIn("Mon idée initiale", prompt)
        self.assertIn("Ma précision", prompt)

    async def test_temps_ecoule_distingue_non_atteintes_et_echecs(self):
        self.colle.debut = 0
        evts = await evenements(self.examinateur.bilan())
        texte = self.texte(evts)
        self.assertIn("**Note : 0/20**", texte)
        self.assertIn("interrompue, pas un échec", texte)
        self.assertIn("Exercice 3 : **0/2 point(s)** — non atteinte faute de temps, pas un échec", texte)
        self.assertIn("aucune tâche notée sous ce seuil", texte)

    async def test_reponse_juste_valide_et_affiche_la_question_suivante(self):
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        self.client.textes = ["Exact : c'est la bonne définition."]
        reference = self.colle.tache["reference"]
        evts = await evenements(self.examinateur.tour("  Ma définition  "))
        types = [e["type"] for e in evts]
        self.assertEqual(types[:2], ["statut", "action"])
        self.assertEqual(evts[1], {"type": "action", "action": "valider", "verdict": "correcte"})
        self.assertEqual(types[-2:], ["question", "etat"])
        self.assertEqual(self.texte(evts), "Exact : c'est la bonne définition.")
        self.assertEqual(evts[-2]["question"]["texte"], self.colle.tache["question"])
        self.assertEqual(self.colle.etape, "demonstration")
        self.assertEqual([m["role"] for m in self.colle.messages], ["colleur", "eleve", "colleur"])
        self.assertEqual(self.colle.messages[1]["texte"], "Ma définition")
        # La référence est donnée au colleur en consigne privée, jamais diffusée telle quelle.
        flux = self.client.appels_flux()[0]
        self.assertIn(reference, flux["input"][-1]["content"])
        self.assertEqual(flux["input"][-1]["role"], "developer")
        self.assertEqual(flux["input"][-2], {"role": "user", "content": "Ma définition"})
        self.assertEqual(sum(1 for m in flux["input"] if m.get("content") == "Ma définition"), 1)
        self.assertNotIn(reference, json.dumps(evts, ensure_ascii=False))
        self.assertTrue(Profil.charger(self.chemin).taches)

    async def test_demande_d_indice_sans_evaluation_retenue(self):
        self.client.intentions = ["demande_indice"]
        self.client.textes = ["Pensez aux sommes partielles."]
        question = self.colle.tache["question"]
        evts = await evenements(self.examinateur.tour("Un indice ?"))
        self.assertEqual(evts[1]["action"], "donner_indice")
        self.assertIsNone(evts[1]["verdict"])
        self.assertEqual(self.colle.tache["indices"], 1)
        self.assertEqual(self.colle.tache["reponses"], [])
        self.assertEqual(self.colle.tache["question"], question)
        self.assertNotIn("question", [e["type"] for e in evts])
        self.assertIn("indice ciblé", self.client.appels_flux()[0]["input"][-1]["content"])
        self.assertFalse(any(a.get("text", {}).get("format", {}).get("name") == "evaluation" for a in self.client.appels))

    async def test_panne_d_analyse_ne_modifie_rien(self):
        self.client.intentions = [APIConnectionError(request=httpx.Request("POST", "https://example.test"))]
        avant = json.dumps(self.colle.to_dict(), sort_keys=True)
        with self.assertLogs("app.examinateur", level="ERROR"):
            evts = await evenements(self.examinateur.tour("Ma réponse"))
        self.assertEqual(evts[-1]["type"], "erreur")
        self.assertIn("réessayez", evts[-1]["texte"])
        self.assertEqual(json.dumps(self.colle.to_dict(), sort_keys=True), avant)

    async def test_panne_du_flux_complete_par_un_repli(self):
        self.client.intentions = ["reponse"]
        self.client.evaluations = [FAUX]
        self.client.textes = [("Attention, ", RuntimeError("coupure"))]
        with self.assertLogs("app.examinateur", level="ERROR"):
            evts = await evenements(self.examinateur.tour("Une réponse fausse"))
        texte = self.texte(evts)
        self.assertTrue(texte.startswith("Attention, "))
        self.assertIn("erreur", texte)
        self.assertEqual(self.colle.tache["echecs"], 1)
        self.assertEqual(self.colle.messages[-1]["texte"], texte.strip())

    async def test_question_de_cours_avec_recherche_et_citation(self):
        self.client.intentions = ["question"]
        passage = {"identifiant": "16.1.5", "titre": "Définition 16.1.5 (Convergence d'une série)",
                   "texte": "On dit que la série converge si...", "page_source": {"pdf": [140]}}
        with patch("app.examinateur.chercher_dans_cours", new=AsyncMock(return_value={"passages": [passage]})) as recherche:
            evts = await evenements(self.examinateur.tour("C'est quoi une somme partielle ?"))
        recherche.assert_awaited_once()
        self.assertIn("X-hôlleur cherche dans le cours…", [e.get("texte") for e in evts])
        consigne = self.client.appels_flux()[0]["input"][-1]["content"]
        self.assertIn("Définition 16.1.5 (Convergence d'une série) (page PDF 140)", consigne)
        self.assertIn("Hors du cours extrait :", consigne)

    async def test_passage_aux_exercices_avec_cache_et_ecart(self):
        self.colle.etape = "applications"
        self.colle.tache = None
        self.colle.ouvrir_question_cours()
        self.cache.resultats = {"x2": None, "x1": {"enonce": "Énoncé 1 propre", "corrige": "Corrigé 1 propre"}}
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        evts = await evenements(self.examinateur.tour("Ma solution"))
        self.assertIn("X-hôlleur choisit un exercice…", [e.get("texte") for e in evts])
        question = next(e for e in evts if e["type"] == "question")["question"]
        self.assertEqual(question["texte"], "Énoncé 1 propre")
        self.assertEqual(question["libelle"], "Exercices · difficulté 1/5")
        self.assertEqual(self.cache.demandes[:3], ["x2", "x3", "x1"])
        self.assertIn("x2", self.colle.ecartes)
        self.assertEqual(self.colle.tache["reference"], "Corrigé 1 propre")

    async def test_temps_ecoule_pas_de_nouvelle_question(self):
        self.colle.debut -= 3600
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        evts = await evenements(self.examinateur.tour("Ma définition"))
        self.assertNotIn("question", [e["type"] for e in evts])
        self.assertIn("Le temps est écoulé", self.texte(evts))
        self.assertTrue(self.colle.terminee)
        self.assertIsNone(self.colle.tache)
        self.assertEqual(self.client.appels, [])
        suite = await evenements(self.examinateur.tour("Encore ?"))
        self.assertEqual(suite[-1]["type"], "erreur")

    async def test_ancien_exercice_refuse_ne_bloque_pas_la_reprise(self):
        self.colle.ouvrir_exercice(EXERCICES[0], {"enonce": "ancien", "corrige": "illisible"}, PLAN)
        self.colle.tache["etapes_resolution"] = []
        self.client.plans = [{"exploitable": False, "etapes": []}]
        self.cache.resultats = {"x2": {"enonce": "nouveau", "corrige": "corrigé"}}
        evts = await evenements(self.examinateur.tour("ancienne réponse"))
        self.assertIn("sans pénalité", self.texte(evts))
        self.assertEqual(self.colle.tache["source"], "x2")
        self.assertFalse(self.chemin.exists())

    async def test_bilan_diffuse_puis_archive(self):
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        await evenements(self.examinateur.tour("Ma définition"))
        self.client.textes = ["**Points forts** Le cours."]
        evts = await evenements(self.examinateur.bilan())
        self.assertIn("**Note : 3/20**", self.texte(evts))
        self.assertTrue(evts[-1]["etat"]["terminee"])
        self.assertIn("100 %", self.texte(evts))
        self.assertIn("interrompue", self.texte(evts))
        self.assertEqual(Profil.charger(self.chemin).colles[0]["bilan"], self.texte(evts).strip())
        self.assertEqual(len(self.client.appels_flux()), 1)
        self.assertTrue(self.colle.messages[-1]["bilan"])
        # Un second appel renvoie le bilan enregistré, sans nouvel appel au modèle.
        nombre = len(self.client.appels)
        await evenements(self.examinateur.bilan())
        self.assertEqual(len(self.client.appels), nombre)

    async def test_message_invalide(self):
        for message in ("", "   ", "x" * 6001, None):
            evts = await evenements(self.examinateur.tour(message))
            self.assertEqual([e["type"] for e in evts], ["erreur"])
        self.assertEqual(self.client.appels, [])

    async def test_exercice_guide_correction_et_confidentialite(self):
        self.colle.ouvrir_exercice(EXERCICES[0], {"enonce": "ENTIER", "corrige": "CORRIGE_ENTIER_PRIVE"}, PLAN)
        identifiant = self.colle.tache["id"]
        self.client.intentions = ["blocage", "reponse", "reponse", "reponse"]
        self.client.evaluations = [FAUX, FAUX, CORRECT]
        evts = await evenements(self.examinateur.tour("bloqué"))
        self.assertNotIn("Conclusion ?", json.dumps(evts))
        self.assertNotIn("CORRIGE_ENTIER_PRIVE", json.dumps(evts))
        await evenements(self.examinateur.tour("faux"))
        evts = await evenements(self.examinateur.tour("encore faux"))
        self.assertIn("Conclusion ?", self.texte(evts))
        self.assertEqual(self.colle.tache["id"], identifiant)
        self.assertEqual(element_actif(self.colle.tache)["tentatives"], 0)
        self.assertNotIn("2", element_actif(self.colle.tache)["reponses"])
        await evenements(self.examinateur.tour("4"))
        archive = Profil.charger(self.chemin).taches[identifiant]
        self.assertFalse(archive["acquise"])
        self.assertLessEqual(archive["score"], .25)
        appels = [a for a in self.client.appels if a.get("text", {}).get("format", {}).get("name") == "evaluation"]
        self.assertEqual(len(appels), 3)
        self.assertNotIn("CORRIGE_ENTIER_PRIVE", appels[0]["input"][0]["content"])
        self.assertIn("encore faux", appels[-1]["input"][0]["content"])

    async def test_indetermination_sans_essai_et_reussite_etape(self):
        self.colle.ouvrir_exercice(EXERCICES[0], {"enonce": "ENTIER", "corrige": "C"}, PLAN)
        self.client.intentions = ["blocage", "reponse", "reponse"]
        self.client.evaluations = [evaluation("indeterminable"), CORRECT]
        await evenements(self.examinateur.tour("aide"))
        await evenements(self.examinateur.tour("?"))
        self.assertEqual(element_actif(self.colle.tache)["tentatives"], 0)
        await evenements(self.examinateur.tour("2"))
        self.assertEqual(self.colle.tache["etape_active"], 1)
        self.assertFalse(self.chemin.exists())

    async def test_panne_preparation_reessayable_sans_fin_prematuree(self):
        self.colle.etape = "exercices"
        self.colle.tache = None
        self.cache.resultats = {"x2": ValueError("panne"), "x1": None, "x3": None, "x4": None}
        with self.assertLogs("app.examinateur", level="WARNING"):
            evts = await evenements(self.examinateur.tour("continuer"))
        self.assertEqual(evts[-1]["type"], "erreur")
        self.assertNotIn("x2", self.colle.ecartes)
        self.cache.resultats["x2"] = {"enonce": "E", "corrige": "C"}
        evts = await evenements(self.examinateur.tour("réessayer"))
        self.assertIn("question", [e["type"] for e in evts])

    @patch.dict(os.environ, {"COLLE_EVALUATEUR": "pipelex"})
    async def test_mode_pipelex_evalue_seulement_les_reponses(self):
        self.client.intentions = ["demande_indice", "reponse"]
        with patch("app.examinateur.evaluer", new=AsyncMock(return_value=CORRECT)) as evaluer:
            await evenements(self.examinateur.tour("Un indice ?"))
            evaluer.assert_not_awaited()
            evts = await evenements(self.examinateur.tour("Ma définition"))
        evaluer.assert_awaited_once()
        self.assertIsNotNone(evaluer.await_args.kwargs["pipelex"])
        self.assertIn("X-hôlleur compare avec le corrigé…", [e.get("texte") for e in evts])


if __name__ == "__main__":
    unittest.main()
