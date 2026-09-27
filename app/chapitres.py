"""Correspondance interne des supports et intitulé présenté à l'élève."""

import difflib
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

CHAPITRE_SERIES = "17 — Série de réels ou de complexes"
NOM_SERIES = "Séries numériques"
# Le cours indexé (chapitre 16 du polycopié de cours) et les exercices
# (chapitre 17 du recueil) portent des numéros différents : même notion.
FORMES_SERIES = {"series", "series numeriques", "serie de reels ou de complexes", "series de reels ou de complexes"}

# Chapitres pour lesquels une colle complète est possible (cours indexé et banque de questions).
COLLES = {
    CHAPITRE_SERIES: {
        "nom": NOM_SERIES,
        "index": RACINE / "data" / "cours_index.json",
        "questions": RACINE / "data" / "questions_cours.json",
    },
}


def normaliser(texte):
    texte = unicodedata.normalize("NFKD", texte.lower())
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"^\s*\d+\s*[—–-]\s*", "", texte)
    mots = [m for m in re.findall(r"[a-z]+", texte) if m not in ("les", "la", "le", "des")]
    return " ".join(m[:-1] if m.endswith("s") and len(m) > 3 else m for m in mots)


def est_series(chapitre):
    if not isinstance(chapitre, str) or not chapitre.strip():
        return False
    forme = normaliser(chapitre)
    formes = {normaliser(f) for f in FORMES_SERIES}
    return forme in formes or any(
        difflib.SequenceMatcher(None, forme, f).ratio() >= 0.9 for f in formes if len(forme) > 8)


def nom_chapitre(chapitre):
    return NOM_SERIES if est_series(chapitre) else chapitre


def chapitre_catalogue(chapitre):
    return CHAPITRE_SERIES if est_series(chapitre) else chapitre


def donnees_publiques(valeur):
    """Masque les intitulés des supports sans toucher aux textes ni aux sources."""
    if isinstance(valeur, dict):
        return {k: nom_chapitre(v) if k == "chapitre" else donnees_publiques(v)
                for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [donnees_publiques(v) for v in valeur]
    return valeur
