"""Correspondance interne des supports et intitulé présenté à l'élève."""

CHAPITRE_SERIES = "17 — Série de réels ou de complexes"
NOM_SERIES = "Series numeriques"
ALIASES_SERIES = {CHAPITRE_SERIES, "16 — Séries numériques", "Séries numériques", NOM_SERIES}


def nom_chapitre(chapitre):
    return NOM_SERIES if chapitre in ALIASES_SERIES else chapitre


def chapitre_catalogue(chapitre):
    return CHAPITRE_SERIES if chapitre in ALIASES_SERIES else chapitre


def donnees_publiques(valeur):
    """Masque les intitulés des supports sans toucher aux textes ni aux sources."""
    if isinstance(valeur, dict):
        return {k: nom_chapitre(v) if k == "chapitre" else donnees_publiques(v)
                for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [donnees_publiques(v) for v in valeur]
    return valeur
