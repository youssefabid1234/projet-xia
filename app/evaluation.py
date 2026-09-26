"""Appel Pipelex commun au script de test et à l'interface web."""

from pathlib import Path

from pipelex_sdk.client import PipelexAPIClient

BUNDLE_DIR = Path(__file__).resolve().parent.parent / "methods" / "evaluation_maths_prepa"
PIPE_CODE = "evaluation_maths_prepa.evaluer_reponse"


async def evaluer_reponse(client: PipelexAPIClient, enonce: str, reponse: str, corrige: str):
    if not isinstance(corrige, str) or not corrige.strip():
        raise ValueError("Correction impossible : le corrigé du catalogue est absent ou vide.")
    fichiers = sorted(BUNDLE_DIR.rglob("*.mthds"))
    if not fichiers:
        raise ValueError(f"Aucun fichier .mthds trouvé dans {BUNDLE_DIR}.")
    return await client.start_and_wait(
        pipe_code=PIPE_CODE,
        mthds_contents=[f.read_text(encoding="utf-8") for f in fichiers],
        inputs={"enonce": enonce, "reponse_eleve": reponse, "corrige": corrige},
    )
