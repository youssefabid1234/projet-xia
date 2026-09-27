"""Retire les coordonnées documentaires des textes destinés à l'élève."""
import re


def texte_eleve(texte):
    texte = re.sub(r"\b(Définition|Definition|Théorème|Theoreme|Proposition|Lemme|Corollaire|Remarque)\s+\d+(?:\.\d+)+\b", r"\1", texte, flags=re.I)
    texte = re.sub(r"[,;]?\s*\(?pages?\s+PDF\s+\d+(?:\s*[,–-]\s*\d+)*\)?", "", texte, flags=re.I)
    return texte


def message_eleve(message):
    if message.get("role") != "colleur":
        return message
    resultat = {**message, "texte": texte_eleve(message["texte"])}
    if message.get("question"):
        resultat["question"] = {**message["question"], "texte": texte_eleve(message["question"]["texte"])}
    return resultat


def compte_rendu(taches, libelles, interrompue=False):
    """Constats issus exclusivement des scores ; aucun jugement supplémentaire du modèle."""
    lignes = []
    for i, t in enumerate(taches, 1):
        score = t.get("score")
        resultat = "non notée" if score is None else f"{score * 100:g} %"
        lignes.append(f"- {i}. {libelles[t['etape']]} — {texte_eleve(t['question'])} : **{resultat}** "
                      f"({t.get('indices', 0)} aide(s), {t.get('tentatives_totales', 0)} tentative(s)).")
    notes = [(i, t) for i, t in enumerate(taches, 1) if t.get("score") is not None]
    forts = [str(i) for i, t in notes if t["score"] >= .8]
    faibles = [str(i) for i, t in notes if t["score"] < .8]
    lignes += ["", "**Points forts (score ≥ 80 %) :** " + ("tâches " + ", ".join(forts) if forts else "aucune tâche à ce seuil."),
               "**À retravailler (score < 80 %) :** " + ("tâches " + ", ".join(faibles) if faibles else "aucune tâche notée sous ce seuil.")]
    if notes:
        pire, _ = min(notes, key=lambda item: item[1]["score"])
        lignes.append(f"**Conseil :** reprenez sans aide la tâche {pire}, qui a le score le plus bas." if faibles
                      else "**Conseil :** poursuivez avec des notions nouvelles.")
    if interrompue:
        lignes.append("La tâche interrompue n'entre pas dans la note ; elle n'est pas comptée comme un échec.")
    return "\n".join(lignes)
