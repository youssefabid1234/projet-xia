"""Outils du khôlleur vocal : définitions pour le LLM et effets sur state. [lane A]

Les effets de bord hors state (pousser une nouvelle config, lancer le
compte-rendu) sont dans main.py.
"""

from __future__ import annotations

import json

import gradbot

from . import exercises, state


def _outil(nom: str, description: str) -> gradbot.ToolDef:
    sans_parametre = {"type": "object", "properties": {}, "required": []}
    return gradbot.ToolDef(nom, description, json.dumps(sans_parametre))


OUTILS = [
    _outil(
        "donner_indice",
        "Donne l'indice suivant de la question en cours. À appeler quand l'étudiant est "
        "bloqué ou demande de l'aide. Reformule ensuite l'indice en une phrase, à l'oral, "
        "sans aucun symbole.",
    ),
    _outil(
        "question_suivante",
        "Passe à la question suivante, une fois la réponse juste obtenue. Renvoie la "
        "question à poser, ou fin=true s'il n'y en a plus.",
    ),
    _outil(
        "terminer_colle",
        "Termine la khôlle et lance la rédaction du compte-rendu. À appeler juste après "
        "avoir annoncé la fin à l'étudiant, jamais avant qu'il ait répondu à la dernière question.",
    ),
]


def donner_indice() -> dict:
    s = state.get_session()
    ex = exercises.get(s.exercise_id)
    indices = exercises.question(ex, s.question_index).get("indices", [])
    niveau = 1 + sum(h.question_index == s.question_index for h in s.hints)
    if niveau > len(indices):
        return {"indice": None, "message": "plus d'indice"}
    state.add_hint(s.question_index, niveau)
    return {"niveau": niveau, "indice": indices[niveau - 1]}


def question_suivante() -> dict:
    """Reste sur la dernière question quand il n'y en a plus (question_index valide)."""
    s = state.get_session()
    try:
        q = exercises.question(exercises.get(s.exercise_id), s.question_index + 1)
    except IndexError:
        return {"fin": True}
    s.question_index += 1
    return {"question": q["question_orale"]}


def terminer_colle() -> dict:
    state.get_session().finished = True
    return {"ok": True}


EXECUTER = {
    "donner_indice": donner_indice,
    "question_suivante": question_suivante,
    "terminer_colle": terminer_colle,
}
