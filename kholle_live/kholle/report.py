"""Compte-rendu de fin de khôlle (prompts/report_rubric.md). [lane C]

Le dossier de la khôlle est rédigé par la méthode pipelex/compte_rendu.mthds,
exécutée sur l'API Pipelex. Si elle échoue ou tarde, la même méthode (même
système, même prompt, même schéma de sortie, lus dans le .mthds) part chez
OpenAI en sortie structurée ; le champ `moteur` du compte-rendu dit lequel a
répondu. Autonomie, note finale, prénom et exercices conseillés sont calculés ici.

Variables : PIPELEX_API_KEY, OPENAI_API_KEY, REPORT_ENGINE (pipelex | openai),
REPORT_MODEL (repli OpenAI, gpt-5.4 par défaut), PIPELEX_TIMEOUT_S (19 s).
Les clés absentes de kholle_live/.env sont lues dans le .env de la racine.

Attention : report_rubric.md contient d'autres accolades que {tags} ;
remplir avec str.replace("{tags}", ...), pas str.format.

Essai hors serveur : uv run python -m kholle.report tests/fixtures/session_demo.json
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime
import json
import logging
import os
import re
import sys
import time
import tomllib
from collections import Counter
from pathlib import Path

import fastapi
import jinja2
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from . import exercises, state
from .state import BoardLine, HintUse, Session, Turn

logger = logging.getLogger(__name__)

ICI = Path(__file__).resolve().parent.parent
METHODE = ICI / "pipelex" / "compte_rendu.mthds"
RUBRIQUE = ICI / "prompts" / "report_rubric.md"
RAPPORTS = ICI / "data" / "reports"
PROFIL = ICI / "data" / "profile.json"
GABARITS = ICI / "templates"

PIPE_CODE = "compte_rendu_kholle.rediger_compte_rendu"
SYMBOLES = {"ok": "✓", "faux": "✗", "?": "?"}
POIDS_INDICES = {1: 0.5, 2: 1.0, 3: 1.5}
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre")

router = APIRouter(tags=["compte-rendu"])


def _charger_env() -> None:
    """kholle_live/.env d'abord, puis le .env de la racine pour les clés manquantes."""
    load_dotenv(ICI / ".env")
    load_dotenv(ICI.parent / ".env")


# ── Dossier envoyé au LLM ────────────────────────────────────────────────────


def _mmss(t: float) -> str:
    return f"{int(t) // 60:02d}:{int(t) % 60:02d}"


def duree(s: Session) -> float:
    temps = [x.t for x in s.transcript] + [x["t"] for x in s.board_snapshots] + [h.t for h in s.hints]
    return max(temps, default=0.0)


def _ligne(l: dict) -> str:
    texte = f"{SYMBOLES.get(l['verdict'], '?')} {l['texte']}"
    if l.get("detail"):
        texte += f" ({l['detail']})"
    return texte


def historique_tableau(s: Session) -> list[str]:
    """Les instantanés réduits à leurs changements, ligne par ligne."""
    evenements, avant = [], {}
    for inst in s.board_snapshots:
        t, apres = _mmss(inst["t"]), {l["n"]: l for l in inst["lines"]}
        for n, l in apres.items():
            ancienne = avant.get(n)
            if ancienne is None:
                evenements.append(f"[{t}] ligne {n} écrite : {_ligne(l)}")
            elif ancienne["texte"] != l["texte"]:
                evenements.append(f"[{t}] ligne {n} réécrite : {_ligne(l)}")
            elif l["barre"] and not ancienne["barre"]:
                evenements.append(f"[{t}] ligne {n} barrée")
            elif ancienne["verdict"] != l["verdict"]:
                evenements.append(f"[{t}] ligne {n} : {_ligne(l)}")
        evenements += [f"[{t}] ligne {n} effacée" for n in avant if n not in apres]
        avant = apres
    return evenements


def _texte_indice(ex: dict, h: HintUse) -> str | None:
    if h.question_index == 0:
        indices = ex.get("indices", [])
    else:
        suivantes = ex.get("questions_suivantes", [])
        indices = suivantes[h.question_index - 1].get("indices", []) if h.question_index <= len(suivantes) else []
    return indices[h.niveau - 1] if 0 < h.niveau <= len(indices) else None


def construire_dossier(s: Session) -> dict:
    ex = exercises.get(s.exercise_id)
    return {
        "exercice": {
            "titre": ex["titre"],
            "enonce": ex["enonce_latex"],
            "reponse_attendue": ex.get("reponse", {}).get("latex"),
            "corrige": ex.get("corrige_latex"),
            "pieges": ex.get("pieges", []),
            "questions_suivantes": [
                {"question": q["question_orale"], "reponse": q.get("reponse")}
                for q in ex.get("questions_suivantes", [])
            ],
        },
        "duree": f"{int(duree(s)) // 60} min {int(duree(s)) % 60:02d} s",
        "transcription": [
            f"[{_mmss(x.t)}] {'Khôlleur' if x.qui == 'kholleur' else 'Étudiant'} : {x.texte}"
            for x in s.transcript
        ],
        "tableau_final": [
            f"{l.n}. {_ligne(dataclasses.asdict(l))}" + (" [barrée]" if l.barre else "")
            for l in s.board_lines
        ],
        "historique_tableau": historique_tableau(s),
        "indices_donnes": [
            {
                "moment": _mmss(h.t),
                "question": "exercice principal" if h.question_index == 0 else f"question suivante {h.question_index}",
                "niveau": h.niveau,
                "indice": _texte_indice(ex, h),
            }
            for h in s.hints
        ],
    }


# ── Méthode .mthds : exécution Pipelex, ou repli OpenAI ─────────────────────


def bareme() -> str:
    return RUBRIQUE.read_text(encoding="utf-8").replace("{tags}", ", ".join(exercises.all_tags()))


def _schema(concepts: dict, nom: str, domaine: str) -> dict:
    """Schéma JSON strict (OpenAI) d'un concept structuré du .mthds."""
    types = {"text": "string", "integer": "integer", "number": "number", "boolean": "boolean"}

    def champ(spec: dict) -> dict:
        if spec.get("type") == "list":
            if spec.get("item_type") == "concept":
                items = _schema(concepts, spec["item_concept_ref"].removeprefix(domaine + "."), domaine)
            else:
                items = {"type": types[spec["item_type"]]}
            sortie = {"type": "array", "items": items}
        else:
            sortie = {"type": types[spec.get("type", "text")]}
        if not spec.get("required"):
            sortie["type"] = [sortie["type"], "null"]
        return sortie | {"description": spec.get("description", "")}

    structure = {k: v if isinstance(v, dict) else {"description": v}
                 for k, v in concepts[nom]["structure"].items()}
    return {"type": "object", "properties": {k: champ(v) for k, v in structure.items()},
            "required": list(structure), "additionalProperties": False}


async def _via_openai(entrees: dict[str, str]) -> dict:
    from openai import AsyncOpenAI

    methode = tomllib.loads(METHODE.read_text(encoding="utf-8"))
    pipe = methode["pipe"][methode["main_pipe"]]
    concepts = methode.get("concept", {})
    prompt = re.sub(r"@(\w+)", lambda m: entrees.get(m.group(1), m.group(0)), pipe["prompt"])
    modele = os.environ.get("REPORT_MODEL") or "gpt-5.4"
    reponse = await AsyncOpenAI(timeout=60, max_retries=1).chat.completions.create(
        model=modele,
        **({"temperature": 0.2} if modele.startswith("gpt-4") else {"reasoning_effort": "low"}),
        messages=[
            {"role": "system", "content": methode.get("system_prompt", "").strip()},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": pipe["output"], "strict": True,
            "schema": _schema(concepts, pipe["output"], methode["domain"]),
        }},
    )
    return json.loads(reponse.choices[0].message.content)


async def _via_pipelex(entrees: dict[str, str]) -> dict:
    from pipelex_sdk.client import PipelexAPIClient
    from pipelex_sdk.runs import WaitForResultOptions

    async with PipelexAPIClient() as client:
        resultat = await client.start_and_wait(
            pipe_code=PIPE_CODE,
            mthds_contents=[METHODE.read_text(encoding="utf-8")],
            inputs=entrees,
            wait_options=WaitForResultOptions(interval_seconds=0.5, timeout_seconds=120),
        )
    return dict(resultat.main_stuff)


async def executer_methode(dossier: dict) -> tuple[dict, str]:
    """Renvoie (sortie brute de la méthode, moteur qui a répondu).

    Pipelex met 15 à 19 s : le repli OpenAI part en même temps et ne sert que si
    Pipelex échoue ou dépasse PIPELEX_TIMEOUT_S, pour tenir le compte-rendu sous 20 s.
    """
    _charger_env()
    entrees = {"bareme": bareme(), "dossier": json.dumps(dossier, ensure_ascii=False, indent=1)}
    if os.environ.get("REPORT_ENGINE", "pipelex").strip().lower() == "openai":
        return await _via_openai(entrees), "openai"
    pipelex, repli = asyncio.create_task(_via_pipelex(entrees)), asyncio.create_task(_via_openai(entrees))
    try:
        brut = await asyncio.wait_for(pipelex, float(os.environ.get("PIPELEX_TIMEOUT_S", 19)))
        repli.cancel()
        return brut, "pipelex"
    except Exception as e:
        logger.warning("Méthode Pipelex en échec (%r, %r) : repli sur OpenAI.", e, getattr(e, "error", None))
    return await repli, "openai"


# ── Parties déterministes ────────────────────────────────────────────────────


def _demi_point(x, maxi: float = 5.0) -> float:
    try:
        return min(maxi, max(0.0, round(float(x) * 2) / 2))
    except (TypeError, ValueError):
        return 0.0


def normaliser(brut: dict, s: Session) -> dict:
    """Bornes et formats garantis, quel que soit le moteur."""
    tags = {t.casefold(): t for t in exercises.all_tags()}
    lignes = {l.n for l in s.board_lines}
    erreurs = []
    for e in brut.get("erreurs") or []:
        ligne = e.get("ligne")
        erreurs.append({
            "ligne": ligne if isinstance(ligne, int) and ligne in lignes else None,
            "description": str(e.get("description", "")).strip(),
            "corrigee_apres_question": bool(e.get("corrigee_apres_question")),
        })
    a_retravailler = [
        {"tag": tags[str(a.get("tag", "")).strip().casefold()], "conseil": str(a.get("conseil", "")).strip()}
        for a in brut.get("a_retravailler") or []
        if str(a.get("tag", "")).strip().casefold() in tags
    ]
    return {
        "appreciation": str(brut.get("appreciation", "")).strip(),
        "points_forts": [str(p).strip() for p in brut.get("points_forts") or []][:3],
        "erreurs": erreurs,
        "a_retravailler": a_retravailler[:2],
        "oral": _demi_point(brut.get("oral")),
        "rigueur": _demi_point(brut.get("rigueur")),
        "cours": _demi_point(brut.get("cours")),
    }


def autonomie(hints: list[HintUse]) -> float:
    return max(0.0, 5 - sum(POIDS_INDICES.get(h.niveau, 1.5) for h in hints))


_NON_PRENOMS = {"bonjour", "bonsoir", "salut", "oui", "non", "euh", "alors", "moi", "je", "c'est",
                "madame", "monsieur", "merci", "enchanté", "enchantée", "ok", "d'accord"}


def prenom(s: Session) -> str:
    """Réponse de l'étudiant à la première question du khôlleur, sinon « l'étudiant »."""
    if s.eleve:
        return s.eleve
    premiere = next((i for i, x in enumerate(s.transcript) if x.qui == "kholleur"), None)
    reponse = next((x.texte for x in s.transcript[(premiere or 0) + 1:] if x.qui == "eleve"), None)
    if premiere is None or reponse is None:
        return "l'étudiant"
    nom = r"([A-ZÀ-Ý][a-zà-ÿ]+(?:-[A-ZÀ-Ý][a-zà-ÿ]+)?)"
    m = re.search(r"(?:je m'appelle|je m’appelle|moi c'est|moi, c'est|c'est|je suis|appelez-moi)\s+" + nom,
                  reponse, re.IGNORECASE)
    if m:
        return m.group(1)[0].upper() + m.group(1)[1:]
    mots = re.findall(r"[\wÀ-ÿ'-]+", reponse)
    if len(mots) <= 3:
        for mot in mots:
            if mot[0].isupper() and mot.casefold() not in _NON_PRENOMS:
                return mot
    return "l'étudiant"


def exercices_conseilles(tags: list[str], exclure: str, faiblesses: dict | None = None) -> list[dict]:
    """Les 2 exercices dont les tags recoupent le mieux `tags` ; à égalité, les faiblesses passées."""
    faiblesses = faiblesses or {}
    cibles = set(tags)

    def score(ex: dict) -> tuple[int, int]:
        siens = set(ex.get("tags", []))
        return len(siens & cibles), sum(faiblesses.get(t, {}).get("count", 0) for t in siens)

    candidats = [e for e in exercises.all() if e["id"] != exclure]
    choisis = sorted(candidats, key=score, reverse=True)[:2]  # tri stable : ordre du YAML à égalité
    return [{"id": e["id"], "titre": e["titre"], "enonce_latex": e["enonce_latex"], "tags": e.get("tags", [])}
            for e in choisis]


def lire_profil() -> dict:
    try:
        return json.loads(PROFIL.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"eleve": None, "faiblesses": {}, "historique": []}


def _ecrire(chemin: Path, contenu: str) -> None:
    provisoire = chemin.with_suffix(chemin.suffix + ".tmp")
    provisoire.write_text(contenu, encoding="utf-8")
    os.replace(provisoire, chemin)


def mettre_a_jour_profil(cr: dict) -> dict:
    profil = lire_profil()
    profil["eleve"] = cr["eleve"] if cr["eleve"] != "l'étudiant" else profil.get("eleve")
    for tag in dict.fromkeys(a["tag"] for a in cr["a_retravailler"]):
        f = profil.setdefault("faiblesses", {}).setdefault(tag, {"count": 0, "last_seen": None})
        f["count"] += 1
        f["last_seen"] = cr["date"]
    profil.setdefault("historique", []).append(
        {"date": cr["date"], "exercise": cr["exercice"]["id"], "note": cr["note"]})
    _ecrire(PROFIL, json.dumps(profil, ensure_ascii=False, indent=2) + "\n")
    return profil


# ── Rendus HTML et LaTeX ─────────────────────────────────────────────────────


def fr(x: float) -> str:
    """13.5 -> « 13,5 », 14.0 -> « 14 »."""
    return f"{x:g}".replace(".", ",")


def date_longue(iso: str) -> str:
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"


_ECHAPPEMENTS = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_",
                 "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "$": r"\$"}


def tex(texte: str) -> str:
    """Échappe le texte LaTeX en gardant les formules $...$ intactes."""
    def echapper(t: str) -> str:
        return "".join(_ECHAPPEMENTS.get(c, c) for c in t)
    morceaux = str(texte).split("$")
    if len(morceaux) % 2 == 0:  # dollars dépareillés : tout est texte
        return echapper(str(texte))
    return "$".join(m if i % 2 else echapper(m) for i, m in enumerate(morceaux))


_env = jinja2.Environment(loader=jinja2.FileSystemLoader(GABARITS), autoescape=True,
                          trim_blocks=True, lstrip_blocks=True)
# Délimiteurs à part pour le .tex : les accolades LaTeX ne gênent pas Jinja.
_env_tex = jinja2.Environment(loader=jinja2.FileSystemLoader(GABARITS), trim_blocks=True, lstrip_blocks=True,
                              block_start_string="<%", block_end_string="%>",
                              variable_start_string="<<", variable_end_string=">>",
                              comment_start_string="<#", comment_end_string="#>")
for _e in (_env, _env_tex):
    _e.filters |= {"fr": fr, "date_longue": date_longue, "tex": tex, "mmss": _mmss}


def rendre_html(cr: dict) -> str:
    return _env.get_template("compte_rendu.html").render(cr=cr)


def rendre_tex(cr: dict) -> str:
    return _env_tex.get_template("compte_rendu.tex").render(cr=cr)


def texte_console(cr: dict) -> str:
    lignes = [
        f"Khôlle de mathématiques — {cr['eleve']} — {fr(cr['note'])}/20",
        f"{cr['exercice']['titre']} · {date_longue(cr['date'])} · {_mmss(cr['duree_s'])} · "
        f"moteur {cr['moteur']} ({cr['duree_generation_s']} s)",
        "   ".join(f"{k.capitalize()} {fr(cr[k])}/5" for k in ("oral", "rigueur", "autonomie", "cours")),
        "", "Appréciation", f"  {cr['appreciation']}", "", "Points forts",
        *(f"  + {p}" for p in cr["points_forts"]), "", "Erreurs",
        *(f"  - {'ligne ' + str(e['ligne']) if e['ligne'] else 'à l’oral'} : {e['description']}"
          f" ({'corrigée après question' if e['corrigee_apres_question'] else 'non corrigée'})"
          for e in cr["erreurs"]),
        *([] if cr["erreurs"] else ["  (aucune)"]), "", "À retravailler",
        *(f"  * [{a['tag']}] {a['conseil']}" for a in cr["a_retravailler"]), "",
        "Prochaine khôlle : deux exercices ciblés",
        *(f"  {i}. {e['titre']} — {e['enonce_latex']}" for i, e in enumerate(cr["exercices_conseilles"], 1)),
    ]
    return "\n".join(lignes)


# ── Génération ───────────────────────────────────────────────────────────────


async def generer(s: Session, *, enregistrer_profil: bool = True) -> dict:
    """Dossier -> méthode -> parties déterministes -> fichiers et profil. Remplit s.report."""
    debut = time.perf_counter()
    brut, moteur = await executer_methode(construire_dossier(s))
    cr = normaliser(brut, s)
    ex = exercises.get(s.exercise_id)
    profil = lire_profil()
    horodatage = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    cr |= {
        "autonomie": autonomie(s.hints),
        "eleve": prenom(s),
        "session_id": s.id,
        "horodatage": horodatage,
        "date": datetime.date.fromtimestamp(s.started_at).isoformat(),
        "duree_s": round(duree(s)),
        "exercice": {
            "id": ex["id"],
            "titre": ex["titre"],
            "enonce_latex": ex["enonce_latex"],
            "questions_suivantes": [q["question_orale"] for q in ex.get("questions_suivantes", [])],
        },
        "tableau": [dataclasses.asdict(l) for l in s.board_lines],
        "indices": [dataclasses.asdict(h) for h in s.hints],
        "moteur": moteur,
    }
    cr["note"] = cr["oral"] + cr["rigueur"] + cr["autonomie"] + cr["cours"]
    cr["exercices_conseilles"] = exercices_conseilles(
        [a["tag"] for a in cr["a_retravailler"]] or ex.get("tags", []), ex["id"], profil.get("faiblesses"))
    cr["duree_generation_s"] = round(time.perf_counter() - debut, 1)

    RAPPORTS.mkdir(parents=True, exist_ok=True)
    _ecrire(RAPPORTS / f"{horodatage}.json", json.dumps(cr, ensure_ascii=False, indent=2) + "\n")
    _ecrire(RAPPORTS / f"{horodatage}.tex", rendre_tex(cr))
    _ecrire(RAPPORTS / f"{horodatage}.html", rendre_html(cr))
    if enregistrer_profil:
        mettre_a_jour_profil(cr)
    s.report = cr
    return cr


def dernier_rapport() -> dict | None:
    fichiers = sorted(RAPPORTS.glob("*.json"))
    return json.loads(fichiers[-1].read_text(encoding="utf-8")) if fichiers else None


# ── Routes ───────────────────────────────────────────────────────────────────

_en_cours: dict[str, asyncio.Task] = {}


@router.post("/api/report")
async def creer_rapport(force: bool = False):
    """Idempotent par session : un second appel attend la même rédaction."""
    s = state.get_session()
    if s.report is None or force:
        tache = _en_cours.get(s.id)
        if tache is None:
            tache = asyncio.create_task(generer(s))
            _en_cours[s.id] = tache
            tache.add_done_callback(lambda _t, id=s.id: _en_cours.pop(id, None))
        try:
            await asyncio.shield(tache)
        except Exception as e:
            logger.exception("Compte-rendu en échec")
            raise fastapi.HTTPException(502, f"Compte-rendu en échec : {e}")
    return {"json": s.report, "html": rendre_html(s.report)}


@router.get("/api/report/status")
def statut_rapport():
    s = state.get_session()
    return {"session_id": s.id, "finished": s.finished, "pret": s.report is not None, "en_cours": s.id in _en_cours}


@router.get("/api/report/latest", response_class=HTMLResponse)
def dernier_rapport_html(session: str | None = None):
    """Compte-rendu de la session courante ; sans `session`, à défaut le dernier enregistré."""
    s = state.get_session()
    if session is not None and session != s.id:
        raise fastapi.HTTPException(404, "Session inconnue.")
    cr = s.report or (None if session else dernier_rapport())
    if cr is None:
        raise fastapi.HTTPException(404, "Pas encore de compte-rendu.")
    return rendre_html(cr)


@router.get("/api/profile")
def profil():
    return lire_profil()


# ── Ligne de commande ────────────────────────────────────────────────────────


def session_depuis_dict(d: dict) -> Session:
    return Session(**(d | {
        "transcript": [Turn(**x) for x in d.get("transcript", [])],
        "board_lines": [BoardLine(**x) for x in d.get("board_lines", [])],
        "hints": [HintUse(**x) for x in d.get("hints", [])],
    }))


def main(args: list[str]) -> None:
    if not args or args[0].startswith("-"):
        raise SystemExit("Usage : python -m kholle.report <session.json> [--profil]")
    logging.basicConfig(level=logging.WARNING)
    s = session_depuis_dict(json.loads(Path(args[0]).read_text(encoding="utf-8")))
    cr = asyncio.run(generer(s, enregistrer_profil="--profil" in args))
    print(texte_console(cr))
    print("\n" + "\n".join(f"-> {RAPPORTS / cr['horodatage']}.{ext}" for ext in ("json", "html", "tex")))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
