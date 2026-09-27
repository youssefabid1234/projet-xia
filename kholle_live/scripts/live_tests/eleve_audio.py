"""Élève synthétique (lane A) : parle au khôlleur par /ws/chat comme le ferait le navigateur.

Voix Gradium (Jules) -> PCM -> ffmpeg (Ogg Opus, pages de 40 ms, en temps réel) -> WebSocket.
Journalise tout ce que renvoie le serveur, pousse des tableaux PNG par /api/board.
Serveur visé : SERVEUR (défaut 127.0.0.1:8011). Sorties (voix en cache, journal) dans sortie/.
"""

import asyncio
import json
import os
import random
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx
import websockets
from dotenv import load_dotenv

KL = Path(__file__).resolve().parents[2]
load_dotenv(KL / ".env")
load_dotenv(KL.parent / ".env")
import gradium  # noqa: E402
from gradium import speech  # noqa: E402

ICI = Path(__file__).parent / "sortie"
ICI.mkdir(exist_ok=True)
SERVEUR = os.environ.get("SERVEUR", "127.0.0.1:8011")
SR = 48000
PAS = 0.02
VOIX_ELEVE = "YKeBw3OV1RgpdhLh"  # Jules
T0 = time.time()
JOURNAL = open(ICI / "journal_audio.txt", "w", encoding="utf-8")


def log(*a):
    ligne = f"[{time.time() - T0:6.1f}] " + " ".join(str(x) for x in a)
    print(ligne, flush=True)
    JOURNAL.write(ligne + "\n")
    JOURNAL.flush()


# ── Micro virtuel : PCM en temps réel -> ffmpeg -> pages Ogg ──────────


class Micro:
    def __init__(self, boucle, file):
        self.parole = bytearray()
        self.verrou = threading.Lock()
        self.actif = True
        self.ffmpeg = subprocess.Popen(
            ["ffmpeg", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "pipe:0",
             "-c:a", "libopus", "-b:a", "32k", "-ar", "24000", "-frame_duration", "20", "-application", "voip",
             "-page_duration", "40000", "-flush_packets", "1", "-f", "ogg", "pipe:1"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        )
        self.boucle, self.file = boucle, file
        threading.Thread(target=self._nourrir, daemon=True).start()
        threading.Thread(target=self._lire, daemon=True).start()

    def dire(self, pcm: bytes) -> float:
        with self.verrou:
            self.parole += pcm
            return len(self.parole) / 2 / SR

    def _nourrir(self):
        n = int(SR * PAS)
        prochain = time.perf_counter()
        while self.actif:
            with self.verrou:
                morceau = bytes(self.parole[: 2 * n])
                del self.parole[: 2 * n]
            if len(morceau) < 2 * n:  # bruit de fond très faible plutôt qu'un zéro numérique
                bruit = struct.pack(f"<{n}h", *(random.randint(-6, 6) for _ in range(n)))
                morceau += bruit[len(morceau):]
            try:
                self.ffmpeg.stdin.write(morceau)
                self.ffmpeg.stdin.flush()
            except OSError:
                return
            prochain += PAS
            time.sleep(max(0.0, prochain - time.perf_counter()))

    def _lire(self):
        tampon = b""
        while True:
            d = self.ffmpeg.stdout.read1(65536)
            if not d:
                return
            tampon += d
            while len(tampon) >= 27 and tampon[:4] == b"OggS":
                nseg = tampon[26]
                if len(tampon) < 27 + nseg:
                    break
                taille = 27 + nseg + sum(tampon[27:27 + nseg])
                if len(tampon) < taille:
                    break
                page, tampon = tampon[:taille], tampon[taille:]
                self.boucle.call_soon_threadsafe(self.file.put_nowait, page)

    def fermer(self):
        self.actif = False
        self.ffmpeg.kill()


# ── Tableau : PNG tapé, lu par la lane B ──────────────────────────────


def png_tableau(lignes: list[str], nom: str) -> bytes:
    txt = ICI / f"{nom}.txt"
    txt.write_text("\n".join(lignes), encoding="utf-8")
    png = ICI / f"{nom}.png"
    police = "C\\:/Windows/Fonts/arial.ttf"
    fichier = str(txt).replace("\\", "/").replace(":", "\\:")
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=white:s=1400x520", "-vf",
         f"drawtext=fontfile='{police}':textfile='{fichier}':fontsize=46:fontcolor=black:x=40:y=40:line_spacing=40",
         "-frames:v", "1", str(png)],
        check=True,
    )
    return png.read_bytes()


async def pousser_tableau(http: httpx.AsyncClient, lignes: list[str], nom: str) -> list:
    r = await http.post("/api/board", content=png_tableau(lignes, nom), headers={"Content-Type": "image/png"})
    log("TABLEAU envoyé", r.status_code, r.text)
    for _ in range(120):
        await asyncio.sleep(0.5)
        etat = (await http.get("/api/board/state")).json()
        if not etat["lecture_en_cours"] and etat["lines"]:
            break
    lu = [(l["n"], l["verdict"], l["texte"], l.get("detail")) for l in etat["lines"]]
    log("TABLEAU lu :", json.dumps(lu, ensure_ascii=False), "erreur:", etat["erreur"])
    return lu


# ── Scénario ──────────────────────────────────────────────────────────


class Kholle:
    def __init__(self):
        self.tour_texte: dict = {}
        self.fin_parole = asyncio.Event()
        self.outils: list = []
        self.parle = False
        self.tour = None
        self.tours_finis: set = set()
        self.repliques: list[tuple[float, str]] = []

    async def recevoir(self, ws):
        async for msg in ws:
            if isinstance(msg, bytes):
                continue
            m = json.loads(msg)
            t = m.get("type")
            if t == "agent_text":
                # Le texte suit l'audio : un morceau d'un tour déjà fini ne relance pas la parole.
                if m["turn_idx"] not in self.tours_finis:
                    self.parle, self.tour = True, m["turn_idx"]
                self.tour_texte.setdefault(m["turn_idx"], []).append(m["text"])
            elif t == "user_text":
                pass
            elif t == "event":
                if m["event"] not in ("first_word", "first_tts_audio"):
                    log("   évènement", m["event"])
                if m["event"] == "end_tts_audio" and self.parle:
                    self.tours_finis.add(self.tour)
                    phrase = " ".join(self.tour_texte[self.tour])
                    self.repliques.append((time.time() - T0, phrase))
                    log(f"KHÔLLEUR [tour {self.tour}] :", phrase)
                    self.parle = False
                    self.fin_parole.set()
            elif t == "outil":
                self.outils.append((m["nom"], m["resultat"]))
                log("OUTIL", m["nom"], json.dumps(m["resultat"], ensure_ascii=False))
            elif t in ("session", "error"):
                log("SERVEUR", m)
            elif t != "audio_timing":
                log("   ?", m)

    async def attendre_kholleur(self, delai=40.0) -> str | None:
        """Attend la fin de la prochaine prise de parole, puis le temps que l'audio finisse côté navigateur."""
        self.fin_parole.clear()
        try:
            await asyncio.wait_for(self.fin_parole.wait(), delai)
        except TimeoutError:
            log("   (pas de réponse en", delai, "s)")
            return None
        await asyncio.sleep(1.5)
        return self.repliques[-1][1]


async def synthese(client, cle: str, texte: str) -> bytes:
    """Une à la fois et en cache : la clé Gradium n'accepte que 2 sessions simultanées."""
    cache = ICI / "voix" / f"{cle}.pcm"
    if cache.exists() and (ICI / "voix" / f"{cle}.txt").read_text(encoding="utf-8") == texte:
        return cache.read_bytes()
    r = await speech.tts(client, {"voice_id": VOIX_ELEVE, "output_format": "pcm"}, texte)
    assert r.sample_rate == SR
    cache.parent.mkdir(exist_ok=True)
    cache.write_bytes(r.pcm16().tobytes())
    (ICI / "voix" / f"{cle}.txt").write_text(texte, encoding="utf-8")
    return cache.read_bytes()


async def main():
    phrases = {
        "prenom": "Bonjour, je m'appelle Pierre.",
        "debut": "D'accord. Je pose u égal sinus de x, qui tend vers zéro. J'utilise le développement de logarithme de un plus u à l'ordre deux.",
        "memoire": "Pardon, j'ai un trou. Vous pouvez me rappeler mon prénom, et ce qu'on cherche ?",
        "bloque": "Je suis bloqué, je ne vois pas où est le problème.",
        "correction": "Ah, il faut développer le logarithme à l'ordre trois, avec plus u cube sur trois. Donc f de x égale x moins x carré sur deux plus x cube sur six, plus petit o de x cube.",
        "suite": "f de x moins x vaut moins x carré sur deux plus petit o de x carré, c'est négatif près de zéro, donc la courbe est en dessous de sa tangente, des deux côtés.",
        "fini": "J'ai terminé.",
    }
    client = gradium.client.GradiumClient(api_key=os.environ["GRADIUM_API_KEY"])
    audio = {cle: await synthese(client, cle, p) for cle, p in phrases.items()}
    log("Phrases synthétisées :", {k: round(len(v) / 2 / SR, 1) for k, v in audio.items()})

    boucle = asyncio.get_running_loop()
    file: asyncio.Queue = asyncio.Queue()
    k = Kholle()
    async with httpx.AsyncClient(base_url=f"http://{SERVEUR}", timeout=60) as http:
        log("Démo :", (await http.post("/api/session/new", json={})).json())
        async with websockets.connect(f"ws://{SERVEUR}/ws/chat", max_size=None) as ws:
            await ws.send(json.dumps({"type": "start"}))
            micro = Micro(boucle, file)

            async def envoyer():
                while True:
                    await ws.send(await file.get())

            taches = [asyncio.create_task(envoyer()), asyncio.create_task(k.recevoir(ws))]

            async def dire(cle):
                duree = micro.dire(audio[cle])
                log(f"ÉLÈVE dit ({duree:.1f} s) :", phrases[cle])
                await asyncio.sleep(duree)

            await k.attendre_kholleur()                      # salut + prénom
            await dire("prenom")
            await k.attendre_kholleur()                      # énoncé
            await dire("debut")
            await k.attendre_kholleur()

            # Silence : l'élève écrit une troisième ligne fausse (troncature à l'ordre deux).
            log("--- SILENCE, tableau poussé pendant le silence")
            debut_silence = time.time()
            await pousser_tableau(http, [
                "u = sin x = x - x^3/6 + o(x^3)",
                "ln(1+u) = u - u^2/2 + o(u^2)",
                "f(x) = x - x^2/2 - x^3/6 + o(x^3)",
            ], "tableau1")
            t_tableau = time.time()
            log(f"   tableau à jour {t_tableau - debut_silence:.1f} s après le début du silence")
            # On se tait jusqu'à ce que le khôlleur parle APRÈS la mise à jour du tableau.
            while True:
                r = await k.attendre_kholleur(delai=45)
                if r is None or k.repliques[-1][0] + T0 > t_tableau:
                    break
                log("   (réplique d'avant la mise à jour du tableau, on continue de se taire)")

            if "court" in sys.argv:
                await ws.send(json.dumps({"type": "stop"}))
                micro.fermer()
                return
            log("--- MÉMOIRE après la poussée de config")
            await dire("memoire")
            await k.attendre_kholleur()

            await dire("bloque")
            await k.attendre_kholleur()

            await dire("correction")
            await pousser_tableau(http, [
                "u = sin x = x - x^3/6 + o(x^3)",
                "ln(1+u) = u - u^2/2 + u^3/3 + o(u^3)",
                "f(x) = x - x^2/2 + x^3/6 + o(x^3)",
            ], "tableau2")
            await k.attendre_kholleur()
            if not any(n == "question_suivante" for n, _ in k.outils):
                await k.attendre_kholleur(delai=15)

            await dire("suite")
            await k.attendre_kholleur()
            for _ in range(16):
                if any(n == "terminer_colle" for n, _ in k.outils):
                    log("   terminer_colle appelé par le khôlleur lui-même")
                    break
                await asyncio.sleep(0.5)
            else:
                log("   terminer_colle PAS appelé 8 s après sa réponse : l'élève dit avoir fini")
                await dire("fini")
                await k.attendre_kholleur()
            await asyncio.sleep(3)

            await ws.send(json.dumps({"type": "stop"}))
            micro.fermer()
            for t in taches:
                t.cancel()
        await asyncio.sleep(2)
        log("Compte-rendu :", (await http.get("/api/report/status")).json())
    log("OUTILS :", [n for n, _ in k.outils])
    log("TEXTE COMPLET DU KHÔLLEUR PAR TOUR :")
    for idx, morceaux in sorted(k.tour_texte.items()):
        log(f"   [{idx}]", " ".join(morceaux))


if __name__ == "__main__":
    asyncio.run(main())
