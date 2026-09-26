"""Repérer les sauts de ligne suspects dans les énoncés, sans modifier le catalogue.

Détection heuristique : formules délimitées sur plusieurs lignes, opérateurs en
bout de ligne et fragments mathématiques isolés (dont X/Y/Z issus du PDF).
--tous-multilignes inclut aussi les autres énoncés multilignes pour une revue
exhaustive : du texte brut seul ne permet pas de reconnaître toute formule.
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMULE = re.compile(r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$[^$]*?(?<!\\)\$|\\\[.*?\\\]|\\\(.*?\\\)", re.S)
MOTS = re.compile(r"[^\W\d_]+", re.UNICODE)
FONCTIONS = {"sin", "cos", "tan", "exp", "ln", "log", "ch", "sh", "lim", "sup", "inf", "dx", "dt"}
MARQUEURS = re.compile(r"[=+*/^_<>≤≥∈∑∏∫√∞→−×]|\\[A-Za-z]+")
OPERATEUR_FINAL = re.compile(r"[=+*/^_<>≤≥→−×]$")


def fragment_formule(ligne):
    """Un fragment court sans mots de prose ; volontairement inclusif."""
    ligne = ligne.strip()
    if not ligne or len(ligne) > 90 or re.fullmatch(r"\d+[.)]", ligne):
        return False
    mots = MOTS.findall(ligne)
    return (bool(mots or re.search(r"\d|[∑∏∫√∞]", ligne))
            and all(len(mot) <= 2 or mot in FONCTIONS for mot in mots))


def ruptures_suspectes(enonce):
    """Retourne les numéros (base 1) des lignes précédant une rupture suspecte."""
    texte = enonce.replace("\r\n", "\n").replace("\r", "\n")
    suspects = {}
    for formule in FORMULE.finditer(texte):
        for saut in re.finditer("\n", formule.group()):
            numero = texte.count("\n", 0, formule.start() + saut.start()) + 1
            suspects[numero] = "saut de ligne dans une formule délimitée"
    # Les formules déjà délimitées sont traitées ci-dessus. Les masquer évite
    # de confondre deux formules complètes sur deux lignes avec une rupture.
    texte_brut = FORMULE.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), texte)
    lignes = texte_brut.split("\n")
    for numero, (avant, apres) in enumerate(zip(lignes, lignes[1:]), 1):
        avant, apres = avant.strip(), apres.strip()
        if not avant or not apres:
            continue  # Un simple paragraphe n'est pas une formule coupée.
        if OPERATEUR_FINAL.search(avant):
            suspects.setdefault(numero, "opérateur en fin de ligne")
        elif (fragment_formule(avant) or fragment_formule(apres)):
            suspects.setdefault(numero, "fragment mathématique isolé")
        elif MARQUEURS.search(avant[-20:]) and MARQUEURS.search(apres[:20]):
            suspects.setdefault(numero, "symboles mathématiques de part et d'autre")
    return [{"ligne": numero, "raison": raison} for numero, raison in sorted(suspects.items())]


def analyser(exercices, tous_multilignes=False):
    resultat = []
    for exercice in exercices:
        enonce = exercice["enonce"]
        ruptures = ruptures_suspectes(enonce)
        if ruptures or (tous_multilignes and len(enonce.splitlines()) > 1):
            resultat.append({
                "identifiant": exercice.get("identifiant", exercice.get("id", "?")),
                "chapitre": exercice.get("chapitre", ""),
                "page_source": exercice.get("page_source", {}),
                "ruptures": ruptures,
                "enonce": enonce,
            })
    return resultat


def rapport_markdown(resultats, total):
    blocs = ["# Énoncés à vérifier", "",
             f"{len(resultats)} énoncé(s) signalé(s) sur {total}.", "",
             "Détection heuristique : vérifier les formules dans le PDF avant correction.",
             "Les numéros désignent les lignes du champ enonce, pas celles du fichier JSON.",
             "Le catalogue n'a pas été modifié.", ""]
    for resultat in resultats:
        blocs += [f"## {resultat['identifiant']} — {resultat['chapitre']}", "",
                  "Source : " + json.dumps(resultat["page_source"], ensure_ascii=False), ""]
        blocs += [f"- Lignes {r['ligne']}–{r['ligne'] + 1} : {r['raison']}."
                  for r in resultat["ruptures"]] or ["Autre énoncé multiligne, inclus pour revue exhaustive."]
        blocs += ["", "```text"]
        blocs += [f"{n:>3} | {ligne}" for n, ligne in enumerate(resultat["enonce"].splitlines(), 1)]
        blocs += ["```", ""]
    return "\n".join(blocs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogue", nargs="?", type=Path, default=ROOT / "data/exercices.json")
    parser.add_argument("--sortie", type=Path, help="Rapport UTF-8 ; sinon affichage sur la sortie standard.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--tous-multilignes", action="store_true")
    args = parser.parse_args()
    if args.sortie and args.sortie.resolve() == args.catalogue.resolve():
        parser.error("Le rapport ne doit pas écraser le catalogue.")
    exercices = json.loads(args.catalogue.read_text(encoding="utf-8"))
    resultats = analyser(exercices, args.tous_multilignes)
    rapport = (json.dumps(resultats, ensure_ascii=False, indent=2) if args.format == "json"
               else rapport_markdown(resultats, len(exercices)))
    if args.sortie:
        args.sortie.write_text(rapport + "\n", encoding="utf-8")
        print(f"{len(resultats)} / {len(exercices)} : {args.sortie}")
    else:
        print(rapport)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()
