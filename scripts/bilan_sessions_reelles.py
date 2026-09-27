"""Extraction factuelle des traces de l'audit, sans appel de modèle."""
import argparse
from collections import Counter
import json
from pathlib import Path

from app.profil import charger_exercices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dossier")
    args = parser.parse_args()
    root = Path(args.dossier)
    catalog = {e["id"]: e for e in charger_exercices()}
    results = []
    sections = []
    for kind in ("faible", "moyen", "fort"):
        for number in range(1, 5):
            stem = f"{kind}-session-{number}"
            path = root / f"{stem}.json"
            if not path.exists():
                continue
            turns = json.loads(path.read_text(encoding="utf-8"))
            before = json.loads((root / f"{stem}-avant.json").read_text(encoding="utf-8"))
            previous = before
            tasks = []
            evaluations = []
            for turn in turns:
                state = turn["profil_apres"]
                for tid, task in state.get("taches", {}).items():
                    old = previous.get("taches", {}).get(tid)
                    if old is None:
                        key = (task.get("etape"), task.get("nature"), task.get("source"))
                        matches = [t for t in previous.get("taches", {}).values()
                            if ((task.get("etape") == "exercices" and t.get("exercice_id") == task.get("exercice_id"))
                                or (task.get("etape") != "exercices" and (t.get("etape"), t.get("nature"), t.get("source")) == key))]
                        validated = [t for t in matches if t.get("acquise") and t.get("evaluations") and t["evaluations"][-1].get("verdict") == "correcte"]
                        entry = {"echange": turn["echange"], "id": tid,
                            **{k: task.get(k) for k in ("enonce", "etape", "nature", "source", "exercice_id")},
                            "difficulte": catalog.get(task.get("exercice_id"), {}).get("difficulte"),
                            "repetition_source_nature": bool(matches), "deja_validee": bool(validated)}
                        tasks.append(entry)
                    for ev in task.get("evaluations", [])[len((old or {}).get("evaluations", [])):]:
                        evaluations.append({"echange": turn["echange"], "tache": tid, **ev})
                previous = state
            after = turns[-1]["profil_apres"]
            for task in tasks:
                final = after.get("taches", {}).get(task["id"], {})
                task["acquise_fin"] = final.get("acquise", False)
                task["verdicts"] = [e.get("verdict") for e in final.get("evaluations", [])]
            first_app = next((t["echange"] for t in tasks if t["etape"] == "applications"), None)
            first_ex = next((t["echange"] for t in tasks if t["etape"] == "exercices"), None)
            chapter = next(iter(after.get("niveaux", {})), "17 — Série de réels ou de complexes")
            n_before = before.get("niveaux", {}).get(chapter, 1.5)
            n_after = after.get("niveaux", {}).get(chapter, 1.5)
            gained = [tid for tid, t in after.get("taches", {}).items() if t.get("acquise") and not before.get("taches", {}).get(tid, {}).get("acquise")]
            result = {"profil": kind, "session": number, "echanges": len(turns),
                "http_ok": all(t["http"] == 200 for t in turns), "premiere_application": first_app,
                "premier_exercice_catalogue": first_ex, "niveau_avant": n_before, "niveau_apres": n_after,
                "nouveaux_acquis": len(gained), "evaluations": dict(Counter(e["verdict"] for e in evaluations)),
                "taches": tasks, "details_evaluations": evaluations,
                "secondes_tuteur": round(sum(t["secondes_tuteur"] for t in turns), 1)}
            results.append(result)
            sections += [f"## {kind.capitalize()} — session {number}", "",
                f"[Conversation complète]({stem}.md). {len(turns)} échanges. Niveau {n_before:.1f} → {n_after:.1f}. {len(gained)} nouveaux acquis.", "",
                f"Première application : {first_app or 'aucune'}. Premier exercice du catalogue : {first_ex or 'aucun'}.", "",
                "Évaluations : " + ", ".join(f"{key} : {value}" for key, value in result["evaluations"].items()) + ".", ""]
            for task in tasks:
                difficulty = f" ; difficulté catalogue {task['difficulte']}/5" if task["difficulte"] is not None else " ; difficulté non chiffrée"
                sections += [f"### E{task['echange']} — {task['etape']} / {task['nature'] or 'catalogue'}{difficulty}", "",
                    task["enonce"], "",
                    f"Source : {task['source'] or task['exercice_id']}. Acquise en fin de session : {task['acquise_fin']}. "
                    f"Même source/nature déjà proposée : {task['repetition_source_nature']}. Déjà validée avant cette proposition : {task['deja_validee']}.", ""]
    lines = ["# Audit pédagogique — relevé factuel", "",
        "Sessions réelles via l'interface HTTP et les APIs OpenAI/Pipelex. Seul l'élève est joué par un modèle ; le tuteur et ses outils ne sont pas simulés.", "",
        "Un seul compte, sans remise à zéro, dans l'ordre faible → moyen → fort. La comparaison est influencée par cet ordre et les acquis conservés. Le niveau chiffré évolue lors des évaluations du catalogue, pas lors des acquisitions de cours.", "",
        "Chaque session est plafonnée à 20 échanges (choix du chapitre inclus en E1). « Avant l'échange 10 » signifie E1 à E9. Une session peut s'arrêter au plafond sans que le tuteur ait terminé sa progression.", "",
        "Les repetitions ci-dessous sont détectées par couple source/nature pour le cours et par identifiant pour le catalogue ; elles nécessitent une lecture des conversations pour distinguer rappel, question équivalente et nouvelle acquisition.", "",
        "Attention : ce tableau compte les tâches enregistrées par le serveur. Un exercice affiché librement sans outil (notamment une répétition) peut apparaître plus tôt dans la conversation ; le bilan relu corrige cette différence.", "",
        "| Profil | Session | Échanges | Application enregistrée | Catalogue enregistré | Niveau | Nouveaux acquis |",
        "|---|---:|---:|---:|---:|---|---:|"]
    for r in results:
        lines.append(f"| {r['profil']} | {r['session']} | {r['echanges']} | {r['premiere_application'] or '—'} | {r['premier_exercice_catalogue'] or '—'} | {r['niveau_avant']:.1f} → {r['niveau_apres']:.1f} | {r['nouveaux_acquis']} |")
    (root / "releve-factuel.md").write_text("\n".join(lines + [""] + sections), encoding="utf-8")
    (root / "mesures.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{k: v for k, v in r.items() if k not in ("taches", "details_evaluations")} for r in results], ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
