"""Contrôles locaux du découpage et de l'association texte-vecteur, sans API."""
import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from index_cours import ROOT, apply_review, embed, extract, main


class CourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = extract(ROOT / "data/cours/analyse.pdf")

    def test_numbered_units_and_cross_page_proof(self):
        rows = {p["identifiant"]: p for p in self.payload["passages"]}
        expected = [f"16.{section}.{i}" for section, count in [(1, 15), (2, 23), (3, 6), (4, 25), (5, 8), (6, 3)] for i in range(1, count + 1)]
        self.assertEqual(list(rows), expected)
        self.assertEqual(rows["16.1.1"]["page_source"]["pdf"], [139, 140])
        theorem = rows["16.1.12"]
        self.assertEqual(theorem["page_source"]["pdf"], [141, 142])
        self.assertIn("Écrire un = Sn −Sn−1.", theorem["texte"])
        self.assertTrue(theorem["contient_preuve"])
        self.assertNotIn("CHAPITRE 16", theorem["texte"])
        self.assertNotIn("Divergence grossière", theorem["texte"])
        self.assertTrue(all(p["texte"].strip() for p in rows.values()))
        self.assertTrue(all(139 <= n <= 157 for p in rows.values() for n in p["page_source"]["pdf"]))

    def test_review_and_pdf_fingerprint(self):
        payload = copy.deepcopy(self.payload)
        review = ROOT / "scripts/transcriptions/cours_series.json"
        apply_review(payload, review)
        self.assertEqual(sum(p["transcription_relue"] for p in payload["passages"]), 10)
        self.assertIn(r"\sum", payload["passages"][0]["texte"])
        self.assertEqual(payload["passages"][0]["texte_brut"], self.payload["passages"][0]["texte"])
        payload["pdf_sha256"] = "changed"
        with self.assertRaisesRegex(ValueError, "incompatibles"):
            apply_review(payload, review)

    def test_embedding_order_batches_and_invalid_response(self):
        payload = {**self.payload, "passages": self.payload["passages"][:3]}
        client = Mock()
        client.embeddings.create.side_effect = [
            SimpleNamespace(data=[SimpleNamespace(index=1, embedding=[2., 3.]), SimpleNamespace(index=0, embedding=[0., 1.])]),
            SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[4., 5.])]),
        ]
        tokens = SimpleNamespace(encoding_for_model=lambda model: SimpleNamespace(encode=lambda text: list(text)))
        with patch.dict("sys.modules", {"tiktoken": tokens}):
            result = embed(payload, client, "text-embedding-3-small", batch_size=2)
            self.assertEqual([p["embedding"] for p in result["passages"]], [[0., 1.], [2., 3.], [4., 5.]])
            self.assertEqual(result["dimensions"], 2)
            self.assertNotIn("embedding", payload["passages"][0])
            client.embeddings.create.side_effect = None
            client.embeddings.create.return_value = SimpleNamespace(data=[])
            with self.assertRaisesRegex(ValueError, "incomplète"):
                embed(payload, client, "text-embedding-3-small")

    def test_preview_never_calls_openai_or_writes_index(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            folder = Path(directory)
            fake_openai = Mock()
            with patch.dict("sys.modules", {"openai": fake_openai}), patch("builtins.print"):
                main(["--passages", str(folder / "passages.json"), "--apercu", str(folder / "apercu.md"), "--output", str(folder / "index.json")])
            fake_openai.OpenAI.assert_not_called()
            self.assertFalse((folder / "index.json").exists())
            self.assertEqual((folder / "apercu.md").read_text(encoding="utf-8").count("\n## "), 10)


if __name__ == "__main__":
    unittest.main()
