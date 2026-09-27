"""Reprise ciblée d'une erreur attestée dans un bilan privé."""
from copy import deepcopy
import json
from pathlib import Path

from app.cours import INDEX, scores_lexicaux
from app.chapitres import chapitre_catalogue
from app.enonces import verifier_enonce
from app.profil import Profil


def point_a_reprendre(profil, session_id, tache_id):
    bilan = profil.bilans.get(session_id)
    if not bilan:
        return None
    return next((deepcopy(p) for p in bilan.get("points", [])
                 if p.get("tache_id") == tache_id
                 and p.get("statut") == "a_retravailler"
                 and p.get("verdict") in ("incorrecte", "incomplete")), None)


def reprises_du_bilan(profil, session_id):
    """Les preuves nouvelles restent séparées du bilan d'origine immuable."""
    reprises = {}
    for tache in profil.taches.values():
        origine = tache.get("reprise_de", {})
        if origine.get("bilan_id") != session_id:
            continue
        evaluations = tache.get("evaluations", [])
        derniere = evaluations[-1] if evaluations else {}
        a_jour = derniere.get("reponse") == "\n".join(tache.get("echanges", []))
        statut = ("validee" if a_jour and derniere.get("verdict") == "correcte"
                  and tache.get("acquise") and tache.get("cloturee") else "a_poursuivre")
        reprises[origine["tache_id"]] = {"statut": statut, "session_id": tache.get("session"),
                                          "bilan_disponible": tache.get("session") in profil.bilans}
    return reprises


async def preparer_reprise(agent, session_id, tache_id, reflexion, *, chemin_cours=INDEX, client=None):
    """Préparer et vérifier avant toute écriture ; l'ancien bilan est conservé."""
    reflexion = reflexion.strip()
    if not 1 <= len(reflexion) <= 2000:
        raise ValueError("Expliquez ce que vous changez dans votre raisonnement (1 à 2 000 caractères).")
    profil = Profil.charger(agent.chemin_profil)
    point = point_a_reprendre(profil, session_id, tache_id)
    if point is None:
        raise ValueError("Cette question n'est pas une erreur à reprendre dans vos bilans.")
    chapitre = profil.bilans[session_id]["chapitre"]
    if chapitre not in agent.chapitres:
        raise ValueError("Ce chapitre n'est pas disponible pour une reprise.")
    ancienne = profil.taches.get(tache_id, {})
    original = next((ex for ex in agent.exercices if ex["id"] == ancienne.get("exercice_id")), None)
    cible = original.get("difficulte", 1) if original else min(2, profil.niveau(chapitre))
    deja_proposes = {t.get("exercice_id") for t in profil.taches.values()}
    candidats = [ex for ex in agent.exercices if ex["chapitre"] == chapitre
                 and ex["id"] not in set(profil.exercices_vus) | deja_proposes
                 and ex.get("corrige", "").strip() and ex.get("difficulte", 1) <= cible]
    question = " ".join(point.get("notions", [])) + " " + point["question"]
    documents = [{"titre": " ".join(ex.get("notions", [])), "texte": ex["enonce"]}
                 for ex in candidats]
    scores = scores_lexicaux(question, documents) if documents else []
    classes = sorted(zip(candidats, scores), key=lambda item: (-item[1], abs(item[0].get("difficulte", 1) - cible)))
    exercice = None
    for candidat, score in [c for c in classes if c[1] > 0][:3]:
        enonce = await verifier_enonce(candidat["enonce"], candidat["corrige"], client)
        if enonce:
            exercice = {**candidat, "enonce": enonce}
            break
    mode = "exercice_proche"
    if exercice is None:
        mode = "question_origine"
        corrige = original.get("corrige", "") if original else ""
        if not corrige and point.get("source"):
            try:
                index = json.loads(Path(chemin_cours).read_text(encoding="utf-8"))
                passage = next((p for p in index.get("passages", [])
                                if p.get("identifiant") == point["source"]), None)
                if (passage and passage.get("transcription_relue")
                        and chapitre_catalogue(index.get("chapitre")) == chapitre):
                    corrige = passage.get("texte", "")
            except (OSError, ValueError):
                pass
        if not corrige:
            raise ValueError("Aucun exercice proche ni corrigé de référence disponible pour cette reprise.")
        enonce = await verifier_enonce(point["question"], corrige, client)
        if not enonce:
            raise ValueError("La question d'origine ne peut pas être reprise avec un énoncé suffisamment fiable.")
        exercice = {"id": ancienne.get("exercice_id", "reprise-" + tache_id),
                    "chapitre": chapitre, "enonce": enonce, "corrige": corrige}
    agent.chapitre = chapitre
    # Une séance ciblée n'accorde pas les étapes de cours de la khôlle normale.
    agent.etape = "exercices"
    agent.exercice = exercice
    agent.revision = {"bilan_id": session_id, "tache_id": tache_id, "mode": mode,
                      "question_origine": point["question"], "notions": point.get("notions", []),
                      "retour_precedent": point.get("justification", ""), "reflexion": reflexion}
    agent.ouvrir_tache(exercice)
    texte = ("Appliquons votre nouvelle démarche à cet exercice du même chapitre."
             if mode == "exercice_proche" else
             "Aucun nouvel exercice proche exploitable n'est disponible. Reprenons la question d'origine.")
    texte += "\n\n" + exercice["enonce"] + "\n\nQuelle idée du cours utilisez-vous et quelles hypothèses devez-vous vérifier ?"
    # La réflexion concerne l'erreur passée, jamais une réponse à l'exercice nouveau.
    agent.messages = [{"role": "user", "content": "Ce que je change : " + reflexion},
                      {"role": "assistant", "content": texte}]
    agent.historique = deepcopy(agent.messages)
    return agent
