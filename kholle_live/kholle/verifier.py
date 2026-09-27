"""Vérification SymPy d'une ligne de DL. [lane B]"""

from __future__ import annotations

from .state import BoardLine


def check_line(line: BoardLine, defs: dict) -> BoardLine:
    """Renvoie la ligne avec verdict "ok" / "faux" / "?" et un détail éventuel.

    `defs` : les definitions_sympy de l'exercice, ex. {"f(x)": "log(1+sin(x))"}.
    """
    # TODO(B) : series(lhs, var, point, ordre + 1) comparé à rhs.
    return line
