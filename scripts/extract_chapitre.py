"""Extraction d'un chapitre du polycopié, fusion par identifiant et audit.

python scripts/extract_chapitre.py --chapitre 2 --enonces 10 12 --corriges 99 106

Les pages sont numérotées à partir de 1 dans le PDF. Les transcriptions relues
sont séparées du moteur : sans transcription, le texte PDF brut est conservé
et signalé comme non relu dans l'audit. Aucun corrigé manquant n'est inventé.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
# Police embarquée vérifiée visuellement et via /Encoding [/star /star_empty].
# Les deux glyphes ont le même Unicode U+22C6 : get_text() ne les distingue pas.
STAR_FONT_SHA256 = "bc40e37bf565e88bf27f2627fed71dd7704f2e27305489bdba6d1739c6316c18"
TITLE = re.compile(r"^(?:Solution de l[’']exercice|Exercice) (\d+\.\d+)$")
SUBHEADINGS = {
    "Sans changement de variable ou intégration par parties",
    "Avec changement de variable ou intégration par parties",
}


def lines(page):
    return [
        ("".join(s["text"] for s in line["spans"]), line["bbox"])
        for block in page.get_text("dict")["blocks"] if "lines" in block
        for line in block["lines"]
    ]


def extract_difficulties(page):
    """Associe les cinq glyphes sur la ligne de chaque titre à son identifiant."""
    titles = [(TITLE.fullmatch(text.strip())[1], box) for text, box in lines(page)
              if text.startswith("Exercice ") and TITLE.fullmatch(text.strip())]
    if not titles:
        return {}
    fonts = [font for font in page.get_fonts() if "FontAwesome" in font[3]]
    if len(fonts) != 1 or hashlib.sha256(page.parent.extract_font(fonts[0][0])[3]).hexdigest() != STAR_FONT_SHA256:
        raise ValueError(f"Police d’étoiles non reconnue, page {page.number + 1}")
    stars = [char for span in page.get_texttrace() if span["font"] == "FontAwesome"
             for char in span["chars"]]
    result = {}
    for identifier, box in titles:
        row = [char for char in stars if box[0] < char[2][0] < box[2] + 100
               and abs((char[3][1] + char[3][3] - box[1] - box[3]) / 2) < 3]
        if len(row) != 5 or any(char[1] not in (1, 2) for char in row):
            raise ValueError(f"Notation non reconnue pour {identifier}, page {page.number + 1}")
        result[identifier] = sum(char[1] == 1 for char in row)
    return result


def update_difficulties(doc, records):
    """Met à jour seulement la notation, depuis la première page de l'énoncé."""
    cache = {}
    for record in records:
        pages = record["page_source"]["enonce"]["pdf"]
        number = pages[0] if isinstance(pages, list) else pages
        if number not in cache:
            cache[number] = extract_difficulties(doc[number - 1])
        identifier = record["identifiant"]
        if identifier not in cache[number]:
            raise ValueError(f"Énoncé {identifier} absent de la page {number}")
        record["difficulte"] = cache[number][identifier]


def split_sections(doc, bounds, chapter, solution=False):
    """Conserve l'exercice courant entre pages et retire les éléments éditoriaux."""
    result = {}
    current = None
    for number in range(bounds[0], bounds[1] + 1):
        page = doc[number - 1]
        all_lines = lines(page)
        footer = next((box[1] for text, box in all_lines if text == "Quentin De Muynck"), page.rect.height - 30)
        footer_text = page.get_text(clip=pymupdf.Rect(0, footer, page.rect.width, page.rect.height))
        printed_match = re.search(r"(?m)^\s*(\d+)\s*$", footer_text)
        printed = int(printed_match[1]) if printed_match else None
        for text, box in all_lines:
            text = text.strip()
            if box[1] >= footer or not text:
                continue
            match = TITLE.fullmatch(text)
            if match:
                if text.startswith("Solution") != solution:
                    raise ValueError(f"Mauvais type de page : {number}")
                current = match[1]
                if not current.startswith(f"{chapter}."):
                    raise ValueError(f"Autre chapitre rencontré : {current}")
                if current in result:
                    raise ValueError(f"Titre répété : {current}")
                result[current] = {"lines": [], "pages": {}, "regions": {}}
                result[current]["pages"][number] = printed
                continue
            if current is None:
                continue
            if (text.startswith("CHAPITRE ") or text.startswith("Solution p.")
                    or text == "Énoncé" or text in SUBHEADINGS
                    or re.fullmatch(r"[⋆★☆]+", text)):
                continue
            entry = result[current]
            entry["lines"].append(text)
            entry["pages"][number] = printed
            entry["regions"].setdefault(number, []).append(box)
    for entry in result.values():
        entry["text"] = unicodedata.normalize("NFC", "\n".join(entry.pop("lines")))
    return result


def source_pages(section):
    pages = list(section["pages"])
    printed = list(section["pages"].values())
    return {"pdf": pages[0] if len(pages) == 1 else pages,
            "imprimee": printed[0] if len(printed) == 1 else printed}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=ROOT / "data/poly.pdf")
    parser.add_argument("--output", type=Path, default=ROOT / "data/exercices.json")
    parser.add_argument("--chapitre", type=int)
    parser.add_argument("--enonces", type=int, nargs=2, metavar=("DEBUT", "FIN"))
    parser.add_argument("--corriges", type=int, nargs=2, metavar=("DEBUT", "FIN"))
    parser.add_argument("--difficultes-seulement", action="store_true",
                        help="Complète la difficulté de toutes les entrées existantes")
    parser.add_argument("--titre", help="Détecté sur la première page si absent")
    parser.add_argument("--transcriptions", type=Path, help="JSON de transcriptions relues")
    args = parser.parse_args(argv)
    if args.output.resolve() == args.pdf.resolve():
        parser.error("La sortie ne peut pas remplacer le PDF")
    if args.difficultes_seulement:
        if not args.output.exists():
            parser.error("Fichier d’exercices inexistant")
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        with pymupdf.open(args.pdf) as doc:
            update_difficulties(doc, existing)
        write_json(args.output, existing)
        for record in sorted(existing, key=lambda r: tuple(map(int, r["identifiant"].split('.')))):
            print(f"{record['identifiant']} : {record['difficulte']}")
        return
    if args.chapitre is None or args.enonces is None or args.corriges is None:
        parser.error("Préciser --chapitre, --enonces et --corriges")
    reviewed_path = args.transcriptions or ROOT / f"scripts/transcriptions/chapitre_{args.chapitre}.json"
    reviewed = json.loads(reviewed_path.read_text(encoding="utf-8")) if reviewed_path.exists() else {}
    digest = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    if reviewed and reviewed["pdf_sha256"] != digest:
        parser.error("Les transcriptions relues ne correspondent pas à ce PDF")
    existing = json.loads(args.output.read_text(encoding="utf-8")) if args.output.exists() else []
    if len({x["identifiant"] for x in existing}) != len(existing):
        parser.error("Identifiants dupliqués dans la sortie existante")
    with pymupdf.open(args.pdf) as doc:
        for start, end in (args.enonces, args.corriges):
            if not 1 <= start <= end <= len(doc):
                parser.error("Plage de pages invalide")
        start_text = doc[args.enonces[0] - 1].get_text()
        heading = re.search(r"Chapitre [IVXLCDM]+\s*\n([^\n]+)", start_text)
        name = args.titre or (heading[1].strip() if heading else None)
        if not name:
            parser.error("Titre non détecté : préciser --titre")
        statements = split_sections(doc, args.enonces, args.chapitre)
        solutions = split_sections(doc, args.corriges, args.chapitre, True)
        if not statements or statements.keys() != solutions.keys():
            parser.error("Les identifiants des énoncés et corrigés ne correspondent pas")
        ids = sorted(statements, key=lambda s: tuple(map(int, s.split('.'))))
        if ids != [f"{args.chapitre}.{i}" for i in range(1, len(ids) + 1)]:
            parser.error("Numérotation incomplète du chapitre")
        audit, records = [], []
        for identifier in ids:
            values = {}
            for field, section in (("enonce", statements[identifier]), ("corrige", solutions[identifier])):
                values[field] = reviewed.get("exercices", {}).get(identifier, {}).get(field, section["text"])
                # Quelques passages du PDF ont une mise en page défectueuse :
                # leur fac-similé préserve exactement les formules et figures.
                if field in reviewed.get("exercices", {}).get(identifier, {}).get("facsimile_fields", []):
                    links = []
                    for page_number, boxes in section["regions"].items():
                        page = doc[page_number - 1]
                        clip = pymupdf.Rect(0, max(0, min(b[1] for b in boxes) - 2),
                                            page.rect.width, max(b[3] for b in boxes) + 2)
                        dest = args.output.parent / "extraits" / f"{identifier}_{field}_{page_number}.png"
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        page.get_pixmap(matrix=pymupdf.Matrix(2, 2), clip=clip).save(dest)
                        links.append(f"![{field.capitalize()} {identifier}, page PDF {page_number}](extraits/{dest.name})")
                    values[field] += "\n\n" + "\n\n".join(links)
            records.append({"identifiant": identifier, "chapitre": f"{args.chapitre} — {name}",
                            **values, "page_source": {"fichier": args.pdf.relative_to(ROOT).as_posix() if args.pdf.is_relative_to(ROOT) else str(args.pdf),
                            "enonce": source_pages(statements[identifier]),
                            "corrige": source_pages(solutions[identifier])}})
            audit.append({"identifiant": identifier,
                          "enonce_brut": statements[identifier]["text"],
                          "corrige_brut": solutions[identifier]["text"],
                          "transcription_relue": identifier in reviewed.get("exercices", {}),
                          "corrige_vide_dans_source": not solutions[identifier]["text"]})
        update_difficulties(doc, records)
    merged = {record["identifiant"]: record for record in existing}
    merged.update({record["identifiant"]: record for record in records})
    write_json(args.output.parent / f"extraction_chapitre_{args.chapitre}.audit.json",
               {"pdf_sha256": digest, "exercices": audit})
    write_json(args.output, list(merged.values()))
    print(f"{len(records)} exercices extraits : {', '.join(ids)}")


if __name__ == "__main__":
    main()
