"""Page réelle avec état fictif pour vérifier les canaux dans un navigateur."""
import json
from flask import render_template
from app.web import create_app


def fixture():
    app = create_app({"TESTING": True, "SECRET_KEY": "fixture"})
    question = "Énoncé public : calculer $x^2$."
    etat = {"debut": 1, "etape": "cours", "etapes": [{"cle": "cours", "libelle": "Cours"}],
            "resultats": [], "terminee": False, "temps_restant": 900,
            "tache": {"question": question, "question_active": question, "etape_resolution": None}}
    donnees = {"chapitres": [], "anciennes": [], "duree": 30, "etat": etat,
               "messages": [{"role": "colleur", "texte": "Bienvenue.",
                             "question": {"libelle": "Cours", "texte": question}}]}
    with app.test_request_context("/"):
        return {"html": render_template("chat.html", donnees=donnees), "donnees": donnees}


if __name__ == "__main__":
    print(json.dumps(fixture(), ensure_ascii=True))
