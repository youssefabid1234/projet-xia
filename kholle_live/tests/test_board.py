import json
import threading
import time
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import main
from kholle import board, board_reader, exercises, state
from kholle.state import BoardLine

PNG_A = b"\x89PNG\r\n\x1a\n" + b"A" * 32
PNG_B = b"\x89PNG\r\n\x1a\n" + b"B" * 32


def ligne_brute(n, lhs, rhs, ordre=3, var="x"):
    return {
        "n": n, "texte": f"{lhs} = {rhs} + o({var}^{ordre})", "barre": False, "lisible": True,
        "verifiable": True, "lhs": lhs, "rhs": rhs, "var": var, "point": "0", "ordre": ordre,
    }


class FauxOpenAI:
    """1re lecture au fil appelant, 2e (à défaut la 1re) au fil de relecture, lancées
    ensemble ; une exception est levée."""

    def __init__(self, *lectures):
        self.lectures = lectures
        self.appels = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.appels.append(kwargs)
        relecture = threading.current_thread().name.startswith("relecture")
        lecture = self.lectures[min(int(relecture), len(self.lectures) - 1)]
        if isinstance(lecture, Exception):
            raise lecture
        return SimpleNamespace(output_text=json.dumps({"lines": lecture}))


JUSTE = ligne_brute(1, "f(x)", "x - x**2/2 + x**3/6")
FAUSSE = ligne_brute(2, "f(x)", "x - x**2/2 - x**3/6")
FAUSSE_RELUE_JUSTE = ligne_brute(2, "f(x)", "x - x**2/2 + x**3/6")


def lire(monkeypatch, *lectures):
    faux = FauxOpenAI(*lectures)
    monkeypatch.setattr(board_reader, "_client", lambda: faux)
    avant = board_reader.stats()
    lignes = board_reader.read_board(PNG_A, exercises.get("dl_ln_sin"))
    apres = board_reader.stats()
    ecart = {k: apres[k] - avant[k] for k in apres}
    return lignes, len(faux.appels), ecart


def test_pas_de_relecture_sans_ligne_fausse(monkeypatch):
    # La seconde lecture part quand même, mais n'est ni attendue ni comptée.
    lignes, _, ecart = lire(monkeypatch, [JUSTE])
    assert [l.verdict for l in lignes] == ["ok"]
    assert ecart == {"relectures": 0, "desaccords": 0}


def test_faux_confirme_par_une_seconde_lecture(monkeypatch):
    lignes, appels, ecart = lire(monkeypatch, [JUSTE, FAUSSE], [JUSTE, FAUSSE])
    assert [l.verdict for l in lignes] == ["ok", "faux"]
    assert lignes[1].detail == "erreur sur le terme en x^3"
    assert appels == 2
    assert ecart == {"relectures": 1, "desaccords": 0}


def test_faux_non_confirme_devient_inconnu(monkeypatch):
    lignes, appels, ecart = lire(monkeypatch, [JUSTE, FAUSSE], [JUSTE, FAUSSE_RELUE_JUSTE])
    assert [l.verdict for l in lignes] == ["ok", "?"]
    assert lignes[1].texte == FAUSSE["texte"]
    assert appels == 2
    assert ecart == {"relectures": 1, "desaccords": 1}


def test_faux_absent_de_la_seconde_lecture_devient_inconnu(monkeypatch):
    lignes, _, ecart = lire(monkeypatch, [JUSTE, FAUSSE], [JUSTE])
    assert [l.verdict for l in lignes] == ["ok", "?"]
    assert ecart == {"relectures": 1, "desaccords": 1}


def test_seconde_lecture_en_echec_jamais_faux(monkeypatch):
    lignes, appels, _ = lire(monkeypatch, [JUSTE, FAUSSE], TimeoutError("réseau"))
    assert [l.verdict for l in lignes] == ["ok", "?"]
    assert appels == 2


def test_read_board_verifie_chaque_ligne(monkeypatch):
    faux = FauxOpenAI([
        ligne_brute(1, "f(x)", "x - x**2/2 + x**3/6"),
        ligne_brute(2, "f(x)", "x - x**2/2 - x**3/6"),
        {"n": 3, "texte": "on pose u = sin x", "barre": False, "lisible": True, "verifiable": False,
         "lhs": None, "rhs": None, "var": None, "point": None, "ordre": None},
    ])
    monkeypatch.setattr(board_reader, "_client", lambda: faux)
    monkeypatch.setenv("VISION_MODEL", "modele-test")

    lignes = board_reader.read_board(PNG_A, exercises.get("dl_ln_sin"))

    assert [l.verdict for l in lignes] == ["ok", "faux", "?"]
    assert lignes[1].detail == "erreur sur le terme en x^3"
    appel = faux.appels[0]
    assert appel["model"] == "modele-test"
    assert "f(x) = log(1+sin(x))" in appel["instructions"]
    assert "{definitions}" not in appel["instructions"]
    assert appel["text"]["format"]["type"] == "json_schema"
    image = appel["input"][0]["content"][0]
    assert image["image_url"].startswith("data:image/png;base64,")


@pytest.fixture
def client(monkeypatch, tmp_path):
    lectures = []

    def faux_read_board(png, exercise):
        lectures.append(png)
        time.sleep(0.2)
        fausse = png == PNG_B
        rhs = "x - x**2/2 - x**3/6" if fausse else "x - x**2/2 + x**3/6"
        return [board_reader.check_line(BoardLine(**ligne_brute(1, "f(x)", rhs)), exercise["definitions_sympy"])]

    monkeypatch.setattr(board, "read_board", faux_read_board)
    monkeypatch.setattr(board, "DOSSIER_ECHANTILLONS", tmp_path)
    board.reinitialiser()
    with TestClient(main.app) as c:
        c.post("/api/session/new", json={})
        c.lectures = lectures
        c.dossier = tmp_path
        yield c


def attendre_lignes(client, verdict, delai=5.0):
    fin = time.time() + delai
    while time.time() < fin:
        etat = client.get("/api/board/state").json()
        if etat["lines"] and etat["lines"][0]["verdict"] == verdict and not etat["lecture_en_cours"]:
            return etat
        time.sleep(0.05)
    raise AssertionError(f"pas de ligne {verdict} : {etat}")


def test_post_board_puis_etat(client):
    assert client.get("/api/board/state").json()["lines"] == []
    assert client.get("/api/board/latest.png").status_code == 404

    r = client.post("/api/board", content=PNG_B, headers={"content-type": "image/png"})
    assert r.status_code == 202

    etat = attendre_lignes(client, "faux")
    assert etat["lines"][0]["detail"] == "erreur sur le terme en x^3"
    assert etat["image_url"].startswith("/api/board/latest.png")
    assert etat["updated_at"] > 0
    assert client.get("/api/board/latest.png").content == PNG_B
    assert state.get_session().board_lines[0].verdict == "faux"


def test_image_identique_ignoree(client):
    client.post("/api/board", content=PNG_A)
    attendre_lignes(client, "ok")
    r = client.post("/api/board", content=PNG_A)
    assert r.json()["status"] == "identique"
    assert client.lectures == [PNG_A]


def test_une_lecture_a_la_fois_et_seule_la_derniere_image(client):
    autre = b"\x89PNG\r\n\x1a\n" + b"C" * 32
    client.post("/api/board", content=PNG_A)
    client.post("/api/board", content=autre)
    client.post("/api/board", content=PNG_B)
    attendre_lignes(client, "faux")
    assert client.lectures == [PNG_A, PNG_B]


def test_image_vide_refusee(client):
    assert client.post("/api/board", content=b"").status_code == 400


def test_echantillon_eval(client):
    r = client.post("/api/eval/sample?label=E3", content=PNG_A)
    assert r.status_code == 200
    fichiers = list(client.dossier.glob("E3_*.png"))
    assert len(fichiers) == 1 and fichiers[0].read_bytes() == PNG_A
    assert client.post("/api/eval/sample?label=../x", content=PNG_A).status_code == 422
