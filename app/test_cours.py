"""Recherche et erreurs vérifiées hors ligne, sans consommation API."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from app.cours import chercher_dans_cours, scores_lexicaux


class CourseSearchTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "index.json"
        self.index = {"statut": "indexe", "dimensions": 2, "modele_embedding": "text-embedding-3-small",
                      "chapitre": "Séries numériques", "passages": [
                          {"identifiant": str(i), "titre": "Passage", "type": "définition", "texte": "Texte",
                           "page_source": {"pdf": [139 + i]}, "embedding": vector}
                          for i, vector in enumerate([[1., 1.], [0., 1.], [20., 0.], [-1., 0.], [1., 2.], [1., -1.]])]}
        self.path.write_text(json.dumps(self.index), encoding="utf-8")
        self.client = SimpleNamespace(embeddings=SimpleNamespace(create=AsyncMock(
            return_value=SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[1., 0.])]))))

    async def test_cosine_ranking_model_and_sources(self):
        result = await chercher_dans_cours("Définition ?", self.client, chemin=self.path)
        self.assertEqual(len(result["passages"]), 5)
        self.assertEqual(result["passages"][0]["identifiant"], "2")
        self.assertAlmostEqual(result["passages"][0]["score"], 1.)
        self.assertEqual(result["passages"][0]["page_source"], {"pdf": [141]})
        self.assertNotIn("embedding", result["passages"][0])
        self.client.embeddings.create.assert_awaited_once_with(
            model="text-embedding-3-small", input=["Définition ?"], dimensions=2, encoding_format="float")

    def test_rare_term_and_accents_retrieve_definition_inside_passage(self):
        passages = [
            {"titre": "Définition (Convergence)", "texte": "Le reste d'une série convergente est la somme moins la somme partielle."},
            {"titre": "Définition (Série)", "texte": "Suite des sommes partielles d'une série."},
            {"titre": "Séries géométriques", "texte": "Une série de raison a."},
        ]
        scores = scores_lexicaux("definition du reste d'une serie", passages)
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[0], scores[2])
        self.assertEqual(scores_lexicaux("série géométrique", passages).index(1.), 2)

    async def test_bad_question_or_missing_index_before_network(self):
        for question in ("", "   ", None, "x" * 2001):
            with self.assertRaises(ValueError):
                await chercher_dans_cours(question, self.client, chemin=self.path)
        with self.assertRaisesRegex(ValueError, "pas encore indexé"):
            await chercher_dans_cours("Question", self.client, chemin=self.path.with_name("absent.json"))
        self.client.embeddings.create.assert_not_awaited()

    async def test_corrupt_index_and_query_vector(self):
        self.client.embeddings.create.return_value.data[0].embedding = [0., 0.]
        with self.assertRaisesRegex(ValueError, "nul"):
            await chercher_dans_cours("Question", self.client, chemin=self.path)
        self.index["passages"][0]["embedding"] = [1.]
        self.path.write_text(json.dumps(self.index), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalide"):
            await chercher_dans_cours("Question", self.client, chemin=self.path)
