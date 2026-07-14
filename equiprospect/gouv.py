"""Enrichissement & sourcing GRATUITS via recherche-entreprises.api.gouv.fr.

API publique de l'État, **gratuite et sans clé** — l'option la moins coûteuse
pour :
  1. remplir l'effectif RÉEL de chaque société (le filtre « <100 salariés »
     devient fiable au lieu d'être estimé par le nom) ;
  2. sourcer de nouveaux dirigeants de petites écuries/haras (élevage équin
     NAF 01.43Z), qui cumulent souvent une activité commerciale = cible PME.

Aucune dépendance (urllib stdlib). Se lance en local :
  python -m equiprospect gouv --enrichir
  python -m equiprospect gouv --sourcer "haras" --activite 01.43Z
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

BASE = "https://recherche-entreprises.api.gouv.fr/search"

# Codes INSEE « tranche effectif salarié » -> libellé lisible.
TRANCHES = {
    "NN": "non renseigné", "": "non renseigné", None: "non renseigné",
    "00": "0 salarié", "01": "1-2", "02": "3-5", "03": "6-9",
    "11": "10-19", "12": "20-49", "21": "50-99",
    "22": "100-199", "31": "200-249", "32": "250-499", "41": "500-999",
    "42": "1000-1999", "51": "2000-4999", "52": "5000-9999", "53": "10000+",
}
# Une entreprise est « < 100 salariés » tant que le code est <= "21".
_CODES_MOINS_100 = {"NN", "", None, "00", "01", "02", "03", "11", "12", "21"}


def moins_de_100(code: str | None) -> bool:
    return code in _CODES_MOINS_100


def tranche_label(code: str | None) -> str:
    return TRANCHES.get(code, f"code {code}")


def rechercher(q: str, *, activite: str | None = None, page: int = 1,
               par_page: int = 20, timeout: int = 20) -> dict:
    """Appel brut à l'API (retourne le JSON décodé)."""
    params = {"q": q, "page": page, "per_page": par_page}
    if activite:
        params["activite_principale"] = activite
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "equiprospect/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _premier_resultat(nom_entreprise: str) -> dict | None:
    try:
        data = rechercher(nom_entreprise, par_page=1)
    except Exception as exc:  # réseau coupé, 5xx… on n'interrompt pas le lot
        print(f"    (échec API pour « {nom_entreprise} » : {exc})")
        return None
    res = data.get("results") or []
    return res[0] if res else None


def enrichir_effectif(lignes: list[dict], pause_s: float = 0.2) -> int:
    """Renseigne effectif_reel / siren / effectif_moins_100 sur chaque ligne.

    Retourne le nombre de lignes enrichies. Idempotent : ignore celles déjà
    renseignées et celles sans nom d'entreprise exploitable.
    """
    enrichies = 0
    for ligne in lignes:
        ent = (ligne.get("entreprise") or "").strip()
        if not ent or ligne.get("effectif_reel"):
            continue
        # on retire les précisions entre parenthèses pour améliorer le matching
        requete = ent.split("(")[0].split("/")[0].strip()
        if len(requete) < 3:
            continue
        r = _premier_resultat(requete)
        time.sleep(pause_s)
        if not r:
            continue
        code = r.get("tranche_effectif_salarie")
        ligne["siren"] = r.get("siren", "")
        ligne["effectif_reel"] = tranche_label(code)
        ligne["effectif_moins_100"] = "oui" if moins_de_100(code) else "non"
        enrichies += 1
    return enrichies


def sourcer(q: str, *, activite: str | None = "01.43Z", pages: int = 3,
            qualites=("président", "gérant", "directeur", "associé")) -> list[dict]:
    """Source des dirigeants de petites structures équines.

    NAF 01.43Z = élevage de chevaux et d'autres équidés (haras).
    Retourne des candidats prêts à devenir des lignes de la base.
    """
    candidats: list[dict] = []
    vus = set()
    for page in range(1, pages + 1):
        try:
            data = rechercher(q, activite=activite, page=page, par_page=25)
        except Exception as exc:
            print(f"  (échec API page {page} : {exc})")
            break
        for r in data.get("results") or []:
            code = r.get("tranche_effectif_salarie")
            if not moins_de_100(code):
                continue
            siege = r.get("siege") or {}
            for d in r.get("dirigeants") or []:
                prenom = (d.get("prenoms") or "").split()[:1]
                nom_complet = " ".join((prenom + [d.get("nom") or ""])).strip()
                if not nom_complet or nom_complet.lower() in vus:
                    continue
                if qualites and not any(qu in (d.get("qualite") or "").lower() for qu in qualites):
                    continue
                vus.add(nom_complet.lower())
                candidats.append({
                    "nom": nom_complet.title(),
                    "poste": f"{(d.get('qualite') or 'dirigeant').strip()} — {r.get('nom_complet', q)}",
                    "entreprise": r.get("nom_complet") or r.get("nom_raison_sociale") or q,
                    "ville_region": siege.get("libelle_commune", ""),
                    "siren": r.get("siren", ""),
                    "effectif_reel": tranche_label(code),
                    "type_signal_cheval": "Dirigeant(e) d'un élevage équin (NAF 01.43Z) — propriétaire de chevaux",
                    "preuve": f"Fiche entreprise recherche-entreprises.api.gouv.fr (SIREN {r.get('siren','')})",
                    "source_url": f"https://annuaire-entreprises.data.gouv.fr/entreprise/{r.get('siren','')}",
                })
        time.sleep(0.2)
    return candidats
