"""Classification taille d'entreprise & accessibilité de la cible.

Objectif commercial : écarter les « baleines » (grands groupes >100 salariés et
célébrités/grandes fortunes qu'un vendeur de formation ne peut pas approcher) et
isoler les dirigeants de TPE/PME réellement joignables.

La taille exacte des sociétés n'est pas dans la base — on l'estime par le nom de
l'entreprise (liste de grands groupes connus) ; en production, remplacer par
l'effectif réel via Pappers/annuaire-entreprises (champ `tranche_effectif`).
"""

from __future__ import annotations

import unicodedata

# Grands groupes / ETI (> 100 salariés) reconnus par le nom
GRANDS_GROUPES = [
    "maisons du monde", "econocom", "carmignac", "indexia", "sfam", "hubside",
    "chanel", "jcdecaux", "rothschild", "savencia", "casden", "clarins", "orange",
    "chateauform", "châteauform", "rakuten", "lvmh", "moet", "moët", "pernod",
    "ricard", "quilvest", "richelieu", "stellantis", "bnp", "capgemini", "procter",
    "p&g", "schmidt", "alstom", "ugecam", "france travail", "hermes", "hermès",
    "kering", "artemis", "artémis", "unifrance", "medef", "samsic", "afnor",
    "eurosport", "total", "credit agricole", "crédit agricole", "maxi zoo", "ldc",
    " ey", "gl events", "ring capital", "steervision", "clarins fragrance",
]

# Célébrités & grandes fortunes = inatteignables pour une prospection formation
CELEBRITES = {
    "guillaume canet", "julien courbet", "nicolas canteloup", "antoine griezmann",
    "tony parker", "édouard carmignac", "edouard carmignac", "hugues carmignac",
    "alain wertheimer", "gérard wertheimer", "gerard wertheimer",
    "édouard de rothschild", "edouard de rothschild", "mathilde pinault",
    "jean-françois decaux", "jean-francois decaux", "patrick guerrand-hermès",
    "patrick guerrand-hermes", "xavier marie", "jean-louis bouchard",
    "sadri fegaier", "geneviève mégret", "genevieve megret", "william kriegel",
    "birger strom", "robert strom", "gérard augustin-normand", "guy pariente",
    "pierre pilarski", "jean-pierre barjon", "kamel chehboub", "sandrine groslier",
    "christian baillet", "jean-claude seroul", "emmanuèle perron-pette", "armand pette",
}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def classer_ligne(ligne: dict) -> tuple[str, str]:
    """Comme classer(), mais privilégie l'effectif RÉEL (gouv.py) s'il est là."""
    reel = ligne.get("effectif_moins_100")
    if reel in ("oui", "non") and _norm(ligne.get("nom", "")) not in {_norm(c) for c in CELEBRITES}:
        if reel == "non":
            return f"{ligne.get('effectif_reel', '>=100')} salariés", "non"
        return f"{ligne.get('effectif_reel', '<100')} salariés (vérifié)", "oui"
    return classer(ligne.get("nom", ""), ligne.get("entreprise", ""))


def classer(nom: str, entreprise: str) -> tuple[str, str]:
    """Retourne (taille_estimee, cible_accessible) : 'oui'/'non'/'a_confirmer'."""
    if _norm(nom) in {_norm(c) for c in CELEBRITES}:
        return "grande fortune / célébrité", "non"
    ent = _norm(entreprise)
    if any(_norm(g) in ent for g in GRANDS_GROUPES):
        return "grande entreprise (>100)", "non"
    # associations/fédérations = fonctions bénévoles, joignables mais pas "PME employeur"
    if any(m in ent for m in ["france galop", "le trot", "setf", "unat", "snpt",
                              "ff polo", "polo", "societe des courses", "société des courses",
                              "hippodrome", "club grc", "fpg", "apgo", "cde", "comite", "comité"]):
        return "association/fédération (bénévole)", "a_confirmer"
    return "TPE/PME estimée (<100)", "oui"
