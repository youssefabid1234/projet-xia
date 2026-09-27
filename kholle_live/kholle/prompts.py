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


def nouvelles_erreurs(lignes: Iterable[BoardLine], deja_faux: Collection[str]) -> list[BoardLine]:
    return [l for l in lignes if not l.barre and l.verdict == "faux" and cle_ligne(l) not in deja_faux]


def build_instructions(session: Session, deja_faux: Collection[str] = ()) -> str:
    """Consignes complètes : alerte éventuelle + modèle + exercice (sans les indices) + tableau.

    `deja_faux` : les `erreurs()` du tableau lors de l'envoi précédent. Les lignes
    fausses absentes de cet ensemble sont préfixées « NOUVELLE ERREUR ».
    """
    modele = (PROMPTS / "kholleur_system.md").read_text(encoding="utf-8")
    texte = modele.replace("{exercice}", _exercice(session)).replace(
        "{tableau}", rendre_tableau(session.board_lines, deja_faux)
    )
    nouvelles = nouvelles_erreurs(session.board_lines, deja_faux)
    return f"{alerte(nouvelles) if nouvelles else SILENCE}\n\n{texte}"


# En tête, comme l'alerte : dans le corps des consignes, la règle n'était suivie
# qu'une fois sur deux (le khôlleur reformulait sa question avec une piste).
SILENCE = (
    "SI L'ÉTUDIANT SE TAIT (son message est « ... ») : demande seulement où il en est, "
    "sans aucune piste mathématique et sans reposer ta question sous un autre angle. "
    "Toute piste passe par donner_indice."
)


def alerte(nouvelles: list[BoardLine]) -> str:
    """En tête des consignes : en fin de consignes, le tableau se noie dans le long
    prompt système de gradbot et, en audio, le LLM répondait à côté après un silence."""
    lignes = "\n".join(
        f"- ligne {l.n} : « {l.texte} »" + (f" ({l.detail})" if l.detail else "") for l in nouvelles
    )
    return (
        "PRIORITÉ ABSOLUE : l'étudiant vient d'écrire au tableau une ligne fausse.\n"
        f"{lignes}\n"
        "Ta prochaine prise de parole, même après un silence (« ... »), désigne cette ligne "
        "(« votre troisième ligne ») et pose UNE question qui oriente vers la cause de l'erreur, "
        "sans la corriger. C'est l'exception à la règle du silence : ne demande ni où il en est "
        "ni ce qu'il cherche."
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
    # En audio, le khôlleur disait la phrase de fin sans appeler terminer_colle.
    if session.question_index == len(ex.get("questions_suivantes", [])):
        parties.append(
            "C'est la dernière question : dès qu'elle est résolue, dis la phrase de fin et "
            "appelle terminer_colle dans la même réponse, sans attendre que l'étudiant parle."
        )
    return "\n".join(parties)


def rendre_tableau(lignes: list[BoardLine], deja_faux: Collection[str] = ()) -> str:
    """Le champ {tableau} : une ligne par ligne du tableau, puis la priorité éventuelle."""
    if not lignes:
        return "(tableau vide)"
    nouvelles = [l.n for l in nouvelles_erreurs(lignes, deja_faux)]
    texte = "\n".join(_ligne(l, l.n in nouvelles) for l in lignes)
    if nouvelles:
        texte += (
            "\n→ À traiter maintenant : "
            + ", ".join(f"L{n}" for n in nouvelles)
            + " (nouvelle erreur). Désigne cette ligne et pose une question qui oriente vers l'erreur."
        )
    return texte


def _ligne(l: BoardLine, nouvelle: bool) -> str:
    if l.barre:
        return f"L{l.n} (barrée)"
    texte = f"L{l.n} {_SYMBOLES[l.verdict]} {l.texte}"
    if l.verdict != "faux":
        return texte
    if l.detail:
        texte += f" — {l.detail}"
    return f"NOUVELLE ERREUR {texte}" if nouvelle else texte
