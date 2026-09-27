"""Compte-rendu de fin de khôlle (prompts/report_rubric.md). [lane C]

Attention : report_rubric.md contient d'autres accolades que {tags} ;
remplir avec str.replace("{tags}", ...), pas str.format.
"""

from fastapi import APIRouter

router = APIRouter(tags=["compte-rendu"])

# TODO(C) : route qui construit le dossier depuis state.get_session(),
# appelle le LLM, calcule autonomie et note finale, et remplit session.report.
