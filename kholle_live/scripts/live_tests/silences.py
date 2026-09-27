"""Relances après un silence, avec l'élève synthétique (lane A). Une seule khôlle :

(i)   lignes justes écrites en silence pendant 90 s -> aucune relance ;
(ii)  ligne fausse écrite en silence -> pas de question avant 60 s, question vers 60 s ;
(iii) nouvelle ligne fausse, ligne rouge, « Voilà. » -> question sur cette ligne en ~2 s ;
(iv)  « Je ne vois pas. » -> donner_indice.

Le silence se compte comme dans gradbot : depuis la dernière voix du khôlleur.

    SERVEUR=127.0.0.1:8000 uv run python scripts/live_tests/silences.py

Aucun terminer_colle : pas de compte-rendu écrit dans data/.
"""

import asyncio
import json
import os
import re
import sys

import httpx
import websockets

import eleve_audio as ea
from eleve_audio import Micro, log, synthese
from scenario_demo import ATTENTE_MS, CAUSE, L1, L2, L3, PANNEAU_MS, REPONSE, SUR_LA_LIGNE, Suivi, ecrire

import gradium  # noqa: E402

# Nouvelle ligne fausse pour (iii) : le -x³/6 du sinus oublié dans la composition.
L3B = "ln(1+sin x) = x - x^2/2 + x^3/3 + o(x^3)"
SUR_LA_LIGNE_4 = re.compile(r"quatrième ligne|ligne quatre|ligne 4|dernière ligne|nouvelle ligne", re.I)
TERME = re.compile(r"x (au )?cube|coefficient|terme|sinus", re.I)
# Le bon coefficient ; citer la valeur fausse de l'élève (« x au cube sur trois ») est permis.
REPONSE_III = re.compile(r"plus (un sixième|x (au )?cube sur six)|\+ ?x\^?3 ?/ ?6", re.I)

PHRASES = {
    "prenom": "Bonjour, je m'appelle Pierre.",
    "transition": "J'ai écrit les deux développements, je passe à la composition.",
    "voila": "Voilà.",
    "vois_pas": "Je ne vois pas.",
}


async def main():
    client = gradium.client.GradiumClient(api_key=os.environ["GRADIUM_API_KEY"])
    audio = {k: await synthese(client, f"sil_{k}", p) for k, p in PHRASES.items()}
    boucle = asyncio.get_running_loop()
    file: asyncio.Queue = asyncio.Queue()
    s = Suivi()
    res: dict = {}

    def resultat(nom, ok, **infos):
        res[nom] = {"ok": bool(ok), **infos}
        log(f"[{'OK ' if ok else 'KO '}] {nom}", json.dumps(infos, ensure_ascii=False))

    def parole_depuis(t0: float, t1: float = float("inf")) -> dict:
        """Tout ce que le khôlleur a fait entre t0 et t1."""
        return {
            "audio": [round(t - t0, 1) for t, g, _ in s.evts if g == "audio" and t0 < t < t1][:1],
            "llm_started": [round(t - t0, 1) for t, g, e in s.evts if g == "event" and e == "llm_started" and t0 < t < t1],
            "dit": [r for _, r in s.repliques(t0, t1)],
            "outils": [n for t, n, _ in s.outils if t0 < t < t1],
        }

    async with httpx.AsyncClient(base_url=f"http://{ea.SERVEUR}", timeout=60) as http:
        log("Démo :", (await http.post("/api/session/new", json={})).json())
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
                return s.t()

            async def attendre_voix(apres: float, delai: float) -> float | None:
                return await s.attendre(lambda: s.premier_audio(apres), delai)

            await s.calme(0, 30)
            fin = await dire("prenom")
            await s.calme(fin, 30)
            log("KHÔLLEUR :", [r for _, r in s.repliques(fin)])

            # (i) Lignes justes en silence, 90 s.
            log("--- (i) lignes justes écrites en silence, 90 s")
            debut = s.dernier_audio()
            # Envois à 10 s et 40 s (stylet levé ATTENTE_MS plus tôt).
            b1 = await ecrire(http, s, [(L1, False)], "i1", debut + 10 - ATTENTE_MS / 1000)
            b2 = await ecrire(http, s, [(L1, False), (L2, False)], "i2", debut + 40 - ATTENTE_MS / 1000)
            await asyncio.sleep(max(0.0, debut + 90 - s.t()))
            p = parole_depuis(debut + 0.5)
            justes = all(v != "faux" for _, v, _ in b2["lignes"]) and len(b2["lignes"]) == 2
            resultat("(i) aucune relance en 90 s", not p["audio"] and not p["llm_started"] and justes,
                     silence_s=round(s.t() - debut, 1), tableau_1=b1["lignes"], tableau_2=b2["lignes"], **p)

            # L'élève parle : le silence repart de la réponse du khôlleur.
            fin = await dire("transition")
            await s.calme(fin, 20)
            log("KHÔLLEUR :", [r for _, r in s.repliques(fin)])
            await s.muet()

            # (ii) Ligne fausse écrite en silence : question vers 60 s, pas avant.
            log("--- (ii) ligne fausse écrite en silence")
            debut = s.dernier_audio()
            b3 = await ecrire(http, s, [(L1, False), (L2, False), (L3, False)], "ii", s.t() + 1.5)
            rouge = b3["lu"] + PANNEAU_MS / 2000
            voix = await attendre_voix(debut + 0.5, 110)
            await s.calme(debut + 0.5, 30)
            q = s.repliques(debut + 0.5)
            question = q[0][1] if q else None
            depuis_voix = voix and round(voix - debut, 1)
            resultat("(ii) question vers 60 s de silence, pas avant",
                     b3["lignes"][-1][1] == "faux" and depuis_voix and 60 <= depuis_voix <= 75
                     and question and (SUR_LA_LIGNE.search(question) or CAUSE.search(question))
                     and not REPONSE.search(question),
                     silence_vers_question_s=depuis_voix, ligne_rouge_apres_s=round(rouge - debut, 1),
                     rouge_vers_question_s=voix and round(voix - rouge, 1), tableau=b3["lignes"], dit=question)
            await s.muet()

            # (iii) Nouvelle ligne fausse, ligne rouge, « Voilà. ».
            log("--- (iii) nouvelle ligne fausse, ligne rouge, « Voilà. »")
            b4 = await ecrire(http, s, [(L1, False), (L2, False), (L3, True), (L3B, False)], "iii", s.t() + 1.5)
            await asyncio.sleep(PANNEAU_MS / 1000)  # le portable l'affiche au plus tard au sondage suivant
            await s.muet()
            avant = s.t()
            fin = await dire("voila")
            await s.calme(fin, 20)
            voix = s.premier_audio(fin)
            q = s.repliques(fin)
            question = q[0][1] if q else None
            resultat("(iii) « Voilà. » -> question sur la nouvelle ligne en ~2 s",
                     b4["lignes"][-1][1] == "faux" and voix and voix - fin <= 2.5
                     and question and (SUR_LA_LIGNE_4.search(question) or TERME.search(question))
                     and not SUR_LA_LIGNE.search(question)  # la ligne 3 est barrée
                     and not REPONSE_III.search(question),
                     voila_vers_voix_s=voix and round(voix - fin, 2), tableau=b4["lignes"], dit=question,
                     dit_avant_voila=[r for _, r in s.repliques(b4["lu"], avant)])
            await s.muet()

            # (iv) « Je ne vois pas. » -> donner_indice.
            log("--- (iv) « Je ne vois pas. »")
            fin = await dire("vois_pas")
            indice = await s.attendre(lambda: s.outil("donner_indice", fin - 1), 15)
            await s.calme(fin, 20)
            resultat("(iv) donner_indice appelé", indice, indice=indice and indice[1],
                     voix_s=(v := s.premier_audio(fin)) and round(v - fin, 2), dit=[r for _, r in s.repliques(fin)])

            await ws.send(json.dumps({"type": "stop"}))
            micro.fermer()
            for x in taches:
                x.cancel()
    res["erreurs_serveur"] = s.erreurs
    log("=" * 70)
    for nom, r in res.items():
        if nom != "erreurs_serveur":
            log(f"{'RÉUSSI' if r['ok'] else 'ÉCHEC '} {nom}")
    log("Erreurs serveur :", s.erreurs)
    (ea.ICI / "silences.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0 if all(r["ok"] for n, r in res.items() if n != "erreurs_serveur") and not s.erreurs else 1)


if __name__ == "__main__":
    asyncio.run(main())
