"""Pages réelles rendues avec des données de test, sans compte ni appel modèle."""
import json
from flask import render_template
from app.web import create_app


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
            "/chat": render_template("chat.html", donnees={
                "chapitres": [], "anciennes": [], "duree": 20,
                "messages": [{"role": "colleur", "texte": texte}],
                "etat": {"etape": "fin", "etapes": [], "resultats": [], "terminee": True},
            }),
        }


if __name__ == "__main__":
    print(json.dumps(pages(), ensure_ascii=True))
