"""Interface locale avec comptes élèves : python -m app.web."""

import json
import os
import secrets
from pathlib import Path
from threading import Lock

from flask import Flask, Response, g, jsonify, render_template, request, session, stream_with_context

from app.colle import Colle, charger_banque
from app.chapitres import COLLES, nom_chapitre
from app.config import RACINE, charger_env, duree_colle_minutes
from app.enonces import CACHE, CacheEnonces
from app.evaluation import evaluer_reponse, valider
from app.examinateur import Examinateur, prechauffer
from app.profil import Profil, charger_exercices, choisir_exercice
from app.services import services as services_partages
from app.web.auth import auth

VERDICTS = {
    "correcte": "Réponse correcte",
    "incorrecte": "Réponse incorrecte",
    "incomplete": "Réponse incomplète",
    "indeterminable": "Évaluation indéterminable",
}


async def corriger(enonce, reponse, corrige):
    """Correction de l'interface classique, par l'API Pipelex."""
    from pipelex_sdk.runs import WaitForResultOptions
    client = await services_partages().pipelex()
    resultat = await evaluer_reponse(client, enonce, reponse, corrige,
                                     WaitForResultOptions(interval_seconds=0.5, timeout_seconds=120))
    return valider(resultat.main_stuff)


def create_app(config=None):
    charger_env()
    app = Flask(__name__)
    app.jinja_env.filters["nom_chapitre"] = nom_chapitre
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        UTILISATEURS_PATH=RACINE / "data" / "utilisateurs.json",
        PROFILS_DIR=RACINE / "data" / "profils",
        EXERCICES_PATH=RACINE / "data" / "exercices.json",
        CACHE_ENONCES=CACHE,
        COLLES=COLLES,
        DUREE_COLLE=duree_colle_minutes(),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)
    app.register_blueprint(auth)
    services = app.config.get("SERVICES") or services_partages()
    if not app.testing and os.environ.get("OPENAI_API_KEY", "").strip():
        services.lancer(prechauffer(services))
    cache = CacheEnonces(app.config["CACHE_ENONCES"])
    verrou = Lock()               # protège les dictionnaires ci-dessous, jamais un appel réseau
    examinateurs = {}             # identifiant élève -> Examinateur de la colle en cours
    occupes = set()               # élèves dont un tour est en cours de traitement
    verrous_classique = {}
    banques = {}

    def utilisateur():
        return session["utilisateur"]

    def chemin_colle():
        return Path(app.config["PROFILS_DIR"]) / f"{utilisateur()}.colle.json"

    def chapitres():
        catalogue = {ex["chapitre"] for ex in charger_exercices(app.config["EXERCICES_PATH"])}
        return [c for c in app.config["COLLES"] if c in catalogue]

    def banque(chapitre):
        if chapitre not in banques:
            config = app.config["COLLES"][chapitre]
            banques[chapitre] = charger_banque(config["questions"], config["index"])
        return banques[chapitre]

    def examinateur_actif():
        """Colle en cours de l'élève, rechargée depuis le disque après un redémarrage."""
        with verrou:
            examinateur = examinateurs.get(utilisateur())
        if examinateur is None and chemin_colle().exists():
            try:
                donnees = json.loads(chemin_colle().read_text(encoding="utf-8"))
                colle = Colle.from_dict(donnees, g.profil_path, charger_exercices(app.config["EXERCICES_PATH"]),
                                        banque(donnees["chapitre"]))
            except (OSError, ValueError, KeyError):
                app.logger.exception("Colle enregistrée illisible ; elle est ignorée")
                return None
            examinateur = Examinateur(colle, services, cache)
            with verrou:
                examinateur = examinateurs.setdefault(utilisateur(), examinateur)
        return examinateur

    def verifier_requete():
        """CSRF par en-tête et clé OpenAI présente ; renvoie une réponse d'erreur ou None."""
        jeton = request.headers.get("X-CSRF-Token", "")
        if not secrets.compare_digest(jeton.encode(), session.get("csrf", "").encode()):
            return jsonify(erreur="La session a expiré. Rechargez la page."), 400
        if not os.environ.get("OPENAI_API_KEY", "").strip():
            return jsonify(erreur="Le colleur est indisponible : configurez OPENAI_API_KEY (fichier .env)."), 503
        return None

    def etat_public(examinateur):
        profil = Profil.charger(g.profil_path)
        return {
            "chapitres": [{"index": i, "nom": nom_chapitre(c)} for i, c in enumerate(chapitres())],
            "duree": app.config["DUREE_COLLE"],
            "anciennes": [{"chapitre": nom_chapitre(c["chapitre"]), "debut": c["debut"], "bilan": c["bilan"]}
                          for c in reversed(profil.colles[-5:])],
            "messages": examinateur.colle.messages if examinateur else [],
            "etat": examinateur.colle.etat() if examinateur else None,
        }

    def diffuser(examinateur, generateur):
        """Diffuse les événements en NDJSON ; la colle est sauvegardée à la fin du tour."""
        eleve, chemin = utilisateur(), chemin_colle()

        async def tour():
            try:
                async for evenement in generateur:
                    yield evenement
            finally:
                try:
                    examinateur.colle.sauvegarder(chemin)
                finally:
                    with verrou:
                        occupes.discard(eleve)

        evenements = services.iterer(tour())  # démarre le tour sans attendre le navigateur

        def lignes():
            try:
                for evenement in evenements:
                    yield json.dumps(evenement, ensure_ascii=False) + "\n"
            except Exception:
                app.logger.exception("Échec du tour de colle")
                yield json.dumps({"type": "erreur", "texte": "Le colleur est indisponible. Réessayez."},
                                 ensure_ascii=False) + "\n"

        return Response(stream_with_context(lignes()), mimetype="application/x-ndjson",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    def reserver():
        with verrou:
            if utilisateur() in occupes:
                return False
            occupes.add(utilisateur())
            return True

    def liberer():
        with verrou:
            occupes.discard(utilisateur())

    @app.get("/")
    def chat():
        session.setdefault("csrf", secrets.token_urlsafe(32))
        return render_template("chat.html", donnees=etat_public(examinateur_actif()))

    @app.get("/api/etat")
    def api_etat():
        return jsonify(etat_public(examinateur_actif()))

    @app.post("/api/colle")
    def api_demarrer():
        if erreur := verifier_requete():
            return erreur
        disponibles = chapitres()
        choix = (request.get_json(silent=True) or {}).get("chapitre")
        if type(choix) is not int or not 0 <= choix < len(disponibles):
            return jsonify(erreur="Choix de chapitre indisponible."), 400
        chapitre = disponibles[choix]
        actif = examinateur_actif()
        if actif and not actif.colle.terminee:
            return jsonify(erreur="Une colle est déjà en cours."), 409
        if not reserver():
            return jsonify(erreur="Une action est déjà en cours."), 409
        try:
            colle = Colle(g.profil_path, chapitre, charger_exercices(app.config["EXERCICES_PATH"]),
                          banque(chapitre), app.config["DUREE_COLLE"])
            examinateur = Examinateur(colle, services, cache)
            services.executer(examinateur.demarrer(), timeout=180)
            colle.sauvegarder(chemin_colle())
            with verrou:
                examinateurs[utilisateur()] = examinateur
        except Exception:
            app.logger.exception("Impossible de démarrer la colle")
            return jsonify(erreur="Le colleur est indisponible. Réessayez."), 502
        finally:
            liberer()
        return jsonify(etat_public(examinateur))

    @app.post("/api/message")
    def api_message():
        if erreur := verifier_requete():
            return erreur
        message = (request.get_json(silent=True) or {}).get("message", "")
        examinateur = examinateur_actif()
        if examinateur is None:
            return jsonify(erreur="Choisissez d'abord un chapitre."), 400
        if not isinstance(message, str) or not message.strip() or len(message) > 6000:
            return jsonify(erreur="Écrivez un message de 1 à 6 000 caractères."), 400
        if not reserver():
            return jsonify(erreur="Le colleur vous répond déjà : attendez la fin de sa réponse."), 409
        return diffuser(examinateur, examinateur.tour(message))

    @app.post("/api/bilan")
    def api_bilan():
        if erreur := verifier_requete():
            return erreur
        examinateur = examinateur_actif()
        if examinateur is None:
            return jsonify(erreur="Aucune colle en cours."), 400
        if not reserver():
            return jsonify(erreur="Une action est déjà en cours."), 409
        return diffuser(examinateur, examinateur.bilan())

    @app.post("/api/nouvelle")
    def api_nouvelle():
        jeton = request.headers.get("X-CSRF-Token", "")
        if not secrets.compare_digest(jeton.encode(), session.get("csrf", "").encode()):
            return jsonify(erreur="La session a expiré. Rechargez la page."), 400
        if not reserver():
            return jsonify(erreur="Une action est déjà en cours."), 409
        try:
            with verrou:
                examinateurs.pop(utilisateur(), None)
            chemin_colle().unlink(missing_ok=True)
        finally:
            liberer()
        return jsonify(etat_public(None))

    @app.route("/classique", methods=["GET", "POST"])
    def index():
        exercices = charger_exercices(app.config["EXERCICES_PATH"])
        liste = list(dict.fromkeys(ex["chapitre"] for ex in exercices))
        chapitre = request.values.get("chapitre", liste[0] if liste else "")
        session.setdefault("csrf", secrets.token_urlsafe(32))
        erreur, evaluation, reponse, statut = None, None, "", 200
        # Sérialise les corrections et la sauvegarde du profil de cet élève seulement.
        with verrou:
            verrou_eleve = verrous_classique.setdefault(utilisateur(), Lock())
        with verrou_eleve:
            profil = Profil.charger(g.profil_path)
            exercice = choisir_exercice(profil, chapitre, exercices)
            if chapitre not in liste and liste:
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
                        evaluation = services.executer(
                            corriger(exercice["enonce"], reponse, exercice.get("corrige", "")), timeout=180)
                        profil.enregistrer(exercice["id"], chapitre,
                                           evaluation["verdict"], evaluation["type_erreur"])
                        profil.sauvegarder(g.profil_path)
                    except Exception:
                        app.logger.exception("Échec de la correction ou de sa sauvegarde")
                        profil = Profil.charger(g.profil_path)
                        evaluation = None
                        erreur, statut = "La correction n’a pas pu être enregistrée. Votre réponse est conservée ; réessayez.", 502
            return render_template(
                "index.html", chapitres=liste, chapitre=chapitre,
                profil=profil, exercice=exercice, reponse=reponse,
                evaluation=evaluation, erreur=erreur, verdicts=VERDICTS,
            ), statut

    return app
