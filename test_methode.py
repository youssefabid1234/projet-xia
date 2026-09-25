"""Exécute evaluation_maths_prepa via l'API hébergée Pipelex.

Dépendance : python -m pip install "pipelex-sdk>=0.10.2"
Définir PIPELEX_API_KEY dans l'environnement, puis : python test_methode.py
Le SDK lit cette variable directement ; aucun fichier .env n'est chargé.

Documentation : https://docs.pipelex.com/latest/get-started/quick-start/#via-api
"""

import asyncio
import json
import os
from pathlib import Path

from pipelex_sdk.client import PipelexAPIClient


BUNDLE_DIR = Path(__file__).resolve().parent / "methods" / "evaluation_maths_prepa"
PIPE_CODE = "evaluation_maths_prepa.evaluer_reponse"

# Réponse volontairement erronée : l'exercice permet de tester le diagnostic.
EXEMPLE = {
    "enonce": (
        "Soit f : R -> R définie par f(x) = x exp(x). "
        "Calculer f'(x) en justifiant la formule utilisée."
    ),
    "reponse_eleve": (
        "La dérivée d'un produit est le produit des dérivées. "
        "Donc f'(x) = 1 * exp(x) = exp(x)."
    ),
}


async def main() -> None:
    if not os.environ.get("PIPELEX_API_KEY", "").strip():
        raise SystemExit("Veuillez définir la variable d'environnement PIPELEX_API_KEY.")

    fichiers = sorted(BUNDLE_DIR.rglob("*.mthds"))
    if not fichiers:
        raise SystemExit(f"Aucun fichier .mthds trouvé dans {BUNDLE_DIR}.")
    contenus = [fichier.read_text(encoding="utf-8") for fichier in fichiers]

    # Le SDK lit PIPELEX_API_KEY et attend la fin de l'exécution distante.
    async with PipelexAPIClient() as client:
        resultat = await client.start_and_wait(
            pipe_code=PIPE_CODE,
            mthds_contents=contenus,
            inputs=EXEMPLE,
        )

    print(f"Exécution : {resultat.pipeline_run_id}")
    print(json.dumps(resultat.main_stuff, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
