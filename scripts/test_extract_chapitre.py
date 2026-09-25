"""Vérifie pagination, corrigés absents et fusion sans perte sur un PDF synthétique."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pymupdf

from extract_chapitre import ROOT, extract_difficulties, main


class ExtractionTests(unittest.TestCase):
    def test_multpage_empty_solution_and_idempotent_merge(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "source.pdf"
            output = root / "exercices.json"
            preserved = {"identifiant": "18.1", "enonce": "inchangé", "corrige": "inchangé"}
            output.write_text(json.dumps([preserved]), encoding="utf-8")
            with pymupdf.open() as doc:
                bodies = [
                    "Chapitre XCIX\nEssai\nExercice 99.1\nDebut enonce",
                    "CHAPITRE XCIX. ESSAI\nSuite enonce\nExercice 99.2\nAutre enonce",
                    "Solution de l'exercice 99.1\nDebut corrige",
                    "Suite corrige\nSolution de l'exercice 99.2",
                ]
                for number, body in enumerate(bodies, 1):
                    page = doc.new_page()
                    page.insert_text((40, 60), body)
                    page.insert_text((40, 790), f"Quentin De Muynck\n{number}")
                doc.save(pdf)
            argv = ["--pdf", str(pdf), "--output", str(output), "--chapitre", "99",
                    "--enonces", "1", "2", "--corriges", "3", "4"]
            with contextlib.redirect_stdout(io.StringIO()), patch(
                "extract_chapitre.extract_difficulties", return_value={"99.1": 2, "99.2": 0}
            ):
                main(argv)
                first = output.read_bytes()
                main(argv)
            self.assertEqual(first, output.read_bytes())
            records = json.loads(first)
            self.assertEqual(records[0], preserved)
            self.assertEqual(len(records), 3)
            self.assertEqual(records[1]["enonce"], "Debut enonce\nSuite enonce")
            self.assertEqual(records[1]["corrige"], "Debut corrige\nSuite corrige")
            self.assertEqual(records[1]["page_source"]["enonce"]["pdf"], [1, 2])
            self.assertEqual(records[1]["page_source"]["corrige"]["pdf"], [3, 4])
            self.assertEqual(records[2]["corrige"], "")
            self.assertEqual(records[1]["difficulte"], 2)
            self.assertEqual(records[2]["difficulte"], 0)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(argv[:-1] + ["3"])
            self.assertEqual(first, output.read_bytes())

    def test_actual_star_glyphs(self):
        with pymupdf.open(ROOT / "data/poly.pdf") as doc:
            self.assertEqual(extract_difficulties(doc[9]), {
                "2.1": 0, "2.2": 2, "2.3": 1, "2.4": 0,
                "2.5": 1, "2.6": 0, "2.7": 3,
            })
            self.assertEqual(extract_difficulties(doc[10])["2.10"], 4)
            self.assertEqual(extract_difficulties(doc[10])["2.19"], 2)
            self.assertEqual({k: v for k, v in extract_difficulties(doc[51]).items()
                              if k in ("18.1", "18.2", "18.3")},
                             {"18.1": 0, "18.2": 0, "18.3": 0})

    def test_missing_stars_are_not_zero(self):
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((40, 60), "Exercice 1.1")
            with self.assertRaisesRegex(ValueError, "Police"):
                extract_difficulties(page)


if __name__ == "__main__":
    unittest.main()
