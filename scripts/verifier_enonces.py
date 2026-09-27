"""Vérifie d'avance les exercices du catalogue et remplit data/enonces_verifies.json.

Exécution depuis la racine :
    python -m scripts.verifier_enonces [--chapitre 17] [--refaire | --ecartes] [--modele gpt-4.1]
Un appel OpenAI par exercice non encore vérifié (ou dont le texte a changé).
Sans ce cache, la vérification a lieu pendant la colle, au premier exercice proposé.
"""

import argparse
import asyncio
import os
import sys

from openai import AsyncOpenAI

from app.config import charger_env
from app.enonces import CacheEnonces
from app.profil import charger_exercices


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapitre", default="17", help="préfixe du chapitre du catalogue (défaut : 17)")
    parser.add_argument("--refaire", action="store_true", help="revérifier même les exercices en cache")
    parser.add_argument("--ecartes", action="store_true", help="revérifier seulement les exercices écartés")
    parser.add_argument("--modele", help="modèle OpenAI de vérification (défaut : OPENAI_MODEL)")
    options = parser.parse_args()
    charger_env()
    if options.modele:
        os.environ["OPENAI_MODEL"] = options.modele
    cache = CacheEnonces()
    exercices = [ex for ex in charger_exercices() if ex["chapitre"].startswith(options.chapitre)]
    if options.ecartes:
        options.refaire = True
        a_faire = [ex for ex in exercices if cache.lire(ex) == (True, None)]
    else:
        a_faire = [ex for ex in exercices if options.refaire or not cache.lire(ex)[0]]
    print(f"{len(exercices)} exercices, {len(a_faire)} à vérifier.", flush=True)
    limite = asyncio.Semaphore(4)
    async with AsyncOpenAI(timeout=120, max_retries=2) as client:
        async def verifier(exercice):
            async with limite:
                try:
                    if options.refaire:
                        from app.enonces import verifier_exercice
                        resultat = await verifier_exercice(exercice["enonce"], exercice.get("corrige"), client)
                        cache.ecrire(exercice, resultat)
                    else:
                        resultat = await cache.exercice_verifie(exercice, client)
                except ValueError as exc:
                    print(f"  {exercice['id']} : ÉCHEC ({exc}) — sera réessayé", flush=True)
                    return
                print(f"  {exercice['id']} : {'retenu' if resultat else 'écarté (ambigu)'}", flush=True)
        await asyncio.gather(*(verifier(ex) for ex in a_faire))
    retenus = sum(1 for ex in exercices if cache.lire(ex)[1])
    print(f"Exercices exploitables : {retenus}/{len(exercices)}.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
