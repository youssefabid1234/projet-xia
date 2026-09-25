"""Tuteur interactif : python -m app.tuteur (ou python app/tuteur.py).

Dépendance : pipelex-sdk>=0.10.2. Définir PIPELEX_API_KEY dans
l'environnement ; aucun fichier .env n'est chargé automatiquement.
"""

import asyncio
import os
import sys
from pathlib import Path

from pipelex_sdk.client import PipelexAPIClient

if __package__:
    from .profil import GAINS, Profil, charger_exercices, choisir_exercice
else:
    from profil import GAINS, Profil, charger_exercices, choisir_exercice


ROOT = Path(__file__).resolve().parent.parent
CHEMIN_PROFIL = ROOT / "data" / "profil.json"
BUNDLE_DIR = ROOT / "methods" / "evaluation_maths_prepa"
PIPE_CODE = "evaluation_maths_prepa.evaluer_reponse"


async def main() -> None:
    exercices = charger_exercices()
    if not exercices:
        print("Aucun exercice disponible dans la banque.")
        return

    profil = Profil.charger(CHEMIN_PROFIL)
    chapitres = list(dict.fromkeys(ex["chapitre"] for ex in exercices))

    if not os.environ.get("PIPELEX_API_KEY", "").strip():
        raise SystemExit("Veuillez définir la variable d'environnement PIPELEX_API_KEY.")

    fichiers = sorted(BUNDLE_DIR.rglob("*.mthds"))
    if not fichiers:
        raise SystemExit(f"Aucun fichier .mthds trouvé dans {BUNDLE_DIR}.")
    contenus = [fichier.read_text(encoding="utf-8") for fichier in fichiers]

    print(f"Bienvenue, {profil.nom} ! Tapez stop à tout moment pour quitter.")
    async with PipelexAPIClient() as client:
        while True:
            print("\nChapitres disponibles :")
            for numero, chapitre in enumerate(chapitres, start=1):
                print(f"  {numero}. {chapitre} (niveau {profil.niveau(chapitre):.1f})")
            choix = input("Chapitre (numéro de la liste ou nom complet) : ").strip()
            if choix.casefold() == "stop":
                break
            if choix in chapitres:
                chapitre = choix
            else:
                try:
                    numero = int(choix)
                except ValueError:
                    numero = 0
                if not 1 <= numero <= len(chapitres):
                    print("Chapitre inconnu. Choisissez un chapitre de la liste.")
                    continue
                chapitre = chapitres[numero - 1]

            exercice = choisir_exercice(profil, chapitre, exercices)
            if exercice is None:
                print("Aucun exercice non vu disponible pour ce chapitre. "
                      "Choisissez un autre chapitre ou tapez stop.")
                continue

            print(f"\nExercice {exercice['id']} — difficulté {exercice['difficulte']}")
            print(exercice["enonce"])
            reponse = input("Votre réponse : ")
            if reponse.strip().casefold() == "stop":
                break

            print("Évaluation en cours…", flush=True)
            try:
                resultat = await client.start_and_wait(
                    pipe_code=PIPE_CODE,
                    mthds_contents=contenus,
                    inputs={"enonce": exercice["enonce"], "reponse_eleve": reponse},
                )
                evaluation = resultat.main_stuff
                verdict = evaluation["verdict"]
                type_erreur = evaluation["type_erreur"]
                explication = evaluation["explication"]
                if (not isinstance(verdict, str) or verdict not in GAINS
                        or not isinstance(type_erreur, str)
                        or not isinstance(explication, str)):
                    raise ValueError("Format d'évaluation invalide.")
            except Exception as erreur:
                print(f"Échec de l'évaluation : {erreur}")
                print("Cette tentative n'a pas été enregistrée.")
                continue

            print(f"Verdict : {verdict}")
            print(f"Explication : {explication}")
            profil.enregistrer(exercice["id"], chapitre, verdict, type_erreur)
            profil.sauvegarder(CHEMIN_PROFIL)
            print(f"Profil sauvegardé. Niveau : {profil.niveau(chapitre):.1f}")

    print("À bientôt !")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        asyncio.run(main())
    except (EOFError, KeyboardInterrupt):
        print("\nÀ bientôt !")
