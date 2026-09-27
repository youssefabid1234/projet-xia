import unittest

from app.notation import normaliser_latex, sans_references_cours


class NotationTests(unittest.TestCase):
    def test_anciens_delimiteurs_commandes_et_multiligne(self):
        texte = r"\(\frac{1}{2}\) et \[\sum_{n=1}^{\infty}u_n\] et $$\mathbb{R}$$"
        attendu = r"$\frac{1}{2}$ et $\sum_{n=1}^{\infty}u_n$ et $\mathbb{R}$"
        self.assertEqual(normaliser_latex(texte), attendu)
        self.assertEqual(normaliser_latex("$$a\n+b$$"), "$a\n+b$")
        self.assertEqual(normaliser_latex(attendu), attendu)
        self.assertEqual(normaliser_latex("$x$$y$"), "$x$ $y$")

    def test_monnaie_echappee_et_texte_html_restent_du_texte(self):
        texte = r"Prix : \$5. <script>alerte</script> $x^2$"
        self.assertEqual(normaliser_latex(texte), texte)

    def test_localisateurs_uniquement(self):
        self.assertEqual(sans_references_cours("Énoncez le théorème 16.2.2 (page PDF 140)."),
                         "Énoncez le théorème.")
        self.assertEqual(sans_references_cours("1. Calculez $1.25 + 2$.\n2. Concluez."),
                         "1. Calculez $1.25 + 2$.\n2. Concluez.")
        self.assertEqual(sans_references_cours("Utilisez le lemme 2.3 pour calculer $1.2.3$."),
                         "Utilisez le lemme pour calculer $1.2.3$.")
