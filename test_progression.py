"""Simulation locale de six réponses, sans Pipelex ni dépendance externe.

Exécution : python test_progression.py
Le rapport est écrit dans test_progression.md, sans modifier la banque d'exercices.
"""

import json
from math import isclose
from pathlib import Path

from app.profil import CHEMIN_EXERCICES, Profil, charger_exercices, choisir_exercice

ROOT = Path(__file__).resolve().parent
CHAPITRE = "2 — Dérivation et Intégration"
PARCOURS = [
    ("correcte", "aucune"),
    ("correcte", "aucune"),
    ("correcte", "aucune"),
    ("correcte", "aucune"),
    ("incomplete", "justification_manquante"),
    ("incorrecte", "calcul"),
]
# Résultats attendus de la logique actuelle, y compris l'ordre de départage
# des égalités (première occurrence dans le JSON).
ATTENDUS = [
    ("2.1", 1, 1.8),
    ("2.2", 2, 2.1),
    ("2.19", 2, 2.4),
    ("2.7", 3, 2.7),
    ("2.9", 3, 2.8),
    ("2.11", 3, 2.6),
]


def simuler():
    source_avant = CHEMIN_EXERCICES.read_bytes()
    source = json.loads(source_avant)
    # Vérification du contrat de choisir_exercice AVANT toute sélection.
    integration = [e for e in source if e["identifiant"].startswith("2.")]
    assert len(integration) >= len(PARCOURS), "Pas assez d'exercices d'intégration"
    assert all(e["chapitre"] == CHAPITRE for e in integration), (
        "Le chapitre du JSON doit correspondre exactement au chapitre sélectionné"
    )
    difficultes_source = {e["identifiant"]: e["difficulte"] for e in source}
    exercices = charger_exercices()
    profil = Profil("Élève simulé")
    assert isclose(profil.niveau(CHAPITRE), 1.5)
    lignes = []
    for etape, ((verdict, type_erreur), attendu) in enumerate(zip(PARCOURS, ATTENDUS), 1):
        ancien = profil.niveau(CHAPITRE)
        exercice = choisir_exercice(profil, CHAPITRE, exercices)
        assert exercice is not None, f"Aucun exercice à l'étape {etape}"
        identifiant = exercice["id"]
        assert exercice["chapitre"] == CHAPITRE
        assert identifiant not in profil.exercices_vus, "Exercice déjà proposé"
        assert (identifiant, exercice["difficulte"]) == attendu[:2]
        profil.enregistrer(identifiant, CHAPITRE, verdict, type_erreur)
        nouveau = profil.niveau(CHAPITRE)
        assert isclose(nouveau, attendu[2]), f"Niveau inattendu à l'étape {etape}"
        lignes.append((etape, identifiant, difficultes_source[identifiant],
                       exercice["difficulte"], verdict, ancien, nouveau))
    assert len(profil.historique) == len(profil.exercices_vus) == 6
    assert profil.erreurs_frequentes() == [("justification_manquante", 1), ("calcul", 1)]
    assert profil.niveau("18 — Topologie") == 1.5, "Autre chapitre affecté"
    assert CHEMIN_EXERCICES.read_bytes() == source_avant, "La banque a été modifiée"
    return lignes


def main():
    lignes = simuler()
    rapport = [
        "# Simulation de progression",
        "Chapitre : **2 — Dérivation et Intégration**. Niveau initial : **1,5**.",
        "Le champ `chapitre` du JSON correspond exactement au filtre de "
        "`choisir_exercice` : aucune correction de ce champ n'est nécessaire.",
        "Simulation exécutée avec `app/profil.py`, sans appel Pipelex. "
        "Les verdicts sont fixés dans le script : quatre réponses correctes, "
        "une incomplète (`incomplete`), puis une incorrecte.",
        "Le chargeur associe `identifiant` à `id` en mémoire. Il traite une "
        "difficulté source de 0 comme une difficulté de 1 pour la sélection ; "
        "le JSON reste inchangé. À distance égale du niveau, le premier "
        "exercice dans l'ordre du JSON est retenu.",
        "| Étape | Exercice proposé | Difficulté source | Difficulté utilisée | Verdict simulé | Niveau avant | Nouveau niveau |\n"
        "|---|---|---:|---:|---|---:|---:|",
    ]
    for etape, identifiant, source, utilisee, verdict, ancien, nouveau in lignes:
        rapport[-1] += (
            f"\n| {etape} | {identifiant} | {source} | {utilisee} | {verdict} | "
            f"{ancien:.1f} | {nouveau:.1f} |"
        )
    rapport.extend([
        "Les gains appliqués sont +0,3 pour `correcte`, +0,1 pour `incomplete` "
        "et −0,2 pour `incorrecte`. Le niveau final est **2,6**.",
        "Vérifications réussies : six exercices distincts du bon chapitre, "
        "séquence et niveaux attendus, historique de six réponses, erreurs "
        "enregistrées, autre chapitre inchangé et fichier JSON non modifié.",
        "Reproduction : `python test_progression.py`.",
    ])
    destination = ROOT / "test_progression.md"
    destination.write_text("\n\n".join(rapport) + "\n", encoding="utf-8")
    print(f"Simulation validée : 6 exercices, niveau 1.5 -> 2.6. Rapport : {destination.name}")


if __name__ == "__main__":
    main()
