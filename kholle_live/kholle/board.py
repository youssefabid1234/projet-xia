"""Routes du tableau (tablette -> lecture -> vérification -> state.set_board). [lane B]

Une seule lecture à la fois : les images reçues pendant une lecture ne sont
pas empilées, seule la dernière est lue ensuite.
"""

from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import logging
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from . import exercises, state
from .board_reader import _type_mime, read_board

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tableau"])

DOSSIER_ECHANTILLONS = Path(__file__).resolve().parent.parent / "eval" / "samples"
TAILLE_MAX = 15 * 1024 * 1024


@dataclasses.dataclass
class _Tableau:
    session_id: str | None = None
    empreinte: str | None = None
    image: bytes | None = None
    image_recue_a: float = 0.0
    en_attente: bytes | None = None
    tache: asyncio.Task | None = None
    erreur: str | None = None

    def lecture_en_cours(self) -> bool:
        return self.tache is not None and not self.tache.done()


_tableau = _Tableau()


def reinitialiser() -> None:
    global _tableau
    _tableau = _Tableau()


async def _corps_image(request: Request) -> bytes:
    image = await request.body()
    if not image:
        raise HTTPException(400, "Image vide.")
    if len(image) > TAILLE_MAX:
        raise HTTPException(413, "Image trop lourde.")
    return image


@router.get("/board", include_in_schema=False)
def page_tablette():
    return RedirectResponse("/static/board.html")


@router.post("/api/board", status_code=202)
async def recevoir_tableau(request: Request):
    image = await _corps_image(request)
    s = state.get_session()
    empreinte = hashlib.sha1(image).hexdigest()
    if empreinte == _tableau.empreinte and s.id == _tableau.session_id:
        return JSONResponse({"status": "identique"})

    _tableau.session_id = s.id
    _tableau.empreinte = empreinte
    _tableau.image = image
    _tableau.image_recue_a = time.time()
    if _tableau.lecture_en_cours():
        _tableau.en_attente = image
    else:
        _tableau.tache = asyncio.create_task(_lire_en_boucle(image))
    return {"status": "en lecture"}


async def _lire_en_boucle(image: bytes | None) -> None:
    while image is not None:
        await _lire(image)
        image, _tableau.en_attente = _tableau.en_attente, None


async def _lire(image: bytes) -> None:
    s = state.get_session()
    debut = time.time()
    try:
        lignes = await asyncio.to_thread(read_board, image, exercises.get(s.exercise_id))
    except Exception as e:
        logger.exception("Lecture du tableau en échec")
        _tableau.erreur = f"lecture impossible ({e.__class__.__name__})"
        return
    if state.get_session() is not s:
        return  # nouvelle session pendant la lecture : résultat périmé
    _tableau.erreur = None
    logger.info("Tableau lu en %.1f s : %s", time.time() - debut, [l.verdict for l in lignes])
    state.set_board(lignes)


@router.get("/api/board/state")
def etat_tableau():
    s = state.get_session()
    image_a_jour = _tableau.image is not None and _tableau.session_id == s.id
    return {
        "lines": [dataclasses.asdict(l) for l in s.board_lines],
        "image_url": f"/api/board/latest.png?v={int(_tableau.image_recue_a * 1000)}" if image_a_jour else None,
        "updated_at": s.started_at + s.board_snapshots[-1]["t"] if s.board_snapshots else None,
        "lecture_en_cours": _tableau.lecture_en_cours(),
        "erreur": _tableau.erreur,
    }


@router.get("/api/board/latest.png")
def derniere_image():
    if _tableau.image is None or _tableau.session_id != state.get_session().id:
        raise HTTPException(404, "Aucun tableau reçu.")
    return Response(_tableau.image, media_type=_type_mime(_tableau.image), headers={"Cache-Control": "no-store"})


@router.post("/api/eval/sample")
async def echantillon_eval(request: Request, label: str = Query(pattern=r"^[A-Za-z0-9-]{1,20}$")):
    image = await _corps_image(request)
    DOSSIER_ECHANTILLONS.mkdir(parents=True, exist_ok=True)
    horodatage = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    chemin = DOSSIER_ECHANTILLONS / f"{label}_{horodatage}.png"
    chemin.write_bytes(image)
    return {"fichier": chemin.name}
