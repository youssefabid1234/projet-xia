"""Proxy de patience : le khôlleur ne répond pas à une phrase inachevée.

gradbot clôt le tour de l'étudiant ~1,3 s après le début d'une pause (codé en dur, non réglable).
Ce proxy, compatible OpenAI, se place entre gradbot et l'API et transmet tout tel quel, sauf quand
la dernière réplique de l'étudiant est visiblement inachevée (« Donc je développe… ») : il répond
alors une complétion vide. gradbot ne dit rien et se remet à écouter ; comme il n'a aucune réponse
à mettre dans l'historique, il colle la suite de la phrase au même message utilisateur.

Lancer : uv run uvicorn kholle.llm_proxy:app --port 8001
gradbot : LLM_BASE_URL=http://127.0.0.1:8001/v1 ; sans la variable, gradbot parle directement à OpenAI.
"""

import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import fastapi
import httpx
from fastapi.responses import JSONResponse, Response, StreamingResponse
from starlette.background import BackgroundTask

logging.basicConfig(level=logging.INFO, format="{asctime} {name} {levelname} {message}", style="{")
logger = logging.getLogger("kholle.patience")

AMONT = os.environ.get("PROXY_UPSTREAM_URL", "https://api.openai.com/v1").rstrip("/")

# Une phrase ne s'arrête pas sur ces mots (ni sur une élision : j', l', qu'…) ;
# la seconde ligne : verbes qui attendent leur complément (« Donc je développe »).
MOTS_SUSPENDUS = frozenset("""
    donc et alors mais puis parce car comme si que qui quand de du des le la les un une en à au aux
    par pour sur avec dans je j' on il c'est ça égal égale plus moins fois puissance euh hum heu bah ben bon
    développe pose obtiens obtient trouve calcule écris utilise remplace applique compose prends fais mets vaut
""".split())
FINS_SUSPENDUES = ("…", "...", ",")
JAMAIS = ("voilà", "voila", "j'ai fini", "c'est tout", "je réfléchis")
PONCTUATION = ".;:!?«»\"()"
# Relance de gradbot après SILENCE_TIMEOUT_S sans parole : « ... », en message utilisateur
# ou collé (précédé d'une espace) au dernier message s'il est déjà de l'étudiant.
RELANCE = "..."

ENTETES_TRANSMIS = {"authorization", "content-type", "accept", "openai-organization", "openai-project", "openai-beta"}
ENTETES_ECARTES = {"content-length", "content-encoding", "transfer-encoding", "connection", "keep-alive"}


# ── Classement ──────────────────────────────────────────────


def texte_message(message: dict) -> str:
    contenu = message.get("content")
    if isinstance(contenu, list):
        return " ".join(p.get("text", "") for p in contenu if isinstance(p, dict))
    return contenu or ""


def normaliser(texte: str) -> str:
    return texte.replace("’", "'").lower().strip()


def phrase_inachevee(texte: str) -> tuple[bool, str]:
    """(inachevée, raison). Dans le doute : achevée."""
    t = normaliser(texte)
    if not t:
        return False, "vide"
    if t.endswith("?"):
        return False, "question"
    if jamais := next((m for m in JAMAIS if m in t), None):
        return False, f"« {jamais} »"
    if fin := next((f for f in FINS_SUSPENDUES if t.endswith(f)), None):
        return True, f"finit par « {fin} »"
    dernier = t.split()[-1].strip(PONCTUATION)
    if dernier in MOTS_SUSPENDUS or dernier.endswith("'"):
        return True, f"dernier mot « {dernier} »"
    return False, "phrase finie"


def decision(corps: dict) -> tuple[bool, str]:
    """(retenir, raison) pour une requête /chat/completions."""
    messages = corps.get("messages") or []
    if not messages:
        return False, "aucun message"
    dernier = messages[-1]
    if dernier.get("role") != "user":
        return False, f"dernier message : {dernier.get('role')}"
    texte = texte_message(dernier).strip()
    if texte == RELANCE or texte.endswith(" " + RELANCE):
        return False, "relance après silence"
    if not texte and len(messages) > 1 and messages[-2].get("role") == "tool":
        return False, "résultat d'outil"
    return phrase_inachevee(texte)


def completion_vide(corps: dict, texte: str = "") -> Response:
    """Complétion d'assistant valide, au format demandé (SSE si stream)."""
    ident, cree, modele = f"chatcmpl-patience-{uuid.uuid4().hex[:12]}", int(time.time()), corps.get("model", "")
    if corps.get("stream"):
        morceau = {"id": ident, "object": "chat.completion.chunk", "created": cree, "model": modele,
                   "choices": [{"index": 0, "delta": {"role": "assistant", "content": texte}, "finish_reason": "stop"}]}
        sse = f"data: {json.dumps(morceau, ensure_ascii=False)}\n\ndata: [DONE]\n\n"
        return Response(sse, media_type="text/event-stream")
    return JSONResponse({
        "id": ident, "object": "chat.completion", "created": cree, "model": modele,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": texte}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    })


# ── Journal ─────────────────────────────────────────────────


def _resume(message: dict) -> dict:
    r = {"role": message.get("role"), "content": texte_message(message)[-300:]}
    if appels := message.get("tool_calls"):
        r["tool_calls"] = [a.get("function", {}).get("name") for a in appels]
    if message.get("tool_call_id"):
        r["tool_call_id"] = message["tool_call_id"]
    return r


def _journaliser(chemin: str, corps: dict, retenir: bool | None, raison: str, ms: float) -> None:
    messages = corps.get("messages") or []
    entree = {"t": round(time.time(), 3), "chemin": chemin, "stream": corps.get("stream"),
              "model": corps.get("model"), "n_messages": len(messages),
              "derniers": [_resume(m) for m in messages[-3:]],
              "decision": "retenu" if retenir else "transmis", "raison": raison, "proxy_ms": round(ms, 2)}
    dernier = entree["derniers"][-1] if messages else {}
    logger.info("%s %s (%s) : %s « %s »", entree["decision"].upper(), chemin, raison,
                dernier.get("role"), dernier.get("content", "")[-80:])
    if fichier := os.environ.get("PROXY_LOG"):
        with open(fichier, "a", encoding="utf-8") as f:
            f.write(json.dumps(entree, ensure_ascii=False) + "\n")


# ── Application ─────────────────────────────────────────────


@asynccontextmanager
async def _vie(app: fastapi.FastAPI):
    app.state.client = httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10))
    yield
    await app.state.client.aclose()


app = fastapi.FastAPI(title="Proxy de patience", lifespan=_vie)


@app.api_route("/v1/{chemin:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def relayer(chemin: str, requete: fastapi.Request):
    t0 = time.perf_counter()
    corps = await requete.body()
    if requete.method == "POST" and chemin == "chat/completions":
        try:
            donnees = json.loads(corps)
        except ValueError:
            donnees = None
        if isinstance(donnees, dict):
            retenir, raison = decision(donnees)
            if retenir and os.environ.get("PROXY_HOLD", "1") == "0":
                retenir, raison = False, f"{raison}, retenue désactivée"
            _journaliser(chemin, donnees, retenir, raison, (time.perf_counter() - t0) * 1000)
            if retenir:
                return completion_vide(donnees, os.environ.get("PROXY_HOLD_TEXT", ""))

    entetes = {k: v for k, v in requete.headers.items() if k.lower() in ENTETES_TRANSMIS}
    entetes["accept-encoding"] = "identity"  # octets relayés tels quels : pas de compression
    client: httpx.AsyncClient = app.state.client
    envoi = client.build_request(requete.method, f"{AMONT}/{chemin}", params=requete.query_params,
                                 headers=entetes, content=corps)
    try:
        reponse = await client.send(envoi, stream=True)
    except httpx.HTTPError as exc:
        logger.warning("Amont injoignable : %r", exc)
        return JSONResponse({"error": {"message": f"proxy de patience : {exc!r}"}}, status_code=502)
    logger.debug("amont %s en %.0f ms", reponse.status_code, (time.perf_counter() - t0) * 1000)
    return StreamingResponse(
        reponse.aiter_raw(),
        status_code=reponse.status_code,
        headers={k: v for k, v in reponse.headers.items() if k.lower() not in ENTETES_ECARTES},
        background=BackgroundTask(reponse.aclose),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PROXY_PORT", 8001)))
