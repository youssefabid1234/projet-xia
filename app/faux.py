"""Doublures des services externes pour les tests hors ligne (aucun crédit consommé)."""

import asyncio
import json
from types import SimpleNamespace

from app.services import Services

EVALUATION_PAR_DEFAUT = {"verdict": "incomplete", "type_erreur": "reponse_incomplete", "explication": "Il manque un élément.",
                       "intuition": "partielle", "progression": "stagne", "notions_fragiles": []}


class FauxFlux:
    """Flux de réponse OpenAI : des morceaux de texte, puis éventuellement une panne."""

    def __init__(self, texte, panne=None):
        self.morceaux = [texte[i:i + 7] for i in range(0, len(texte), 7)]
        self.panne = panne

    def __aiter__(self):
        return self._generer()

    async def _generer(self):
        for morceau in self.morceaux:
            yield SimpleNamespace(type="response.output_text.delta", delta=morceau)
        if self.panne:
            raise self.panne
        yield SimpleNamespace(type="response.completed")


class FauxOpenAI:
    """Répond selon le format demandé : analyse, évaluation, vérification ou flux de texte.

    Chaque liste est consommée dans l'ordre ; une exception y est levée telle quelle.
    Pour un flux, un couple (texte, exception) simule une panne en cours de diffusion.
    """

    def __init__(self, intentions=(), evaluations=(), textes=(), verifications=(), plans=()):
        self.intentions = list(intentions)
        self.evaluations = list(evaluations)
        self.textes = list(textes)
        self.verifications = list(verifications)
        self.plans = list(plans)
        self.appels = []
        self.delai = 0  # secondes d'attente simulées avant chaque réponse
        self.responses = SimpleNamespace(create=self._creer)
        self.embeddings = SimpleNamespace(create=self._embedding)

    @staticmethod
    def _suivant(liste, defaut):
        valeur = liste.pop(0) if liste else defaut
        if isinstance(valeur, BaseException):
            raise valeur
        return valeur

    async def _creer(self, **arguments):
        self.appels.append(arguments)
        if self.delai:
            await asyncio.sleep(self.delai)
        if arguments.get("stream"):
            texte = self._suivant(self.textes, "Bien.")
            return FauxFlux(*texte) if isinstance(texte, tuple) else FauxFlux(texte)
        nom = arguments.get("text", {}).get("format", {}).get("name")
        if nom == "analyse":
            contenu = {"intention": self._suivant(self.intentions, "reponse")}
        elif nom == "evaluation":
            contenu = self._suivant(self.evaluations, EVALUATION_PAR_DEFAUT)
        elif nom == "verification_exercice":
            contenu = self._suivant(self.verifications, {"exploitable": False, "enonce": "", "corrige": ""})
        elif nom == "plan_resolution":
            contenu = self._suivant(self.plans, {"exploitable": True, "etapes": [
                {"objectif": "Résoudre", "question": "Justifiez votre réponse.", "indice": "Reprenez la définition.", "reponse": "Solution de test."}]})
        else:
            raise AssertionError(f"Format inattendu : {nom}")
        return SimpleNamespace(output_text=json.dumps(contenu, ensure_ascii=False), status="completed")

    async def _embedding(self, **arguments):
        raise AssertionError("Recherche dans le cours non simulée pour ce test.")

    def appels_flux(self):
        return [a for a in self.appels if a.get("stream")]


class FauxServices(Services):
    """Vraie boucle asynchrone partagée, clients externes simulés."""

    def __init__(self, openai):
        super().__init__()
        self._openai = openai
        self._pipelex = SimpleNamespace()


class ServicesSimples:
    """Pour les tests asynchrones : seulement les clients."""

    def __init__(self, openai):
        self.client = openai

    async def openai(self):
        return self.client

    async def pipelex(self):
        return SimpleNamespace()
