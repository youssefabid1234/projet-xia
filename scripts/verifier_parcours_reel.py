"""Deux vérifications ciblées avec le vrai agent et les vraies APIs.

Le second scénario initialise directement l'étape catalogue : il teste la borne
par étape, pas une colle complète. Aucun client ou évaluateur n'est remplacé.
"""
import asyncio
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from app.agent import Agent, CHAPITRE_SERIES
from app.profil import charger_exercices


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cours-seulement", action="store_true")
    args = parser.parse_args()
    root = Path("reports") / ("parcours-borne-reel-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    root.mkdir(parents=True)
    traces = []
    print(str(root), flush=True)

    async def tour(agent, scenario, message):
        texte = await agent.repondre(message)
        traces.append({"scenario": scenario, "eleve": message, "tuteur": texte})
        (root / "conversations.json").write_text(json.dumps(traces, ensure_ascii=False, indent=2), encoding="utf-8")
        lines = ["# Vérification réelle des bornes", "", "Deux scénarios ciblés ; le scénario exercice commence directement au catalogue.", ""]
        for i, t in enumerate(traces, 1):
            lines += [f"## {i} — {t['scenario']}", "", "**Élève**", "", t["eleve"], "", "**Tuteur**", "", t["tuteur"], ""]
        (root / "conversations.md").write_text("\n".join(lines), encoding="utf-8")
        print(json.dumps({"scenario": scenario, "tour": len(traces), "tuteur": texte[:180]}, ensure_ascii=True), flush=True)
        return texte

    cours = Agent(root / "profil-cours.json", charger_exercices())
    cours.selectionner_chapitre(CHAPITRE_SERIES)
    await tour(cours, "cours", "Chapitre sélectionné : Series numeriques")
    ancienne = cours.tache
    await tour(cours, "cours", "Une série converge lorsque ses sommes partielles tendent vers plus l'infini.")
    correction = await tour(cours, "cours", "Une série converge dès que son terme général tend vers zéro : cette condition suffit toujours.")
    assert cours.etape_active()["tentatives"] == 2
    assert cours.etape_active()["statut"] == "reformulation"
    assert "Référence :" in correction and "page PDF" in correction
    await tour(cours, "cours", "Il faut que les sommes partielles admettent une limite finie, pas seulement que les termes tendent vers zéro.")
    assert ancienne["cloturee"] and not ancienne["acquise"]
    assert ancienne["etapes_resolution"][0]["franchissement"] == "donnee_par_agent"
    assert cours.tache["id"] != ancienne["id"]
    if args.cours_seulement:
        (root / "resultat.json").write_text(json.dumps({"cours": "ok", "exercice": "non execute", "echanges": len(traces)}, indent=2), encoding="utf-8")
        print("VERIFICATION_COURS_REEL_OK", flush=True)
        return

    exercice = Agent(root / "profil-exercice.json", charger_exercices())
    exercice.selectionner_chapitre(CHAPITRE_SERIES)
    exercice.etape = "exercices"
    presentation = await tour(exercice, "exercice ciblé", "Chapitre sélectionné : Series numeriques")
    assert "Plan de résolution" in presentation
    ancien_exercice = exercice.tache
    premiere = exercice.etape_active()
    await tour(exercice, "exercice ciblé", "Tous les résultats sont égaux à moins 999, car 0 est égal à 1.")
    await tour(exercice, "exercice ciblé", "Je confirme que 0 est égal à 1, et que tous les résultats valent moins 999.")
    assert premiere["tentatives"] == 2 and premiere["statut"] == "reformulation"
    # Copier la solution révélée ne doit jamais créer un acquis.
    await tour(exercice, "exercice ciblé", premiere["reponse"])
    assert premiere["statut"] == "terminee" and not premiere["acquise"]
    assert premiere["franchissement"] == "donnee_par_agent"
    assert exercice.tache is not ancien_exercice or exercice.tache["etape_resolution"] == 1
    assert exercice.etape_active()["tentatives"] == 0
    (root / "resultat.json").write_text(json.dumps({"cours": "ok", "exercice": "ok", "echanges": len(traces)}, indent=2), encoding="utf-8")
    print("VERIFICATION_REELLE_OK", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
