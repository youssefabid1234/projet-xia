"""Évaluation d'une réponse d'élève avec la méthode methods/evaluation_maths_prepa.

La méthode .mthds est la seule source des consignes de correction. Elle peut
être exécutée de deux façons :
- par l'API Pipelex (« pipelex ») : 7 à 20 s par appel, mesuré sur l'API hébergée ;
- localement (« local ») : le même prompt, le même système et le même schéma de
  sortie, envoyés directement à OpenAI en sortie structurée (1 à 3 s).
Le dialogue de colle utilise « local » par défaut (variable COLLE_EVALUATEUR).
"""

import json
import re
import tomllib
from functools import lru_cache
from pathlib import Path

from app.config import evaluateur, parametres_modele
from app.moteur_colle import valider_evaluation
from app.catalogue_pedagogique import notions_cours

BUNDLE_DIR = Path(__file__).resolve().parent.parent / "methods" / "evaluation_maths_prepa"
PIPE_CODE = "evaluation_maths_prepa.evaluer_reponse"
VERDICTS = ("correcte", "incorrecte", "incomplete", "indeterminable")


def fichiers_methode():
    fichiers = sorted(BUNDLE_DIR.rglob("*.mthds"))
    if not fichiers:
        raise ValueError(f"Aucun fichier .mthds trouvé dans {BUNDLE_DIR}.")
    return fichiers


def valider(evaluation):
    return valider_evaluation(evaluation, notions_cours())


def contexte_json(contexte=None):
    return json.dumps({**(contexte or {}), "notions_autorisees": list(notions_cours())}, ensure_ascii=False)


def verifier_corrige(corrige):
    if not isinstance(corrige, str) or not corrige.strip():
        raise ValueError("Correction impossible : le corrigé du catalogue est absent ou vide.")


async def evaluer_reponse(client, enonce: str, reponse: str, corrige: str, wait_options=None, *, contexte=None):
    """Exécution par l'API Pipelex (interface classique et tuteur en terminal)."""
    verifier_corrige(corrige)
    return await client.start_and_wait(
        pipe_code=PIPE_CODE,
        mthds_contents=[f.read_text(encoding="utf-8") for f in fichiers_methode()],
        inputs={"enonce": enonce, "reponse_eleve": reponse, "corrige": corrige, "contexte": contexte_json(contexte)},
        wait_options=wait_options,
    )


@lru_cache(maxsize=1)
def methode_locale():
    """Lit le système, le prompt et le schéma de sortie de la méthode .mthds."""
    methode = tomllib.loads(fichiers_methode()[0].read_text(encoding="utf-8"))
    pipe = methode["pipe"][methode["main_pipe"]]
    concepts = methode.get("concept", {})
    structure = concepts[pipe["output"]]["structure"]
    proprietes = {}
    for nom, champ in structure.items():
        if isinstance(champ, str):
            champ = {"description": champ}
        propriete = {"type": "string", "description": champ.get("description", "")}
        if champ.get("type") == "list":
            if champ.get("item_type") != "text":
                raise ValueError("Type de liste non pris en charge.")
            propriete.update(type="array", items={"type": "string"})
        if "choices" in champ:
            propriete["enum"] = list(champ["choices"])
        proprietes[nom] = propriete
    entrees = {nom: concepts.get(concept, {}).get("description", nom)
               for nom, concept in pipe["inputs"].items()}
    return {
        "systeme": methode.get("system_prompt", "").strip(),
        "prompt": pipe["prompt"],
        "entrees": entrees,
        "format": {"type": "json_schema", "name": pipe["output"].lower(), "strict": True,
                   "schema": {"type": "object", "properties": proprietes,
                              "required": list(proprietes), "additionalProperties": False}},
    }


def rendre_prompt(methode, valeurs):
    def bloc(correspondance):
        nom = correspondance.group(1)
        if nom not in valeurs:
            return correspondance.group(0)
        return f"<{nom} description=\"{methode['entrees'][nom]}\">\n{valeurs[nom]}\n</{nom}>"
    return re.sub(r"@(\w+)", bloc, methode["prompt"])


async def evaluer_localement(client, enonce, reponse, corrige, *, contexte=None):
    verifier_corrige(corrige)
    methode = methode_locale()
    resultat = await client.responses.create(
        **parametres_modele(0.1), instructions=methode["systeme"],
        input=[{"role": "user", "content": rendre_prompt(methode, {
            "enonce": enonce, "reponse_eleve": reponse, "corrige": corrige, "contexte": contexte_json(contexte)})}],
        text={"format": methode["format"]}, store=False,
    )
    if resultat.status != "completed":
        raise ValueError("Évaluation interrompue.")
    return valider(json.loads(resultat.output_text))


async def evaluer(enonce, reponse, corrige, *, openai=None, pipelex=None, moteur=None, contexte=None):
    """Évalue avec le moteur configuré ; les clients partagés sont réutilisés."""
    moteur = moteur or evaluateur()
    if moteur == "pipelex":
        from pipelex_sdk.runs import WaitForResultOptions
        resultat = await evaluer_reponse(pipelex, enonce, reponse, corrige,
                                         WaitForResultOptions(interval_seconds=0.5, timeout_seconds=120), contexte=contexte)
        return valider(resultat.main_stuff)
    return await evaluer_localement(openai, enonce, reponse, corrige, contexte=contexte)
