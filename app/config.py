"""Configuration : lecture du fichier .env local et réglages communs."""

import os
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]


def charger_env(chemin=RACINE / ".env"):
    """Ajoute les variables du fichier .env sans écraser celles déjà définies."""
    chemin = Path(chemin)
    if not chemin.is_file():
        return
    for ligne in chemin.read_text(encoding="utf-8-sig").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        cle, valeur = cle.strip().removeprefix("export ").strip(), valeur.strip()
        if len(valeur) >= 2 and valeur[0] == valeur[-1] and valeur[0] in "\"'":
            valeur = valeur[1:-1]
        if cle:
            os.environ.setdefault(cle, valeur)


def modele():
    return os.environ.get("OPENAI_MODEL", "").strip() or "gpt-4.1-mini"


def parametres_modele(temperature):
    """Modèle et température ; les modèles à raisonnement refusent la température."""
    nom = modele()
    if nom.startswith(("gpt-4", "gpt-3")):
        return {"model": nom, "temperature": temperature}
    return {"model": nom}


def evaluateur():
    """« local » : méthode d'évaluation exécutée via OpenAI ; « pipelex » : API Pipelex."""
    valeur = os.environ.get("COLLE_EVALUATEUR", "").strip().lower()
    return valeur if valeur in ("local", "pipelex") else "local"


def duree_colle_minutes():
    try:
        return max(5, min(120, int(os.environ.get("COLLE_DUREE_MINUTES", "30"))))
    except ValueError:
        return 30
