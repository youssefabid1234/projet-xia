"""Lane A : consignes, outils et boucle vocale (gradbot.run remplacé par un double)."""

import asyncio
import json
import time
from types import SimpleNamespace

import gradbot
import pydantic
import pytest
from fastapi.testclient import TestClient

import main
from kholle import exercises, outils, prompts, state


def ligne(n, texte, verdict="?", barre=False, detail=None):
    return state.BoardLine(n, texte, barre, True, False, None, None, None, None, None, verdict, detail)


# ── Consignes ───────────────────────────────────────────────


def test_consignes_exercice_sans_indices():
    s = state.new_session("dl_ln_sin")
    ex = exercises.get("dl_ln_sin")
    texte = prompts.build_instructions(s)
    assert ex["enonce_latex"] in texte
    assert ex["enonce_oral"] in texte
    assert ex["reponse"]["latex"] in texte
    assert ex["pieges"][0] in texte
    assert "(tableau vide)" in texte
    assert "{exercice}" not in texte and "{tableau}" not in texte
    for indice in ex["indices"] + ex["questions_suivantes"][0]["indices"]:
        assert indice not in texte
    assert "QUESTION EN COURS" not in texte

    s.question_index = 1
    texte = prompts.build_instructions(s)
    suite = ex["questions_suivantes"][0]
    assert suite["question_orale"] in texte and suite["reponse"] in texte
    assert all(indice not in texte for indice in suite["indices"])


def test_consignes_tableau():
    s = state.new_session("dl_ln_sin")
    s.board_lines = [
        ligne(1, "u = sin x", "ok"),
        ligne(2, "ln(1+u) = u - u^2/2", "?"),
        ligne(3, "f(x) = x - x^2/2 - x^3/6", "faux", detail="coefficient de x^3"),
        ligne(4, "f(x) = x", "faux", barre=True),
    ]
    texte = prompts.build_instructions(s)
    assert "L1 ✓ u = sin x\n" in texte
    assert "L2 ? ln(1+u) = u - u^2/2\n" in texte
    assert "NOUVELLE ERREUR L3 ✗ f(x) = x - x^2/2 - x^3/6 — coefficient de x^3\n" in texte
    assert texte.rstrip().endswith("L4 (barrée)")

    deja = prompts.erreurs(s.board_lines)
    assert deja == {"f(x) = x - x^2/2 - x^3/6"}
    # La même erreur, renumérotée, n'est plus nouvelle.
    s.board_lines = [ligne(4, "f(x)  =  x - x^2/2 - x^3/6", "faux")]
    texte = prompts.build_instructions(s, deja)
    assert "L4 ✗ f(x)  =  x - x^2/2 - x^3/6" in texte and "NOUVELLE ERREUR L" not in texte


# ── Outils ──────────────────────────────────────────────────


def test_donner_indice_niveaux_par_question():
    state.new_session("dl_ln_sin")
    ex = exercises.get("dl_ln_sin")
    for n in (1, 2, 3):
        assert outils.donner_indice() == {"niveau": n, "indice": ex["indices"][n - 1]}
    assert outils.donner_indice() == {"indice": None, "message": "plus d'indice"}

    assert outils.question_suivante() == {"question": ex["questions_suivantes"][0]["question_orale"]}
    assert outils.donner_indice()["niveau"] == 1
    s = state.get_session()
    assert [(h.question_index, h.niveau) for h in s.hints] == [(0, 1), (0, 2), (0, 3), (1, 1)]


def test_question_suivante_puis_fin():
    s = state.new_session("dl_exp_sin")
    assert "question" in outils.question_suivante()
    assert outils.question_suivante() == {"fin": True}
    assert s.question_index == 1
    assert outils.terminer_colle() == {"ok": True} and s.finished


def test_outils_declares():
    assert [o.name for o in outils.OUTILS] == list(outils.EXECUTER)
    for o in outils.OUTILS:
        assert json.loads(o.parameters_json)["type"] == "object"


# ── Boucle vocale ───────────────────────────────────────────


class FausseSession:
    """Double de gradbot.run : note ce qu'on lui envoie, émet ce que le test injecte."""

    def __init__(self):
        self.config_initiale = None
        self.configs = []
        self.audio = []
        self.resultats = []

    async def run(self, *, session_config, **_):
        self.config_initiale = session_config
        self.boucle = asyncio.get_running_loop()
        self.file = asyncio.Queue()
        session = self

        class Entree:
            async def send_audio(self, data):
                session.audio.append(data)

            async def send_config(self, config):
                session.configs.append(config)

            async def close(self):
                session.file.put_nowait(None)

        class Sortie:
            async def receive(self):
                return await session.file.get()

        return Entree(), Sortie()

    def emettre(self, msg_type, **champs):
        msg = SimpleNamespace(msg_type=msg_type, event=None, data=None, **champs)
        self.boucle.call_soon_threadsafe(self.file.put_nowait, msg)

    def appel_outil(self, nom):
        session = self

        class Poignee:
            async def send(self, resultat):
                session.resultats.append((nom, json.loads(resultat)))

            async def send_error(self, erreur):
                session.resultats.append((nom, {"erreur": erreur}))

        appel = SimpleNamespace(tool_name=nom, args_json="{}", call_id=nom)
        self.emettre("tool_call", tool_call=appel, tool_call_handle=Poignee())


def attendre(condition, delai=3.0):
    fin = time.time() + delai
    while not condition():
        assert time.time() < fin, "délai dépassé"
        time.sleep(0.02)


@pytest.fixture
def fausse(monkeypatch):
    f = FausseSession()
    monkeypatch.setattr(gradbot, "run", f.run)
    monkeypatch.setattr(main.CONFIG.gradium, "api_key", pydantic.SecretStr("test"))
    monkeypatch.delenv("KHOLLEUR_VOICE_ID", raising=False)
    monkeypatch.setenv("SILENCE_TIMEOUT_S", "12")
    rapports = []

    async def faux_compte_rendu():
        rapports.append(state.get_session().id)

    monkeypatch.setattr(main, "_lancer_compte_rendu", faux_compte_rendu)
    f.rapports = rapports
    return f


def test_kholle_vocale(fausse):
    client = TestClient(main.app)
    client.post("/api/session/new", json={"exercise_id": "dl_ln_sin"})
    ancienne = state.get_session().id
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"type": "start"})
        debut = ws.receive_json()
        s = state.get_session()
        assert debut == {"type": "session", "id": s.id, "exercise_id": "dl_ln_sin"}
        assert s.id != ancienne

        cfg = fausse.config_initiale
        assert cfg.voice_id == gradbot.flagship_voice("Gaspard").voice_id
        assert cfg.language == gradbot.Lang.Fr and cfg.assistant_speaks_first
        assert cfg.silence_timeout_s == 12.0
        assert [t.name for t in cfg.tools] == list(outils.EXECUTER)
        assert "Donnez-moi le développement limité" in cfg.instructions

        # Transcription : répliques regroupées, relayées au navigateur.
        fausse.emettre("tts_text", text="Bonjour,", turn_idx=0, start_s=0.0, stop_s=0.4)
        fausse.emettre("tts_text", text="votre prénom ?", turn_idx=0, start_s=0.4, stop_s=1.0)
        fausse.emettre("stt_text", text="Pierre", start_s=1.5, stop_s=2.0)
        assert ws.receive_json()["type"] == "agent_text"
        assert ws.receive_json()["type"] == "agent_text"
        assert ws.receive_json() == {"type": "user_text", "text": "Pierre", "stop_s": 2.0, "turn_idx": None}
        ws.send_bytes(b"opus")
        attendre(lambda: fausse.audio == [b"opus"])

        # Outil.
        fausse.appel_outil("donner_indice")
        msg = ws.receive_json()
        assert msg["type"] == "outil" and msg["resultat"]["niveau"] == 1
        assert fausse.resultats[-1][1]["niveau"] == 1

        # Tableau poussé en direct, depuis un autre fil.
        state.set_board([ligne(1, "f(x) = x - x^2/2 - x^3/6", "faux")])
        attendre(lambda: len(fausse.configs) == 1)
        assert "NOUVELLE ERREUR L1 ✗" in fausse.configs[0].instructions
        state.set_board([ligne(1, "f(x) = x - x^2/2 - x^3/6", "faux"), ligne(2, "donc", "?")])
        attendre(lambda: len(fausse.configs) == 2)
        assert "NOUVELLE ERREUR L" not in fausse.configs[1].instructions
        assert not fausse.configs[1].assistant_speaks_first

        # Question suivante : nouvelles consignes avant la réponse à l'outil.
        fausse.appel_outil("question_suivante")
        assert ws.receive_json()["nom"] == "question_suivante"
        assert "QUESTION EN COURS" in fausse.configs[-1].instructions

        fausse.emettre("tts_text", text="On s'arrête là.", turn_idx=1, start_s=3.0, stop_s=4.0)
        fausse.appel_outil("terminer_colle")
        assert ws.receive_json()["type"] == "agent_text"
        assert ws.receive_json() == {"type": "outil", "nom": "terminer_colle", "resultat": {"ok": True}}
        attendre(lambda: fausse.rapports == [s.id])
        assert s.finished
        ws.send_json({"type": "stop"})

    attendre(lambda: main._en_cours is None)
    assert [(t.qui, t.texte) for t in s.transcript] == [
        ("kholleur", "Bonjour, votre prénom ?"),
        ("eleve", "Pierre"),
        ("kholleur", "On s'arrête là."),
    ]
    assert all(a.t <= b.t for a, b in zip(s.transcript, s.transcript[1:]))


def test_sans_cle_gradium(monkeypatch):
    monkeypatch.setattr(main.CONFIG.gradium, "api_key", None)
    with TestClient(main.app).websocket_connect("/ws/chat") as ws:
        ws.send_json({"type": "start"})
        assert "GRADIUM_API_KEY" in ws.receive_json()["message"]
