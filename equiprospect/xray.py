"""Module 1 — Sourcing : génération de requêtes X-ray Google/LinkedIn.

Ces requêtes croisent un titre de décideur et un marqueur équestre personnel.
Elles se collent dans Google (ou s'envoient à une API SERP : SerpAPI,
Serper.dev, DataForSEO…) ; chaque résultat `linkedin.com/in/...` est un
candidat "niveau B" à qualifier par le Module 2.
"""

from itertools import product

TITRES_DECIDEURS = [
    '"DRH"',
    '"directrice des ressources humaines"',
    '"directeur des ressources humaines"',
    '"responsable formation"',
    '"responsable RH"',
    '"head of people"',
    '"directeur général"',
    '"directrice générale"',
    '"fondateur"',
    '"fondatrice"',
    '"dirigeante"',
    '"président"',
]

MARQUEURS_EQUESTRES = [
    '"passionnée d\'équitation"',
    '"passionné d\'équitation"',
    '"cavalière depuis"',
    '"cavalier depuis"',
    '"cavalière amateur"',
    '"cavalier amateur"',
    '"concours complet"',
    '"CSO" "équitation"',
    '"dressage" "équitation"',
    '"propriétaire de chevaux"',
    '"mon cheval"',
]

SITES = ["site:fr.linkedin.com/in", "site:linkedin.com/posts"]

# Requêtes presse/annuaires qui ont fait leurs preuves lors de la constitution
# manuelle de la base (voir README) :
REQUETES_PRESSE = [
    'site:pappers.fr/dirigeant "haras" holding OR SAS président',
    'site:pappers.fr/dirigeant "écurie" "président de" société',
    '"propriétaire" écurie OR haras "fondateur" OR "PDG" OR "chef d\'entreprise" jumping OR trot OR galop',
    'équicoaching témoignage "DRH" OR "directeur général" OR "présidente" entreprise',
    '"cavalier amateur" OR "cavalière amateur" "chef d\'entreprise" portrait presse',
    'polo France "patron" équipe "fondateur" OR "PDG" entreprise',
]


def generer_requetes(max_requetes: int | None = None) -> list[str]:
    """Produit la liste des requêtes X-ray (titre × marqueur × site)."""
    requetes = [
        f"{site} {titre} {marqueur}"
        for site, (titre, marqueur) in product(
            SITES, product(TITRES_DECIDEURS, MARQUEURS_EQUESTRES)
        )
    ]
    requetes += REQUETES_PRESSE
    return requetes[:max_requetes] if max_requetes else requetes
