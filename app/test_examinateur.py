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
        self.assertEqual(self.colle.tache["nature"], "theoreme")
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
        self.assertEqual(evts[1]["action"], "indice")
        self.assertIsNone(evts[1]["verdict"])
        self.assertEqual(self.colle.tache["indices"], 1)
        self.assertEqual(self.colle.tache["reponses"], [])
        self.assertEqual(self.colle.tache["question"], question)
        self.assertNotIn("question", [e["type"] for e in evts])
        self.assertIn("indice n°1", self.client.appels_flux()[0]["input"][-1]["content"])

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
        self.assertIn("Le colleur cherche dans le cours…", [e.get("texte") for e in evts])
        consigne = self.client.appels_flux()[0]["input"][-1]["content"]
        self.assertIn("Définition 16.1.5 (Convergence d'une série) (page PDF 140)", consigne)
        self.assertIn("Hors du cours extrait :", consigne)

    async def test_passage_aux_exercices_avec_cache_et_ecart(self):
        self.colle.programme = 3  # dernière étape du cours : l'application
        self.colle.essais_etape = 0
        self.colle.tache = None
        self.colle.ouvrir_question_cours()
        self.cache.resultats = {"x2": None, "x1": {"enonce": "Énoncé 1 propre", "corrige": "Corrigé 1 propre"}}
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        evts = await evenements(self.examinateur.tour("Ma solution"))
        self.assertIn("Le colleur choisit un exercice…", [e.get("texte") for e in evts])
        question = next(e for e in evts if e["type"] == "question")["question"]
        self.assertEqual(question["texte"], "Énoncé 1 propre")
        self.assertEqual(question["libelle"], "Exercices · difficulté 1/5")
        self.assertEqual(self.cache.demandes[:2], ["x2", "x1"])
        self.assertIn("x2", self.colle.ecartes)
        self.assertEqual(self.colle.tache["reference"], "Corrigé 1 propre")

    async def test_temps_ecoule_pas_de_nouvelle_question(self):
        self.colle.debut -= 3600
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        evts = await evenements(self.examinateur.tour("Ma définition"))
        self.assertNotIn("question", [e["type"] for e in evts])
        self.assertIn("Le temps est écoulé", self.texte(evts))
        self.assertIsNone(self.colle.tache)
        suite = await evenements(self.examinateur.tour("Encore ?"))
        self.assertEqual(suite[-1]["type"], "erreur")

    async def test_bilan_diffuse_puis_archive(self):
        self.client.intentions = ["reponse"]
        self.client.evaluations = [CORRECT]
        await evenements(self.examinateur.tour("Ma définition"))
        self.client.textes = ["**Note : 16/20**\n\n**Points forts** Le cours."]
        evts = await evenements(self.examinateur.bilan())
        self.assertIn("**Note : 16/20**", self.texte(evts))
        self.assertTrue(evts[-1]["etat"]["terminee"])
        donnees = json.loads(self.client.appels_flux()[-1]["input"][0]["content"])
        self.assertEqual([q["resultat"] for q in donnees["questions"]], ["acquise", "en cours (non terminée)"])
        self.assertEqual(Profil.charger(self.chemin).colles[0]["bilan"], "**Note : 16/20**\n\n**Points forts** Le cours.")
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

    @patch.dict(os.environ, {"COLLE_EVALUATEUR": "pipelex"})
    async def test_mode_pipelex_evalue_seulement_les_reponses(self):
        self.client.intentions = ["demande_indice", "reponse"]
        with patch("app.examinateur.evaluer", new=AsyncMock(return_value=CORRECT)) as evaluer:
            await evenements(self.examinateur.tour("Un indice ?"))
            evaluer.assert_not_awaited()
            evts = await evenements(self.examinateur.tour("Ma définition"))
        evaluer.assert_awaited_once()
        self.assertIsNotNone(evaluer.await_args.kwargs["pipelex"])
        self.assertIn("Le colleur compare avec le corrigé…", [e.get("texte") for e in evts])


if __name__ == "__main__":
    unittest.main()
