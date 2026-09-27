import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main
from kholle import report, state
from kholle.state import HintUse, Turn

FIXTURE = Path(__file__).parent / "fixtures" / "session_demo.json"
BRUT = {
    "appreciation": "Oral clair, justifications présentes.",
    "points_forts": ["DL de $\\sin x$ connu"],
    "erreurs": [
        {"ligne": 3, "description": "Troncature de $\\ln(1+u)$ à l'ordre 2.", "corrigee_apres_question": True},
        {"ligne": 42, "description": "Ligne inexistante.", "corrigee_apres_question": False},
    ],
    "a_retravailler": [
        {"tag": "Ordre de troncature", "conseil": "Anticiper l'ordre utile."},
        {"tag": "tag inventé", "conseil": "À ignorer."},
    ],
    "oral": 3.7,
    "rigueur": 7,
    "cours": "3.5",
}


def session_demo():
    return report.session_depuis_dict(json.loads(FIXTURE.read_text(encoding="utf-8")))


def test_autonomie():
    assert report.autonomie([]) == 5
    assert report.autonomie([HintUse(0, 0, 1)]) == 4.5
    assert report.autonomie([HintUse(0, 0, 1), HintUse(0, 0, 2), HintUse(0, 0, 3)]) == 2
    assert report.autonomie([HintUse(0, 0, 3)] * 4) == 0


@pytest.mark.parametrize("reponse, attendu", [
    ("Bonjour, je m'appelle Camille.", "Camille"),
    ("Moi c'est Jean-Baptiste", "Jean-Baptiste"),
    ("Léa.", "Léa"),
    ("Bonjour !", "l'étudiant"),
    ("Je préfère commencer tout de suite par l'exercice si possible", "l'étudiant"),
])
def test_prenom(reponse, attendu):
    s = session_demo()
    s.transcript = [Turn(0, "kholleur", "Comment vous appelez-vous ?"), Turn(3, "eleve", reponse)]
    assert report.prenom(s) == attendu


def test_prenom_fixture_et_sans_transcription():
    s = session_demo()
    assert report.prenom(s) == "Camille"
    s.transcript = []
    assert report.prenom(s) == "l'étudiant"


def test_exercices_conseilles():
    ids = [e["id"] for e in report.exercices_conseilles(["ordre de troncature"], "dl_ln_sin")]
    assert ids == ["dl_exp_sin", "dl_cos_sin"]
    assert report.exercices_conseilles(["limites par DL"], "dl_ln_sin")[0]["id"] == "lim_inv_sin2"


def test_normaliser():
    cr = report.normaliser(BRUT, session_demo())
    assert (cr["oral"], cr["rigueur"], cr["cours"]) == (3.5, 5.0, 3.5)
    assert [e["ligne"] for e in cr["erreurs"]] == [3, None]
    assert cr["a_retravailler"] == [{"tag": "ordre de troncature", "conseil": "Anticiper l'ordre utile."}]


def test_dossier_historique():
    d = report.construire_dossier(session_demo())
    assert "[02:22] ligne 3 barrée" in d["historique_tableau"]
    assert d["indices_donnes"][0]["indice"].startswith("Que vaut f(x) moins x")
    assert d["transcription"][1] == "[00:04] Étudiant : Bonjour, je m'appelle Camille."


def test_tex_garde_les_formules():
    assert report.tex("a_b $x_1$ 50%") == r"a\_b $x_1$ 50\%"
    assert report.tex("prix : 5 $") == r"prix : 5 \$"


@pytest.fixture
def client(tmp_path, monkeypatch):
    async def faux_moteur(dossier):
        return BRUT, "pipelex"
    monkeypatch.setattr(report, "executer_methode", faux_moteur)
    monkeypatch.setattr(report, "RAPPORTS", tmp_path / "reports")
    monkeypatch.setattr(report, "PROFIL", tmp_path / "profile.json")
    return TestClient(main.app)


def test_routes(client, tmp_path):
    demo = session_demo()
    s = state.new_session("dl_ln_sin")
    s.transcript, s.hints, s.board_lines = demo.transcript, demo.hints, demo.board_lines
    assert client.get("/api/report/status").json() == {
        "session_id": s.id, "finished": False, "pret": False, "en_cours": False}
    assert client.get(f"/api/report/latest?session={s.id}").status_code == 404

    r = client.post("/api/report").json()
    assert r["json"]["note"] == 3.5 + 5 + 4.5 + 3.5
    assert r["json"]["eleve"] == "Camille"
    assert "Khôlle de mathématiques — Camille — <span class=\"note\">16,5/20</span>" in r["html"]
    assert "corrigée après question" in r["html"]
    assert len(list((tmp_path / "reports").glob("*.tex"))) == 1

    assert client.get("/api/report/status").json()["pret"] is True
    assert "Prochaine khôlle" in client.get(f"/api/report/latest?session={s.id}").text
    profil = client.get("/api/profile").json()
    assert profil["eleve"] == "Camille"
    assert profil["faiblesses"]["ordre de troncature"]["count"] == 1
    assert profil["historique"][-1]["note"] == 16.5
