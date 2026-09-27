"""Références relevées dans les corrigés de séries ; ne modifie pas les sources."""
import json
from app.catalogue_pedagogique import DATA, empreinte, notions_cours

# Une annotation atteste une notion mobilisée, pas la validité du corrigé extrait.
REFERENCES = {
    1: ["16.1.15", "16.2.17"], 2: ["16.2.9", "16.1.9"],
    3: ["16.2.2", "16.1.15"], 4: ["16.2.9", "16.2.17"],
    5: ["16.2.1"], 6: ["16.2.13", "16.2.9"],
    7: ["16.2.2", "16.2.17"], 8: ["16.2.2", "16.1.15"],
    9: ["16.2.9"], 10: ["16.2.8", "16.2.17"],
    11: ["16.1.13", "16.2.17"], 12: ["16.2.2", "16.1.12", "16.2.9"],
    13: ["16.1.9", "16.2.3", "16.1.13"], 14: ["16.2.9", "16.1.9", "16.2.17"],
    15: ["16.1.5"], 16: ["16.2.1", "16.2.17"],
    17: ["16.2.17"], 18: ["16.2.20", "16.2.9", "16.1.9"],
    19: ["16.2.1"], 20: ["16.2.20", "16.2.3"],
    21: ["16.2.8", "16.2.17"], 22: ["16.1.5"],
    23: ["16.2.1", "16.1.5"], 24: ["16.1.13", "16.2.20", "16.2.3"],
    25: ["16.3.2", "16.2.7"], 26: ["16.3.2", "16.1.15"],
    27: ["16.3.2"], 28: ["16.3.2", "16.2.9", "16.2.2"],
    29: ["16.2.7", "16.1.5"], 30: ["16.3.2", "16.2.9", "16.2.17"],
    31: ["16.1.5", "16.1.13", "16.2.1"],
}


def main():
    disponibles = {p["identifiant"] for p in notions_cours().values()}
    exercices = json.loads((DATA / "exercices.json").read_text(encoding="utf-8"))
    annotations = {}
    for ex in exercices:
        identifiant = ex["identifiant"]
        if identifiant.startswith("17."):
            references = REFERENCES[int(identifiant.split(".")[1])]
            assert set(references) <= disponibles
            annotations[identifiant] = {"empreinte": empreinte(ex), "references": references}
    (DATA / "notions_exercices.json").write_text(json.dumps(annotations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(annotations)} exercices annotés.")


if __name__ == "__main__":
    main()
