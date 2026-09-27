"""Pages réelles rendues avec des données de test, sans compte ni appel modèle."""
import json
from flask import render_template
from app.web import create_app
from app.profil import Profil
from app.chapitres import CHAPITRE_SERIES


def pages():
    texte = (r"Fraction : \(\frac{1}{n^2}\). "
             r"Somme : \[\sum_{n=1}^{\infty}\frac{1}{n^2}\]. "
             r"Ensemble : $$\mathbb{R}$$. "
             r"Limite : $\lim_{n\to\infty}u_n=0$. "
             r"Alignement : $\begin{aligned}a&=b+c\\d&=e\end{aligned}$. "
             r"<script>window.injection=true</script>")
    app = create_app({"TESTING": True, "SECRET_KEY": "fixture"})
    with app.test_request_context("/"):
        return {
            "/chat": render_template("chat.html", etape="exercices", chapitre_selectionne=True,
                chapitres=[], messages=[{"role": "assistant", "content": texte}]),
            "/classique": render_template("index.html", chapitre=CHAPITRE_SERIES,
                chapitres=[CHAPITRE_SERIES], profil=Profil("fixture"),
                exercice={"id": "fixture", "enonce": texte, "difficulte": 1}),
        }


if __name__ == "__main__":
    print(json.dumps(pages(), ensure_ascii=True))
