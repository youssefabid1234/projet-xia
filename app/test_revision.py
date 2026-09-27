"""Preuves et transitions de la reprise, avec évaluations simulées."""
from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from app.agent import Agent
from app.bilan import terminer_colle
from app.chapitres import CHAPITRE_SERIES
from app.profil import Profil
from app.revision import point_a_reprendre, preparer_reprise, reprises_du_bilan
from app.test_agent import appel, sortie


def installer_bilan(chemin):
    profil = Profil.charger(chemin)
    profil.niveaux = {CHAPITRE_SERIES: 2}
    profil.exercices_vus = ["origine"]
    profil.taches["erreur"] = {
        "id": "erreur", "session": "ancienne", "chapitre": CHAPITRE_SERIES,
        "etape": "cours", "nature": "theoreme", "source": "cours-1", "exercice_id": "origine",
        "enonce": "Justifier une comparaison de séries positives.", "notions": ["comparaison", "positivité"],
        "echanges": ["Je compare sans vérifier le signe."],
        "evaluations": [{"reponse": "Je compare sans vérifier le signe.", "verdict": "incorrecte",
                         "type_erreur": "hypothese", "explication": "La positivité doit être justifiée."}],
    }
    profil.sauvegarder(chemin)
    ancien = SimpleNamespace(session_colle="ancienne", chapitre=CHAPITRE_SERIES,
                             debut_colle="2026-09-27T10:00:00+00:00", etape="cours", messages=[])
    return terminer_colle(chemin, ancien)


CATALOGUE = [
    {"id": "origine", "chapitre": CHAPITRE_SERIES, "difficulte": 2,
     "enonce": "Justifier une comparaison de séries positives.", "corrige": "REFERENCE_ORIGINE"},
    {"id": "proche", "chapitre": CHAPITRE_SERIES, "difficulte": 1,
     "enonce": "Comparer ces séries positives et justifier la comparaison.", "corrige": "REFERENCE_PRIVEE"},
    {"id": "autre", "chapitre": CHAPITRE_SERIES, "difficulte": 1,
     "enonce": "Calculer une intégrale.", "corrige": "REFERENCE_AUTRE"},
]


class RevisionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        dossier = TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.path = Path(dossier.name) / "eleve.json"
        self.bilan = installer_bilan(self.path)
        self.agent = Agent(self.path, deepcopy(CATALOGUE))
        verif = patch("app.revision.verifier_enonce", new_callable=AsyncMock)
        self.verifier = verif.start()
        self.addCleanup(verif.stop)
        self.verifier.side_effect = lambda enonce, corrige, client: enonce
        self.client = SimpleNamespace(responses=SimpleNamespace(create=AsyncMock()))

    async def commencer(self):
        return await preparer_reprise(self.agent, "ancienne", "erreur", "REFLEXION_ELEVE : vérifier la positivité")

    async def test_selection_ciblee_reference_privee_et_bilan_immuable(self):
        await self.commencer()
        self.assertEqual(self.agent.exercice["id"], "proche")
        self.assertEqual(self.agent.tache["echanges"], [])
        self.assertEqual(self.agent.tache["reprise_de"]["tache_id"], "erreur")
        self.assertIn(self.agent.exercice["enonce"], self.agent.messages[-1]["content"])
        self.assertNotIn("REFERENCE_PRIVEE", str(self.agent.messages))
        profil = Profil.charger(self.path)
        self.assertEqual(profil.bilans["ancienne"], self.bilan)
        self.assertEqual(profil.niveaux, {CHAPITRE_SERIES: 2})
        self.assertEqual(profil.exercices_vus, ["origine"])

    async def test_exercice_deja_propose_evite_meme_sans_evaluation(self):
        profil = Profil.charger(self.path)
        profil.taches["non-fini"] = {"exercice_id": "proche"}
        profil.sauvegarder(self.path)
        await self.commencer()
        self.assertEqual(self.agent.revision["mode"], "question_origine")
        self.assertIn("Reprenons la question d'origine", self.agent.messages[-1]["content"])

    async def test_pas_de_question_non_evaluee_ou_deja_validee(self):
        for statut, verdict in (("valide", "correcte"), ("non_evalue", None), ("a_confirmer", "indeterminable")):
            profil = Profil.charger(self.path)
            profil.bilans["ancienne"]["points"][0].update(statut=statut, verdict=verdict)
            profil.sauvegarder(self.path)
            self.assertIsNone(point_a_reprendre(profil, "ancienne", "erreur"))
            with self.assertRaises(ValueError):
                await self.commencer()
        self.verifier.assert_not_awaited()

    async def test_absence_reference_ne_cree_pas_de_tache(self):
        self.agent.exercices = [{**CATALOGUE[2], "corrige": ""}]
        avant = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "corrigé de référence"):
            await preparer_reprise(self.agent, "ancienne", "erreur", "Comprendre", chemin_cours=self.path.parent / "absent")
        self.assertEqual(self.path.read_bytes(), avant)

    async def test_refus_enonce_puis_repli_et_panne_reessayable(self):
        self.verifier.side_effect = [None, CATALOGUE[0]["enonce"]]
        await self.commencer()
        self.assertEqual(self.agent.revision["mode"], "question_origine")
        autre = Agent(self.path, deepcopy(CATALOGUE))
        avant = self.path.read_bytes()
        self.verifier.side_effect = RuntimeError("API indisponible")
        with self.assertRaises(RuntimeError):
            await preparer_reprise(autre, "ancienne", "erreur", "Réessayer")
        self.assertEqual(self.path.read_bytes(), avant)

    async def test_repli_question_cours_depuis_source_relue_du_bon_chapitre(self):
        self.agent.exercices = [CATALOGUE[2]]
        index = self.path.parent / "cours.json"
        index.write_text(json.dumps({"chapitre": "16 — Séries numériques", "passages": [
            {"identifiant": "cours-1", "texte": "REFERENCE_COURS", "transcription_relue": True}]}))
        await preparer_reprise(self.agent, "ancienne", "erreur", "Vérifier les signes", chemin_cours=index)
        self.assertEqual(self.agent.exercice["corrige"], "REFERENCE_COURS")
        self.assertNotIn("REFERENCE_COURS", str(self.agent.historique))

    async def test_erreur_relance_reaction_reussite_persistante(self):
        await self.commencer()
        observation = appel("observer_tour", tentative="oui", indice_demande="non", indice_donne="non",
                            rappel_cours="non", intuition="pertinente", notions="positivité", blocage="non",
                            fini="non", correction="non", reformulation="non")
        self.client.responses.create.side_effect = [sortie(appels=[observation]), sortie("Quel signe faut-il vérifier ?")]
        faux = {"verdict": "incorrecte", "type_erreur": "hypothese", "explication": "Justifiez les signes."}
        vrai = {"verdict": "correcte", "type_erreur": "aucune", "explication": "La comparaison est maintenant justifiée."}
        with patch.object(self.agent, "evaluer_reponse", new=AsyncMock(side_effect=[faux, vrai])):
            self.assertEqual(await self.agent.repondre("Ils convergent.", self.client), "Quel signe faut-il vérifier ?")
            self.assertFalse(self.agent.tache["cloturee"])
            self.assertEqual(reprises_du_bilan(Profil.charger(self.path), "ancienne")["erreur"]["statut"], "a_poursuivre")
            await self.agent.repondre("Les termes sont positifs et majorés par une série convergente.", self.client)
        self.assertTrue(self.agent.tache["cloturee"])
        self.assertEqual(len(self.agent.tache["echanges"]), 2)
        self.assertEqual(len(self.agent.tache["evaluations"]), 2)
        self.assertEqual(self.client.responses.create.await_count, 2)
        nouvelle = terminer_colle(self.path, self.agent)
        self.assertEqual(nouvelle["compteurs"]["valide"], 1)
        profil = Profil.charger(self.path)
        self.assertEqual(reprises_du_bilan(profil, "ancienne")["erreur"]["statut"], "validee")
        self.assertEqual(profil.bilans["ancienne"], self.bilan)
        for appel_api in self.client.responses.create.call_args_list:
            args = appel_api.kwargs
            self.assertNotIn("REFLEXION_ELEVE", args["instructions"])
            self.assertIn("REFLEXION_ELEVE", args["input"][0]["content"])
            self.assertEqual(args["input"][0]["role"], "user")
            self.assertNotIn("REFERENCE_PRIVEE", str(args))

    async def test_indeterminable_ne_valide_pas_et_ne_change_pas_de_question(self):
        await self.commencer()
        self.agent.tache["echanges"] = ["Une réponse ambiguë"]
        with patch.object(self.agent, "evaluer_reponse", new=AsyncMock(return_value={
                "verdict": "indeterminable", "type_erreur": "non_determinable", "explication": "Ambiguïté"})):
            await self.agent.evaluer_tache()
        self.assertFalse(self.agent.tache["acquise"])
        with self.assertRaises(ValueError):
            await self.agent.proposer_exercice(CHAPITRE_SERIES, self.client)

    async def test_reprise_conserve_projet_et_transmet_les_deux_contextes(self):
        profil = Profil.charger(self.path)
        projet = {"filiere": "MPI", "objectifs": "OBJECTIF_CENTRALE", "rang_maths": 3, "effectif": 40}
        profil.projet_eleve = projet
        profil.sauvegarder(self.path)
        await self.commencer()
        self.client.responses.create.return_value = sortie("Quelle hypothèse manque ?")
        with patch.object(self.agent, "evaluer_reponse", new=AsyncMock(return_value={
                "verdict": "incomplete", "type_erreur": "hypothese", "explication": "Justifiez les signes."})):
            await self.agent.repondre("Je compare les termes.", self.client)
        args = self.client.responses.create.call_args.kwargs
        for marqueur in ("OBJECTIF_CENTRALE", "REFLEXION_ELEVE"):
            self.assertNotIn(marqueur, args["instructions"])
            self.assertTrue(any(marqueur in item.get("content", "") and item.get("role") == "user"
                                for item in args["input"]))
        self.assertNotIn("Contexte de reprise", str(self.agent.historique))
        terminer_colle(self.path, self.agent)
        relu = Profil.charger(self.path)
        self.assertEqual(relu.projet_eleve, projet)
        self.assertEqual(relu.bilans["ancienne"], self.bilan)
        self.assertEqual(len(relu.bilans), 2)

    async def test_evaluation_reelle_simulee_ne_change_pas_niveau(self):
        await self.commencer()
        with patch.dict(os.environ, {"PIPELEX_API_KEY": "test"}), patch("app.agent.PipelexAPIClient") as classe:
            pipelex = AsyncMock()
            classe.return_value.__aenter__.return_value = pipelex
            pipelex.start_and_wait.return_value.main_stuff = {
                "verdict": "correcte", "type_erreur": "aucune", "explication": "Preuve complète"}
            await self.agent.evaluer_reponse(self.agent.exercice["enonce"], "Preuve réelle")
            self.assertEqual(pipelex.start_and_wait.call_args.kwargs["inputs"]["corrige"], "REFERENCE_PRIVEE")
        self.assertEqual(Profil.charger(self.path).exercices_vus, ["origine"])
        self.assertEqual(Profil.charger(self.path).niveaux, {CHAPITRE_SERIES: 2})


if __name__ == "__main__":
    unittest.main()
