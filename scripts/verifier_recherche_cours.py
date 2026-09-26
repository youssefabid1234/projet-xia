"""Test réel explicite des trois questions : recherche puis dialogue de l'agent.

Consomme du crédit OpenAI. Exécuter depuis la racine avec
python -m scripts.verifier_recherche_cours
"""
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

from openai import AsyncOpenAI

from app.agent import Agent
from app.cours import INDEX

CASES = [
    ("qu'est-ce qu'une serie geometrique", {"16.1.9", "16.2.14"}),
    ("comment montrer qu'une serie diverge", {"16.1.12", "16.1.13", "16.2.2", "16.2.17", "16.2.20", "16.2.22"}),
    ("definition du reste d'une serie", {"16.1.5"}),
]


async def main():
    report = {"date_utc": datetime.now(timezone.utc).isoformat(),
              "index_sha256": hashlib.sha256(INDEX.read_bytes()).hexdigest(),
              "modele_agent": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"), "tests": []}
    with tempfile.TemporaryDirectory() as directory:
        async with AsyncOpenAI(timeout=60, max_retries=1) as client:
            for question, expected in CASES:
                agent = Agent(Path(directory) / "profil.json", [])
                direct = await agent.chercher_dans_cours(question, client)
                response = await agent.repondre(question, client)
                calls = [x for x in agent.historique if x.get("type") == "function_call" and x.get("name") == "chercher_dans_cours"]
                call_ids = {x["call_id"] for x in calls}
                results = [json.loads(x["output"]) for x in agent.historique
                           if x.get("type") == "function_call_output" and x["call_id"] in call_ids]
                found = {p["identifiant"] for p in direct["passages"]}
                passed = bool(found & expected) and bool(calls) and all("passages" in x for x in results)
                report["tests"].append({"question": question, "recherche_directe": direct,
                                        "appels_agent": calls, "resultats_agent": results,
                                        "reponse_agent": response, "reussi": passed})
                print(question, "—", "OK" if passed else "ECHEC", flush=True)
                print([(p["identifiant"], p["score"]) for p in direct["passages"]], flush=True)
                print(response, flush=True)
    target = INDEX.parent / "cours_recherche_tests.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(test["reussi"] for test in report["tests"]):
        raise SystemExit("Au moins une question ne satisfait pas le contrôle de recherche.")


if __name__ == "__main__":
    asyncio.run(main())
