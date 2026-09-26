"""Tests HTTP du chat, sans services externes."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.web import create_app
from app.profil import Profil


class ChatTests(unittest.TestCase):
    def setUp(self):
        repertoire = tempfile.TemporaryDirectory()
        self.addCleanup(repertoire.cleanup)
        root = Path(repertoire.name)
        exercices = root / "exercices.json"
        exercices.write_text(json.dumps([]), encoding="utf-8")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test",
                               "PROFILS_DIR": root / "profils", "UTILISATEURS_PATH": root / "utilisateurs.json", "EXERCICES_PATH": exercices})
        self.client = self.app.test_client()
        self.client.get("/inscription")
        with self.client.session_transaction() as session:
            csrf = session["csrf"]
        self.client.post("/inscription", data={"csrf": csrf, "identifiant": "test", "mot_de_passe": "secret"})
        self.client.get("/")
        with self.client.session_transaction() as session:
            self.tokens = {cle: session[cle] for cle in ("csrf", "tour")}

    def envoyer(self, **valeurs):
        return self.client.post("/", data={**self.tokens, "message": "Bonjour", **valeurs})

    def test_accueil_et_ancienne_interface(self):
        self.assertIn(b'/classique', self.client.get("/").data)
        self.assertEqual(self.client.get("/classique").status_code, 200)

    @patch("app.agent.Agent.repondre", autospec=True)
    def test_validation_avant_api(self, repondre):
        for valeurs in ({"csrf": "faux"}, {"message": " "}, {"message": "x" * 12001}):
            self.assertEqual(self.envoyer(**valeurs).status_code, 400)
        self.assertEqual(self.envoyer(tour="ancien").status_code, 409)
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            self.assertEqual(self.envoyer().status_code, 503)
        repondre.assert_not_called()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"})
    @patch("app.agent.Agent.repondre", autospec=True)
    def test_dialogue_isole_echappement_et_nouvelle_discussion(self, repondre):
        async def parler(agent, message):
            agent.messages.extend([{"role": "user", "content": message},
                                   {"role": "assistant", "content": "<script>secret</script>"}])
        repondre.side_effect = parler
        ancien_cookie = self.client.get_cookie("session").value
        self.assertEqual(self.envoyer().status_code, 302)
        page = self.client.get("/")
        self.assertIn(b"&lt;script&gt;secret", page.data)
        self.assertNotIn(b"<script>secret", page.data)
        self.assertEqual(self.envoyer().status_code, 409)
        # Même une requête concurrente avec l'ancien cookie doit être refusée.
        self.client.set_cookie("session", ancien_cookie)
        self.assertEqual(self.envoyer().status_code, 409)
        self.assertEqual(repondre.call_count, 1)
        with self.app.test_client() as autre:
            self.assertNotIn(b"secret", autre.get("/").data)
        with self.client.session_transaction() as session:
            self.tokens["tour"] = session["tour"]
        self.assertEqual(self.envoyer(action="nouvelle").status_code, 302)
        self.assertNotIn(b"secret", self.client.get("/").data)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"})
    @patch("app.agent.Agent.repondre", autospec=True)
    def test_echec_conserve_brouillon(self, repondre):
        repondre.side_effect = RuntimeError("réseau")
        with self.assertLogs(self.app.logger, level="ERROR"):
            page = self.envoyer(message="Mon raisonnement")
        self.assertEqual(page.status_code, 502)
        self.assertIn(b"Mon raisonnement", page.data)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "PIPELEX_API_KEY": "test"})
    @patch("app.agent.Agent.repondre", autospec=True)
    @patch("app.agent.PipelexAPIClient")
    def test_bouton_corrige_dernier_message_et_persiste(self, classe, repondre):
        async def parler(agent, message):
            agent.exercice = {"id": "a", "chapitre": "Analyse", "enonce": "Calculer 1+1.",
                              "corrige": "La somme 1+1 vaut 2."}
            agent.chapitres = ["Analyse"]
            agent.derniere_reponse = message
            agent.messages.append({"role": "user", "content": message})
        repondre.side_effect = parler
        pipelex = AsyncMock()
        classe.return_value.__aenter__.return_value = pipelex
        pipelex.start_and_wait.return_value.main_stuff = {
            "verdict": "correcte", "type_erreur": "aucune", "explication": "La somme vaut 2."}
        self.assertEqual(self.envoyer(action="corriger").status_code, 400)
        self.assertEqual(self.envoyer(message="2").status_code, 302)
        with self.client.session_transaction() as session:
            self.tokens["tour"] = session["tour"]
        self.assertIn('Corriger ma réponse'.encode(), self.client.get("/").data)
        self.assertEqual(self.envoyer(action="corriger", csrf="faux").status_code, 400)
        with patch.dict(os.environ, {"PIPELEX_API_KEY": ""}):
            self.assertEqual(self.envoyer(action="corriger").status_code, 503)
        pipelex.start_and_wait.side_effect = RuntimeError("réseau")
        with self.assertLogs(self.app.logger, level="ERROR"):
            self.assertEqual(self.envoyer(action="corriger").status_code, 502)
        self.assertEqual(Profil.charger(self.app.config["PROFILS_DIR"] / "test.json").historique, [])
        pipelex.start_and_wait.side_effect = None
        # La correction ne dépend pas du modèle de conversation ni du texte du formulaire.
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            self.assertEqual(self.envoyer(action="corriger", message="texte falsifié").status_code, 302)
        self.assertEqual(pipelex.start_and_wait.call_args.kwargs["inputs"]["reponse_eleve"], "2")
        page = self.client.get("/").data
        self.assertIn(b"Verdict : correcte", page)
        self.assertIn(b"La somme vaut 2.", page)
        self.assertIn(b"1,8/5", page)
        self.assertEqual(self.envoyer(action="corriger").status_code, 409)
        with self.client.session_transaction() as session:
            self.tokens["tour"] = session["tour"]
        self.assertEqual(self.envoyer(action="corriger").status_code, 400)
        self.assertEqual(len(Profil.charger(self.app.config["PROFILS_DIR"] / "test.json").historique), 1)


if __name__ == "__main__":
    unittest.main()
