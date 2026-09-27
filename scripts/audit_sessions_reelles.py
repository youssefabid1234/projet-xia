"""Audit longitudinal via HTTP et APIs réelles, sans modification du tuteur."""
import argparse
import html
import json
import logging
import os
from pathlib import Path
import re
import secrets
from threading import Thread
import time

import httpx
from openai import OpenAI
from werkzeug.serving import make_server

from app.web import create_app


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dossier", required=True)
    parser.add_argument("--profil", choices=["faible", "moyen", "fort"], required=True)
    parser.add_argument("--reprendre", action="store_true")
    args = parser.parse_args()
    root = Path(args.dossier)
    root.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(root / f"{args.profil}-serveur.log", encoding="utf-8")])
    logging.getLogger("app.agent").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    app = create_app({"UTILISATEURS_PATH": root / "utilisateurs.json", "PROFILS_DIR": root / "profils"})
    server = make_server("127.0.0.1", 0, app)
    Thread(target=server.serve_forever, daemon=True).start()
    profile_path = root / "profils" / "audit-longitudinal.json"
    # Le secret n'est pas journalisé. Les prochains lots réutilisent le même
    # compte par connexion avec le secret local, hors des conversations.
    secret_path = root / ".compte-secret"
    fresh = not secret_path.exists()
    password = secrets.token_urlsafe(32) if fresh else secret_path.read_text(encoding="utf-8")
    if fresh:
        secret_path.write_text(password, encoding="utf-8")
        (root / ".gitignore").write_text(".compte-secret\nutilisateurs.json\n", encoding="utf-8")

    patterns = {
        "faible": ["erronee", "partielle", "indice", "correcte_apres_aide"],
        "moyen": ["correcte", "partielle", "correcte", "erronee"],
        "fort": ["correcte"] * 8 + ["partielle"] + ["correcte"],
    }
    student_instructions = """Tu joues uniquement le rôle d'un élève français de prépa dans un test réel de tuteur.
Écris uniquement le prochain message de l'élève, sans étiquette, sans décrire le test.
Réponds précisément à la dernière question du tuteur. Ne pose pas de nouveau problème.
Tu n'as accès qu'à la conversation visible, jamais aux corrigés privés ni au profil serveur.
Respecte le comportement demandé pour ce tour :
- erronee : fais une tentative plausible contenant une erreur mathématique réelle ; pas un refus.
- partielle : propose une piste ou une réponse incomplète, en laissant une hypothèse ou justification importante.
- indice : indique ce que tu as essayé et demande un petit indice, sans fournir la solution.
- correcte_apres_aide : utilise l'aide reçue pour répondre correctement à la question précise, en mots simples ; si elle reste hors de portée donne un progrès partiel.
- correcte : fournis une réponse juste et une justification complète, vérifie les hypothèses et calculs.
Si le tuteur demande de reformuler une erreur, traite cette demande en priorité, avec le degré de compréhension demandé.
Le profil faible hésite, apprend progressivement grâce aux indices et reste bref ; il ne devient pas expert après une correction.
Le profil moyen répond juste environ une fois sur deux. Le profil fort maîtrise presque tout et justifie rigoureusement.
N'invente pas de connaissance d'une session précédente non fournie. N'exige pas d'être déclaré correct.
"""
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    write_json(root / f"{args.profil}-protocole.json", {
        "profil": args.profil, "sessions": 4, "echanges_max": 20,
        "compte": "audit-longitudinal", "modele_eleve": model,
        "instructions_eleve": student_instructions, "cycle": patterns[args.profil],
        "comptage": "E1 = choix du chapitre et réponse du tuteur ; E2..E20 = message élève et réponse du tuteur",
        "seuil": "Premier exercice strictement avant E10 (E1..E9) ; application et catalogue distingués.",
    })

    def snapshot():
        return json.loads(profile_path.read_text(encoding="utf-8")) if profile_path.exists() else {}

    page = ""
    with httpx.Client(base_url=f"http://127.0.0.1:{server.server_port}", follow_redirects=True, timeout=900) as browser, OpenAI(timeout=120, max_retries=1) as llm:
        page = browser.get("/inscription" if fresh else "/connexion").text

        def post(route, **fields):
            nonlocal page
            tokens = dict(re.findall(r'name="(csrf|tour)" value="([^"]+)"', page))
            response = browser.post(route, data={**tokens, **fields})
            page = response.text
            return response

        auth = post("/inscription" if fresh else "/connexion", identifiant="audit-longitudinal", mot_de_passe=password)
        auth.raise_for_status()
        if 'name="chapitre"' not in page:
            raise RuntimeError("Connexion sans choix de chapitre")
        for number in range(1, 5):
            stem = f"{args.profil}-session-{number}"
            saved = root / f"{stem}.json"
            turns = json.loads(saved.read_text(encoding="utf-8")) if args.reprendre and saved.exists() else []
            if len(turns) >= 20:
                continue
            if not turns:
                before = snapshot()
                write_json(root / f"{stem}-avant.json", before)
            else:
                for old in turns:
                    if old["http"] != 200:
                        old["tuteur"] = "[Erreur HTTP 502 : tuteur indisponible. Aucune nouvelle réponse.]"
            first_exchange = len(turns) + 1
            for exchange in range(first_exchange, 21):
                mode = None
                if exchange == first_exchange:
                    message = "[Choix du chapitre : Séries numériques]" if exchange == 1 else "[Reconnexion après interruption du serveur ; même compte ; choix du chapitre : Séries numériques]"
                    fields = {"action": "chapitre", "chapitre": "0"}
                elif turns[-1]["http"] != 200:
                    message = "La connexion a été interrompue. Pouvez-vous reprendre à partir de mon dernier message ?"
                    fields = {"message": message}
                else:
                    mode = patterns[args.profil][(exchange - 2) % len(patterns[args.profil])]
                    visible = [{"eleve": t["eleve"], "tuteur": t["tuteur"]} for t in turns]
                    result = llm.responses.create(model=model, instructions=student_instructions,
                        input=f"Profil : {args.profil}. Session : {number}. Comportement de ce tour : {mode}.\nConversation :\n" + json.dumps(visible, ensure_ascii=False))
                    message = result.output_text.strip()
                    if not message:
                        raise RuntimeError("Message élève vide")
                    fields = {"message": message}
                started = time.monotonic()
                response = post("/", **fields)
                dialogue = [{"role": role, "content": html.unescape(content)} for role, content in re.findall(
                    r'<article class="chat-message (user|assistant)"[^>]*>\s*<h2>.*?</h2>\s*<div class="math prose">(.*?)</div>', page, re.S)]
                assistant = dialogue[-1]["content"] if dialogue and dialogue[-1]["role"] == "assistant" else "[Aucune réponse du tuteur]"
                if response.status_code != 200:
                    assistant = f"[Erreur HTTP {response.status_code} : tuteur indisponible. Aucune nouvelle réponse.]"
                state = snapshot()
                step = re.search(r'<p class="muted">Étape : (.*?)\.</p>', page)
                turns.append({"echange": exchange, "eleve": message, "tuteur": assistant,
                    "comportement_eleve": mode, "http": response.status_code,
                    "secondes_tuteur": round(time.monotonic() - started, 2),
                    "etape": html.unescape(step.group(1)) if step else None, "profil_apres": state,
                    "dialogue_visible": dialogue})
                write_json(root / f"{stem}.json", turns)
                write_json(root / f"{stem}-apres.json", state)
                lines = [f"# Profil {args.profil} — session {number}", "",
                    "Compte partagé : audit-longitudinal. APIs réelles. E1 inclut le choix du chapitre.", ""]
                for t in turns:
                    lines += [f"## Échange {t['echange']}", "", "**Élève**", "", t["eleve"], "", "**Tuteur**", "", t["tuteur"], "",
                              f"*Étape : {t['etape']} — HTTP {t['http']} — {t['secondes_tuteur']} s.*", ""]
                (root / f"{stem}.md").write_text("\n".join(lines), encoding="utf-8")
                print(json.dumps({"profil": args.profil, "session": number, "echange": exchange,
                    "http": response.status_code, "etape": turns[-1]["etape"], "secondes": turns[-1]["secondes_tuteur"],
                    "tuteur": assistant[:200]}, ensure_ascii=True), flush=True)
                if len(turns) >= 3 and all(t["http"] != 200 for t in turns[-3:]):
                    raise RuntimeError("Trois échecs HTTP consécutifs ; traces conservées.")
            print(f"SESSION_COMPLETE {stem}", flush=True)
            if number != 4:
                post("/deconnexion").raise_for_status()
                post("/connexion", identifiant="audit-longitudinal", mot_de_passe=password).raise_for_status()
    server.shutdown()


if __name__ == "__main__":
    main()
