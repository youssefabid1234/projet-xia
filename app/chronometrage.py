"""Mesures par échange, sans enregistrer le contenu ni les identifiants élèves."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
import logging
from time import perf_counter
from uuid import uuid4

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_echange = ContextVar("chronometrage_echange", default=None)
ETAPES = ("dialogue_openai", "recherche_cours", "evaluation_pipelex", "progression")


@contextmanager
def mesurer(etape):
    suivi = _echange.get()
    debut = perf_counter()
    statut = "ok"
    try:
        yield
    except BaseException:
        statut = "erreur"
        raise
    finally:
        duree = perf_counter() - debut
        if suivi is not None:
            suivi["appels"].append({"etape": etape, "secondes": duree, "statut": statut})
            logger.info("TEMPS etape echange=%s etape=%s secondes=%.3f statut=%s",
                        suivi["id"], etape, duree, statut)


def chronometrer(etape):
    def decorer(fonction):
        @wraps(fonction)
        async def appel(*args, **kwargs):
            with mesurer(etape):
                return await fonction(*args, **kwargs)
        return appel
    return decorer


@contextmanager
def mesurer_echange():
    suivi = {"id": uuid4().hex[:12], "appels": []}
    token = _echange.set(suivi)
    debut = perf_counter()
    statut = "ok"
    try:
        yield suivi
    except BaseException:
        statut = "erreur"
        raise
    finally:
        total = perf_counter() - debut
        _echange.reset(token)
        repartition = {}
        for etape in ETAPES:
            appels = [a for a in suivi["appels"] if a["etape"] == etape]
            secondes = sum(a["secondes"] for a in appels)
            repartition[etape] = {"appels": len(appels), "secondes": round(secondes, 6),
                                  "pourcentage": round(100 * secondes / total, 2) if total else 0}
        autres = total - sum(a["secondes"] for a in suivi["appels"])
        suivi.update(statut=statut, total_secondes=round(total, 6),
                     autres_secondes=round(autres, 6), repartition=repartition)
        logger.info("TEMPS echange %s", json.dumps(suivi, ensure_ascii=False))
