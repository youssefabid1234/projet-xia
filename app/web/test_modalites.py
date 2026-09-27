"""Contrats HTTP des conversions : aucun tour, score ni profil implicite."""

import io
import os
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from PIL import Image

from app.modalites import Convertisseur, MAX_AUDIO, MAX_IMAGE, audio_valide, texte_oral
from app.web import test_chat


def png():
    sortie = io.BytesIO()
    Image.new("RGB", (80, 40), "white").save(sortie, "PNG")
    return sortie.getvalue()


def wav(secondes=1, frequence=24000):
    sortie = io.BytesIO()
    with wave.open(sortie, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(frequence)
        audio.writeframes(b"\0\0" * int(secondes * frequence))
    return sortie.getvalue()


class FauxConvertisseur:
    def __init__(self):
        self.manuscrit = AsyncMock(return_value=r"$x^2 = 3$ : ma réponse")
        self.dictee = AsyncMock(return_value="x carré égale trois")
        self.lecture = AsyncMock(return_value=wav())

    def disponibilites(self):
        return {"manuscrit": True, "dictee": True, "lecture": True}


@patch.dict(os.environ, {"OPENAI_API_KEY": "test", "COLLE_EVALUATEUR": "local"})
class ModalitesTests(unittest.TestCase):
    # Réutiliser le montage d'une vraie application, pas sa suite de tests.
    creer_app = test_chat.ChatTests.creer_app
    csrf = test_chat.ChatTests.csrf
    api = test_chat.ChatTests.api
    demarrer = test_chat.ChatTests.demarrer
    flux = test_chat.ChatTests.flux

    def setUp(self):
        test_chat.ChatTests.setUp(self)
        self.conversions = FauxConvertisseur()
        self.app.config["CONVERTISSEUR"] = self.conversions
        self.demarrer()

    def media(self, mode="manuscrit", data=None, type="image/png", **kwargs):
        return self.client.post("/api/modalites/" + mode, data=png() if data is None else data,
                                content_type=type, headers={"X-CSRF-Token": self.csrf()}, **kwargs)

    def etat(self):
        return self.client.get("/api/etat").get_json()

    def fichiers(self):
        return {str(p): p.read_bytes() for p in (self.root / "profils").glob("*.json")}

    def test_conversions_sans_effet_et_soumission_textuelle_unique(self):
        avant, fichiers = self.etat(), self.fichiers()
        for mode, data, type in [("manuscrit", png(), "image/png"), ("dictee", wav(), "audio/wav")]:
            resultat = self.media(mode, data, type)
            self.assertEqual(resultat.status_code, 200, resultat.data)
            self.assertEqual(set(resultat.json), {"texte"})
            self.assertEqual(resultat.headers["Cache-Control"], "no-store")
        self.assertEqual(self.fichiers(), fichiers)
        self.assertEqual(self.etat()["messages"], avant["messages"])
        self.assertFalse(self.openai.appels)
        self.openai.intentions = ["reponse"]
        self.openai.evaluations = [test_chat.CORRECT]
        self.openai.textes = ["Réponse reçue."]
        texte = self.conversions.dictee.return_value
        self.flux(self.api("/api/message", {"message": texte}))
        eleve = [m for m in self.etat()["messages"] if m["role"] == "eleve"]
        self.assertEqual([m["texte"] for m in eleve], [texte])

    def test_auth_csrf_formats_et_limites_independantes(self):
        anonyme = self.app.test_client()
        for route in ("", "/manuscrit", "/dictee", "/lecture"):
            self.assertEqual(anonyme.get("/api/modalites" + route).status_code, 401)
        for route in ("manuscrit", "dictee", "lecture"):
            self.assertEqual(self.client.post("/api/modalites/" + route, json={}).status_code, 400)
        self.assertEqual(self.media(data=b"not PNG").status_code, 400)
        self.assertEqual(self.media(type="image/svg+xml").status_code, 400)
        self.assertEqual(self.media(data=b"x" * (MAX_IMAGE + 1)).status_code, 413)
        self.assertEqual(self.media("dictee", b"x" * (MAX_AUDIO + 1), "audio/wav").status_code, 413)
        self.assertEqual(self.api("/api/message", {"message": "x" * 66000}).status_code, 413)
        # Les médias valides > 64 Kio passent, sans modifier la limite globale.
        self.assertEqual(self.media("dictee", wav(2), "audio/wav").status_code, 200)
        self.assertEqual(self.app.config["MAX_CONTENT_LENGTH"], 65536)
        for data in (b"", b"not WAV", wav(121), wav(1, 48000), wav()[:-4]):
            self.assertEqual(self.media("dictee", data, "audio/wav").status_code, 400)

    def test_lecture_liste_blanche_sans_corrige_ni_bilan(self):
        question = self.etat()["etat"]["tache"]["question_active"]
        fichiers = self.fichiers()
        for corps in ({"question": "corrigé secret"}, {"question": "étape future"},
                      {"question": question, "texte": "corrigé"}, [question], {}):
            self.assertEqual(self.api("/api/modalites/lecture", corps).status_code, 400)
        reponse = self.api("/api/modalites/lecture", {"question": question})
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.mimetype, "audio/wav")
        self.conversions.lecture.assert_awaited_once_with(question)
        self.assertEqual(self.fichiers(), fichiers)
        self.flux(self.api("/api/bilan"))
        self.assertEqual(self.api("/api/modalites/lecture", {"question": question}).status_code, 400)

    def test_indisponibilite_erreur_et_resultats_invalides(self):
        with patch.object(self.conversions, "disponibilites", return_value={"manuscrit": False}):
            self.assertEqual(self.media().status_code, 503)
        self.conversions.manuscrit.side_effect = RuntimeError("secret fournisseur")
        resultat = self.media()
        self.assertEqual(resultat.status_code, 502)
        self.assertNotIn(b"secret fournisseur", resultat.data)
        self.conversions.manuscrit.side_effect = None
        for texte in ("", "x" * 6001, None):
            self.conversions.manuscrit.return_value = texte
            self.assertEqual(self.media().status_code, 422)
        self.conversions.manuscrit.return_value = "reprise"
        self.assertEqual(self.media().json, {"texte": "reprise"})

    def test_image_dimensions_et_erreurs_fournisseur_privees(self):
        sortie = io.BytesIO()
        Image.new("RGB", (2001, 2000), "white").save(sortie, "PNG")
        self.assertEqual(self.media(data=sortie.getvalue()).status_code, 400)
        self.conversions.manuscrit.assert_not_awaited()
        self.conversions.manuscrit.side_effect = ValueError("secret fournisseur")
        reponse = self.media()
        self.assertEqual(reponse.status_code, 502)
        self.assertNotIn(b"secret fournisseur", reponse.data)

    def test_conversions_concurrentes_et_isolation_eleves(self):
        import threading
        entre, sortir = threading.Event(), threading.Event()
        async def attendre(_):
            entre.set()
            self.assertTrue(sortir.wait(5))
            return "transcription"
        self.conversions.manuscrit.side_effect = attendre
        autre = self.app.test_client()
        with autre.session_transaction() as s:
            s.update(utilisateur="test", csrf=self.csrf())
        resultats = []
        fil = threading.Thread(target=lambda: resultats.append(autre.post(
            "/api/modalites/manuscrit", data=png(), content_type="image/png",
            headers={"X-CSRF-Token": self.csrf(autre)})))
        fil.start()
        try:
            self.assertTrue(entre.wait(3))
            self.assertEqual(self.media().status_code, 409)
            # Un autre compte n'a ni accès au tableau, ni accès à la colle de test.
            autre_eleve = self.app.test_client()
            autre_eleve.get("/inscription")
            autre_eleve.post("/inscription", data={"csrf": self.csrf(autre_eleve),
                             "identifiant": "autre", "mot_de_passe": "secret"})
            r = autre_eleve.post("/api/modalites/manuscrit", data=png(), content_type="image/png",
                                headers={"X-CSRF-Token": self.csrf(autre_eleve)})
            self.assertEqual(r.status_code, 400)
        finally:
            sortir.set()
            fil.join(5)
        self.assertFalse(fil.is_alive())
        self.assertEqual(resultats[0].status_code, 200)

    def test_expiration_et_changement_pendant_conversion(self):
        from app.web.modalites import creer_modalites
        from flask import Flask
        etat = {"debut": 1, "etape": "cours", "resultats": [], "terminee": False,
                "temps_restant": 10, "tache": {"question_active": "Q"}}
        app = Flask(__name__)
        app.config.update(TESTING=True, SECRET_KEY="test", CONVERTISSEUR=self.conversions)
        app.register_blueprint(creer_modalites(lambda: etat.copy()))
        client = app.test_client()
        with client.session_transaction() as s:
            s.update(utilisateur="test", csrf="jeton")
        async def modifier(_):
            etat["tache"] = {"question_active": "Q suivante"}
            return "ancien texte"
        self.conversions.manuscrit.side_effect = modifier
        r = client.post("/api/modalites/manuscrit", data=png(), content_type="image/png",
                        headers={"X-CSRF-Token": "jeton"})
        self.assertEqual(r.status_code, 409)
        etat["temps_restant"] = 0
        r = client.post("/api/modalites/dictee", data=wav(), content_type="audio/wav",
                        headers={"X-CSRF-Token": "jeton"})
        self.assertEqual(r.status_code, 400)
        self.conversions.dictee.assert_not_awaited()


class AdaptateursTests(unittest.IsolatedAsyncioTestCase):
    async def test_gradium_separe_stt_tts(self):
        pcm = audio_valide(wav())
        with patch.dict(os.environ, {"GRADIUM_API_KEY": "test", "KHOLLEUR_VOICE_ID": "voix-test"}), \
             patch("gradium.speech.stt", new_callable=AsyncMock, return_value=SimpleNamespace(text="ma réponse")) as stt, \
             patch("gradium.speech.tts", new_callable=AsyncMock, return_value=SimpleNamespace(raw_data=b"wav")) as tts:
            c = Convertisseur()
            self.assertEqual(await c.dictee(pcm), "ma réponse")
            self.assertEqual(await c.lecture("$x^2 = 3$"), b"wav")
            self.assertEqual(stt.await_args.args[2], pcm)
            self.assertEqual(stt.await_args.args[1]["input_format"], "pcm")
            self.assertEqual(tts.await_args.args[1]["voice_id"], "voix-test")
            self.assertEqual(tts.await_args.args[2], "x au carré égale 3")

    def test_formules_non_modifiees(self):
        source = r"$\frac{x}{2}+\sqrt{y}=z^3$"
        self.assertEqual(texte_oral(source), "(x) sur (2) plus racine carrée de (y) égale z au cube")
        self.assertEqual(source, r"$\frac{x}{2}+\sqrt{y}=z^3$")

    async def test_vision_sans_reference_ni_verification(self):
        reponse = SimpleNamespace(output_text='{"texte":"$1+1=3$"}')
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.responses.create.return_value = reponse
        with patch("openai.AsyncOpenAI", return_value=client):
            self.assertEqual(await Convertisseur().manuscrit(png()), "$1+1=3$")
        parametres = client.responses.create.await_args.kwargs
        self.assertFalse(parametres["store"])
        self.assertNotIn("tools", parametres)
        self.assertEqual(len(parametres["input"]), 1)


if __name__ == "__main__":
    unittest.main()
