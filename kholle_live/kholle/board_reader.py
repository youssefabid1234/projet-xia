"""Lecture du tableau manuscrit par un modèle de vision (prompts/board_reader.md). [lane B]

Contre les fausses alertes : l'image est lue deux fois en parallèle. Dès qu'une
ligne sort "faux" de la première lecture, elle ne reste "faux" que si la seconde
la trouve fausse aussi ; sinon elle passe à "?". Sans ligne fausse, la seconde
lecture n'est pas attendue.
"""

from __future__ import annotations

import base64
import dataclasses
import functools
import json
import logging
import os
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from openai import OpenAI

from .state import BoardLine
from .verifier import check_line

logger = logging.getLogger(__name__)

# Lignes "faux" relues, et relectures qui ne l'ont pas confirmé (depuis le démarrage).
_stats = {"relectures": 0, "desaccords": 0}

PROMPT = Path(__file__).resolve().parent.parent / "prompts" / "board_reader.md"

_TEXTE_OU_NUL = {"type": ["string", "null"]}
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["lines"],
    "properties": {
        "lines": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["n", "texte", "barre", "lisible", "verifiable", "lhs", "rhs", "var", "point", "ordre"],
                "properties": {
                    "n": {"type": "integer"},
                    "texte": {"type": "string"},
                    "barre": {"type": "boolean"},
                    "lisible": {"type": "boolean"},
                    "verifiable": {"type": "boolean"},
                    "lhs": _TEXTE_OU_NUL,
                    "rhs": _TEXTE_OU_NUL,
                    "var": _TEXTE_OU_NUL,
                    "point": _TEXTE_OU_NUL,
                    "ordre": {"type": ["integer", "null"]},
                },
            },
        }
    },
}
FORMAT = {"type": "json_schema", "name": "tableau", "strict": True, "schema": SCHEMA}


@functools.cache
def _client() -> OpenAI:
    return OpenAI(timeout=30.0, max_retries=1)


def _consignes(exercise: dict) -> str:
    defs = exercise.get("definitions_sympy") or {}
    definitions = "; ".join(f"{k} = {v}" for k, v in defs.items()) or "none"
    # Le prompt contient d'autres accolades : str.replace, pas str.format.
    return PROMPT.read_text(encoding="utf-8").replace("{definitions}", definitions)


def _type_mime(image: bytes) -> str:
    if image.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if image[:4] == b"RIFF" and image[8:12] == b"WEBP":
        return "image/webp"
    if image.startswith(b"GIF8"):
        return "image/gif"
    return "image/png"


def stats() -> dict[str, int]:
    return dict(_stats)


# Seconde lecture lancée avec la première : une ligne fausse s'affiche après une
# lecture au lieu de deux (5,6 s -> ~3 s sur un tableau de trois lignes).
_RELECTURE = ThreadPoolExecutor(max_workers=2, thread_name_prefix="relecture")


def read_board(png: bytes, exercise: dict) -> list[BoardLine]:
    """Transcrit le tableau (PNG, ou photo JPEG), vérifie chaque ligne avec SymPy
    et fait confirmer chaque ligne "faux" par une seconde lecture, faite en même temps."""
    seconde = _RELECTURE.submit(_lire, png, exercise)
    lignes = _lire(png, exercise)
    if any(l.verdict == "faux" for l in lignes):
        lignes = _confirmer(lignes, seconde)
    return lignes


def _confirmer(lignes: list[BoardLine], lecture: Future) -> list[BoardLine]:
    try:
        seconde = {l.n: l for l in lecture.result()}
    except Exception:
        logger.exception("Seconde lecture du tableau en échec")
        seconde = {}
    resultat = []
    for l in lignes:
        if l.verdict == "faux":
            _stats["relectures"] += 1
            autre = seconde.get(l.n)
            if autre is None or autre.verdict != "faux":
                _stats["desaccords"] += 1
                logger.info("L%d non confirmée : 1re lecture %r, 2e %r", l.n, l.texte, autre and autre.texte)
                l = dataclasses.replace(l, verdict="?", detail="non confirmée par une seconde lecture")
        resultat.append(l)
    logger.info("Relectures : %(desaccords)d désaccord(s) sur %(relectures)d ligne(s) fausse(s)", _stats)
    return resultat


def _lire(png: bytes, exercise: dict) -> list[BoardLine]:
    url = f"data:{_type_mime(png)};base64,{base64.b64encode(png).decode('ascii')}"
    reponse = _client().responses.create(
        model=os.environ.get("VISION_MODEL") or "gpt-4.1-mini",
        instructions=_consignes(exercise),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": url, "detail": "high"},
                    {"type": "input_text", "text": "Transcribe this board."},
                ],
            }
        ],
        text={"format": FORMAT},
        store=False,
    )
    brutes = json.loads(reponse.output_text)["lines"]
    defs = exercise.get("definitions_sympy") or {}
    return [check_line(BoardLine(**brute), defs) for brute in brutes]
