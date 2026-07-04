"""CLI EquiProspect.

Exemples :
  python -m equiprospect queries                      # M1 : requêtes X-ray à coller dans Google
  python -m equiprospect classify --heuristique       # M2 : pré-tri hors-ligne (sans clé API)
  python -m equiprospect classify                     # M2 : classifieur Claude (1 appel/ligne)
  python -m equiprospect classify --batch             # M2 : Batches API (−50 %, gros volumes)
  python -m equiprospect classify --model claude-haiku-4-5 --batch   # lot économique
  python -m equiprospect score                        # M3 : calcule la colonne score
  python -m equiprospect top --n 20                   # M3 : top prospects chauds
  python -m equiprospect enrich                       # M4 : emails via Dropcontact (clé requise)

Le classifieur lit data/prospects.csv et travaille sur le texte disponible
(colonnes preuve + type_signal_cheval + poste). Pour classifier du texte de
profil complet, ajoutez une colonne `texte_profil` (scraping LinkedIn en aval).
"""

from __future__ import annotations

import argparse
import sys

from . import export, scoring, xray
from .export import CHEMIN_BASE


def _texte_ligne(ligne: dict) -> str:
    return " | ".join(
        filter(None, [ligne.get("texte_profil"), ligne.get("type_signal_cheval"),
                      ligne.get("preuve"), ligne.get("poste"), ligne.get("entreprise")])
    )


def cmd_queries(args) -> None:
    for r in xray.generer_requetes(args.n):
        print(r)


def cmd_classify(args) -> None:
    from . import classifier

    lignes = export.charger()
    if args.heuristique:
        for ligne in lignes:
            resultat = classifier.classifier_heuristique(_texte_ligne(ligne))
            _appliquer(ligne, resultat)
    elif args.batch:
        profils = {ligne["id"]: _texte_ligne(ligne) for ligne in lignes}
        resultats = classifier.classifier_llm_batch(profils, modele=args.model)
        for ligne in lignes:
            if ligne["id"] in resultats:
                _appliquer(ligne, resultats[ligne["id"]])
    else:
        for i, ligne in enumerate(lignes, 1):
            print(f"[{i}/{len(lignes)}] {ligne['nom']}")
            resultat = classifier.classifier_llm(_texte_ligne(ligne), modele=args.model)
            _appliquer(ligne, resultat)
    export.sauvegarder(lignes, CHEMIN_BASE)
    oui = sum(1 for l in lignes if l.get("llm_cavalier") == "oui")
    print(f"OK — {len(lignes)} lignes classifiées ({oui} 'oui') → {CHEMIN_BASE}")


def _appliquer(ligne: dict, resultat: dict) -> None:
    ligne["llm_cavalier"] = resultat["cavalier"]
    ligne["llm_type_signal"] = resultat["type_signal"]
    ligne["llm_indice"] = resultat["indice"]
    ligne["llm_confiance"] = str(resultat["confiance"])


def cmd_score(args) -> None:
    lignes = export.charger()
    for ligne in lignes:
        type_signal = ligne.get("llm_type_signal") or scoring.type_signal_depuis_base(
            ligne.get("type_signal_cheval", ""), ligne.get("niveau_preuve", "")
        )
        # on garde la meilleure confiance : vérification manuelle vs classifieur
        confiance = max(
            float(ligne.get("llm_confiance") or 0),
            float(ligne.get("confiance_0_100") or 0),
        )
        ligne["score"] = str(scoring.calculer_score(ligne.get("poste", ""), type_signal, confiance))
    export.sauvegarder(lignes, CHEMIN_BASE)
    print(f"OK — scores calculés → {CHEMIN_BASE}")


def cmd_top(args) -> None:
    lignes = export.charger()
    if not any(l.get("score") for l in lignes):
        print("Pas de colonne score — lancez d'abord : python -m equiprospect score")
        sys.exit(1)
    for ligne in export.top_prospects(lignes, args.n):
        print(f"{ligne['score']:>5}  {ligne['nom']:<28} {ligne['poste'][:38]:<40} {ligne.get('entreprise','')[:30]}")


def cmd_enrich(args) -> None:
    from . import enrich

    lignes = export.charger()
    cibles = [l for l in lignes if not l.get("email")][: args.n]
    personnes = []
    for ligne in cibles:
        morceaux = ligne["nom"].split(" ", 1)
        personnes.append({
            "first_name": morceaux[0],
            "last_name": morceaux[1] if len(morceaux) > 1 else "",
            "company": ligne.get("entreprise", ""),
        })
    enrichis = enrich.enrichir_dropcontact(personnes)
    for ligne, res in zip(cibles, enrichis):
        emails = res.get("email") or []
        if emails:
            ligne["email"] = emails[0].get("email", "")
    export.sauvegarder(lignes, CHEMIN_BASE)
    print(f"OK — {sum(1 for l in cibles if l.get('email'))} emails trouvés → {CHEMIN_BASE}")


def main() -> None:
    p = argparse.ArgumentParser(prog="equiprospect", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("queries", help="M1 : génère les requêtes X-ray")
    q.add_argument("-n", type=int, default=None, help="limite du nombre de requêtes")
    q.set_defaults(func=cmd_queries)

    c = sub.add_parser("classify", help="M2 : classifie le signal cavalier")
    c.add_argument("--heuristique", action="store_true", help="mots-clés hors-ligne (sans clé API)")
    c.add_argument("--batch", action="store_true", help="Batches API Claude (−50 %%)")
    c.add_argument("--model", default="claude-opus-4-8",
                   help="modèle Claude (claude-haiku-4-5 pour gros lots économiques)")
    c.set_defaults(func=cmd_classify)

    s = sub.add_parser("score", help="M3 : calcule les scores")
    s.set_defaults(func=cmd_score)

    t = sub.add_parser("top", help="M3 : affiche les prospects les plus chauds")
    t.add_argument("--n", type=int, default=20)
    t.set_defaults(func=cmd_top)

    e = sub.add_parser("enrich", help="M4 : emails pro via Dropcontact")
    e.add_argument("--n", type=int, default=50, help="nb max de lignes à enrichir")
    e.set_defaults(func=cmd_enrich)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
