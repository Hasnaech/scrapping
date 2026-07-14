"""Module 3 — Scoring & priorisation.

score = poids(pouvoir de décision) × poids(type de signal) × confiance/100 × 100

Le score est sur 100. La taille d'entreprise et la proximité d'un centre
équestre (brief) pourront pondérer en plus quand ces colonnes seront
enrichies (Pappers/annuaire-entreprises pour l'effectif, géocodage pour la
distance).
"""

from __future__ import annotations

import unicodedata

_POIDS_POSTE = [
    # (mots-clés dans le poste, poids) — le premier qui matche gagne
    (["drh", "ressources humaines", "responsable formation", "head of people",
      "learning", "l&d", "responsable rh", "talent"], 1.0),
    (["directeur general", "directrice generale", "dg ", "pdg", "president",
      "presidente", "ceo", "fondateur", "fondatrice", "co-fondateur",
      "cofondateur", "dirigeant", "dirigeante", "gerant", "gerante",
      "proprietaire"], 0.9),
    (["directeur", "directrice", "associe", "of counsel", "avocat"], 0.7),
    (["cadre", "manager", "responsable", "consultant"], 0.6),
    (["acteur", "humoriste", "animateur", "cavaliere de concours"], 0.4),
]

_POIDS_SIGNAL = {
    "cavalier_pratiquant": 1.0,
    "proprietaire_chevaux": 0.85,
    "affinite_cheval": 0.7,
    "mention_professionnelle_seulement": 0.2,
    "homonymie_ou_bruit": 0.05,
    "aucun": 0.0,
}


def _normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFD", (texte or "").lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def poids_poste(poste: str) -> float:
    p = _normaliser(poste)
    for mots, poids in _POIDS_POSTE:
        if any(m in p for m in mots):
            return poids
    return 0.5


def calculer_score(poste: str, type_signal: str, confiance: int | float) -> float:
    """Score 0-100."""
    signal = _POIDS_SIGNAL.get(type_signal, 0.5)
    return round(poids_poste(poste) * signal * (float(confiance) / 100.0) * 100, 1)


def type_signal_depuis_base(type_signal_cheval: str, niveau: str) -> str:
    """Mappe les libellés du CSV manuel vers les catégories du classifieur."""
    t = _normaliser(type_signal_cheval)
    if "equicoaching" in t or "affinite" in t:
        return "affinite_cheval"
    if any(m in t for m in ["proprietaire", "ecurie", "haras", "trotteur", "eleveur"]):
        return "proprietaire_chevaux"
    if any(m in t for m in ["cavalier", "cavaliere", "polo", "cso", "dressage",
                            "jumping", "cadre noir", "equitation"]):
        return "cavalier_pratiquant"
    if "a qualifier" in _normaliser(niveau) or "b-" in _normaliser(niveau):
        return "affinite_cheval"
    return "affinite_cheval"
