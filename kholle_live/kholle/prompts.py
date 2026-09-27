"""Consignes du khôlleur vocal. [lane A]

Attention : les .md de prompts/ contiennent d'autres accolades que les
champs à remplir ; utiliser str.replace, pas str.format.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from . import exercises
from .state import Session

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
_SYMBOLES = {"ok": "✓", "faux": "✗", "?": "?"}


def build_instructions(session: Session) -> str:
    # TODO(A) : n'envoyer que la question courante, les indices déjà donnés, etc.
    modele = (PROMPTS / "kholleur_system.md").read_text(encoding="utf-8")
    exercice = yaml.safe_dump(
        exercises.get(session.exercise_id), allow_unicode=True, sort_keys=False
    )
    tableau = "\n".join(
        f"{l.n}. {_SYMBOLES[l.verdict]} {l.texte}" + (" (barrée)" if l.barre else "")
        for l in session.board_lines
    ) or "(vide)"
    return modele.replace("{exercice}", exercice).replace("{tableau}", tableau)
