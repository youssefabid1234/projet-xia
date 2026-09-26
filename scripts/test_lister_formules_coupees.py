import unittest

from scripts.lister_formules_coupees import analyser, ruptures_suspectes


class FormulesCoupeesTests(unittest.TestCase):
    def test_fraction_aplatie(self):
        ruptures = ruptures_suspectes("Soit un+1 =\n1\nn + 1e−un.")
        self.assertEqual([r["ligne"] for r in ruptures], [1, 2])

    def test_somme_et_formule_latex(self):
        for texte in ("Calculer\nX\nn=0\n1/n2", "$\\frac{1}{\nn+1}$", "$$x =\ny$$"):
            with self.subTest(texte=texte):
                self.assertTrue(ruptures_suspectes(texte))

    def test_prose_et_questions_ne_sont_pas_signalees(self):
        for texte in ("Première phrase.\nDeuxième phrase.", "Calculer $1+1$.\n\nJustifier.",
                      "Soit $x=1$.\nCalculer $x+1$.",
                      "1. Montrer la convergence.\n2. Calculer la limite."):
            self.assertEqual(ruptures_suspectes(texte), [])

    def test_source_et_texte_conserves(self):
        exercice = {"identifiant": "17.4", "enonce": "1\nn+1", "page_source": {"enonce": {"pdf": 50}}}
        resultat = analyser([exercice])[0]
        self.assertEqual(resultat["enonce"], exercice["enonce"])
        self.assertEqual(resultat["page_source"], exercice["page_source"])

    def test_mode_exhaustif(self):
        exercices = [{"id": "a", "enonce": "Première phrase.\nDeuxième phrase."}]
        self.assertEqual(analyser(exercices), [])
        self.assertEqual(len(analyser(exercices, True)), 1)
