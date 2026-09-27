"""Cas attendus écrits avant exécution, avec la véritable méthode Pipelex."""
import asyncio
import json
from pathlib import Path
from pipelex_sdk.client import PipelexAPIClient
from app.evaluation import evaluer_reponse

CAS = [
    ("Définir une série convergente.", "Les sommes partielles tendent vers une limite finie.",
     "Quand on additionne de plus en plus de termes, ça se rapproche d'un nombre fini.", "correcte", "solide"),
    ("Définir une série convergente.", "Les sommes partielles tendent vers une limite finie.",
     "C'est quand les termes vont vers zéro, ça suffit.", "incorrecte", None),
    ("Justifier la convergence de la série de terme 1/n².", "Série de Riemann d'exposant 2 strictement supérieur à 1, donc convergente.",
     "C'est une Riemann, le deux est au-dessus de un donc ça converge.", "correcte", "solide"),
    ("Démontrer que la convergence absolue entraîne la convergence.",
     "Pour m>n, la valeur absolue de la somme de k=n+1 à m de u_k est majorée par la somme correspondante de |u_k|. Celle-ci tend uniformément vers zéro puisque la série des |u_k| converge. Les sommes partielles sont de Cauchy, donc convergent dans R ou C.",
     "Je prendrais la valeur absolue et l'inégalité triangulaire, mais je ne sais pas conclure.", "incomplete", None),
    ("Étudier la série dont le terme est [fraction illisible].", "Le numérateur et le dénominateur sont illisibles.",
     "Elle converge.", "indeterminable", None),
    ("u_0 est réel quelconque et u_(n+1)=exp(-u_n)/(n+1). Montrer que u_n >= 0 pour tout n >= 0.",
     "Par récurrence, u_n >= 0 pour tout n >= 0.", "Tous les résultats valent -999 car 0=1.", "indeterminable", None),
]


async def main():
    records = []
    path = Path("reports/evaluation-orale-architecture.json")
    async with PipelexAPIClient() as client:
        for enonce, corrige, reponse, verdict, intuition in CAS:
            result = await evaluer_reponse(client, enonce, reponse, corrige)
            value = result.main_stuff
            ok = value["verdict"] == verdict and (intuition is None or value["intuition"] == intuition)
            records.append(dict(enonce=enonce, corrige=corrige, reponse=reponse,
                attendu={"verdict": verdict, "intuition": intuition}, obtenu=value, reussi=ok))
            path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            print(len(records), ok, value["verdict"], flush=True)
    if not all(r["reussi"] for r in records):
        raise AssertionError("Consulter " + str(path))


if __name__ == "__main__":
    asyncio.run(main())
