import json

import httpx
import pytest
from fastapi.testclient import TestClient

from kholle import llm_proxy
from kholle.llm_proxy import decision

SYSTEME = {"role": "system", "content": "Tu es le khôlleur."}


def requete(*messages):
    return {"model": "gpt-4.1", "stream": True, "messages": [SYSTEME, *messages]}


def eleve(texte):
    return {"role": "user", "content": texte}


@pytest.mark.parametrize("texte", [
    "Donc je développe",
    "alors je pose u égal",
    "ça fait x moins x carré sur",
    "euh",
    "on a ln de un plus u égal u moins…",
    "Donc, je développe,",           # ponctuation de la transcription Gradium
    "Je pose u égal.",
    "et on a d’",                    # élision, apostrophe typographique
])
def test_retenu(texte):
    assert decision(requete(eleve(texte)))[0] is True


@pytest.mark.parametrize("texte", [
    "Voilà.",
    "J'ai fini",
    "Je réfléchis",
    "Oui",
    "Moins un demi",
    "À quel ordre ?",
    "J'obtiens x moins x carré sur deux plus x cube sur six",
    "Donc je développe, voilà",
    "C'est tout, donc",
    "[start]",
])
def test_transmis(texte):
    assert decision(requete(eleve(texte)))[0] is False


def test_relance_apres_silence():
    # Après une réponse du khôlleur : nouveau message « ... ».
    assert decision(requete(eleve("Bonjour"), {"role": "assistant", "content": "Je vous écoute."},
                            eleve("...")))[0] is False
    # Après un fragment retenu : gradbot colle « ... » au même message, éventuellement plusieurs fois.
    assert decision(requete(eleve("Donc, je développe, ...")))[0] is False
    assert decision(requete(eleve("Donc, je développe, ... ...")))[0] is False


def test_outils_toujours_transmis():
    appel = {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function", "function": {"name": "donner_indice", "arguments": "{}"}}]}
    resultat = {"role": "tool", "tool_call_id": "c1", "content": '{"niveau": 1}'}
    assert decision(requete(eleve("Je ne vois pas"), appel))[0] is False
    assert decision(requete(eleve("Je ne vois pas"), appel, resultat))[0] is False
    # Après un résultat d'outil, gradbot relance le LLM avec un message utilisateur vide.
    assert decision(requete(eleve("Je ne vois pas"), appel, resultat, eleve("")))[0] is False
    # Un fragment qui suit un résultat d'outil reste retenu.
    assert decision(requete(eleve("Je ne vois pas"), appel, resultat, eleve("Donc je")))[0] is True


def test_contenu_en_parties():
    assert decision(requete({"role": "user", "content": [{"type": "text", "text": "alors je pose"}]}))[0] is True


# ── Application ─────────────────────────────────────────────

MORCEAUX_AMONT = [
    b'data: {"choices":[{"index":0,"delta":{"role":"assistant","content":"Bonjour"}}]}\n\n',
    b'data: {"choices":[{"index":0,"delta":{"content":"."},"finish_reason":"stop"}]}\n\n',
    b"data: [DONE]\n\n",
]
SSE_AMONT = b"".join(MORCEAUX_AMONT)


class Flux(httpx.AsyncByteStream):
    async def __aiter__(self):
        for morceau in MORCEAUX_AMONT:
            yield morceau


@pytest.fixture
def proxy(monkeypatch):
    monkeypatch.delenv("PROXY_HOLD", raising=False)
    monkeypatch.delenv("PROXY_HOLD_TEXT", raising=False)
    monkeypatch.delenv("PROXY_LOG", raising=False)
    recu = []

    def amont(req: httpx.Request):
        recu.append(req)
        return httpx.Response(200, stream=Flux(), headers={"content-type": "text/event-stream"})

    with TestClient(llm_proxy.app) as client:
        llm_proxy.app.state.client = httpx.AsyncClient(transport=httpx.MockTransport(amont))
        yield client, recu


def evenements(texte):
    return [l[len("data: "):] for l in texte.splitlines() if l.startswith("data: ")]


def test_transmission_intacte(proxy):
    client, recu = proxy
    corps = requete(eleve("Voilà."))
    r = client.post("/v1/chat/completions", json=corps, headers={"Authorization": "Bearer sk-test"})
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/event-stream")
    assert r.content == SSE_AMONT
    assert str(recu[0].url) == "https://api.openai.com/v1/chat/completions"
    assert recu[0].headers["authorization"] == "Bearer sk-test"
    assert json.loads(recu[0].content) == corps


def test_retenue_flux_vide(proxy):
    client, recu = proxy
    r = client.post("/v1/chat/completions", json=requete(eleve("Donc je développe")))
    assert recu == []
    donnees = evenements(r.text)
    assert donnees[-1] == "[DONE]" and len(donnees) == 2
    choix = json.loads(donnees[0])["choices"][0]
    assert choix["delta"]["content"] == "" and choix["finish_reason"] == "stop"


def test_retenue_sans_flux_et_interrupteur(proxy, monkeypatch):
    client, recu = proxy
    corps = requete(eleve("Donc je développe")) | {"stream": False}
    r = client.post("/v1/chat/completions", json=corps).json()
    assert r["choices"][0]["message"] == {"role": "assistant", "content": ""}
    monkeypatch.setenv("PROXY_HOLD", "0")
    client.post("/v1/chat/completions", json=corps)
    assert len(recu) == 1
