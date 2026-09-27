"""Boucle asyncio dédiée et clients API partagés entre les requêtes.

Flask traite les requêtes dans des threads synchrones. Plutôt que de créer une
boucle et de nouveaux clients HTTP à chaque message (connexions TLS et poignée
de main Pipelex refaites à chaque fois), une seule boucle tourne en arrière-plan
et conserve les clients OpenAI et Pipelex.
"""

import asyncio
import queue
import threading

from app.config import charger_env

_FIN = object()


class Services:
    def __init__(self):
        self._boucle = asyncio.new_event_loop()
        self._fil = threading.Thread(target=self._boucle.run_forever, name="services-async", daemon=True)
        self._fil.start()
        self._openai = None
        self._pipelex = None

    def executer(self, coroutine, timeout=None):
        """Exécute une coroutine sur la boucle partagée et attend son résultat."""
        return asyncio.run_coroutine_threadsafe(coroutine, self._boucle).result(timeout)

    def lancer(self, coroutine):
        """Lance une coroutine sur la boucle partagée sans attendre son résultat."""
        return asyncio.run_coroutine_threadsafe(coroutine, self._boucle)

    def iterer(self, generateur):
        """Lance tout de suite un générateur asynchrone et renvoie un itérateur synchrone.

        Le générateur s'exécute jusqu'au bout sur la boucle partagée, même si
        personne ne lit la suite (navigateur fermé) : l'état reste cohérent.
        """
        file = queue.Queue()

        async def pomper():
            try:
                async for element in generateur:
                    file.put(element)
            except BaseException as exc:  # transmis au thread appelant
                file.put(exc)
            finally:
                file.put(_FIN)

        asyncio.run_coroutine_threadsafe(pomper(), self._boucle)

        def lire():
            while True:
                element = file.get()
                if element is _FIN:
                    return
                if isinstance(element, BaseException):
                    raise element
                yield element
        return lire()

    async def openai(self):
        if self._openai is None:
            import httpx
            from openai import AsyncOpenAI, DefaultAsyncHttpxClient
            charger_env()
            # Connexions gardées ouvertes pendant que l'élève réfléchit (5 s par
            # défaut), pour éviter une nouvelle poignée de main TLS à chaque tour.
            self._openai = AsyncOpenAI(timeout=45, max_retries=2, http_client=DefaultAsyncHttpxClient(
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=120)))
        return self._openai

    async def pipelex(self):
        if self._pipelex is None:
            from pipelex_sdk.client import PipelexAPIClient
            charger_env()
            self._pipelex = PipelexAPIClient().start_client()
        return self._pipelex


_services = None
_verrou = threading.Lock()


def services():
    global _services
    with _verrou:
        if _services is None:
            _services = Services()
        return _services
