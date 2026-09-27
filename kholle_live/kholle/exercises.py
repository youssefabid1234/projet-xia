"""Banque d'exercices : data/exercises.yaml. [lane A]"""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

FICHIER = Path(__file__).resolve().parent.parent / "data" / "exercises.yaml"


@functools.cache
def _charger() -> dict[str, dict]:
    with FICHIER.open(encoding="utf-8") as f:
        return {e["id"]: e for e in yaml.safe_load(f)}


def get(id: str) -> dict:
    """Lève KeyError si l'identifiant est inconnu."""
    return _charger()[id]


def all() -> list[dict]:
    return list(_charger().values())


def all_tags() -> list[str]:
    tags: dict[str, None] = {}
    for e in all():
        tags.update(dict.fromkeys(e.get("tags", [])))
    return list(tags)


def demo() -> dict:
    """L'exercice marqué `demo: true` (à défaut, le premier)."""
    exos = all()
    return next((e for e in exos if e.get("demo")), exos[0])


def question(ex: dict, index: int) -> dict:
    """Question n° `index` : 0 = l'exercice lui-même, k >= 1 = questions_suivantes[k-1].

    Lève IndexError si elle n'existe pas.
    """
    if index == 0:
        return ex
    suivantes = ex.get("questions_suivantes", [])
    if not 1 <= index <= len(suivantes):
        raise IndexError(f"{ex['id']} n'a pas de question {index}")
    return suivantes[index - 1]
