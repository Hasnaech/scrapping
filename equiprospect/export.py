"""Module 5 — Export (CSV ; Google Sheet/Airtable = import direct du CSV).

Lecture/écriture de data/prospects.csv (schéma documenté dans le README).
"""

from __future__ import annotations

import csv
from pathlib import Path

CHEMIN_BASE = Path(__file__).resolve().parent.parent / "data" / "prospects.csv"


def charger(chemin: Path = CHEMIN_BASE) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sauvegarder(lignes: list[dict], chemin: Path) -> None:
    if not lignes:
        raise ValueError("rien à sauvegarder")
    champs: list[str] = []
    for ligne in lignes:  # union ordonnée des colonnes
        for c in ligne:
            if c not in champs:
                champs.append(c)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)


def top_prospects(lignes: list[dict], n: int = 20) -> list[dict]:
    avec_score = [l for l in lignes if l.get("score")]
    return sorted(avec_score, key=lambda l: float(l["score"]), reverse=True)[:n]
