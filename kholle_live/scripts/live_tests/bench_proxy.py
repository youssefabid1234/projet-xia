"""Latence ajoutée par le proxy : premier octet SSE, en direct puis via le proxy (8002 et 8003 doivent être libres).

1) amont factice local (8002) : isole le coût du proxy (saut local + analyse + relais) ;
2) OpenAI réel : direct vs proxy de 8001, en alternance.
"""

import asyncio
import os
import statistics
import sys
import threading
import time
from pathlib import Path

KL = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KL))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(KL / ".env")
load_dotenv(KL.parent / ".env")
os.environ["PROXY_UPSTREAM_URL"] = "http://127.0.0.1:8002/v1"
os.environ.pop("PROXY_LOG", None)

import fastapi  # noqa: E402
import httpx  # noqa: E402
import uvicorn  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402

from kholle import llm_proxy  # noqa: E402

faux = fastapi.FastAPI()


@faux.post("/v1/chat/completions")
async def completions():
    async def flux():
        yield b'data: {"choices":[{"index":0,"delta":{"content":"Bonjour"}}]}\n\n'
        yield b"data: [DONE]\n\n"
    return StreamingResponse(flux(), media_type="text/event-stream")


def lancer(app, port):
    serveur = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=serveur.run, daemon=True).start()
    return serveur


CORPS = {
    "model": os.environ.get("LLM_MODEL", "gpt-4.1").strip(), "stream": True, "max_completion_tokens": 5,
    "messages": [{"role": "system", "content": "Tu es un khôlleur de mathématiques. " * 250},
                 {"role": "user", "content": "Voilà."}],
}


async def premier_octet(client, url, cle=None):
    t0 = time.perf_counter()
    entetes = {"Authorization": f"Bearer {cle}"} if cle else {}
    async with client.stream("POST", url, json=CORPS, headers=entetes) as r:
        async for _ in r.aiter_raw():
            return (time.perf_counter() - t0) * 1000


async def main():
    lancer(faux, 8002)
    lancer(llm_proxy.app, 8003)
    await asyncio.sleep(2)
    async with httpx.AsyncClient(timeout=60) as client:
        for _ in range(5):  # chauffe
            await premier_octet(client, "http://127.0.0.1:8002/v1/chat/completions")
            await premier_octet(client, "http://127.0.0.1:8003/v1/chat/completions")
        direct, proxy = [], []
        for _ in range(100):
            direct.append(await premier_octet(client, "http://127.0.0.1:8002/v1/chat/completions"))
            proxy.append(await premier_octet(client, "http://127.0.0.1:8003/v1/chat/completions"))
        print(f"Amont local : direct médiane {statistics.median(direct):.1f} ms, via proxy {statistics.median(proxy):.1f} ms, "
              f"surcoût médian {statistics.median(proxy) - statistics.median(direct):.1f} ms, "
              f"p95 via proxy {sorted(proxy)[94]:.1f} ms")

        cle = os.environ.get("LLM_API_KEY") or os.environ["OPENAI_API_KEY"]
        od, op = [], []
        for _ in range(8):
            od.append(await premier_octet(client, "https://api.openai.com/v1/chat/completions", cle))
            op.append(await premier_octet(client, "http://127.0.0.1:8001/v1/chat/completions", cle))
        print(f"OpenAI ({CORPS['model']}) : direct médiane {statistics.median(od):.0f} ms {[round(x) for x in od]}")
        print(f"               via proxy 8001 médiane {statistics.median(op):.0f} ms {[round(x) for x in op]}")


asyncio.run(main())
