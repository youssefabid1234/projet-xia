"""Lecture du tableau manuscrit par un modèle de vision (prompts/board_reader.md). [lane B]"""

from __future__ import annotations

from .state import BoardLine


def read_board(png: bytes, exercise: dict) -> list[BoardLine]:
    # TODO(B) : appel VISION_MODEL, JSON -> BoardLine (verdict laissé à "?").
    return []
