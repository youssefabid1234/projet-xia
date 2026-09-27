"""Khôlle live : voix (gradbot), tableau sur tablette, compte-rendu. [lane A]

Lancer : uv run uvicorn main:app --host 0.0.0.0 --port 8000
"""

import dataclasses
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

ICI = Path(__file__).resolve().parent
# Avant tout le reste : gradbot.config.from_env() est mis en cache au premier appel.
load_dotenv(ICI / ".env")

import fastapi  # noqa: E402
import gradbot  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from kholle import board, exercises, prompts, report, state  # noqa: E402

gradbot.init_logging()
CONFIG = gradbot.config.from_env()

app = fastapi.FastAPI(title="Khôlle live")
app.include_router(board.router)
app.include_router(report.router)

state.new_session(exercises.demo()["id"])


class NouvelleSession(BaseModel):
    exercise_id: str | None = None


class Replique(BaseModel):
    qui: Literal["eleve", "kholleur"]
    texte: str


@app.get("/api/exercise")
def exercice_courant():
    ex = exercises.get(state.get_session().exercise_id)
    return {"id": ex["id"], "titre": ex["titre"], "enonce_latex": ex["enonce_latex"]}


@app.post("/api/session/new")
def nouvelle_session(corps: NouvelleSession | None = None):
    exercise_id = (corps and corps.exercise_id) or exercises.demo()["id"]
    try:
        exercises.get(exercise_id)
    except KeyError:
        raise fastapi.HTTPException(404, f"Exercice inconnu : {exercise_id}")
    s = state.new_session(exercise_id)
    return {"id": s.id, "exercise_id": s.exercise_id}


@app.post("/api/transcript")
def transcription(replique: Replique):
    return dataclasses.asdict(state.add_turn(replique.qui, replique.texte))


# Voix : point de départ minimal (modèle : gradbot demos/fantasy_shop/main.py).
# Protocole client : {"type": "start"} puis trames audio binaires ; {"type": "stop"}.
@app.websocket("/ws/kholle")
async def ws_kholle(websocket: fastapi.WebSocket):
    def on_start(msg: dict) -> gradbot.SessionConfig:
        langue = gradbot.LANGUAGES["fr"]
        return gradbot.SessionConfig(
            voice_id=os.environ.get("KHOLLEUR_VOICE_ID") or None,
            instructions=prompts.build_instructions(state.get_session()),
            language=langue,
            tools=[],  # TODO(A) : donner_indice, question_suivante, terminer_colle
            **{
                "rewrite_rules": langue.rewrite_rules,
                "assistant_speaks_first": True,
                "silence_timeout_s": float(os.environ.get("SILENCE_TIMEOUT_S", 10)),
            }
            | CONFIG.session_kwargs,
        )

    await gradbot.websocket.handle_session(websocket, config=CONFIG, on_start=on_start)


# Monte /static (notre dossier) et /static/js (worklets audio fournis par gradbot),
# plus GET / -> static/index.html et GET /api/audio-config. À garder en dernier.
gradbot.routes.setup(app, config=CONFIG, static_dir=ICI / "static")
