"""Point d’entrée historique : extraction paramétrable de chapitres complets.

Exemple : python scripts/extract_topologie.py --chapitre 2 --enonces 10 12 --corriges 99 106
Le moteur fusionne les entrées par identifiant sans effacer les autres chapitres.
"""

from extract_chapitre import main


if __name__ == "__main__":
    main()
