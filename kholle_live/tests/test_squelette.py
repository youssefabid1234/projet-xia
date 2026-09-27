from fastapi.testclient import TestClient

import main
from kholle import state

client = TestClient(main.app)


def test_session_et_exercice():
    r = client.post("/api/session/new", json={})
    assert r.status_code == 200 and r.json()["exercise_id"] == "dl_ln_sin"
    assert client.get("/api/exercise").json()["titre"] == "DL de ln(1 + sin x)"

    r = client.post("/api/session/new", json={"exercise_id": "dl_exp_sin"})
    assert r.json()["exercise_id"] == "dl_exp_sin"
    assert client.post("/api/session/new", json={"exercise_id": "inconnu"}).status_code == 404


def test_transcript():
    client.post("/api/session/new")
    r = client.post("/api/transcript", json={"qui": "eleve", "texte": "Bonjour"})
    assert r.json()["qui"] == "eleve"
    assert state.get_session().transcript[-1].texte == "Bonjour"
    assert client.post("/api/transcript", json={"qui": "prof", "texte": "x"}).status_code == 422


def test_set_board_instantane_et_rappel():
    state.new_session("dl_ln_sin")
    vus = []
    state.on_board_change(lambda s: vus.append(len(s.board_lines)))
    ligne = state.BoardLine(1, "f(x) = x + o(x)", False, True, True, "f(x)", "x", "x", "0", 1)
    state.set_board([ligne])
    assert vus == [1]
    assert state.get_session().board_snapshots[-1]["lines"][0]["texte"] == "f(x) = x + o(x)"


def test_pages_statiques():
    assert client.get("/static/index.html").status_code == 200
    assert client.get("/static/board.html").status_code == 200
