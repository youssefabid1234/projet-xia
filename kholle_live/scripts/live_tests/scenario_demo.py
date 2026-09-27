"""Scénario de la démo de bout en bout, avec l'élève synthétique (lane A).

« Démo » -> prénom -> énoncé -> l'élève écrit trois lignes en parlant, la troisième fausse
-> ligne rouge -> à la pause suivante, question sur l'ordre ou le reste, sans la réponse
-> ligne 3 barrée, résultat juste -> ✓ -> question_suivante (tangente) -> « je suis bloqué »
-> donner_indice niveau 1 -> bonne réponse -> terminer_colle -> compte-rendu, avec l'erreur
de la ligne 3 « corrigée après question ».

Tableau tapé (Comic Sans), pas manuscrit : la lecture sur la vraie tablette reste à chronométrer
à la main. Stylet levé = fin de la phrase qui accompagne la ligne ; l'image part ATTENTE_MS plus
tard, comme dans static/board.html. Le panneau du portable interroge le serveur toutes les
PERIODE_MS de static/board_panel.js : on l'ajoute au temps mesuré côté serveur.

    SERVEUR=127.0.0.1:8000 uv run python scripts/live_tests/scenario_demo.py [passages]

Écrit un compte-rendu dans data/ comme une vraie khôlle : remise à zéro avant la démo (RUN.md).
"""

import asyncio
import contextlib
import json
import re
import statistics
import subprocess
import sys
import time

import httpx
import websockets

import eleve_audio as ea
from eleve_audio import SR, Micro, log, synthese

import gradium  # noqa: E402

KL = ea.KL


def _constante(fichier: str, nom: str) -> int:
    return int(re.search(rf"{nom} = (\d+)", (KL / fichier).read_text(encoding="utf-8")).group(1))


ATTENTE_MS = _constante("static/board.html", "ATTENTE_MS")
PANNEAU_MS = _constante("static/board_panel.js", "PERIODE_MS")
RAPPORT_MS = _constante("static/report_panel.js", "PERIODE_MS")

L1 = "sin x = x - x^3/6 + o(x^3)"
L2 = "ln(1+u) = u - u^2/2 + o(u^2)"
L3 = "ln(1+sin x) = x - x^2/2 - x^3/6 + o(x^3)"
L4 = "ln(1+sin x) = x - x^2/2 + x^3/6 + o(x^3)"

PHRASES = {
    "prenom": "Bonjour, je m'appelle Pierre.",
    "l1": "Je commence par le développement de sinus de x à l'ordre trois : x moins x cube sur six, plus petit o de x cube.",
    "l2": "Ensuite, logarithme de un plus u égale u moins u carré sur deux, plus petit o de u carré.",
    "l3": "Et je compose : logarithme de un plus sinus de x égale x moins x carré sur deux moins x cube sur six, plus petit o de x cube.",
    "reprise": "Ah oui, un reste en petit o de u carré ne suffit pas, il faut développer le logarithme à l'ordre trois. Je barre la troisième ligne.",
    "l4": "Avec plus u cube sur trois, j'obtiens x moins x carré sur deux plus x cube sur six, plus petit o de x cube.",
    "bloque": "Je suis bloqué, je ne vois pas comment faire.",
    "tangente": "f de x moins x vaut moins x carré sur deux plus petit o de x carré, c'est négatif près de zéro, donc la courbe est en dessous de sa tangente.",
}

# Ce qui trahirait la réponse (le bon coefficient, ou le terme en u cube qui manque). Citer
# la valeur fausse de l'étudiant (« moins un sixième ») est permis.
REPONSE = re.compile(r"plus (un sixième|x (au )?cube sur six)|(u|x) (au )?cube sur trois|un tiers|\+ ?x\^?3 ?/ ?6", re.I)
SUR_LA_LIGNE = re.compile(r"troisième ligne|ligne trois|ligne 3", re.I)
CAUSE = re.compile(r"ordre|reste|petit o|développ", re.I)
POLICE = "C\\:/Windows/Fonts/comic.ttf"


def png(lignes: list[tuple[str, bool]], nom: str) -> bytes:
    """Tableau tapé ; (texte, barrée)."""
    filtres = []
    for i, (texte, barre) in enumerate(lignes):
        y = 50 + 130 * i
        txt = ea.ICI / f"{nom}_{i}.txt"
        txt.write_text(texte, encoding="utf-8")
        chemin = str(txt).replace("\\", "/").replace(":", "\\:")
        filtres.append(f"drawtext=fontfile='{POLICE}':textfile='{chemin}':fontsize=54:fontcolor=0x1a237e:x=50:y={y}")
        if barre:
            filtres.append(f"drawbox=x=40:y={y + 30}:w={25 * len(texte) + 20}:h=6:color=0x1a237e:t=fill")
    sortie = ea.ICI / f"{nom}.png"
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=white:s=1600x{130 * len(lignes) + 100}",
         "-vf", ",".join(filtres), "-frames:v", "1", str(sortie)],
        check=True,
    )
    return sortie.read_bytes()


class Suivi:
    def __init__(self):
        self.evts: list[tuple[float, str, object]] = []
        self.tours: dict[int, dict] = {}
        self.outils: list[tuple[float, str, dict]] = []
        self.erreurs: list[str] = []
        self.session: str | None = None  # celle du compte-rendu : créée au « start »

    @staticmethod
    def t() -> float:
        return time.time() - ea.T0

    async def recevoir(self, ws):
        async for msg in ws:
            now = self.t()
            if isinstance(msg, bytes):
                self.evts.append((now, "audio", None))
                continue
            m = json.loads(msg)
            ty = m.get("type")
            if ty == "agent_text":
                tour = self.tours.setdefault(m["turn_idx"], {"texte": [], "t": now})
                tour["texte"].append(m["text"])
            elif ty == "event":
                self.evts.append((now, "event", m["event"]))
            elif ty == "outil":
                self.outils.append((now, m["nom"], m["resultat"]))
                log("OUTIL", m["nom"], json.dumps(m["resultat"], ensure_ascii=False))
            elif ty == "session":
                self.session = m["id"]
            elif ty == "error":
                log("SERVEUR", m)
                self.erreurs.append(m.get("message"))

    def premier_audio(self, apres: float) -> float | None:
        return next((t for t, g, _ in self.evts if g == "audio" and t >= apres), None)

    def repliques(self, apres: float, avant: float = float("inf")) -> list[tuple[float, str]]:
        return [(v["t"], " ".join(v["texte"])) for _, v in sorted(self.tours.items()) if apres <= v["t"] < avant]

    def outil(self, nom: str, apres: float):
        return next(((t, r) for t, n, r in self.outils if n == nom and t >= apres), None)

    async def calme(self, apres: float, delai: float = 30.0, calme: float = 1.5) -> bool:
        """Le khôlleur a parlé après `apres` et se tait depuis `calme` s."""
        fin = time.time() + delai
        while time.time() < fin:
            await asyncio.sleep(0.2)
            audios = [t for t, g, _ in self.evts if g == "audio" and t >= apres]
            if audios and self.t() - audios[-1] > calme:
                return True
        return False

    async def attendre(self, condition, delai: float):
        fin = time.time() + delai
        while time.time() < fin:
            if r := condition():
                return r
            await asyncio.sleep(0.2)
        return None


async def passage(n: int, audio: dict, http: httpx.AsyncClient) -> dict:
    boucle = asyncio.get_running_loop()
    file: asyncio.Queue = asyncio.Queue()
    s = Suivi()
    m: dict = {"passage": n, "latences_parole_s": {}, "etapes": {}, "écarts": []}

    def etape(nom, ok, **infos):
        m["etapes"][nom] = {"ok": bool(ok), **infos}
        log(f"[{'OK ' if ok else 'KO '}] {nom}", json.dumps(infos, ensure_ascii=False))

    session = (await http.post("/api/session/new", json={})).json()
    log(f"=== Passage {n} : Démo", session)
    async with websockets.connect(f"ws://{ea.SERVEUR}/ws/chat", max_size=None) as ws:
        await ws.send(json.dumps({"type": "start"}))
        micro = Micro(boucle, file)

        async def envoyer():
            while True:
                await ws.send(await file.get())

        taches = [asyncio.create_task(envoyer()), asyncio.create_task(s.recevoir(ws))]

        async def dire(cle) -> float:
            duree = micro.dire(audio[cle])
            log(f"ÉLÈVE ({duree:.1f} s) :", PHRASES[cle])
            await asyncio.sleep(duree)
            fin = s.t()
            asyncio.create_task(noter_latence(cle, fin))
            return fin

        async def noter_latence(cle, fin):
            await asyncio.sleep(8)
            premier = s.premier_audio(fin)
            m["latences_parole_s"][cle] = round(premier - fin, 2) if premier and premier - fin < 8 else None

        async def ecrire(lignes, nom, stylo_leve: float) -> dict:
            """Envoi ATTENTE_MS après le stylet levé, puis attente de la lecture."""
            image = png(lignes, nom)
            await asyncio.sleep(max(0.0, stylo_leve + ATTENTE_MS / 1000 - s.t()))
            envoi = s.t()
            await http.post("/api/board", content=image, headers={"Content-Type": "image/png"})
            await asyncio.sleep(0.3)
            while True:
                etat = (await http.get("/api/board/state")).json()
                if not etat["lecture_en_cours"]:
                    break
                await asyncio.sleep(0.1)
            lu = s.t()
            lignes_lues = [(l["n"], "barrée" if l["barre"] else l["verdict"], l["texte"]) for l in etat["lines"]]
            log(f"TABLEAU {nom} lu {lu - envoi:.1f} s après l'envoi :", lignes_lues, etat["erreur"] or "")
            return {"stylo": stylo_leve, "envoi": envoi, "lu": lu, "lignes": lignes_lues}

        # Accueil, prénom, énoncé.
        ok = await s.calme(0, 30)
        etape("accueil", ok, dit=[r for _, r in s.repliques(0)])
        fin = await dire("prenom")
        await s.calme(fin, 30)
        enonce = " ".join(r for _, r in s.repliques(fin))
        etape("énoncé lu", "développement limité" in enonce and "Pierre" in enonce, dit=enonce)

        # Trois lignes écrites en parlant.
        fin = await dire("l1")
        t1 = asyncio.create_task(ecrire([(L1, False)], "b1", fin))
        await s.calme(fin, 20)
        await t1
        fin = await dire("l2")
        t2 = asyncio.create_task(ecrire([(L1, False), (L2, False)], "b2", fin))
        await s.calme(fin, 20)
        await t2
        debut_l3 = s.t()
        fin_l3 = await dire("l3")
        b3 = await ecrire([(L1, False), (L2, False), (L3, False)], "b3", fin_l3)
        rouge = next((l for l in b3["lignes"] if l[0] == 3), None)
        rouge_ok = rouge is not None and rouge[1] == "faux"
        faux_ailleurs = [l for l in b3["lignes"] if l[0] != 3 and l[1] == "faux"]
        m["stylo_rouge_s"] = round(b3["lu"] - b3["stylo"] + PANNEAU_MS / 2000, 2)
        etape("ligne 3 rouge", rouge_ok and not faux_ailleurs, lignes=b3["lignes"],
              stylo_serveur_s=round(b3["lu"] - b3["stylo"], 2), avec_panneau_s=m["stylo_rouge_s"])

        # À la pause suivante : une question sur la ligne 3 (ordre, reste), sans la réponse.
        def question_l3():
            for t, r in s.repliques(b3["lu"]):
                if SUR_LA_LIGNE.search(r) or CAUSE.search(r):
                    return t, r
            return None

        await s.attendre(question_l3, 30)
        await s.calme(b3["lu"], 5)
        avant_rouge = [r for _, r in s.repliques(fin_l3, b3["lu"])]
        apres = s.repliques(b3["lu"])
        q = question_l3()
        premiere = apres[0][1] if apres else None
        etape("question sur la ligne 3", q and q[1] == premiere and not REPONSE.search(q[1]),
              dit_avant_la_ligne_rouge=avant_rouge, dit=premiere,
              rouge_vers_question_s=q and round(q[0] - b3["lu"], 1))
        m["rouge_vers_question_s"] = q and round(q[0] - b3["lu"], 1)
        await s.calme(b3["lu"], 20)

        # Ligne 3 barrée, résultat juste.
        fin = await dire("reprise")
        await s.calme(fin, 20)
        debut = s.t()
        fin_l4 = await dire("l4")
        b4 = await ecrire([(L1, False), (L2, False), (L3, True), (L4, False)], "b4", fin_l4)
        l3 = next((l for l in b4["lignes"] if l[0] == 3), None)
        l4 = next((l for l in b4["lignes"] if l[0] == 4), None)
        etape("ligne 3 barrée, ligne 4 ✓", l3 and l3[1] == "barrée" and l4 and l4[1] == "ok", lignes=b4["lignes"])
        qs = await s.attendre(lambda: s.outil("question_suivante", debut), 30)
        etape("question_suivante", qs, resultat=qs and qs[1])
        if qs:
            await s.calme(qs[0], 20)
            etape("question de la tangente posée", True, dit=[r for _, r in s.repliques(qs[0])])

        # Bloqué, indice de niveau 1.
        fin = await dire("bloque")
        ind = await s.attendre(lambda: s.outil("donner_indice", fin - 3), 20)
        etape("donner_indice niveau 1", ind and ind[1].get("niveau") == 1, resultat=ind and ind[1])
        await s.calme(fin, 25)
        etape("indice reformulé", True, dit=[r for _, r in s.repliques(fin)])

        # Bonne réponse, fin, compte-rendu.
        fin = await dire("tangente")
        tc = await s.attendre(lambda: s.outil("terminer_colle", fin - 3), 25)
        if not tc:
            m["écarts"].append("terminer_colle pas appelé seul : l'élève dit avoir fini")
            etape("terminer_colle", False, dit=[r for _, r in s.repliques(fin)])
        else:
            etape("terminer_colle", True, dit=[r for _, r in s.repliques(fin - 3)])
            fin_colle = tc[0]
            pret = None
            while s.t() - fin_colle < 60:
                st = (await http.get("/api/report/status")).json()
                if st["pret"]:
                    pret = s.t()
                    break
                await asyncio.sleep(0.25)
            rapport = {}
            for f in sorted((KL / "data" / "reports").glob("*.json"), reverse=True):
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("session_id") == s.session:
                    rapport = d
                    break
            html = (await http.get("/api/report/latest")).text
            e3 = [e for e in rapport.get("erreurs", []) if e.get("ligne") == 3]
            m["rapport_s"] = pret and round(pret - fin_colle, 1)
            m["rapport_affiché_s"] = pret and round(pret - fin_colle + RAPPORT_MS / 2000, 1)
            etape("compte-rendu < 20 s, ligne 3 « corrigée après question »",
                  pret and m["rapport_affiché_s"] <= 20 and e3 and e3[0].get("corrigee_apres_question")
                  and "corrigée après question" in html,
                  genere_s=rapport.get("duree_generation_s"), moteur=rapport.get("moteur"),
                  terminer_colle_vers_pret_s=m["rapport_s"], erreurs=rapport.get("erreurs"))
        with contextlib.suppress(Exception):
            await ws.send(json.dumps({"type": "stop"}))
        micro.fermer()
        for x in taches:
            x.cancel()
    await asyncio.sleep(2)
    m["erreurs_serveur"] = s.erreurs
    m["ok"] = all(e["ok"] for e in m["etapes"].values()) and not s.erreurs
    return m


async def main():
    passages = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    client = gradium.client.GradiumClient(api_key=__import__("os").environ["GRADIUM_API_KEY"])
    audio = {k: await synthese(client, f"scn_{k}", p) for k, p in PHRASES.items()}
    log(f"Serveur {ea.SERVEUR}, envoi {ATTENTE_MS} ms après le stylet, panneau {PANNEAU_MS} ms, rapport {RAPPORT_MS} ms")
    resultats = []
    async with httpx.AsyncClient(base_url=f"http://{ea.SERVEUR}", timeout=60) as http:
        for n in range(1, passages + 1):
            resultats.append(await passage(n, audio, http))
            await asyncio.sleep(3)
    log("=" * 70)
    for r in resultats:
        lat = [v for v in r["latences_parole_s"].values() if v is not None]
        log(f"Passage {r['passage']} : {'RÉUSSI' if r['ok'] else 'ÉCHEC'}")
        for nom, e in r["etapes"].items():
            if not e["ok"]:
                log(f"   KO {nom} :", json.dumps(e, ensure_ascii=False))
        log(f"   stylet levé -> ligne rouge (portable) : {r.get('stylo_rouge_s')} s")
        log(f"   ligne rouge -> question du khôlleur : {r.get('rouge_vers_question_s')} s")
        log(f"   fin de parole -> voix du khôlleur : médiane {statistics.median(lat) if lat else None} s, "
            f"max {max(lat) if lat else None} s, {r['latences_parole_s']}")
        log(f"   terminer_colle -> compte-rendu prêt : {r.get('rapport_s')} s (affiché : {r.get('rapport_affiché_s')} s)")
    (ea.ICI / "scenario_demo.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0 if all(r["ok"] for r in resultats) else 1)


if __name__ == "__main__":
    asyncio.run(main())
