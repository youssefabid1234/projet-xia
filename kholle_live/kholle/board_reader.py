"""Lecture du tableau manuscrit par un modèle de vision (prompts/board_reader.md). [lane B]"""

from __future__ import annotations

import base64
import functools
import json
import os
from pathlib import Path

from openai import OpenAI

from .state import BoardLine
from .verifier import check_line

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


def read_board(png: bytes, exercise: dict) -> list[BoardLine]:
    """Transcrit le tableau (PNG, ou photo JPEG) puis vérifie chaque ligne avec SymPy."""
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
