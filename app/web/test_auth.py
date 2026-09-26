"""Authentification et isolation des profils, sans API externe."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from werkzeug.security import check_password_hash

from app.profil import Profil
from app.web import create_app


class AuthTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        exercices = self.root / "exercices.json"
        exercices.write_text(json.dumps([
            {"id": "a", "chapitre": "Analyse", "difficulte": 1, "enonce": "1+1 ?"}
        ]), encoding="utf-8")
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "test",
            "UTILISATEURS_PATH": self.root / "utilisateurs.json",
            "PROFILS_DIR": self.root / "profils", "EXERCICES_PATH": exercices,
        })
        self.client = self.app.test_client()

    def csrf(self, client):
        with client.session_transaction() as session:
            return session["csrf"]

    def compte(self, client, nom="alice", route="/inscription", password="mon secret"):
        client.get(route)
        return client.post(route, data={"csrf": self.csrf(client), "identifiant": nom,
                                       "mot_de_passe": password})

    def quitter(self, client):
        return client.post("/deconnexion", data={"csrf": self.csrf(client)})

    def test_protection(self):
        for route in ("/", "/classique"):
            for method in (self.client.get, self.client.post):
                response = method(route)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.location.endswith("/connexion"))

    def test_inscription_hachage_connexion_et_deconnexion(self):
        self.assertEqual(self.compte(self.client, "Alice").status_code, 302)
        comptes = json.loads((self.root / "utilisateurs.json").read_text())
        self.assertNotIn("mon secret", json.dumps(comptes))
        self.assertTrue(check_password_hash(comptes["alice"]["mot_de_passe"], "mon secret"))
        self.assertEqual(Profil.charger(self.root / "profils/alice.json").nom, "alice")
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.post("/deconnexion", data={"csrf": "faux"}).status_code, 400)
        self.assertEqual(self.quitter(self.client).status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("utilisateur", session)
            self.assertNotIn("conversation", session)
        self.assertEqual(self.compte(self.client, route="/connexion", password="faux").status_code, 401)
        self.assertEqual(self.compte(self.client, route="/connexion").status_code, 302)
        self.assertEqual(self.client.get("/classique").status_code, 200)

    def test_validation_et_doublons(self):
        self.client.get("/inscription")
        self.assertEqual(self.client.post("/inscription", data={"identifiant": "alice", "mot_de_passe": "secret"}).status_code, 400)
        for nom in ("../alice", "a/b", "a\\b", "CON", "LPT1", "", "a" * 65):
            self.assertEqual(self.compte(self.client, nom).status_code, 400)
        self.assertFalse((self.root / "utilisateurs.json").exists())
        self.assertEqual(self.compte(self.client, password="").status_code, 400)
        self.compte(self.client)
        avant = (self.root / "profils/alice.json").read_bytes()
        self.quitter(self.client)
        self.assertEqual(self.compte(self.client, "ALICE").status_code, 409)
        self.assertEqual((self.root / "profils/alice.json").read_bytes(), avant)

    @patch.dict("os.environ", {"PIPELEX_API_KEY": "test"})
    @patch("app.web.corriger", new_callable=AsyncMock)
    def test_profils_isoles_et_reconnexion(self, corriger):
        corriger.return_value = {"verdict": "correcte", "type_erreur": "aucune", "explication": "2"}
        self.compte(self.client)
        autre = self.app.test_client()
        self.compte(autre, "bob")
        self.client.post("/classique", data={"csrf": self.csrf(self.client), "chapitre": "Analyse",
                                            "exercice_id": "a", "reponse": "2"})
        self.assertEqual(len(Profil.charger(self.root / "profils/alice.json").historique), 1)
        self.assertEqual(Profil.charger(self.root / "profils/bob.json").historique, [])
        self.assertIn(b"Exercice a", autre.get("/classique").data)
        self.quitter(self.client)
        self.compte(self.client, route="/connexion")
        self.assertNotIn(b"Exercice a", self.client.get("/classique").data)


if __name__ == "__main__":
    unittest.main()
