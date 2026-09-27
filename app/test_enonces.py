"""Tests du vérificateur privé, sans appel payant."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
from openai import APIConnectionError, AsyncOpenAI

from app.enonces import CacheEnonces, verifier_enonce, verifier_exercice


class EnoncesTests(unittest.IsolatedAsyncioTestCase):
    def client(self, contenu, status="completed"):
        return SimpleNamespace(responses=SimpleNamespace(create=AsyncMock(
            return_value=SimpleNamespace(output_text=contenu, status=status))))

    async def test_reconstruction_avec_sdk_et_transport_simule(self):
        propre = r"Étudier $u_{n+1}=\frac{e^{-u_n}}{n+1}$."
        requetes = []

        def transport(requete):
            corps = json.loads(requete.content)
            requetes.append(corps)
            self.assertEqual(json.loads(corps["input"][0]["content"]),
                             {"enonce": "un+1 =\n1\nn + 1e−un", "corrige": "SECRET_CORRIGE"})
            self.assertTrue(corps["text"]["format"]["strict"])
            self.assertEqual(corps["text"]["format"]["type"], "json_schema")
            self.assertFalse(corps["store"])
            self.assertNotIn("tools", corps)
            return httpx.Response(200, json={
                "id": "r1", "object": "response", "created_at": 0,
                "status": "completed", "model": corps["model"],
                "output": [{"type": "message", "id": "m1", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "annotations": [], "text": json.dumps(
                                {"exploitable": True, "enonce": propre, "corrige": "Corrigé propre"})}]}]})

        async with AsyncOpenAI(api_key="test", http_client=httpx.AsyncClient(
                transport=httpx.MockTransport(transport))) as client:
            self.assertEqual(await verifier_enonce("un+1 =\n1\nn + 1e−un", "SECRET_CORRIGE", client), propre)
        self.assertEqual(len(requetes), 1)

    async def test_ambiguite_retourne_none(self):
        client = self.client('{"exploitable": false, "enonce": "", "corrige": ""}')
        self.assertIsNone(await verifier_enonce("X\nun", "Corrigé ambigu", client))

    async def test_absence_source_ne_declenche_pas_api(self):
        for enonce, corrige in (("", "corrigé"), ("énoncé", ""), ("énoncé", None)):
            client = self.client("")
            self.assertIsNone(await verifier_enonce(enonce, corrige, client))
            client.responses.create.assert_not_awaited()

    async def test_sorties_invalides_ne_sont_pas_des_rejets_pedagogiques(self):
        for contenu in ("", "pas du JSON", "[]", '{"exploitable": "true", "enonce": "x", "corrige": "y"}',
                        '{"exploitable": true, "enonce": "x"}',
                        '{"exploitable": true, "enonce": " ", "corrige": "y"}',
                        '{"exploitable": true, "enonce": "x", "corrige": ""}',
                        '{"exploitable": false, "enonce": "x", "corrige": ""}'):
            with self.subTest(contenu=contenu), self.assertRaises(ValueError):
                await verifier_enonce("énoncé", "corrigé", self.client(contenu))
        with self.assertRaises(ValueError):
            await verifier_enonce("énoncé", "corrigé", self.client(
                '{"exploitable": true, "enonce": "x", "corrige": "y"}', status="incomplete"))

    async def test_panne_reseau_ne_retourne_pas_un_enonce_non_verifie(self):
        client = self.client("")
        client.responses.create.side_effect = APIConnectionError(request=httpx.Request("POST", "https://example.test"))
        with self.assertRaisesRegex(ValueError, "temporairement indisponible"):
            await verifier_enonce("énoncé", "corrigé", client)

    async def test_cache_une_seule_verification_par_exercice(self):
        with tempfile.TemporaryDirectory() as dossier:
            cache = CacheEnonces(Path(dossier) / "cache.json")
            exercice = {"id": "17.1", "enonce": "X\nun", "corrige": "corrigé"}
            client = self.client(json.dumps({"exploitable": True, "enonce": r"$\sum u_n$", "corrige": "Propre"}))
            attendu = {"enonce": r"$\sum u_n$", "corrige": "Propre"}
            self.assertEqual(await cache.exercice_verifie(exercice, client), attendu)
            self.assertEqual(await CacheEnonces(cache.chemin).exercice_verifie(exercice, client), attendu)
            client.responses.create.assert_awaited_once()
            # Un exercice ambigu reste écarté sans nouvel appel.
            rejete = {"id": "17.2", "enonce": "X", "corrige": "c"}
            refus = self.client('{"exploitable": false, "enonce": "", "corrige": ""}')
            self.assertIsNone(await cache.exercice_verifie(rejete, refus))
            self.assertEqual(cache.lire(rejete), (True, None))
            # Un texte modifié invalide l'entrée.
            self.assertEqual(cache.lire({**exercice, "enonce": "autre"}), (False, None))

    async def test_panne_non_mise_en_cache(self):
        with tempfile.TemporaryDirectory() as dossier:
            cache = CacheEnonces(Path(dossier) / "cache.json")
            client = self.client("")
            client.responses.create.side_effect = APIConnectionError(request=httpx.Request("POST", "https://example.test"))
            with self.assertRaises(ValueError):
                await cache.exercice_verifie({"id": "a", "enonce": "e", "corrige": "c"}, client)
            self.assertFalse(cache.chemin.exists())

    async def test_verifier_exercice_renvoie_enonce_et_corrige(self):
        client = self.client('{"exploitable": true, "enonce": "E", "corrige": "C"}')
        self.assertEqual(await verifier_exercice("e", "c", client), {"enonce": "E", "corrige": "C"})
