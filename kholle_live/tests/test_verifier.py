import pytest

from kholle.state import BoardLine
from kholle.verifier import check_line

DEFS_LN_SIN = {"f(x)": "log(1+sin(x))"}


def ligne(lhs, rhs, ordre, var="x", point="0", **champs):
    valeurs = dict(
        n=1,
        texte=f"{lhs} = {rhs} + o({var}^{ordre})",
        barre=False,
        lisible=True,
        verifiable=True,
        lhs=lhs,
        rhs=rhs,
        var=var,
        point=point,
        ordre=ordre,
    )
    valeurs.update(champs)
    return BoardLine(**valeurs)


@pytest.mark.parametrize(
    "lhs, rhs, ordre, var, defs",
    [
        ("sin(x)", "x - x**3/6", 3, "x", {}),
        ("cos(x)", "1 - x**2/2 + x**4/24", 4, "x", {}),
        ("exp(x)", "1 + x + x**2/2 + x**3/6", 3, "x", {}),
        ("tan(x)", "x + x**3/3", 3, "x", {}),
        ("1/(1-x)", "1 + x + x**2 + x**3", 3, "x", {}),
        ("log(1+sin(x))", "x - x**2/2 + x**3/6", 3, "x", {}),
        ("exp(sin(x))", "1 + x + x**2/2", 3, "x", {}),
        ("log(1+u)", "u - u**2/2", 2, "u", {}),
        ("f(x)", "x - x**2/2 + x**3/6", 3, "x", DEFS_LN_SIN),
    ],
)
def test_ligne_juste(lhs, rhs, ordre, var, defs):
    resultat = check_line(ligne(lhs, rhs, ordre, var), defs)
    assert resultat.verdict == "ok", resultat.detail


@pytest.mark.parametrize(
    "lhs, rhs, ordre, degre",
    [
        ("sin(x)", "x + x**3/6", 3, 3),
        ("cos(x)", "1 - x**2/2 + x**4/12", 4, 4),
        ("log(1+x)", "x - x**2/2 + x**3/6", 3, 3),
        ("tan(x)", "x + x**3/6", 3, 3),
        ("sqrt(1+x)", "1 + x/2 - x**2/4", 2, 2),
        ("log(1+sin(x))", "x - x**2/2 - x**3/6", 3, 3),
        ("exp(sin(x))", "1 + x + x**2/2 + x**3/6", 3, 3),
    ],
)
def test_ligne_fausse_donne_le_premier_terme_faux(lhs, rhs, ordre, degre):
    resultat = check_line(ligne(lhs, rhs, ordre), {})
    assert resultat.verdict == "faux"
    assert resultat.detail == f"erreur sur le terme en x^{degre}"


def test_ligne_non_verifiable():
    texte = BoardLine(1, "on pose u = sin x", False, True, False, None, None, None, None, None)
    assert check_line(texte, {}).verdict == "?"


def test_ligne_illisible_par_sympy():
    assert check_line(ligne("sin(x", "x", 1), {}).verdict == "?"


def test_ligne_marquee_illisible_jamais_fausse():
    assert check_line(ligne("sin(x)", "x + x**3/6", 3, lisible=False), {}).verdict == "?"


def test_ligne_barree_jamais_fausse():
    assert check_line(ligne("sin(x)", "x + x**3/6", 3, barre=True), {}).verdict == "?"


def test_reste_o_laisse_dans_rhs():
    assert check_line(ligne("sin(x)", "x - x**3/6 + o(x**3)", 3), {}).verdict == "ok"


def test_notation_manuscrite():
    assert check_line(ligne("ln(1+x)", "x - x^2/2 + x^3/3", 3), {}).verdict == "ok"
    assert check_line(ligne("cos(x)", "1 - 0.5x^2", 2), {}).verdict == "ok"


def test_autre_point():
    assert check_line(ligne("log(x)", "(x-1) - (x-1)**2/2", 2, point="1"), {}).verdict == "ok"
    resultat = check_line(ligne("log(x)", "(x-1) + (x-1)**2/2", 2, point="1"), {})
    assert resultat.verdict == "faux"
    assert resultat.detail == "erreur sur le terme en (x - 1)^2"


def test_code_arbitraire_refuse():
    attaque = "x.__class__.__mro__[-1].__subclasses__()"
    assert check_line(ligne(attaque, "x", 1), {}).verdict == "?"
