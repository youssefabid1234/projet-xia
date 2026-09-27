"""Routes de conversion isolées : ne soumettent jamais une réponse au moteur."""

import asyncio
import secrets
from threading import Lock

from flask import Blueprint, Response, current_app, jsonify, request, session
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from app.modalites import Convertisseur, MAX_AUDIO, MAX_IMAGE, audio_valide, image_validee


def creer_modalites(etat_actif):
    routes = Blueprint("modalites", __name__, url_prefix="/api/modalites")
    verrou, occupes = Lock(), set()

    def convertisseur():
        return current_app.config.get("CONVERTISSEUR") or Convertisseur()

    @routes.before_request
    def proteger():
        # L'authentification commune s'exécute avant ce hook.
        if request.method == "POST":
            jeton = request.headers.get("X-CSRF-Token", "")
            if not secrets.compare_digest(jeton.encode(), session.get("csrf", "").encode()):
                return jsonify(erreur="La session a expiré. Rechargez la page."), 400
        # Limites locales seulement : les routes existantes restent à 64 Kio.
        limites = {"modalites.manuscrit": MAX_IMAGE, "modalites.dictee": MAX_AUDIO}
        if request.endpoint in limites:
            request.max_content_length = limites[request.endpoint]

    @routes.errorhandler(RequestEntityTooLarge)
    def trop_grand(_):
        return jsonify(erreur="Enregistrement trop volumineux."), 413

    @routes.after_request
    def prive(reponse):
        reponse.headers["Cache-Control"] = "no-store"
        reponse.headers["X-Content-Type-Options"] = "nosniff"
        return reponse

    def contexte():
        etat = etat_actif()
        if not etat or etat["terminee"] or etat["temps_restant"] <= 0 or not etat.get("tache"):
            raise ValueError("La colle n'est plus disponible pour cette saisie.")
        return (etat["debut"], etat["etape"], len(etat["resultats"]), etat["tache"])

    def convertir(mode, preparer):
        cle = (session["utilisateur"], mode)
        with verrou:
            if cle in occupes:
                return jsonify(erreur="Une conversion est déjà en cours."), 409
            occupes.add(cle)
        try:
            avant = contexte()
            if not convertisseur().disponibilites()[mode]:
                return jsonify(erreur="Cette modalité est indisponible. Vous pouvez écrire au clavier."), 503
            entree = preparer(avant)
            try:
                resultat = asyncio.run(getattr(convertisseur(), mode)(entree))
            except Exception:
                # Les erreurs du fournisseur (y compris ValueError) restent privées.
                current_app.logger.warning("Conversion %s indisponible", mode)
                return jsonify(erreur="Conversion indisponible. Votre brouillon est conservé ; vous pouvez écrire au clavier."), 502
            if contexte() != avant:
                return jsonify(erreur="La question a changé. Reprenez votre saisie."), 409
            if mode == "lecture":
                return Response(resultat, mimetype="audio/wav")
            if not isinstance(resultat, str) or not resultat.strip() or len(resultat) > 6000:
                return jsonify(erreur="Transcription vide ou trop longue. Reprenez la saisie ou utilisez le clavier."), 422
            return jsonify(texte=resultat.strip())
        except ValueError as exc:
            return jsonify(erreur=str(exc)), 400
        except HTTPException:
            raise
        except Exception:
            # Ni média, ni transcription, ni message du fournisseur dans les logs.
            current_app.logger.warning("Conversion %s indisponible", mode)
            return jsonify(erreur="Conversion indisponible. Votre brouillon est conservé ; vous pouvez écrire au clavier."), 502
        finally:
            with verrou:
                occupes.discard(cle)

    @routes.get("")
    def disponibilites():
        return jsonify(convertisseur().disponibilites())

    @routes.post("/manuscrit")
    def manuscrit():
        def preparer(_):
            if request.mimetype != "image/png":
                raise ValueError("Tableau PNG attendu.")
            return image_validee(request.get_data())
        return convertir("manuscrit", preparer)

    @routes.post("/dictee")
    def dictee():
        def preparer(_):
            if request.mimetype != "audio/wav":
                raise ValueError("Enregistrement WAV attendu.")
            return audio_valide(request.get_data())
        return convertir("dictee", preparer)

    @routes.post("/lecture")
    def lecture():
        def preparer(avant):
            corps = request.get_json(silent=True)
            if not isinstance(corps, dict) or set(corps) != {"question"}:
                raise ValueError("Une question publique est attendue.")
            question = corps["question"]
            # Liste blanche serveur. Même un client modifié ne peut faire lire un corrigé.
            if not isinstance(question, str) or not question or len(question) > 12000 or question != avant[3]["question_active"]:
                raise ValueError("Seule la consigne actuellement révélée peut être lue.")
            return question
        return convertir("lecture", preparer)

    return routes
