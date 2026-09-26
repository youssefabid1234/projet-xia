"""Interface locale, mono-élève : python -m app.web."""

import asyncio
import os
import secrets
from pathlib import Path
from threading import Lock

from flask import Flask, render_template, request, session
from pipelex_sdk.client import PipelexAPIClient

from app.evaluation import evaluer_reponse
from app.profil import GAINS, Profil, charger_exercices, choisir_exercice

ROOT = Path(__file__).resolve().parents[2]
VERDICTS = {
    "correcte": "Réponse correcte",
    "incorrecte": "Réponse incorrecte",
    "incomplete": "Réponse incomplète",
    "indeterminable": "Évaluation indéterminable",
}


async def corriger(enonce, reponse):
    async with PipelexAPIClient() as client:
        resultat = await evaluer_reponse(client, enonce, reponse)
    evaluation = resultat.main_stuff
    if (not isinstance(evaluation, dict)
            or evaluation.get("verdict") not in GAINS
            or not isinstance(evaluation.get("type_erreur"), str)
            or not isinstance(evaluation.get("explication"), str)):
        raise ValueError("Format d'évaluation invalide.")
    return evaluation


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        PROFIL_PATH=ROOT / "data" / "profil.json",
        EXERCICES_PATH=ROOT / "data" / "exercices.json",
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)
    verrou = Lock()

    @app.route("/", methods=["GET", "POST"])
    def index():
        exercices = charger_exercices(app.config["EXERCICES_PATH"])
        chapitres = list(dict.fromkeys(ex["chapitre"] for ex in exercices))
        chapitre = request.values.get("chapitre", chapitres[0] if chapitres else "")
        session.setdefault("csrf", secrets.token_urlsafe(32))
        erreur, evaluation, reponse, statut = None, None, "", 200
        # Sérialise les corrections et la sauvegarde du profil local partagé.
        with verrou:
            profil = Profil.charger(app.config["PROFIL_PATH"])
            exercice = choisir_exercice(profil, chapitre, exercices)
            if chapitre not in chapitres and chapitres:
                erreur, statut = "Chapitre inconnu. Choisissez un chapitre de la liste.", 400
            elif request.method == "POST":
                reponse = request.form.get("reponse", "")
                if not secrets.compare_digest(request.form.get("csrf", "").encode(), session["csrf"].encode()):
                    erreur, statut = "La session a expiré. Rechargez la page.", 400
                elif exercice is None or request.form.get("exercice_id") != exercice["id"]:
                    erreur, statut = "Cet exercice a déjà été traité ou a changé. Rechargez la page.", 409
                elif len(reponse) > 12000:
                    erreur, statut = "Votre réponse doit contenir au maximum 12 000 caractères.", 400
                elif not os.environ.get("PIPELEX_API_KEY", "").strip():
                    erreur, statut = "La correction est indisponible : configurez PIPELEX_API_KEY sur le serveur.", 503
                else:
                    try:
                        evaluation = asyncio.run(corriger(exercice["enonce"], reponse))
                        profil.enregistrer(exercice["id"], chapitre,
                                           evaluation["verdict"], evaluation["type_erreur"])
                        profil.sauvegarder(app.config["PROFIL_PATH"])
                    except Exception:
                        app.logger.exception("Échec de la correction ou de sa sauvegarde")
                        profil = Profil.charger(app.config["PROFIL_PATH"])
                        evaluation = None
                        erreur, statut = "La correction n’a pas pu être enregistrée. Votre réponse est conservée ; réessayez.", 502
            return render_template(
                "index.html", chapitres=chapitres, chapitre=chapitre,
                profil=profil, exercice=exercice, reponse=reponse,
                evaluation=evaluation, erreur=erreur, verdicts=VERDICTS,
            ), statut

    return app
