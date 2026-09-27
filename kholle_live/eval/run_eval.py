"""Évaluation de la lecture + vérification du tableau sur eval/samples/*.png. [lane B]

Échantillons enregistrés depuis la tablette (bouton « éval ») : <label>_<horodatage>.png.
C* = tableau juste (ne doit rien signaler), E* = tableau avec une erreur (doit être détecté).
Un échantillon est « détecté » si au moins une ligne est "faux".

Lancer depuis kholle_live : uv run python eval/run_eval.py [--exercise dl_ln_sin]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ICI.parent / ".env")

from kholle import exercises  # noqa: E402
from kholle.board_reader import read_board, stats  # noqa: E402

SYMBOLES = {"ok": "✓", "faux": "✗", "?": "?"}


def evaluer(exercise: dict) -> list[dict]:
    resultats = []
    for chemin in sorted((ICI / "samples").glob("*.png")):
        label = chemin.stem.split("_")[0]
        attendu = {"C": False, "E": True}.get(label[:1].upper())
        debut = time.time()
        try:
            lignes = read_board(chemin.read_bytes(), exercise)
            erreur = None
        except Exception as e:
            lignes, erreur = [], f"{e.__class__.__name__}: {e}"
        duree = time.time() - debut
        verdicts = [l.verdict for l in lignes]
        r = {
            "fichier": chemin.name,
            "label": label,
            "attendu": attendu,
            "detecte": "faux" in verdicts,
            "illisible": erreur is not None or not any(v in ("ok", "faux") for v in verdicts),
            "duree": duree if erreur is None else None,
            "erreur": erreur,
            "lignes": lignes,
        }
        resultats.append(r)
        print(f"{chemin.name:40} {'détecté' if r['detecte'] else '-':8} "
              f"{''.join(SYMBOLES[v] for v in verdicts):12} {duree:5.1f} s {erreur or ''}", flush=True)
    return resultats


def resume(resultats: list[dict], exercise_id: str) -> str:
    erreurs = [r for r in resultats if r["attendu"] is True]
    justes = [r for r in resultats if r["attendu"] is False]
    durees = [r["duree"] for r in resultats if r["duree"] is not None]
    moyenne = f"{sum(durees) / len(durees):.1f} s" if durees else "n/a"

    lignes = [
        "# Évaluation du tableau",
        "",
        f"Exercice : `{exercise_id}` — {time.strftime('%Y-%m-%d %H:%M')}",
        "",
        f"- Erreurs détectées : **{sum(r['detecte'] for r in erreurs)}/{len(erreurs)}** (échantillons E*)",
        f"- Fausses alertes : **{sum(r['detecte'] for r in justes)}/{len(justes)}** (échantillons C*)",
        f"- Illisibles : **{sum(r['illisible'] for r in resultats)}** (lecture en échec ou aucune ligne vérifiable)",
        f"- Latence moyenne de lecture : **{moyenne}** (seconde lecture comprise)",
        f"- Relectures des lignes fausses : **{stats()['desaccords']} désaccord(s) sur {stats()['relectures']}**",
        "",
        "| Échantillon | Attendu | Résultat | Lignes | Latence |",
        "|---|---|---|---|---|",
    ]
    for r in resultats:
        attendu = {True: "erreur", False: "juste", None: "?"}[r["attendu"]]
        if r["erreur"]:
            resultat = f"échec : {r['erreur']}"
        else:
            bon = r["attendu"] is None or r["detecte"] == r["attendu"]
            resultat = ("détecté" if r["detecte"] else "rien") + ("" if bon else " ⚠")
        detail = "<br>".join(
            f"L{l.n} {SYMBOLES[l.verdict]} `{l.texte}`" + (f" ({l.detail})" if l.verdict == "faux" else "")
            for l in r["lignes"]
        )
        latence = f"{r['duree']:.1f} s" if r["duree"] is not None else "-"
        lignes.append(f"| {r['fichier']} | {attendu} | {resultat} | {detail} | {latence} |")
    return "\n".join(lignes) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exercise", default=exercises.demo()["id"])
    args = parser.parse_args()

    resultats = evaluer(exercises.get(args.exercise))
    if not resultats:
        print("Aucun échantillon dans eval/samples/ : enregistrez-en depuis la tablette (bouton « éval »).")
        return
    texte = resume(resultats, args.exercise)
    (ICI / "results.md").write_text(texte, encoding="utf-8")
    print()
    print("\n".join(texte.splitlines()[4:9]))
    print(f"\n-> {ICI / 'results.md'}")


if __name__ == "__main__":
    main()
