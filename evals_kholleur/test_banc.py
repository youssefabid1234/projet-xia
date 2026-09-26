"""Tests du banc et de son honnêteté de reporting, jamais des notes du modèle."""

import copy
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from evals_kholleur.banque import CAS
from evals_kholleur.banc import (
    BRANCHES, CRITERES, executer_sonde, exporter, grille_vierge, instantane,
    main, observations, preparer_agent, resumer, selectionner, sondes, verifier,
)


class BanqueTests(unittest.TestCase):
    def test_exactement_cent_situations_et_trois_cents_reactions(self):
        bilan = verifier()
        self.assertEqual(bilan["cas"], 100)
        self.assertEqual(bilan["reactions"], 300)
        self.assertEqual(len({c["objectif_relance"] for c in CAS}), 100)
        self.assertEqual(len({c["relance_exemple"] for c in CAS}), 100)
        self.assertEqual(len({c["reponse_initiale"] for c in CAS}), 100)
        for c in CAS:
            with self.subTest(c=c["id"]):
                self.assertEqual(len({r["eleve"] for r in c["reactions"].values()}), 3)

    def test_cas_corrects_aide_et_correction_presents(self):
        statuts = [c["statut_initial"] for c in CAS]
        self.assertGreaterEqual(statuts.count("correcte"), 10)
        self.assertIn("aide", statuts)
        self.assertIn("correction", statuts)

    def test_refus_de_corpus_incomplet_duplique_ou_sans_reference(self):
        corrompu = copy.deepcopy(CAS)
        corrompu[0]["reference"] = ""
        corrompu[1]["id"] = corrompu[0]["id"]
        corrompu[2]["reactions"].pop("blocage")
        with self.assertRaises(ValueError) as erreur:
            verifier(corrompu)
        self.assertIn("reference", str(erreur.exception))
        self.assertIn("identifiants", str(erreur.exception))
        self.assertIn("trois réactions", str(erreur.exception))

    def test_selection_refuse_identifiants_inconnus(self):
        with self.assertRaises(ValueError):
            selectionner(["K101"])
        with self.assertRaises(ValueError):
            selectionner([])
        self.assertEqual([c["id"] for c in selectionner(["K002", "K001", "K002"])], ["K002", "K001"])

    def test_programme_explicitement_400_sondes_et_non_100_reussites(self):
        programme = list(sondes(CAS, "tout", "toutes"))
        self.assertEqual(len(programme), 400)
        self.assertEqual(len(list(sondes(CAS, "reactions", "justifiee"))), 100)
        self.assertEqual(len(list(sondes(CAS, "initiale", "toutes"))), 100)

    def test_export_json_et_fiches_lisibles(self):
        with tempfile.TemporaryDirectory() as t:
            dossier = Path(t)
            exporter(dossier)
            donnees = json.loads((dossier / "cas_100.json").read_text(encoding="utf-8"))
            self.assertEqual(donnees["cas"], CAS)
            texte = (dossier / "scenarios_100.md").read_text(encoding="utf-8")
            self.assertEqual(texte.count("\n## K"), 100)
            self.assertIn("aucun résultat de réussite", texte)

    def test_simulation_sans_cles_et_sans_appel_agent(self):
        sortie = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), patch("evals_kholleur.banc.executer_sonde") as appel, redirect_stdout(sortie):
            code = main(["executer", "--tous", "--phase", "tout", "--simuler"])
        self.assertEqual(code, 0)
        appel.assert_not_called()
        self.assertEqual(json.loads(sortie.getvalue())["sondes"], 400)

    def test_execution_reelle_exige_les_cles_sans_en_afficher(self):
        with patch.dict(os.environ, {}, clear=True), patch("evals_kholleur.banc.executer_sonde") as appel, patch("sys.stderr", new_callable=io.StringIO) as sortie:
            with self.assertRaises(SystemExit) as erreur:
                main(["executer", "--ids", "K001", "--sortie", "inutilise.jsonl"])
        self.assertEqual(erreur.exception.code, 2)
        self.assertIn("Variables requises absentes", sortie.getvalue())
        appel.assert_not_called()


class ProtocoleTests(unittest.TestCase):
    def setUp(self):
        self.temporaire = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporaire.cleanup)
        self.dossier = Path(self.temporaire.name)

    def test_reference_privee_pas_dans_dialogue_et_profils_separes(self):
        c = copy.deepcopy(CAS[0])
        c["reference"] = "REFERENCE_PRIVEE_SENTINELLE"
        a, message = preparer_agent(c, "initiale", self.dossier / "a.json")
        b, _ = preparer_agent(CAS[1], "initiale", self.dossier / "b.json")
        self.assertNotIn("REFERENCE_PRIVEE_SENTINELLE", json.dumps(a.historique))
        self.assertEqual(a.exercice["corrige"], "REFERENCE_PRIVEE_SENTINELLE")
        self.assertEqual(message, c["reponse_initiale"])
        self.assertNotEqual(a.tache["id"], b.tache["id"])
        self.assertEqual(a.tache["echanges"], [])

    def test_reactions_repondent_a_une_relance_effectivement_presente(self):
        for branche in BRANCHES:
            with self.subTest(branche=branche):
                a, message = preparer_agent(CAS[44], branche, self.dossier / f"{branche}.json")
                self.assertEqual(a.historique[-1], {"role": "assistant", "content": CAS[44]["relance_exemple"]})
                self.assertEqual(message, CAS[44]["reactions"][branche]["eleve"])
                self.assertEqual(a.tache["echanges"], [CAS[44]["reponse_initiale"]])
                self.assertEqual(a.tache["evaluations"], [])

    def test_erreur_kholleur_et_boucle_sont_dans_le_contexte(self):
        a, _ = preparer_agent(CAS[95], "initiale", self.dossier / "erreur.json")
        self.assertEqual(a.historique[-1]["role"], "assistant")
        self.assertIn("diverge puisque", a.historique[-1]["content"])
        self.assertEqual(a.tache["echanges"], [])
        b, _ = preparer_agent(CAS[99], "initiale", self.dossier / "boucle.json")
        self.assertEqual(len(b.tache["echanges"]), 2)
        self.assertTrue(all("2" in m for m in b.tache["echanges"]))

    def test_correction_demandee_presente_avant_verification_comprehension(self):
        a, _ = preparer_agent(CAS[94], "justifiee", self.dossier / "correction.json")
        self.assertIn(CAS[94]["explication_avant_relance"], a.historique[-1]["content"])
        self.assertTrue(a.historique[-1]["content"].endswith(CAS[94]["relance_exemple"]))
        b, _ = preparer_agent(CAS[94], "initiale", self.dossier / "demande.json")
        self.assertNotIn(CAS[94]["explication_avant_relance"], json.dumps(b.historique, ensure_ascii=False))

    def test_snapshot_garde_la_tache_initiale_apres_changement(self):
        a, _ = preparer_agent(CAS[0], "initiale", self.dossier / "profil.json")
        initiale = a.tache["id"]
        a.ouvrir_tache({**a.exercice, "id": "autre"})
        etat = instantane(a, initiale)
        self.assertNotEqual(etat["tache_active_id"], initiale)
        self.assertEqual(etat["tache_testee"]["id"], initiale)

    def test_drapeau_verdict_n_est_pas_un_score(self):
        avant = {"tache_testee": {"echanges": []}}
        apres = {"tache_testee": {"echanges": ["ma réponse"]}}
        obs = observations("Tu as raison. Pourquoi ?", avant, apres, "ma réponse")
        self.assertIn("verdict_explicite_en_entree_a_relire", obs["drapeaux_a_relire"])
        self.assertEqual(obs["evaluation_pedagogique"], "non_automatisee")
        self.assertNotIn("score", obs)
        self.assertNotIn("verdict_explicite_en_entree_a_relire", observations(
            "Dans quel cas cet énoncé serait-il faux ?", avant, apres, "ma réponse")["drapeaux_a_relire"])

    def test_message_present_dans_le_passe_ne_suffit_pas(self):
        etat = {"tache_testee": {"echanges": ["compris"]}}
        obs = observations("Précisez.", etat, etat, "compris")
        self.assertIn("dernier_message_non_enregistre_dans_la_tache", obs["drapeaux_a_relire"])

    def test_aucune_reussite_sans_relecture_complete_et_signee(self):
        def trace(grille):
            return {"statut_execution": "terminee", "relecture": grille}
        notes = {c: 2 for c in CRITERES}
        fichier = self.dossier / "rapport.jsonl"
        traces = [trace(grille_vierge()),
                  trace({"statut": "relue", "criteres": notes}),
                  trace({"statut": "relue", "relecteur": "Test", "criteres": notes}),
                  trace({"statut": "relue", "relecteur": "Test", "criteres": {**notes, CRITERES[0]: 0}}),
                  {"statut_execution": "erreur", "relecture": grille_vierge()}]
        fichier.write_text("\n".join(json.dumps(t) for t in traces), encoding="utf-8")
        self.assertEqual(resumer(fichier), {"sondes": 5, "executions_en_erreur": 1,
            "relues_reussies": 1, "relues_echouees": 1, "a_relire": 2})


class ExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_consigne_locale_traces_et_pas_de_temps_eleve_invente(self):
        from app import agent as module_agent
        initiale = module_agent.INSTRUCTIONS

        async def reponse_simulee(agent, message):
            self.assertIn("faire réagir et justifier", module_agent.INSTRUCTIONS)
            agent.tache["echanges"].append(message)
            agent.sauver_tache()
            return "Quelle hypothèse utilisez-vous ici ?"

        with tempfile.TemporaryDirectory() as t, patch.object(module_agent.Agent, "repondre", reponse_simulee):
            trace = await executer_sonde(CAS[0], "initiale", Path(t), "defi")
        self.assertEqual(module_agent.INSTRUCTIONS, initiale)
        self.assertEqual(trace["statut_execution"], "terminee")
        self.assertEqual(trace["relecture"]["statut"], "a_relire")
        self.assertIsNone(trace["temps_reaction_eleve_secondes"])
        self.assertGreaterEqual(trace["latence_execution_secondes"], 0)
        self.assertEqual(trace["observations"]["drapeaux_a_relire"], [])

    async def test_erreur_fournisseur_ne_divulgue_pas_son_message(self):
        from app import agent as module_agent
        initiale = module_agent.INSTRUCTIONS

        async def panne(agent, message):
            raise RuntimeError("Une clé secrète SENTINELLE_NE_PAS_CONSERVER")

        with tempfile.TemporaryDirectory() as t, patch.object(module_agent.Agent, "repondre", panne):
            trace = await executer_sonde(CAS[0], "initiale", Path(t), "defi")
        self.assertEqual(module_agent.INSTRUCTIONS, initiale)
        self.assertEqual(trace["statut_execution"], "erreur")
        self.assertEqual(trace["type_erreur"], "RuntimeError")
        self.assertNotIn("SENTINELLE_NE_PAS_CONSERVER", json.dumps(trace))
        self.assertEqual(trace["relecture"]["statut"], "a_relire")


if __name__ == "__main__":
    unittest.main()
