"""Test réel explicite de la recherche dans le cours sur trois questions.

Consomme du crédit OpenAI (embeddings). Exécuter depuis la racine avec
python -m scripts.verifier_recherche_cours
"""
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import sys

from openai import AsyncOpenAI

from app.config import charger_env
from app.cours import INDEX, chercher_dans_cours

CASES = [
    ("qu'est-ce qu'une serie geometrique", {"16.1.9", "16.2.14"}),
    ("comment montrer qu'une serie diverge", {"16.1.12", "16.1.13", "16.2.2", "16.2.17", "16.2.20", "16.2.22"}),
    ("definition du reste d'une serie", {"16.1.5"}),
]


async def main():
    charger_env()
    report = {"date_utc": datetime.now(timezone.utc).isoformat(),
              "index_sha256": hashlib.sha256(INDEX.read_bytes()).hexdigest(), "tests": []}
    async with AsyncOpenAI(timeout=60, max_retries=1) as client:
        for question, expected in CASES:
            direct = await chercher_dans_cours(question, client)
            found = {p["identifiant"] for p in direct["passages"]}
            passed = bool(found & expected)
            report["tests"].append({"question": question, "recherche_directe": direct, "reussi": passed})
            print(question, "—", "OK" if passed else "ECHEC", flush=True)
            print([(p["identifiant"], p["score"]) for p in direct["passages"]], flush=True)
    target = INDEX.parent / "cours_recherche_tests.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(test["reussi"] for test in report["tests"]):
        raise SystemExit("Au moins une question ne satisfait pas le contrôle de recherche.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
