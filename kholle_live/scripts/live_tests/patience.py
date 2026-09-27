"""Tests de bout en bout du proxy de patience (a, b, c, e, f) avec l'élève synthétique de la lane A.

Serveur : main:app sur 8011 avec LLM_BASE_URL=http://127.0.0.1:8001/v1 (proxy) ou sans (témoin).
Résultats : sortie/<nom>.json (nom = premier argument, défaut « patience »).
"""

import asyncio
import json
import os
import sys
import time

import httpx
import websockets

import eleve_audio as ea
from eleve_audio import SR, Micro, log, pousser_tableau, synthese

import gradium  # noqa: E402

PHRASES = {
    "t_prenom": "Bonjour, je m'appelle Pierre.",
    "t_a1": "Donc je développe",
    "t_a2": "à l'ordre trois, en posant u égal sinus de x.",
    "t_ecris": "J'écris la suite au tableau.",
    "t_voila": "Voilà.",
    "t_f": "Je ne vois pas.",
}


class Suivi:
    def __init__(self):
        self.evts: list[tuple[float, str, str]] = []
        self.textes: dict[int, list[str]] = {}
        self.outils: list[tuple[float, str]] = []

    def t(self):
        return time.time() - ea.T0

    async def recevoir(self, ws):
        async for msg in ws:
            now = self.t()
            if isinstance(msg, bytes):
                self.evts.append((now, "audio", ""))
                continue
            m = json.loads(msg)
            ty = m.get("type")
            if ty == "agent_text":
                self.textes.setdefault(m["turn_idx"], []).append(m["text"])
                self.evts.append((now, "agent_text", f"{m['turn_idx']}:{m['text']}"))
            elif ty == "user_text":
                self.evts.append((now, "user_text", m["text"]))
                log("   STT :", m["text"])
            elif ty == "event":
                self.evts.append((now, "event", m["event"]))
                if m["event"] in ("flushing", "end_of_turn", "llm_started", "end_tts_audio", "interrupted"):
                    log("   évènement", m["event"])
            elif ty == "outil":
                self.outils.append((now, m["nom"]))
                log("OUTIL", m["nom"], json.dumps(m["resultat"], ensure_ascii=False))
            elif ty == "error":
                self.evts.append((now, "error", m.get("message", "")))
                log("ERREUR SERVEUR", m)
            elif ty not in ("audio_timing", "session"):
                log("   ?", m)

    def premier(self, genre, apres, detail=None):
        return next((t for t, g, d in self.evts if t >= apres and g == genre and (detail is None or d == detail)), None)

    def dit_depuis(self, apres, avant=None):
        tours = sorted({int(d.split(":")[0]) for t, g, d in self.evts
                        if g == "agent_text" and t >= apres and (avant is None or t < avant)})
        return " | ".join(" ".join(self.textes[i]) for i in tours)

    async def fin_kholleur(self, apres, delai=40.0, calme=1.5):
        fin = time.time() + delai
        while time.time() < fin:
            await asyncio.sleep(0.2)
            audios = [t for t, g, _ in self.evts if g == "audio" and t >= apres]
            if audios and self.t() - audios[-1] > calme and self.premier("event", apres, "end_tts_audio"):
                return True
        log("   (pas de réponse en", delai, "s)")
        return False

    async def calme(self, duree=2.0, delai=40.0):
        """Attend `duree` s sans audio du khôlleur."""
        fin = time.time() + delai
        while time.time() < fin:
            dernier = max((t for t, g, _ in self.evts if g == "audio"), default=0)
            if self.t() - dernier > duree:
                return
            await asyncio.sleep(0.2)


async def main():
    client = gradium.client.GradiumClient(api_key=os.environ["GRADIUM_API_KEY"])
    audio = {k: await synthese(client, k, p) for k, p in PHRASES.items()}
    log("Phrases :", {k: round(len(v) / 2 / SR, 1) for k, v in audio.items()})
    boucle = asyncio.get_running_loop()
    file: asyncio.Queue = asyncio.Queue()
    s = Suivi()
    res = {}
    async with httpx.AsyncClient(base_url=f"http://{ea.SERVEUR}", timeout=60) as http:
        log("Démo :", (await http.post("/api/session/new", json={})).json())
        async with websockets.connect(f"ws://{ea.SERVEUR}/ws/chat", max_size=None) as ws:
            await ws.send(json.dumps({"type": "start"}))
            micro = Micro(boucle, file)

            async def envoyer():
                while True:
                    await ws.send(await file.get())

            taches = [asyncio.create_task(envoyer()), asyncio.create_task(s.recevoir(ws))]

            async def dire(cle):
                duree = micro.dire(audio[cle])
                log(f"ÉLÈVE ({duree:.1f} s) :", PHRASES[cle])
                await asyncio.sleep(duree)
                return s.t()

            await s.fin_kholleur(0)
            log("KHÔLLEUR :", s.dit_depuis(0))
            t = await dire("t_prenom")
            await s.fin_kholleur(t)
            log("KHÔLLEUR :", s.dit_depuis(t))
            await s.calme()

            # (a) « Donc je développe » + 4 s + « …à l'ordre trois »
            log("--- (a) pause de réflexion")
            fin_a1 = await dire("t_a1")
            await asyncio.sleep(4.0)
            debut_a2 = s.t()
            audio_pause = [round(tt - fin_a1, 2) for tt, g, _ in s.evts if fin_a1 <= tt < debut_a2 and g == "audio"]
            pendant = [(round(tt - fin_a1, 2), g, d) for tt, g, d in s.evts
                       if fin_a1 <= tt < debut_a2 and g in ("event", "agent_text", "error")]
            fin_a2 = await dire("t_a2")
            await s.fin_kholleur(fin_a2)
            res["a"] = {"audio_pendant_pause": len(audio_pause), "dit_pendant_pause": s.dit_depuis(fin_a1, debut_a2),
                        "évènements_pause": pendant, "réponse": s.dit_depuis(fin_a2),
                        "premier_audio_après_a2_s": (x := s.premier("audio", fin_a2)) and round(x - fin_a2, 2)}
            log("(a)", json.dumps(res["a"], ensure_ascii=False))
            await s.calme()

            # (c) + (b) ligne fausse, puis « Voilà. »
            log("--- (c) tableau faux puis « Voilà. »")
            t = await dire("t_ecris")
            lecture = asyncio.create_task(pousser_tableau(http, [
                "u = sin x = x - x^3/6 + o(x^3)",
                "ln(1+u) = u - u^2/2 + o(u^2)",
                "f(x) = x - x^2/2 - x^3/6 + o(x^3)",
            ], "tableau1"))
            await s.fin_kholleur(t)
            log("KHÔLLEUR :", s.dit_depuis(t))
            lu = await lecture
            await s.calme()
            avant = s.dit_depuis(t)
            fin_v = await dire("t_voila")
            await s.fin_kholleur(fin_v)
            premier_audio = s.premier("audio", fin_v)
            res["b"] = {"latence_premier_audio_s": premier_audio and round(premier_audio - fin_v, 2),
                        "llm_started_s": (x := s.premier("event", fin_v, "llm_started")) and round(x - fin_v, 2),
                        "flushing_s": (x := s.premier("event", fin_v, "flushing")) and round(x - fin_v, 2)}
            res["c"] = {"tableau_lu": lu, "dit_avant_voila": avant, "réponse": s.dit_depuis(fin_v)}
            log("(b)", json.dumps(res["b"], ensure_ascii=False))
            log("(c)", json.dumps(res["c"], ensure_ascii=False))
            await s.calme()

            # (f) « Je ne vois pas » -> donner_indice
            log("--- (f) « Je ne vois pas »")
            fin_f = await dire("t_f")
            await s.fin_kholleur(fin_f)
            await asyncio.sleep(3)
            res["f"] = {"outils": [n for tt, n in s.outils if tt >= fin_f - 1], "réponse": s.dit_depuis(fin_f)}
            log("(f)", json.dumps(res["f"], ensure_ascii=False))
            await s.calme(3.0)

            # (e) fragment retenu puis silence
            log("--- (e) fragment retenu puis silence")
            fin_e = await dire("t_a1")
            await asyncio.sleep(18)
            relance = s.premier("audio", fin_e)
            res["e"] = {"relance_après_s": relance and round(relance - fin_e, 1), "dit": s.dit_depuis(fin_e),
                        "évènements": [(round(tt - fin_e, 2), g, d) for tt, g, d in s.evts
                                       if tt >= fin_e and g in ("event", "error") and d != "first_word"][:12]}
            log("(e)", json.dumps(res["e"], ensure_ascii=False))

            await ws.send(json.dumps({"type": "stop"}))
            micro.fermer()
            for x in taches:
                x.cancel()
    res["erreurs"] = [d for _, g, d in s.evts if g == "error"]
    log("RÉSULTATS", json.dumps(res, ensure_ascii=False, indent=1))
    nom = sys.argv[1] if len(sys.argv) > 1 else "patience"
    (ea.ICI / f"{nom}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
