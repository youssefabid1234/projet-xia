"""Consignes du khôlleur vocal. [lane A]

Attention : les .md de prompts/ contiennent d'autres accolades que les
champs à remplir ; utiliser str.replace, pas str.format.
"""

from __future__ import annotations

from collections.abc import Collection, Iterable
from pathlib import Path

from . import exercises
from .state import BoardLine, Session

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
_SYMBOLES = {"ok": "✓", "faux": "✗", "?": "?"}


def cle_ligne(ligne: BoardLine) -> str:
    """Identifie une ligne d'un envoi à l'autre, même si la numérotation bouge."""
    return " ".join(ligne.texte.split())


def erreurs(lignes: Iterable[BoardLine]) -> set[str]:
    """Clés des lignes fausses (non barrées) : à retenir après chaque envoi au LLM."""
    return {cle_ligne(l) for l in lignes if l.verdict == "faux" and not l.barre}


def build_instructions(session: Session, deja_faux: Collection[str] = ()) -> str:
    """Consignes complètes : modèle + exercice (sans les indices) + tableau.

    `deja_faux` : les `erreurs()` du tableau lors de l'envoi précédent. Les lignes
    fausses absentes de cet ensemble sont préfixées « NOUVELLE ERREUR ».
    """
    modele = (PROMPTS / "kholleur_system.md").read_text(encoding="utf-8")
    return modele.replace("{exercice}", _exercice(session)).replace(
        "{tableau}", _tableau(session.board_lines, deja_faux)
    )


def _exercice(session: Session) -> str:
    ex = exercises.get(session.exercise_id)
    oral = ex.get("enonce_oral") or "(aucun : reformule l'énoncé écrit à voix haute, sans symbole)"
    parties = [
        f"Énoncé écrit (affiché à l'étudiant) : {ex['enonce_latex']}",
        f"Énoncé oral (à lire) : {oral}",
        f"Réponse attendue : {ex['reponse']['latex']}",
    ]
    if ex.get("pieges"):
        parties.append("Pièges :\n" + "\n".join(f"- {p}" for p in ex["pieges"]))
    if session.question_index > 0:
        q = exercises.question(ex, session.question_index)
        parties += [
            "L'exercice principal est résolu. QUESTION EN COURS (déjà posée) : "
            + q["question_orale"],
            f"Réponse attendue à cette question : {q['reponse']}",
        ]
    return "\n".join(parties)


def _tableau(lignes: list[BoardLine], deja_faux: Collection[str]) -> str:
    return "\n".join(_ligne(l, cle_ligne(l) not in deja_faux) for l in lignes) or "(tableau vide)"


def _ligne(l: BoardLine, nouvelle: bool) -> str:
    if l.barre:
        return f"L{l.n} (barrée)"
    texte = f"L{l.n} {_SYMBOLES[l.verdict]} {l.texte}"
    if l.verdict != "faux":
        return texte
    if l.detail:
        texte += f" — {l.detail}"
    return f"NOUVELLE ERREUR {texte}" if nouvelle else texte
