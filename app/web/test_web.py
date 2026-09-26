"""Tests hors ligne : python -m unittest app.web.test_web."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.profil import Profil
from app.web import create_app


class WebTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.profile = root / "profils" / "test.json"
        exercises = root / "exercices.json"
        exercises.write_text(json.dumps([
            {"id": "a", "chapitre": "Analyse", "difficulte": 1,
             "enonce": "Calculer $1+1$. <script>alert(1)</script>", "corrige": "SECRET_CORRIGE"},
            {"id": "b", "chapitre": "Analyse", "difficulte": 3, "enonce": "Calculer $2+2$."},
        ]), encoding="utf-8")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test",
                               "PROFILS_DIR": root / "profils", "UTILISATEURS_PATH": root / "utilisateurs.json", "EXERCICES_PATH": exercises})
        self.client = self.app.test_client()
        self.client.get("/inscription")
        with self.client.session_transaction() as session:
            csrf = session["csrf"]
        self.client.post("/inscription", data={"csrf": csrf, "identifiant": "test", "mot_de_passe": "secret"})
        self.client.get("/classique")
        with self.client.session_transaction() as session:
            self.csrf = session["csrf"]
        key = patch.dict(os.environ, {"PIPELEX_API_KEY": "test-only"})
        key.start()
        self.addCleanup(key.stop)

    def submit(self, **values):
        data = {"csrf": self.csrf, "chapitre": "Analyse", "exercice_id": "a", "reponse": "2"}
        data.update(values)
        return self.client.post("/classique", data=data)

    def test_page_escapes_content_and_hides_solution(self):
        response = self.client.get("/classique")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"&lt;script&gt;", response.data)
        self.assertNotIn(b"SECRET_CORRIGE", response.data)
        self.assertIn(b"katex", response.data)
        self.assertIn(b"1,5", response.data)
        with self.client.get("/static/app.js") as asset:
            self.assertEqual(asset.status_code, 200)

    @patch("app.web.corriger", new_callable=AsyncMock)
    def test_correction_persists_once_and_selects_next(self, correct):
        correct.return_value = {"verdict": "correcte", "type_erreur": "aucune", "explication": "$1+1=2$"}
        response = self.submit()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"1,8", response.data)
        correct.assert_awaited_once_with("Calculer $1+1$. <script>alert(1)</script>", "2", "SECRET_CORRIGE")
        self.assertAlmostEqual(Profil.charger(self.profile).niveau("Analyse"), 1.8)
        self.assertEqual(self.submit().status_code, 409)
        self.assertEqual(correct.await_count, 1)
        self.assertIn(b"Exercice b", self.client.get("/classique").data)

    @patch("app.web.corriger", new_callable=AsyncMock)
    def test_failure_preserves_answer_and_profile(self, correct):
        correct.side_effect = RuntimeError("Unavailable")
        with self.assertLogs(self.app.logger, level="ERROR"):
            response = self.submit(reponse="Mon raisonnement")
        self.assertEqual(response.status_code, 502)
        self.assertIn(b"Mon raisonnement", response.data)
        self.assertEqual(Profil.charger(self.profile).historique, [])

    @patch("app.web.corriger", new_callable=AsyncMock)
    def test_invalid_requests_never_call_pipelex(self, correct):
        for values in ({"csrf": "bad"}, {"chapitre": "Inconnu"}, {"reponse": "x" * 12001}):
            self.assertEqual(self.submit(**values).status_code, 400)
        with patch.dict(os.environ, {"PIPELEX_API_KEY": ""}):
            self.assertEqual(self.submit().status_code, 503)
        correct.assert_not_awaited()

    def test_exhausted_chapter(self):
        profil = Profil("test")
        profil.exercices_vus = ["a", "b"]
        profil.sauvegarder(self.profile)
        response = self.client.get("/classique")
        self.assertIn("Chapitre terminé".encode(), response.data)
        self.assertNotIn(b"<textarea", response.data)

    @patch("app.web.PipelexAPIClient")
    def test_real_adapter_rejects_invalid_result(self, client_class):
        client = AsyncMock()
        client_class.return_value.__aenter__.return_value = client
        client.start_and_wait.return_value.main_stuff = {"verdict": "invalide"}
        with self.assertLogs(self.app.logger, level="ERROR"):
            response = self.submit()
        self.assertEqual(response.status_code, 502)
        self.assertEqual(Profil.charger(self.profile).historique, [])
        self.assertEqual(client.start_and_wait.call_args.kwargs["pipe_code"],
                         "evaluation_maths_prepa.evaluer_reponse")


if __name__ == "__main__":
    unittest.main()
