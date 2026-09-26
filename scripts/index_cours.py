"""Extrait les unités numérotées du cours, puis indexe un aperçu validé.

Par défaut : extraction locale uniquement. --embed lit les passages sauvegardés
(y compris les corrections de relecture), sans refaire le découpage.
Documentation : https://developers.openai.com/api/docs/guides/embeddings
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(
    r"^(Définition|Théorème|Proposition|Corollaire|Lemme|Exemples?|"
    r"Remarques?|Avertissement|Méthode) (16\.\d+\.\d+)(?:\s|$)"
)
TYPES = {"Exemples": "exemple", "Remarques": "remarque"}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def extract(pdf, start=139, end=157):
    import pymupdf

    passages, introductions, section, pending = [], [], [], []
    current = None
    with pymupdf.open(pdf) as doc:
        if not 1 <= start <= end <= len(doc):
            raise ValueError("Plage PDF invalide")
        for number in range(start, end + 1):
            page = doc[number - 1]
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    # Les en-têtes courants et numéros imprimés occupent y < 60.
                    if line["bbox"][1] < 60:
                        continue
                    text = unicodedata.normalize("NFKC", "".join(s["text"] for s in line["spans"])).strip()
                    if not text:
                        continue
                    fonts = {s["font"] for s in line["spans"]}
                    if fonts & {"SFBX1440", "SFBX1200"}:
                        # Une nouvelle section termine le passage précédent.
                        current = None
                        if re.fullmatch(r"[IVX]+(?:\.\d+)?", text):
                            section = [text]
                        else:
                            section.append(text)
                        continue
                    match = HEADING.match(text)
                    if match:
                        context = "\n".join(item["texte"] for item in pending)
                        if pending:
                            introductions.append({"section": " — ".join(section), "lignes": pending})
                            pending = []
                        current = {
                            "identifiant": match[2], "titre": text,
                            "type": TYPES.get(match[1], match[1].lower()),
                            "section": " — ".join(section),
                            "contexte": context,
                            "page_source": {"fichier": pdf.relative_to(ROOT).as_posix() if pdf.is_relative_to(ROOT) else str(pdf),
                                            "pdf": [], "imprimee": []},
                            "regions_source": [], "_lines": [],
                        }
                        passages.append(current)
                    if current is None:
                        pending.append({"page_pdf": number, "texte": text})
                        continue
                    current["_lines"].append(text)
                    current["regions_source"].append({"page_pdf": number, "bbox": list(line["bbox"])})
                    if number not in current["page_source"]["pdf"]:
                        current["page_source"]["pdf"].append(number)
                        current["page_source"]["imprimee"].append(number - 2)
        if pending:
            introductions.append({"section": " — ".join(section), "lignes": pending})
    ids = [p["identifiant"] for p in passages]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Aucun passage ou identifiants répétés")
    for p in passages:
        source_lines = p.pop("_lines")
        # Certains titres contiennent une formule répartie sur plusieurs lignes.
        title_lines = 1
        while "(" in p["titre"] and p["titre"].count("(") > p["titre"].count(")") and title_lines < len(source_lines):
            p["titre"] += " " + source_lines[title_lines]
            title_lines += 1
        p["texte_brut"] = "\n".join(source_lines[title_lines:])
        p["texte"] = p["texte_brut"]
        p["transcription_relue"] = False
        p["contient_preuve"] = "Éléments de preuve" in p["texte"]
    return {"version": 1, "statut": "a_verifier", "chapitre": "16 — Séries numériques",
            "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "pages_pdf": [start, end], "introductions": introductions,
            "avertissement": "Texte PDF brut : indices, exposants et fractions à relire, sauf passages marqués transcription_relue.",
            "passages": passages}


def apply_review(payload, path):
    if not path.exists():
        return
    review = json.loads(path.read_text(encoding="utf-8"))
    if review["pdf_sha256"] != payload["pdf_sha256"]:
        raise ValueError("Transcriptions incompatibles avec le PDF")
    for passage in payload["passages"]:
        corrected = review["passages"].get(passage["identifiant"])
        if corrected is not None:
            passage["texte"] = corrected
            passage["transcription_relue"] = True


def embed(payload, client, model, batch_size=16):
    # Import différé : l'aperçu n'exige ni SDK OpenAI ni clé ni réseau.
    import tiktoken

    encoding = tiktoken.encoding_for_model(model)
    texts = [f"{payload['chapitre']}\n{p['section']}\n{p.get('contexte', '')}\n{p['titre']}\n{p['texte']}" for p in payload["passages"]]
    for p, text in zip(payload["passages"], texts):
        if not p["texte"].strip() or len(encoding.encode(text)) > 8191:
            raise ValueError(f"Passage vide ou trop long : {p['identifiant']}. Revoir le découpage.")
    output, dimensions = [], None
    for offset in range(0, len(texts), batch_size):
        batch = texts[offset:offset + batch_size]
        response = client.embeddings.create(model=model, input=batch, encoding_format="float")
        rows = sorted(response.data, key=lambda item: item.index)
        if [row.index for row in rows] != list(range(len(batch))):
            raise ValueError("Réponse d'embeddings incomplète")
        for row in rows:
            vector = row.embedding
            if not vector or not all(math.isfinite(x) for x in vector):
                raise ValueError("Vecteur d'embedding invalide")
            dimensions = dimensions or len(vector)
            if len(vector) != dimensions:
                raise ValueError("Dimensions d'embeddings incohérentes")
            output.append({**payload["passages"][offset + row.index], "embedding": vector})
    return {**payload, "statut": "indexe", "modele_embedding": model,
            "dimensions": dimensions, "passages": output}


def preview_markdown(payload, count=10):
    parts = ["# Aperçu des passages — Séries numériques", "Pages PDF (numérotation à partir de 1) et pages imprimées indiquées séparément."]
    for p in payload["passages"][:count]:
        parts.extend([f"## {p['titre']}",
                      f"Type : {p['type']} — PDF : {p['page_source']['pdf']} — imprimées : {p['page_source']['imprimee']}",
                      p["texte"]])
    return "\n\n".join(parts) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=ROOT / "data/cours/analyse.pdf")
    parser.add_argument("--pages", nargs=2, type=int, default=[139, 157])
    parser.add_argument("--passages", type=Path, default=ROOT / "data/cours_passages.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/cours_index.json")
    parser.add_argument("--apercu", type=Path, default=ROOT / "data/cours_apercu.md")
    parser.add_argument("--transcriptions", type=Path, default=ROOT / "scripts/transcriptions/cours_series.json")
    parser.add_argument("--embed", action="store_true", help="Après vérification : indexer les passages sauvegardés")
    parser.add_argument("--model", default="text-embedding-3-small")
    args = parser.parse_args(argv)
    paths = [args.pdf, args.passages, args.output, args.apercu, args.transcriptions]
    if len({p.resolve() for p in paths}) != len(paths):
        parser.error("Les chemins source et destination doivent être distincts")
    if args.embed:
        if not os.environ.get("OPENAI_API_KEY"):
            parser.error("Définir OPENAI_API_KEY dans l'environnement ; .env n'est pas chargé automatiquement")
        payload = json.loads(args.passages.read_text(encoding="utf-8"))
        if payload["pdf_sha256"] != hashlib.sha256(args.pdf.read_bytes()).hexdigest():
            parser.error("Le PDF a changé depuis l'aperçu")
        from openai import OpenAI
        with OpenAI(timeout=60, max_retries=3) as client:
            result = embed(payload, client, args.model)
        write_json(args.output, result)
        print(f"{len(result['passages'])} passages indexés dans {args.output}")
    else:
        payload = extract(args.pdf.resolve(), *args.pages)
        apply_review(payload, args.transcriptions)
        write_json(args.passages, payload)
        markdown = preview_markdown(payload)
        args.apercu.parent.mkdir(parents=True, exist_ok=True)
        args.apercu.write_text(markdown, encoding="utf-8")
        print(f"{len(payload['passages'])} passages extraits ; aucun appel API.\n")
        print(markdown)


if __name__ == "__main__":
    main()
