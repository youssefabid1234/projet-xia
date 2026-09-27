"""Tests HTTP de la colle (API JSON et flux NDJSON), sans service externe."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.chapitres import CHAPITRE_SERIES
from app.faux import FauxOpenAI, FauxServices
from app.profil import Profil
from app.test_colle import BANQUE, CORRECT

EXERCICES = [{"id": "17.1", "chapitre": CHAPITRE_SERIES, "enonce": "Question", "corrige": "Réponse", "difficulte": 1},
             {"id": "2.1", "chapitre": "2 — Dérivation et Intégration", "enonce": "Autre", "difficulte": 1}]


@patch.dict(os.environ, {"OPENAI_API_KEY": "test", "COLLE_EVALUATEUR": "local"})
class ChatTests(unittest.TestCase):
    def setUp(self):
        repertoire = tempfile.TemporaryDirectory()
        self.addCleanup(repertoire.cleanup)
        self.root = Path(repertoire.name)
        (self.root / "exercices.json").write_text(json.dumps(EXERCICES), encoding="utf-8")
        (self.root / "questions.json").write_text(json.dumps({"questions": BANQUE}), encoding="utf-8")
        passages = [{"identifiant": q["source"], "titre": q["source"], "texte": "…"} for q in BANQUE]
        (self.root / "index.json").write_text(json.dumps({"passages": passages}), encoding="utf-8")
        self.openai = FauxOpenAI()
        self.app = self.creer_app()
        self.client = self.app.test_client()
        self.client.get("/inscription")
        self.client.post("/inscription", data={"csrf": self.csrf(), "identifiant": "test", "mot_de_passe": "secret"})

    def creer_app(self):
        from app.web import create_app
        return create_app({
            "TESTING": True, "SECRET_KEY": "test", "PROFILS_DIR": self.root / "profils",
            "UTILISATEURS_PATH": self.root / "utilisateurs.json", "EXERCICES_PATH": self.root / "exercices.json",
            "CACHE_ENONCES": self.root / "cache.json", "SERVICES": FauxServices(self.openai),
            "COLLES": {CHAPITRE_SERIES: {"questions": self.root / "questions.json", "index": self.root / "index.json"}},
        })

    def csrf(self, client=None):
        with (client or self.client).session_transaction() as session:
            return session["csrf"]

    def api(self, route, corps=None, csrf=None, client=None):
        client = client or self.client
        return client.post(route, json=corps or {}, headers={"X-CSRF-Token": csrf or self.csrf(client)})

    def flux(self, reponse):
        self.assertEqual(reponse.mimetype, "application/x-ndjson")
        return [json.loads(ligne) for ligne in reponse.get_data(as_text=True).splitlines() if ligne.strip()]

    def demarrer(self):
        reponse = self.api("/api/colle", {"chapitre": 0})
        self.assertEqual(reponse.status_code, 200, reponse.get_data(as_text=True))
        return reponse.get_json()

    def test_accueil_sans_nom_interne_de_chapitre(self):
        page = self.client.get("/").get_data(as_text=True)
        donnees = json.loads(page.split('id="donnees">')[1].split("</script>")[0])
        self.assertEqual(donnees["chapitres"], [{"index": 0, "nom": "Séries numériques"}])
        self.assertNotIn("17", json.dumps(donnees))
        self.assertIsNone(donnees["etat"])
        self.assertIn("colle.js", page)

    def test_validations_avant_tout_appel(self):
        self.assertEqual(self.api("/api/colle", {"chapitre": 0}, csrf="faux").status_code, 400)
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            self.assertEqual(self.api("/api/colle", {"chapitre": 0}).status_code, 503)
        for corps in ({"chapitre": 5}, {"chapitre": "x"}, {}):
            self.assertEqual(self.api("/api/colle", corps).status_code, 400)
        self.assertEqual(self.api("/api/message", {"message": "Bonjour"}).status_code, 400)
        self.demarrer()
        for message in ("", "   ", "x" * 6001, 12):
            self.assertEqual(self.api("/api/message", {"message": message}).status_code, 400)
        self.assertEqual(self.api("/api/colle", {"chapitre": 0}).status_code, 409)
        self.assertEqual(self.openai.appels, [])

    def test_api_protegee(self):
        anonyme = self.app.test_client()
        reponse = anonyme.get("/api/etat")
        self.assertEqual(reponse.status_code, 401)
        self.assertIn("reconnectez-vous", reponse.get_json()["erreur"])

    def test_tour_complet_sauvegarde_et_reprise_apres_redemarrage(self):
        donnees = self.demarrer()
        question = donnees["messages"][0]["question"]["texte"]
        self.assertEqual(donnees["etat"]["etape"], "cours")
        self.openai.intentions = ["reponse"]
        self.openai.evaluations = [CORRECT]
        self.openai.textes = ["C'est <b>exact</b>."]
        evenements = self.flux(self.api("/api/message", {"message": "Ma définition"}))
        types = [e["type"] for e in evenements]
        self.assertEqual(types[0], "statut")
        self.assertIn("texte", types)
        self.assertEqual(types[-2:], ["question", "etat"])
        self.assertEqual("".join(e["texte"] for e in evenements if e["type"] == "texte"), "C'est <b>exact</b>.")
        self.assertTrue((self.root / "profils" / "test.colle.json").exists())
        self.assertEqual(len(Profil.charger(self.root / "profils" / "test.json").taches), 1)

        # Nouveau processus serveur : la colle reprend là où elle était.
        autre_app = self.creer_app()
        with autre_app.test_client() as client:
            with client.session_transaction() as session:
                session["utilisateur"] = "test"
            etat = client.get("/api/etat").get_json()
        self.assertEqual([m["role"] for m in etat["messages"]], ["colleur", "eleve", "colleur"])
        self.assertEqual(etat["messages"][0]["question"]["texte"], question)
        self.assertEqual(etat["etat"]["tache"]["nature"], "theoreme")

    def test_contenu_echappe_dans_la_page(self):
        self.demarrer()
        self.openai.intentions = ["hors_sujet"]
        self.flux(self.api("/api/message", {"message": "</script><script>alert(1)</script>"}))
        page = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("<script>alert(1)", page)
        self.assertIn("\\u003c/script\\u003e", page)

    def test_panne_signalee_sans_perdre_la_colle(self):
        self.demarrer()
        self.openai.intentions = [RuntimeError("réseau")]
        with self.assertLogs("app.examinateur", level="ERROR"):
            evenements = self.flux(self.api("/api/message", {"message": "Ma réponse"}))
        self.assertEqual(evenements[-1]["type"], "erreur")
        self.assertEqual(len(self.client.get("/api/etat").get_json()["messages"]), 1)
        # Le verrou de tour est libéré : l'élève peut réessayer.
        self.openai.intentions = ["reponse"]
        reponse = self.api("/api/message", {"message": "Ma réponse"})
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(self.flux(reponse)[-1]["type"], "etat")

    def test_un_seul_tour_a_la_fois(self):
        self.demarrer()
        self.openai.delai = 0.3
        premiere = self.api("/api/message", {"message": "Réponse 1"})
        # Le premier tour a démarré sans attendre la lecture du flux : il est en cours.
        seconde = self.api("/api/message", {"message": "Réponse 2"})
        self.assertEqual(seconde.status_code, 409)
        self.assertEqual(self.api("/api/bilan").status_code, 409)
        self.assertEqual(self.flux(premiere)[-1]["type"], "etat")
        self.openai.delai = 0
        self.assertEqual(self.flux(self.api("/api/message", {"message": "Réponse 2"}))[-1]["type"], "etat")

    def test_bilan_puis_nouvelle_colle(self):
        self.demarrer()
        self.openai.textes = ["**Note : 12/20**"]
        evenements = self.flux(self.api("/api/bilan"))
        self.assertTrue(evenements[-1]["etat"]["terminee"])
        profil = Profil.charger(self.root / "profils" / "test.json")
        self.assertEqual(profil.colles[0]["bilan"], "**Note : 12/20**")
        accueil = self.api("/api/nouvelle").get_json()
        self.assertIsNone(accueil["etat"])
        self.assertIn("12/20", accueil["anciennes"][0]["bilan"])
        self.assertFalse((self.root / "profils" / "test.colle.json").exists())
        self.assertEqual(self.api("/api/colle", {"chapitre": 0}).status_code, 200)

    def test_ancienne_interface_toujours_disponible(self):
        self.assertEqual(self.client.get("/classique").status_code, 200)


if __name__ == "__main__":
    unittest.main()
