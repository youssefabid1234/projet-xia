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

    assert "C'est la dernière question" not in texte
    assert "N'invente jamais de question" in texte

    s.question_index = 1
    texte = prompts.build_instructions(s)
    suite = ex["questions_suivantes"][0]
    assert suite["question_orale"] in texte and suite["reponse"] in texte
    assert all(indice not in texte for indice in suite["indices"])
    assert "C'est la dernière question" in texte
    assert "N'invente jamais de question" not in texte

    # Sans question suivante, l'exercice principal est la dernière question.
    assert "C'est la dernière question" in prompts.build_instructions(state.new_session("dl_cos_sin"))


def test_consignes_tableau():
    s = state.new_session("dl_ln_sin")
    s.board_lines = [
        ligne(1, "u = sin x", "ok"),
        ligne(2, "ln(1+u) = u - u^2/2", "?"),
        ligne(3, "f(x) = x - x^2/2 - x^3/6", "faux", detail="coefficient de x^3"),
        ligne(4, "f(x) = x", "faux", barre=True),
    ]
    # On teste le tableau seul : le texte du persona peut citer ces marqueurs.
    tableau = prompts.rendre_tableau(s.board_lines)
    assert tableau.splitlines() == [
        "L1 ✓ u = sin x",
        "L2 ? ln(1+u) = u - u^2/2",
        "NOUVELLE ERREUR L3 ✗ f(x) = x - x^2/2 - x^3/6 — coefficient de x^3",
        "L4 (barrée)",
        "→ À traiter maintenant : L3 (nouvelle erreur). "
        "Désigne cette ligne et pose une question qui oriente vers l'erreur.",
    ]
    assert tableau in prompts.build_instructions(s)

    consignes = prompts.build_instructions(s)
    assert consignes.startswith(
        "PRIORITÉ ABSOLUE : l'étudiant vient d'écrire au tableau une ligne fausse.\n"
        "- ligne 3 : « f(x) = x - x^2/2 - x^3/6 » (coefficient de x^3)\n"
    )

    deja = prompts.erreurs(s.board_lines)
    assert deja == {"f(x) = x - x^2/2 - x^3/6"}
    assert prompts.build_instructions(s, deja).startswith(prompts.SILENCE)
    assert prompts.SILENCE not in consignes
    # La même erreur, renumérotée, n'est plus nouvelle.
    s.board_lines = [ligne(4, "f(x)  =  x - x^2/2 - x^3/6", "faux")]
    assert prompts.rendre_tableau(s.board_lines, deja) == "L4 ✗ f(x)  =  x - x^2/2 - x^3/6"
    assert prompts.rendre_tableau(s.board_lines, deja) in prompts.build_instructions(s, deja)


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
        msg = SimpleNamespace(**{"msg_type": msg_type, "event": None, "data": None} | champs)
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
        assert json.loads(cfg.llm_extra_config)["parallel_tool_calls"] is False
        assert [t.name for t in cfg.tools] == list(outils.EXECUTER)
        stt = json.loads(cfg.stt_extra_config)
        assert {"ln", "logarithme", "Logarithme", "cube"} <= set(stt["keywords"]["words"])
        assert "language" not in stt  # gradbot la met à « fr » ; ne pas l'écraser
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
        assert fausse.configs[0].instructions.startswith("PRIORITÉ ABSOLUE")
        assert fausse.configs[0].silence_timeout_s == 4.0  # question à la première pause
        # Le LLM démarre avec l'alerte : elle est retirée des consignes suivantes.
        fausse.emettre("event", event=SimpleNamespace(event_type="llm_started"))
        assert ws.receive_json() == {"type": "event", "event": "llm_started"}
        attendre(lambda: len(fausse.configs) == 2)
        assert not fausse.configs[1].instructions.startswith("PRIORITÉ ABSOLUE")
        assert fausse.configs[1].silence_timeout_s == 12.0
        fausse.emettre("event", event=SimpleNamespace(event_type="llm_started"))
        ws.receive_json()
        state.set_board([ligne(1, "f(x) = x - x^2/2 - x^3/6", "faux"), ligne(2, "donc", "?")])
        attendre(lambda: len(fausse.configs) == 3)
        assert "NOUVELLE ERREUR L" not in fausse.configs[2].instructions
        assert not fausse.configs[2].assistant_speaks_first

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


def test_phrase_de_fin_sans_outil(fausse):
    """Le LLM dit la phrase de fin sans appeler terminer_colle : le serveur termine."""
    client = TestClient(main.app)
    client.post("/api/session/new", json={"exercise_id": "dl_ln_sin"})
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"type": "start"})
        ws.receive_json()
        s = state.get_session()
        fausse.emettre("tts_text", text="Très bien, on s'arrête là, je rédige", turn_idx=3, start_s=0.0, stop_s=1.0)
        fausse.emettre("tts_text", text="votre compte-rendu.", turn_idx=3, start_s=1.0, stop_s=2.0)
        recus = [ws.receive_json() for _ in range(3)]
        assert {"type": "outil", "nom": "terminer_colle", "resultat": {"ok": True}} in recus
        attendre(lambda: fausse.rapports == [s.id])
        assert s.finished

        # Appel tardif du LLM : réponse ok, ni second compte-rendu ni second message.
        fausse.appel_outil("terminer_colle")
        attendre(lambda: fausse.resultats == [("terminer_colle", {"ok": True})])
        ws.send_json({"type": "stop"})
    attendre(lambda: main._en_cours is None)
    assert fausse.rapports == [s.id]


def test_sans_cle_gradium(monkeypatch):
    monkeypatch.setattr(main.CONFIG.gradium, "api_key", None)
    with TestClient(main.app).websocket_connect("/ws/chat") as ws:
        ws.send_json({"type": "start"})
        assert "GRADIUM_API_KEY" in ws.receive_json()["message"]
