"""Un appel vision réel sur une écriture synthétique, sans colle ni profil.

Coût : une reconnaissance d'image via OPENAI_API_KEY. Aucun tour pédagogique.
"""
import asyncio
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import charger_env
from app.modalites import Convertisseur, image_validee


async def main():
    charger_env()
    dossier = Path("reports/verification-modalites")
    dossier.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (900, 230), "white")
    font = ImageFont.truetype("C:/Windows/Fonts/segoepr.ttf", 44)
    dessin = ImageDraw.Draw(image)
    dessin.text((35, 20), "1 + 1 = 3", font=font, fill="black")
    dessin.text((35, 110), "Je ne sais pas justifier.", font=font, fill="black")
    sortie = io.BytesIO()
    image.save(sortie, "PNG")
    (dossier / "manuscrit-test.png").write_bytes(sortie.getvalue())
    texte = await Convertisseur().manuscrit(image_validee(sortie.getvalue()))
    resultat = {"texte": texte, "erreur_mathematique_conservee": "1+1=3" in texte.replace(" ", ""),
                "phrase_conservee": "Je ne sais pas justifier" in texte, "appels_vision": 1}
    (dossier / "vision-reelle.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultat, ensure_ascii=True))
    assert resultat["erreur_mathematique_conservee"] and resultat["phrase_conservee"], resultat


if __name__ == "__main__":
    asyncio.run(main())
