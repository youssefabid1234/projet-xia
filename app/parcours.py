"""Entrées du parcours guidé, désormais intégré à Colle et Examinateur.

L'ancien prototype Agent/ParcoursBorne est remplacé par le moteur unique.
"""
from app.moteur_colle import appliquer_tour, element_actif, installer_tache
from app.plans import demande_preference
