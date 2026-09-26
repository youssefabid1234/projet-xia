"""Recherche sémantique dans le cours indexé, avec références de page."""
from functools import lru_cache
from collections import Counter
import json
import math
from pathlib import Path
import re
import unicodedata

from openai import APIError, AsyncOpenAI

INDEX = Path(__file__).resolve().parents[1] / "data/cours_index.json"

STOP = set("a au aux avec ce ces comment dans de des du elle en est et etre faire il la le les lui montre montrer ne on ou par pas pour qu que quel quelle quelles quels qui se son sont sur un une vous c d l n s t y".split())


def mots(texte):
    texte = "".join(c for c in unicodedata.normalize("NFKD", texte.lower()) if not unicodedata.combining(c))
    return [m.rstrip("s") if len(m) > 4 else m for m in re.findall(r"[a-z]{2,}", texte)
            if m not in STOP]


def scores_lexicaux(question, passages):
    """BM25 : les mots rares (ex. « reste ») complètent la proximité sémantique."""
    documents = [Counter(mots(p["titre"] + " " + p["titre"] + " " + p["texte"])) for p in passages]
    longueurs = [sum(d.values()) for d in documents]
    moyenne = sum(longueurs) / len(documents) or 1
    scores = [0.] * len(documents)
    for mot in set(mots(question)):
        frequence = sum(mot in d for d in documents)
        poids = math.log(1 + (len(documents) - frequence + .5) / (frequence + .5))
        for i, document in enumerate(documents):
            occurrence = document[mot]
            scores[i] += poids * occurrence * 2.5 / (occurrence + 1.5 * (.25 + .75 * longueurs[i] / moyenne))
    maximum = max(scores, default=0) or 1
    return [score / maximum for score in scores]


def normaliser(vecteur, dimensions):
    if len(vecteur) != dimensions or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in vecteur):
        raise ValueError("Dimensions ou valeurs d'embedding invalides.")
    norme = math.sqrt(sum(x * x for x in vecteur))
    if not norme or not math.isfinite(norme):
        raise ValueError("Embedding nul ou invalide.")
    return tuple(x / norme for x in vecteur)


@lru_cache(maxsize=2)
def charger_index(chemin, modification, taille):
    # La signature du fichier invalide le cache après une réindexation.
    try:
        contenu = json.loads(Path(chemin).read_text(encoding="utf-8"))
        dimensions = contenu["dimensions"]
        if contenu["statut"] != "indexe" or not contenu["passages"] or dimensions <= 0:
            raise ValueError("Index vide ou incomplet.")
        vecteurs = [normaliser(p["embedding"], dimensions) for p in contenu["passages"]]
        return contenu, vecteurs
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("L'index du cours est illisible ou invalide. Relancer l'indexation.") from exc


async def chercher_dans_cours(question, client=None, *, chemin=INDEX):
    """Renvoie cinq passages par recherche hybride : cosinus et BM25."""
    if not isinstance(question, str) or not question.strip() or len(question) > 2000:
        raise ValueError("La question de cours doit contenir de 1 à 2 000 caractères.")
    try:
        stat = Path(chemin).stat()
    except OSError as exc:
        raise ValueError("Le cours n'est pas encore indexé sur le serveur.") from exc
    index, vecteurs = charger_index(str(chemin), stat.st_mtime_ns, stat.st_size)
    if client is None:
        async with AsyncOpenAI(timeout=60, max_retries=1) as client:
            return await chercher_dans_cours(question, client, chemin=chemin)
    try:
        resultat = await client.embeddings.create(
            model=index["modele_embedding"], input=[question.strip()],
            dimensions=index["dimensions"], encoding_format="float",
        )
    except APIError as exc:
        raise ValueError("La recherche dans le cours est temporairement indisponible. Réessayez.") from exc
    if len(resultat.data) != 1 or resultat.data[0].index != 0:
        raise ValueError("Réponse d'embedding incomplète.")
    requete = normaliser(resultat.data[0].embedding, index["dimensions"])
    cosinus = [sum(x * y for x, y in zip(requete, vecteur)) for vecteur in vecteurs]
    lexicaux = scores_lexicaux(question, index["passages"])
    scores = [semantic + .25 * lexical for semantic, lexical in zip(cosinus, lexicaux)]
    positions = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
    champs = ("identifiant", "titre", "type", "section", "contexte", "texte", "page_source", "transcription_relue", "contient_preuve")
    return {"question": question, "chapitre": index["chapitre"],
            "information": "Passages classés par proximité ; vérifier leur pertinence. Les formules non relues peuvent être dégradées par l'extraction PDF.",
            "passages": [{**{k: index["passages"][i][k] for k in champs if k in index["passages"][i]},
                          "score": round(scores[i], 6), "similarite_cosinus": round(cosinus[i], 6),
                          "score_lexical": round(lexicaux[i], 6)} for i in positions]}
