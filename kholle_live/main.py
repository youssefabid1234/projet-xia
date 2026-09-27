"""Khôlle live : voix (gradbot), tableau sur tablette, compte-rendu. [lane A]

Lancer : uv run uvicorn main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import contextlib
import dataclasses
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

ICI = Path(__file__).resolve().parent
# Avant tout le reste : gradbot.config.from_env() est mis en cache au premier appel.
load_dotenv(ICI / ".env")
load_dotenv(ICI.parent / ".env")  # clés du dépôt ; celles d'ici priment
# Clé du LLM : à défaut de LLM_API_KEY, celle d'OpenAI (déjà là pour la vision).
if not os.environ.get("LLM_API_KEY") and os.environ.get("OPENAI_API_KEY"):
    os.environ["LLM_API_KEY"] = os.environ["OPENAI_API_KEY"]

import fastapi  # noqa: E402
import gradbot  # noqa: E402
import httpx  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from kholle import board, exercises, outils, prompts, report, state  # noqa: E402

gradbot.init_logging()
logging.basicConfig(level=logging.INFO, format="{asctime} {name} {levelname} {message}", style="{")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("kholle.voix")
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
    s = state.get_session()
    ex = exercises.get(s.exercise_id)
    question = exercises.question(ex, s.question_index) if s.question_index else None
    return {
        "id": ex["id"],
        "titre": ex["titre"],
        "enonce_latex": ex["enonce_latex"],
        "question": question and question["question_orale"],
    }


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


# ── Voix ────────────────────────────────────────────────────
# Modèle : gradbot demos/fantasy_shop, mais avec notre propre boucle autour de
# gradbot.run() (et non handle_session) : il faut garder la poignée d'entrée
# pour pousser une nouvelle config quand le tableau change.
# Protocole client : {"type": "start"}, trames audio Opus, {"type": "stop"}.
# En plus des messages gradbot, le serveur envoie {"type": "session", "id", "exercise_id"}
# au démarrage et {"type": "outil", "nom", "resultat"} après chaque outil.


# Vocabulaire favorisé par la transcription Gradium : mots isolés, casse et accents comptent.
# Pas de « o » seul : il prendrait la place de « au » (« x au cube »).
VOCABULAIRE = (
    "logarithme népérien ln sinus cosinus tangente exponentielle carré cube puissance petit grand "
    "développement limité DL équivalent dérivée voisinage ordre coefficient reste x Taylor Young"
).split()


def stt_config() -> str:
    """json_config de la transcription (la langue, « fr », est ajoutée par gradbot)."""
    mots = VOCABULAIRE + [m.capitalize() for m in VOCABULAIRE if m.islower() and len(m) > 2]
    extra = {"keywords": {"words": mots, "boost": float(os.environ.get("STT_KEYWORDS_BOOST", 3))}}
    if delai := os.environ.get("STT_DELAY_FRAMES"):
        extra["delay_in_frames"] = int(delai)
    return json.dumps(extra | (CONFIG.stt.extra_config or {}))


def silence_s(alerte: bool) -> float:
    """Relance après un silence : longue pour laisser réfléchir, courte quand une nouvelle
    ligne fausse attend (la question vient à la première pause, pas 12 s plus tard)."""
    if alerte:
        return float(os.environ.get("SILENCE_ALERTE_S", 4))
    return float(os.environ.get("SILENCE_TIMEOUT_S", 12))


def session_config(instructions: str, *, premiere: bool, alerte: bool = False) -> gradbot.SessionConfig:
    langue = gradbot.LANGUAGES["fr"]
    voix = os.environ.get("KHOLLEUR_VOICE_ID") or gradbot.flagship_voice("Gaspard").voice_id
    # Un outil à la fois : sinon le LLM enchaîne question_suivante et terminer_colle
    # sans attendre la réponse de l'étudiant (vu avec gpt-4.1).
    llm_extra = {"parallel_tool_calls": False} | (CONFIG.llm.extra_config or {})
    return gradbot.SessionConfig(
        **CONFIG.session_kwargs
        | {
            "llm_extra_config": json.dumps(llm_extra),
            "stt_extra_config": stt_config(),
            "voice_id": voix,
            "instructions": instructions,
            "language": langue,
            "tools": outils.OUTILS,
            "rewrite_rules": langue.rewrite_rules,
            # Sans effet après le démarrage : gradbot ne salue qu'une fois.
            "assistant_speaks_first": premiere,
            "silence_timeout_s": silence_s(alerte),
        }
    )


class Transcription:
    """Regroupe les morceaux de texte STT / TTS en répliques pour state.add_turn."""

    def __init__(self) -> None:
        self.qui: state.Qui | None = None
        self.tour: int | None = None
        self.morceaux: list[str] = []
        self.t = 0.0

    def ajouter(self, qui: state.Qui, texte: str, tour: int | None = None) -> None:
        if (qui, tour) != (self.qui, self.tour):
            self.vider()
        if not self.morceaux:
            self.t = time.time() - state.get_session().started_at
        self.qui, self.tour = qui, tour
        self.morceaux.append(texte)

    def vider(self) -> None:
        if self.morceaux:
            tour = state.add_turn(self.qui, " ".join(" ".join(self.morceaux).split()))
            tour.t = self.t  # début de la réplique, pas sa fin
        self.morceaux = []


# Phrase de fin du DÉROULÉ (prompts/kholleur_system.md). En audio, gpt-4.1 la dit parfois
# sans appeler terminer_colle : le serveur termine alors la khôlle à sa place.
PHRASE_DE_FIN = re.compile(r"rédige votre compte[- ]rendu", re.IGNORECASE)


class Kholle:
    """La khôlle vocale en cours : une session gradbot reliée au navigateur."""

    def __init__(self, websocket: fastapi.WebSocket) -> None:
        self.websocket = websocket
        self.boucle = asyncio.get_running_loop()
        self.entree: gradbot.SessionInputHandle | None = None
        self.transcription = Transcription()
        self.deja_faux: set[str] = set()
        self.alerte = False  # consignes en cours avec l'alerte « nouvelle erreur »
        self.verrou = asyncio.Lock()
        self.taches: set[asyncio.Task] = set()
        self.dit: dict[int | None, str] = {}  # texte du khôlleur par tour

    def config(self, *, premiere: bool = False) -> gradbot.SessionConfig:
        s = state.get_session()
        instructions = prompts.build_instructions(s, self.deja_faux)
        self.alerte = bool(prompts.nouvelles_erreurs(s.board_lines, self.deja_faux))
        self.deja_faux = prompts.erreurs(s.board_lines)
        return session_config(instructions, premiere=premiere, alerte=self.alerte)

    async def pousser_config(self) -> None:
        """Nouvelles consignes (tableau, question) ; gradbot garde l'historique."""
        async with self.verrou:
            await self.entree.send_config(self.config())

    def _en_tache(self, coro) -> None:
        tache = asyncio.create_task(coro)
        self.taches.add(tache)
        tache.add_done_callback(self.taches.discard)

    async def boucle_entree(self) -> None:
        try:
            while True:
                brut = await self.websocket.receive()
                if brut["type"] == "websocket.disconnect":
                    break
                if brut.get("bytes") is not None:
                    await self.entree.send_audio(brut["bytes"])
                elif brut.get("text") and json.loads(brut["text"]).get("type") == "stop":
                    break
        except (fastapi.WebSocketDisconnect, RuntimeError):
            pass
        finally:
            with contextlib.suppress(Exception):
                await self.entree.close()

    async def boucle_sortie(self, sortie: gradbot.SessionOutputHandle) -> None:
        try:
            while (msg := await sortie.receive()) is not None:
                await self.traiter(msg)
        except Exception as exc:
            logger.warning("Sortie gradbot interrompue : %r", exc)
            await _envoyer_erreur(self.websocket, exc)
        finally:
            self.transcription.vider()
            with contextlib.suppress(Exception):
                await self.websocket.close()

    async def traiter(self, msg: gradbot.MsgOut) -> None:
        if msg.msg_type == "tool_call":
            self._en_tache(self.outil(gradbot.ToolHandle(msg.tool_call_handle, msg.tool_call)))
            return
        schema = gradbot.schemas.from_msg(msg)
        if schema is None:
            return
        if isinstance(schema, gradbot.schemas.UserText):
            self.transcription.ajouter("eleve", schema.text)
        elif isinstance(schema, gradbot.schemas.AgentText):
            self.transcription.ajouter("kholleur", schema.text, schema.turn_idx)
            self.dit[schema.turn_idx] = f"{self.dit.get(schema.turn_idx, '')} {schema.text}"
            if PHRASE_DE_FIN.search(self.dit[schema.turn_idx]) and not state.get_session().finished:
                logger.warning("Phrase de fin sans terminer_colle : le serveur termine la khôlle")
                self._en_tache(self.terminer())
        elif isinstance(schema, gradbot.schemas.SessionEvent) and schema.event == "llm_started" and self.alerte:
            # gradbot lit la config au lancement du LLM : cette réponse a vu l'alerte,
            # on la retire pour que les suivantes ne reviennent pas sans cesse sur la ligne.
            self._en_tache(self.pousser_config())
        await self.websocket.send_json(schema.model_dump())
        if msg.msg_type == "audio":
            await self.websocket.send_bytes(msg.data)

    async def outil(self, h: gradbot.ToolHandle) -> None:
        logger.info("Outil %s", h.name)
        executer = outils.EXECUTER.get(h.name)
        if executer is None:
            await h.send_error(f"Outil inconnu : {h.name}")
            return
        if h.name == "terminer_colle" and state.get_session().finished:
            await h.send_json({"ok": True})  # déjà terminée sur la phrase de fin
            return
        try:
            resultat = executer()
            if h.name == "question_suivante" and "question" in resultat:
                await self.pousser_config()
            if h.name == "terminer_colle":
                self.lancer_compte_rendu()
            await h.send_json(resultat)
        except Exception as exc:
            logger.exception("Outil %s en échec", h.name)
            await h.send_error(str(exc))
            return
        await self.signaler_outil(h.name, resultat)

    async def terminer(self) -> None:
        """terminer_colle sans appel du LLM (phrase de fin dite seule)."""
        resultat = outils.terminer_colle()
        self.lancer_compte_rendu()
        await self.signaler_outil("terminer_colle", resultat)

    def lancer_compte_rendu(self) -> None:
        self.transcription.vider()
        _en_arriere_plan(_lancer_compte_rendu())

    async def signaler_outil(self, nom: str, resultat: dict) -> None:
        with contextlib.suppress(Exception):
            await self.websocket.send_json({"type": "outil", "nom": nom, "resultat": resultat})


_en_cours: Kholle | None = None
_taches: set[asyncio.Future] = set()


def _en_arriere_plan(coro) -> None:
    tache = asyncio.ensure_future(coro)
    _taches.add(tache)
    tache.add_done_callback(_taches.discard)


async def _lancer_compte_rendu() -> None:
    """POST /api/report (lane C), servi par l'application elle-même sans passer par le réseau."""
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://kholle", timeout=300
        ) as client:
            r = await client.post("/api/report")
        if r.is_error:
            logger.warning("Compte-rendu : HTTP %s %s", r.status_code, r.text[:200])
    except Exception:
        logger.exception("Compte-rendu impossible")


async def _envoyer_erreur(websocket: fastapi.WebSocket, exc: Exception | str) -> None:
    with contextlib.suppress(Exception):
        await websocket.send_json({"type": "error", "message": str(exc)})


@state.on_board_change
def _tableau_change(session: state.Session) -> None:
    """Pousse le nouveau tableau au khôlleur, quel que soit le fil qui a appelé set_board."""
    k = _en_cours
    if k is None or k.entree is None:
        return
    envoi = asyncio.run_coroutine_threadsafe(k.pousser_config(), k.boucle)
    envoi.add_done_callback(_signaler_echec_envoi)


def _signaler_echec_envoi(envoi) -> None:
    if not envoi.cancelled() and envoi.exception():
        logger.error("Envoi du tableau en échec : %r", envoi.exception())


@app.websocket("/ws/chat")
async def ws_chat(websocket: fastapi.WebSocket):
    global _en_cours
    await websocket.accept()
    debut = await websocket.receive_json()
    if debut.get("type") != "start":
        await websocket.close(code=4000, reason="Message start attendu")
        return
    if not CONFIG.gradbot_server.url and not CONFIG.gradium.api_key:
        await _envoyer_erreur(websocket, "GRADIUM_API_KEY manquante dans kholle_live/.env")
        await websocket.close()
        return

    state.new_session(state.get_session().exercise_id)
    k = Kholle(websocket)
    try:
        k.entree, sortie = await gradbot.run(
            **CONFIG.client_kwargs,
            session_config=k.config(premiere=True),
            input_format=gradbot.AudioFormat.OggOpus,
            output_format=CONFIG.audio_format,
        )
    except Exception as exc:
        logger.exception("Démarrage de la session vocale impossible")
        await _envoyer_erreur(websocket, exc)
        await websocket.close()
        return

    _en_cours = k
    s = state.get_session()
    logger.info("Khôlle vocale démarrée (session %s)", s.id)
    try:
        await websocket.send_json({"type": "session", "id": s.id, "exercise_id": s.exercise_id})
        await asyncio.gather(k.boucle_sortie(sortie), k.boucle_entree())
    finally:
        if _en_cours is k:
            _en_cours = None
        for tache in k.taches:
            tache.cancel()
        logger.info("Khôlle vocale terminée")


# Monte /static (notre dossier) et /static/js (worklets audio fournis par gradbot),
# plus GET / -> static/index.html et GET /api/audio-config. À garder en dernier.
gradbot.routes.setup(app, config=CONFIG, static_dir=ICI / "static")
