"""Session HTTP interactive avec les vrais services, sans mock.

python -m scripts.session_reelle_profil
Saisir les réponses, puis /reconnexion, /bilan et /fin. Les fichiers du compte
et les échanges réels restent sous reports/session-reelle-<date>/.
"""
import json
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread

import httpx
from werkzeug.serving import make_server

from app.config import charger_env
from app.web import create_app


def main():
    charger_env()
    dossier = Path("reports") / ("session-reelle-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    dossier.mkdir(parents=True)
    app = create_app({"UTILISATEURS_PATH": dossier / "utilisateurs.json", "PROFILS_DIR": dossier / "profils"})
    serveur = make_server("127.0.0.1", 0, app, threaded=True)
    Thread(target=serveur.serve_forever, daemon=True).start()
    trace = []
    with httpx.Client(base_url=f"http://127.0.0.1:{serveur.server_port}", follow_redirects=True, timeout=600) as client:
        def csrf(route="/"):
            return re.search(r'name="csrf" (?:value|content)="([^"]+)"', client.get(route).text).group(1)

        def formulaire(route, **champs):
            reponse = client.post(route, data={"csrf": csrf(route if route != "/deconnexion" else "/"), **champs})
            trace.append({"route": route, "statut": reponse.status_code})

        def api(route, corps=None):
            reponse = client.post(route, json=corps or {}, headers={"X-CSRF-Token": csrf()})
            evenements = [json.loads(ligne) for ligne in reponse.text.splitlines() if ligne.strip()] \
                if reponse.headers.get("content-type", "").startswith("application/x-ndjson") else [reponse.json()]
            texte = "".join(e.get("texte", "") for e in evenements if e.get("type") == "texte")
            questions = [e["question"]["texte"] for e in evenements if e.get("type") == "question"]
            trace.append({"route": route, "envoi": corps, "statut": reponse.status_code,
                          "colleur": texte, "questions": questions})
            (dossier / "session.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
            return evenements, texte, questions

        mot_de_passe = secrets.token_urlsafe(24)
        client.get("/inscription")
        formulaire("/inscription", identifiant="verification-profil", mot_de_passe=mot_de_passe)
        (donnees,), _, _ = api("/api/colle", {"chapitre": 0})
        print(donnees["messages"][0]["texte"], "\n>>", donnees["messages"][0]["question"]["texte"], flush=True)
        print(f"PROFIL : {dossier / 'profils/verification-profil.json'}", flush=True)
        while True:
            message = input("Réponse (/reconnexion, /bilan, /fin) : ")
            if message == "/fin":
                break
            if message == "/reconnexion":
                formulaire("/deconnexion")
                client.get("/connexion")
                formulaire("/connexion", identifiant="verification-profil", mot_de_passe=mot_de_passe)
                etat = client.get("/api/etat").json()
                print(f"Reprise : {len(etat['messages'])} messages, étape {etat['etat']['etape']}", flush=True)
                continue
            _, texte, questions = api("/api/bilan" if message == "/bilan" else "/api/message",
                                      None if message == "/bilan" else {"message": message})
            print(texte, *[f"\n>> {q}" for q in questions], flush=True)
    serveur.shutdown()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
