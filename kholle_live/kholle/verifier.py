"""Vérification SymPy d'une ligne de DL. [lane B]

Une ligne « lhs = rhs + o(var^ordre) » au point p est juste si
series(lhs - rhs, var, p, ordre + 1) est nulle. Dans le doute (ligne barrée,
illisible, non vérifiable, incompréhensible pour SymPy, trop longue à
calculer), le verdict est "?", jamais "faux".
"""

from __future__ import annotations

import concurrent.futures
import dataclasses
import logging
import re
from collections import defaultdict

import sympy
from sympy.core.function import AppliedUndef
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_application,
    implicit_multiplication,
    parse_expr,
    standard_transformations,
)

from .state import BoardLine

logger = logging.getLogger(__name__)

DELAI_S = 2.0
ORDRE_MAX = 12
LONGUEUR_MAX = 300

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication,
    implicit_application,
    convert_xor,
)


def _reste(*_args):
    """o(...) ou O(...) laissé par erreur dans rhs : on l'efface."""
    return sympy.Integer(0)


x, u, t = sympy.symbols("x u t")
LOCALES = {
    "x": x,
    "u": u,
    "t": t,
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "exp": sympy.exp,
    "log": sympy.log,
    "ln": sympy.log,
    "sqrt": sympy.sqrt,
    "pi": sympy.pi,
    "E": sympy.E,
    "e": sympy.E,
    "o": _reste,
    "O": _reste,
}
# Juste ce dont les transformations de parse_expr ont besoin, sans builtins.
GLOBALES = {
    "__builtins__": {},
    "Symbol": sympy.Symbol,
    "Function": sympy.Function,
    "Integer": sympy.Integer,
    "Float": sympy.Float,
    "Rational": sympy.Rational,
    "factorial": sympy.factorial,
}
# Accès d'attribut, dunder, lambda, chaînes : rien de tout ça dans un DL manuscrit.
INTERDIT = re.compile(r"__|[A-Za-z_]\s*\.|\.\s*[A-Za-z_]|\blambda\b|['\"\\;]")

_executeur = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="verif")


class NonVerifiable(Exception):
    pass


def check_line(line: BoardLine, defs: dict | None) -> BoardLine:
    """Renvoie la ligne avec verdict "ok" / "faux" / "?" et un détail éventuel.

    `defs` : les definitions_sympy de l'exercice, ex. {"f(x)": "log(1+sin(x))"}.
    """
    if line.barre:
        return _resultat(line, "?", "ligne barrée")
    if not line.lisible:
        return _resultat(line, "?", "ligne mal lue")
    if not line.verifiable or not line.lhs or not line.rhs or not line.var or line.ordre is None:
        return _resultat(line, "?", "ligne non vérifiable")

    tache = _executeur.submit(
        _verifier, line.lhs, line.rhs, line.var, line.point or "0", line.ordre, dict(defs or {})
    )
    try:
        verdict, detail = tache.result(timeout=DELAI_S)
    except concurrent.futures.TimeoutError:
        tache.cancel()
        return _resultat(line, "?", "vérification trop longue")
    except NonVerifiable as e:
        return _resultat(line, "?", str(e))
    except Exception:
        logger.exception("Vérification en échec : %r", line)
        return _resultat(line, "?", "SymPy ne sait pas vérifier cette ligne")
    return _resultat(line, verdict, detail)


def _resultat(line: BoardLine, verdict: str, detail: str | None) -> BoardLine:
    return dataclasses.replace(line, verdict=verdict, detail=detail)


def _verifier(lhs: str, rhs: str, var: str, point: str, ordre: int, defs: dict) -> tuple[str, str | None]:
    ordre = int(ordre)
    if not 0 <= ordre <= ORDRE_MAX:
        raise NonVerifiable(f"ordre {ordre} hors de portée")
    if not re.fullmatch(r"[A-Za-z]\w*", var):
        raise NonVerifiable("variable illisible")

    v = sympy.Symbol(var)
    gauche = _parser(_substituer(lhs, defs))
    droite = sympy.nsimplify(_parser(_substituer(rhs, defs)), rational=True)
    p = _parser(point)
    if p.free_symbols or not p.is_finite:
        raise NonVerifiable("point non géré")

    difference = gauche - droite
    if difference.atoms(AppliedUndef):
        raise NonVerifiable("fonction inconnue")
    if difference.free_symbols - {v}:
        raise NonVerifiable("symboles inconnus")

    h = sympy.Dummy("h")
    developpement = sympy.series(difference.subs(v, p + h), h, 0, ordre + 1).removeO()

    coefficients: dict[sympy.Expr, sympy.Expr] = defaultdict(lambda: sympy.Integer(0))
    for terme in sympy.Add.make_args(sympy.expand(developpement)):
        coeff, exposant = terme.as_coeff_exponent(h)
        if coeff.has(h):
            raise NonVerifiable("développement non polynomial")
        coefficients[exposant] += coeff

    for exposant in sorted(coefficients, key=lambda e: float(e)):
        c = sympy.simplify(coefficients[exposant])
        if c == 0:
            continue
        if c.is_zero is False:
            return "faux", f"erreur sur le {_nom_terme(v, p, exposant)}"
        raise NonVerifiable("coefficient indécidable")
    return "ok", None


def _parser(texte: str) -> sympy.Expr:
    if len(texte) > LONGUEUR_MAX or INTERDIT.search(texte):
        raise NonVerifiable("expression refusée")
    try:
        expr = parse_expr(
            texte,
            local_dict=dict(LOCALES),
            global_dict=dict(GLOBALES),
            transformations=TRANSFORMATIONS,
        )
    except Exception as e:
        raise NonVerifiable("SymPy ne comprend pas la ligne") from e
    if not isinstance(expr, sympy.Expr):
        raise NonVerifiable("expression invalide")
    return expr


def _substituer(texte: str, defs: dict) -> str:
    """Remplace f(x) (ou f seul) par sa définition, ex. f(x) -> (log(1+sin(x)))."""
    for cle, valeur in defs.items():
        m = re.fullmatch(r"\s*([A-Za-z]\w*)\s*(?:\(\s*([A-Za-z]\w*)\s*\))?\s*", str(cle))
        if not m:
            continue
        nom, argument = m.groups()
        remplacement = f"({valeur})"
        if argument:
            texte = re.sub(rf"\b{nom}\s*\(\s*{argument}\s*\)", lambda _: remplacement, texte)
        texte = re.sub(rf"\b{nom}\b(?!\s*\()", lambda _: remplacement, texte)
    return texte


def _nom_terme(v: sympy.Symbol, p: sympy.Expr, exposant: sympy.Expr) -> str:
    if exposant == 0:
        return "terme constant"
    base = str(v) if p == 0 else f"({v - p})"
    if exposant == 1:
        return f"terme en {base}"
    puissance = str(exposant) if exposant.is_Integer else f"({exposant})"
    return f"terme en {base}^{puissance}"
