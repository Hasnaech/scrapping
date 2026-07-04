"""Module 4 — Enrichissement contact (email pro, téléphone).

Dropcontact est recommandé (conforme RGPD, spécialisé France, pas de base
achetée : il déduit/vérifie les emails). Clé API dans DROPCONTACT_API_KEY.
Alternatives : Kaspr, Hunter.io — même logique d'intégration.

Aucun email n'est « deviné » : sans clé API, la colonne reste vide.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request

DROPCONTACT_URL = "https://api.dropcontact.io/batch"


def enrichir_dropcontact(personnes: list[dict], attente_s: int = 15) -> list[dict]:
    """Enrichit une liste de {first_name, last_name, company, website?}.

    Retourne la même liste avec `email` (et `phone` si dispo) quand Dropcontact
    trouve un contact vérifié. Nécessite DROPCONTACT_API_KEY.
    """
    cle = os.environ.get("DROPCONTACT_API_KEY")
    if not cle:
        raise RuntimeError(
            "DROPCONTACT_API_KEY non défini — export DROPCONTACT_API_KEY=... "
            "(https://app.dropcontact.io) puis relancer."
        )

    corps = json.dumps({"data": personnes, "siren": True, "language": "fr"}).encode()
    req = urllib.request.Request(
        DROPCONTACT_URL,
        data=corps,
        headers={"Content-Type": "application/json", "X-Access-Token": cle},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        request_id = json.loads(r.read())["request_id"]

    # Dropcontact est asynchrone : on poll le même endpoint avec le request_id
    while True:
        time.sleep(attente_s)
        req = urllib.request.Request(
            f"{DROPCONTACT_URL}/{request_id}", headers={"X-Access-Token": cle}
        )
        with urllib.request.urlopen(req) as r:
            reponse = json.loads(r.read())
        if reponse.get("success"):
            return reponse["data"]
        print("  … enrichissement Dropcontact en cours")
