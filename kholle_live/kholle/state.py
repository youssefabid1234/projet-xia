"""Contrat partagé : l'état de la khôlle en cours.

Une seule session de démo, en mémoire, sans base de données.
Tous les temps `t` sont en secondes écoulées depuis `Session.started_at`
(lui-même un horodatage `time.time()`).

Ne pas changer une signature sans prévenir les trois lanes.
"""

from __future__ import annotations

import asyncio
import dataclasses
import inspect
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

logger = logging.getLogger(__name__)

Qui = Literal["eleve", "kholleur"]
Verdict = Literal["ok", "faux", "?"]


@dataclass
class Turn:
    t: float
    qui: Qui
    texte: str


@dataclass
class BoardLine:
    n: int
    texte: str
    barre: bool
    lisible: bool
    verifiable: bool
    lhs: str | None
    rhs: str | None
    var: str | None
    point: str | None
    ordre: int | None
    verdict: Verdict = "?"
    detail: str | None = None


@dataclass
class HintUse:
    t: float
    question_index: int
    niveau: int


@dataclass
class Session:
    id: str
    eleve: str | None
    exercise_id: str
    started_at: float
    question_index: int = 0
    transcript: list[Turn] = field(default_factory=list)
    board_lines: list[BoardLine] = field(default_factory=list)
    # Chaque instantané : {"t": float, "lines": [dict de BoardLine, ...]}
    board_snapshots: list[dict] = field(default_factory=list)
    hints: list[HintUse] = field(default_factory=list)
    finished: bool = False
    report: dict | None = None


# Rappel appelé à chaque set_board(session). Peut être async : il est alors
# planifié sur la boucle en cours.
BoardCallback = Callable[[Session], Any]

_session: Session | None = None
_callbacks: list[BoardCallback] = []
_taches: set[asyncio.Task] = set()


def _t(session: Session) -> float:
    return time.time() - session.started_at


def new_session(exercise_id: str) -> Session:
    """Remplace la session courante. Les rappels enregistrés sont conservés."""
    global _session
    _session = Session(
        id=uuid.uuid4().hex[:8],
        eleve=None,
        exercise_id=exercise_id,
        started_at=time.time(),
    )
    return _session


def get_session() -> Session:
    if _session is None:
        raise LookupError("Aucune session : appeler new_session() d'abord.")
    return _session


def add_turn(qui: Qui, texte: str) -> Turn:
    s = get_session()
    turn = Turn(t=_t(s), qui=qui, texte=texte)
    s.transcript.append(turn)
    return turn


def set_board(lines: list[BoardLine]) -> None:
    """Remplace le tableau, ajoute un instantané et prévient les abonnés."""
    s = get_session()
    s.board_lines = list(lines)
    s.board_snapshots.append(
        {"t": _t(s), "lines": [dataclasses.asdict(l) for l in s.board_lines]}
    )
    for callback in list(_callbacks):
        try:
            resultat = callback(s)
            if inspect.isawaitable(resultat):
                _planifier(resultat)
        except Exception:
            logger.exception("Rappel de tableau en échec : %r", callback)


def add_hint(question_index: int, niveau: int) -> HintUse:
    s = get_session()
    hint = HintUse(t=_t(s), question_index=question_index, niveau=niveau)
    s.hints.append(hint)
    return hint


def on_board_change(callback: BoardCallback) -> BoardCallback:
    """Abonne `callback(session)` aux changements de tableau. Utilisable en décorateur."""
    _callbacks.append(callback)
    return callback


def _planifier(coro) -> None:
    try:
        boucle = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
        return
    tache = boucle.create_task(coro)
    _taches.add(tache)
    tache.add_done_callback(_taches.discard)
