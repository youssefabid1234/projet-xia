"""Notation commune aux sorties du tuteur et aux anciens textes du catalogue."""
import re


CONSIGNE_LATEX = r"""Écris toutes les formules en LaTeX compatible KaTeX, entre
$...$ uniquement. Les délimiteurs \(, \), \[, \] et $$ sont interdits.
Conserve les commandes LaTeX utiles (fractions, sommes, ensembles, etc.)."""


def normaliser_latex(texte):
    # Conversion des anciens délimiteurs sans toucher aux commandes des formules
    # ni aux dollars échappés (montants monétaires).
    fin_precedente = -1

    def formule(match):
        nonlocal fin_precedente
        separation = " " if match.start() == fin_precedente else ""
        fin_precedente = match.end()
        return separation + "$" + next(v for v in match.groups() if v is not None) + "$"

    return re.sub(
        r"(?<!\\)(?:\\\((.*?)\\\)|\\\[(.*?)\\\]|\$\$(.*?)\$\$|\$((?:\\.|[^$\\])*)\$)",
        formule,
        texte, flags=re.S,
    )


def sans_references_cours(texte):
    """Retirer les localisateurs bibliographiques, pas la numérotation des questions."""
    morceaux = re.split(r"(\$(?:\\.|[^$\\])*\$)", normaliser_latex(texte))
    return "".join(morceau if i % 2 else _sans_localisateurs(morceau)
                   for i, morceau in enumerate(morceaux))


def _sans_localisateurs(texte):
    original = texte
    texte = re.sub(r"\b(définition|definition|théorème|theoreme|proposition|lemme|corollaire)\s+\d+(?:\.\d+)*",
                   r"\1", texte, flags=re.I)
    texte = re.sub(r"\bpages?\s+(?:PDF\s+)?\d+(?:\s*[-–,]\s*\d+)*", "", texte, flags=re.I)
    texte = re.sub(r"(?<![\w.])\d+(?:\.\d+){2,}(?![\w.]|\.\d)", "", texte)
    if texte == original:
        return texte
    texte = re.sub(r"\(\s*[,;]?\s*\)", "", texte)
    return re.sub(r"[ \t]+([.,])", r"\1", re.sub(r"[ \t]{2,}", " ", texte))
