"""Parcours HTTP de reprise : isolement, reprise après panne et doubles clics."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from app.agent import Agent
from app.profil import Profil
from app.test_revision import CATALOGUE, installer_bilan
from app.web import create_app


class RevisionWebTests(unittest.TestCase):
    def setUp(self):
        dossier = TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.root = Path(dossier.name)
        exercices = self.root / "exercices.json"
        exercices.write_text(json.dumps(CATALOGUE))
        self.config = {"TESTING": True, "SECRET_KEY": "test-revision", "EXERCICES_PATH": exercices,
                       "UTILISATEURS_PATH": self.root / "users.json", "PROFILS_DIR": self.root / "profils"}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.inscrire(self.client, "alice")
        self.path = self.root / "profils/alice.json"
        self.bilan = installer_bilan(self.path)
        self.url = "/bilans/ancienne/retravailler"
        env = patch.dict(os.environ, {"OPENAI_API_KEY": "test", "PIPELEX_API_KEY": "test"})
        env.start()
        self.addCleanup(env.stop)
        verification = patch("app.revision.verifier_enonce", new_callable=AsyncMock)
        self.verifier = verification.start()
        self.addCleanup(verification.stop)
        self.verifier.side_effect = lambda enonce, corrige, client: enonce

    def inscrire(self, client, nom):
        client.get("/inscription")
        with client.session_transaction() as session:
            csrf = session["csrf"]
        client.post("/inscription", data={"csrf": csrf, "identifiant": nom, "mot_de_passe": "test"})

    def formulaire(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)
        with self.client.session_transaction() as session:
            return {"csrf": session["csrf"], "jeton": session["jeton_reprise"],
                    "tache_id": "erreur", "reflexion": "Je vérifierai les signes."}

    def test_bouton_formulaire_et_demarrage_sans_corrige_expose(self):
        page = self.client.get("/bilans/ancienne").get_data(as_text=True)
        self.assertIn("Retravailler mes erreurs", page)
        avant = self.path.read_bytes()
        donnees = self.formulaire()
        self.assertEqual(self.path.read_bytes(), avant)
        self.verifier.assert_not_awaited()
        response = self.client.post(self.url, data=donnees, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("Reprise ciblée de votre erreur", page)
        self.assertIn(CATALOGUE[1]["enonce"], page)
        self.assertNotIn("REFERENCE_PRIVEE", page)
        self.assertEqual(Profil.charger(self.path).bilans["ancienne"], self.bilan)

    def test_csrf_jeton_texte_et_identifiant_invalides_ne_creent_rien(self):
        data = self.formulaire()
        avant = self.path.read_bytes()
        for changement, code in (({"csrf": "x"}, 400), ({"jeton": "x"}, 409),
                                 ({"reflexion": " "}, 400), ({"reflexion": "x" * 2001}, 400),
                                 ({"tache_id": "ailleurs"}, 404)):
            with self.subTest(changement=changement):
                self.assertEqual(self.client.post(self.url, data={**data, **changement}).status_code, code)
        self.assertEqual(self.path.read_bytes(), avant)
        self.verifier.assert_not_awaited()

    def test_double_clic_et_reflexion_html(self):
        data = {**self.formulaire(), "reflexion": "<script>attaque</script>"}
        premiere = self.client.post(self.url, data=data)
        seconde = self.client.post(self.url, data=data)
        self.assertEqual(premiere.location, seconde.location)
        self.verifier.assert_awaited_once()
        self.assertEqual(len(Profil.charger(self.path).taches), 2)
        page = self.client.get("/").get_data(as_text=True)
        self.assertIn("&lt;script&gt;attaque&lt;/script&gt;", page)
        self.assertNotIn("<script>attaque</script>", page)

    def test_autre_compte_et_visiteur_ne_peuvent_lancer_reprise(self):
        autre = self.app.test_client()
        self.inscrire(autre, "bob")
        self.assertEqual(autre.get(self.url).status_code, 404)
        self.assertEqual(autre.post(self.url, data=self.formulaire()).status_code, 404)
        self.assertEqual(self.app.test_client().get(self.url).status_code, 302)
        self.verifier.assert_not_awaited()

    def test_cle_absente_et_panne_conservent_reflexion_et_profil(self):
        data = self.formulaire()
        avant = self.path.read_bytes()
        with patch.dict(os.environ, {"PIPELEX_API_KEY": ""}):
            self.assertEqual(self.client.post(self.url, data=data).status_code, 503)
        self.verifier.side_effect = RuntimeError("indisponible")
        with self.assertLogs(self.app.logger, level="ERROR"):
            response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 503)
        self.assertIn(data["reflexion"], response.get_data(as_text=True))
        self.assertEqual(self.path.read_bytes(), avant)
        self.verifier.side_effect = lambda enonce, corrige, client: enonce
        self.assertEqual(self.client.post(self.url, data=data).status_code, 302)

    def test_une_seance_active_ne_peut_etre_ecrasee(self):
        self.client.get("/")
        with self.client.session_transaction() as session:
            tokens = {k: session[k] for k in ("csrf", "tour")}
        with patch.object(Agent, "repondre", new_callable=AsyncMock):
            self.client.post("/", data={**tokens, "action": "chapitre", "chapitre": "0"})
        response = self.client.post(self.url, data=self.formulaire())
        self.assertEqual(response.status_code, 409)
        self.assertIn("Terminez la séance", response.get_data(as_text=True))
        self.verifier.assert_not_awaited()

    def test_validation_et_nouveau_bilan_retrouves_apres_redemarrage(self):
        self.client.post(self.url, data=self.formulaire())
        self.client.get("/")
        with self.client.session_transaction() as session:
            tokens = {k: session[k] for k in ("csrf", "tour")}
        with patch.object(Agent, "evaluer_reponse", new=AsyncMock(return_value={
                "verdict": "correcte", "type_erreur": "aucune", "explication": "Preuve vérifiée"})):
            resultat = self.client.post("/", data={**tokens, "message": "Ma preuve complète"}, follow_redirects=True)
        self.assertIn("Cette reprise est validée", resultat.get_data(as_text=True))
        self.assertNotIn('id="chat-form"', resultat.get_data(as_text=True))
        with self.client.session_transaction() as session:
            tokens = {k: session[k] for k in ("csrf", "tour")}
        self.assertEqual(self.client.post("/", data={**tokens, "message": "Encore"}).status_code, 409)
        resultat = self.client.post("/", data={**tokens, "action": "terminer"})
        nouveau_bilan = resultat.location
        autre_app = create_app(self.config).test_client()
        autre_app.get("/connexion")
        with autre_app.session_transaction() as session:
            csrf = session["csrf"]
        autre_app.post("/connexion", data={"csrf": csrf, "identifiant": "alice", "mot_de_passe": "test"})
        page = autre_app.get("/bilans/ancienne").get_data(as_text=True)
        self.assertIn("Dernière reprise validée", page)
        self.assertIn(nouveau_bilan, page)
        self.assertIn("Preuve vérifiée", autre_app.get(nouveau_bilan).get_data(as_text=True))

    def test_un_point_valide_ne_propose_pas_reprise(self):
        profil = Profil.charger(self.path)
        profil.bilans["ancienne"]["points"][0].update(statut="valide", verdict="correcte")
        profil.bilans["ancienne"]["compteurs"].update(valide=1, a_retravailler=0)
        profil.sauvegarder(self.path)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertNotIn("Retravailler mes erreurs", self.client.get("/bilans/ancienne").get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
