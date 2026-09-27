"""Colle en terminal avec les vrais services, et mesure de la latence de chaque tour.

python -m scripts.simuler_colle                      # réponses saisies au clavier
python -m scripts.simuler_colle "réponse 1" "réponse 2" ...   # scénario scripté
Commandes : /juste répond avec la réponse attendue (pour parcourir la colle),
/bilan termine la colle. Le profil utilisé est temporaire.
"""

import asyncio
import sys
import tempfile
import time
from pathlib import Path

from app.chapitres import CHAPITRE_SERIES, COLLES
from app.colle import Colle, charger_banque
from app.config import charger_env
from app.enonces import CacheEnonces
from app.examinateur import Examinateur, prechauffer
from app.profil import charger_exercices
from app.services import Services


async def jouer(examinateur, generateur):
    debut = time.perf_counter()
    premier = None
    async for evenement in generateur:
        if evenement["type"] == "statut":
            print(f"  … {evenement['texte']}", flush=True)
        elif evenement["type"] == "texte":
            if premier is None:
                premier = time.perf_counter() - debut
                print("Colleur : ", end="", flush=True)
            print(evenement["texte"], end="", flush=True)
        elif evenement["type"] == "question":
            q = evenement["question"]
            print(f"\n\n  [{q['libelle']}] {q['texte']}", flush=True)
        elif evenement["type"] == "action":
            print(f"  (action serveur : {evenement['action']}, verdict : {evenement['verdict']})", flush=True)
        elif evenement["type"] == "erreur":
            print(f"  ERREUR : {evenement['texte']}", flush=True)
    total = time.perf_counter() - debut
    print(f"\n  ⏱ premier mot après {premier or 0:.1f} s, tour complet en {total:.1f} s\n", flush=True)


async def main(scenario):
    charger_env()
    services = Services()
    debut = time.perf_counter()
    await prechauffer(services)
    print(f"(préchauffage du processus : {time.perf_counter() - debut:.1f} s)\n")
    config = COLLES[CHAPITRE_SERIES]
    with tempfile.TemporaryDirectory() as dossier:
        colle = Colle(Path(dossier) / "eleve.json", CHAPITRE_SERIES, charger_exercices(),
                      charger_banque(config["questions"], config["index"]))
        examinateur = Examinateur(colle, services, CacheEnonces())
        message = await examinateur.demarrer()
        print(f"Colleur : {message['texte']}\n\n  [{message['question']['libelle']}] {message['question']['texte']}\n")
        while True:
            if scenario:
                reponse = scenario.pop(0)
                print(f"Vous : {reponse}")
            elif scenario is not None and not sys.stdin.isatty():
                reponse = "/bilan"
            else:
                reponse = input("Vous : ")
            if reponse.strip() == "/juste" and colle.tache:
                reponse = colle.tache["reference"]
                print(f"  (réponse attendue envoyée : {reponse[:120]}…)")
            if reponse.strip() == "/bilan":
                await jouer(examinateur, examinateur.bilan())
                return
            await jouer(examinateur, examinateur.tour(reponse))
            if scenario == [] and len(sys.argv) > 1:
                await jouer(examinateur, examinateur.bilan())
                return


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main(sys.argv[1:] or None))
