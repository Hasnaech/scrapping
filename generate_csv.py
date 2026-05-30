"""
Generates bailleurs_contacts.csv from all data collected via web search.
Run: python generate_csv.py
"""

import csv

FIELDNAMES = [
    "type", "nom_organisme", "ville", "departement", "site_web",
    "nom_contact", "prenom_contact", "poste", "email", "telephone",
    "source_url",
]

# ─────────────────────────────────────────────────────────────────────────────
# DATA collected via web search (May 2026)
# Each entry: (type, nom, ville, dept, site, contacts)
# contacts: list of (nom_complet, poste, email, tel)
# ─────────────────────────────────────────────────────────────────────────────
DATA = [
    # ── OPH ──────────────────────────────────────────────────────────────────
    ("OPH", "Paris Habitat OPH", "Paris", "75", "https://www.parishabitat.fr", [
        ("Cécile Belard du Plantys", "Directeur Général", "", ""),
        ("Christophe Argoud", "DRH", "", ""),
    ]),
    ("OPH", "Seine-Saint-Denis Habitat", "Bobigny", "93", "https://www.seinesaintdenishabitat.fr", [
        ("Bertrand Prade", "Directeur Général", "", ""),
    ]),
    ("OPH", "Val d'Oise Habitat", "Cergy", "95", "https://www.valdoisehabitat.fr", [
        ("Séverine Leplus", "Directeur Général", "", ""),
    ]),
    ("OPH", "Plaine Commune Habitat", "Saint-Denis", "93", "https://www.plainecommunehabitat.fr", [
        ("Olivier Rougier", "Directeur Général", "", ""),
    ]),
    ("OPH", "Valophis Habitat", "Créteil", "94", "https://www.groupevalophis.fr", [
        ("Christian Harcouët", "Directeur Général (intérimaire)", "", ""),
    ]),
    ("OPH", "Hauts-de-Seine Habitat", "Nanterre", "92", "https://www.hautsdeseinehabitat.fr", [
        ("Yann Chevalier", "Directeur Général", "", ""),
    ]),
    ("OPH", "Essonne Habitat", "Ris-Orangis", "91", "https://www.essonne-habitat.fr", [
        ("Céline Lanctuit", "Directeur Général", "", ""),
    ]),
    ("OPH", "Versailles Habitat", "Versailles", "78", "https://versailles-habitat.fr", [
        ("Éric Le Coz", "Directeur Général", "", ""),
    ]),
    ("OPH", "Oise Habitat", "Creil", "60", "https://oisehabitat.fr", [
        ("Benjamin André", "Directeur Général", "", ""),
    ]),
    ("OPH", "Lyon Métropole Habitat", "Lyon", "69", "https://www.lmhabitat.fr", [
        ("Vincent Cristia", "Directeur Général", "", ""),
        ("Isabelle Scapin", "DRH", "", ""),
    ]),
    ("OPH", "Deux Fleuves Rhône Habitat (ex OPAC du Rhône)", "Lyon", "69", "https://www.rhonehabitat.fr", [
        ("Guillaume Rio", "Directeur Général", "", ""),
    ]),
    ("OPH", "Grenoble Alpes Métropole Habitat", "Grenoble", "38", "https://www.grenoble-habitat.fr", []),
    ("OPH", "Alpes Isère Habitat", "Grenoble", "38", "https://alpeshabitat.fr", [
        ("Laurent Droulez", "Directeur Général", "", ""),
        ("Cécile May", "Responsable Formation", "", ""),
    ]),
    ("OPH", "OPAC Savoie", "Chambéry", "73", "https://www.opac-savoie.fr", [
        ("David Jonnard", "Directeur Général", "", ""),
    ]),
    ("OPH", "Toulouse Métropole Habitat", "Toulouse", "31", "https://www.toulouse-metropole-habitat.fr", [
        ("Luc Laventure", "Directeur Général", "", ""),
    ]),
    ("OPH", "Marseille Habitat", "Marseille", "13", "https://www.marseillehabitat.fr", [
        ("Frédéric Pâris", "Directeur Général", "", ""),
    ]),
    ("OPH", "Provence Métropole Logement (ex Habitat Marseille Provence)", "Marseille", "13", "https://www.habitat-marseille-provence.fr", [
        ("Jean-Bernard Dambier", "Directeur Général", "", ""),
    ]),
    ("OPH", "Var Habitat", "Toulon", "83", "https://www.varhabitat.com", [
        ("Martial Aubry", "Directeur Général", "", ""),
    ]),
    ("OPH", "Gironde Habitat", "Bordeaux", "33", "https://www.gironde-habitat.fr", [
        ("Sigrid Monnier", "Directeur Général", "", ""),
    ]),
    ("OPH", "Aquitanis (OPH Bordeaux Métropole)", "Bordeaux", "33", "https://www.aquitanis.fr", [
        ("Jean-Luc Gorce", "Directeur Général", "", ""),
    ]),
    ("OPH", "Vendée Habitat", "La Roche-sur-Yon", "85", "https://www.vendeehabitat.fr", [
        ("Laurent Saussaye", "Directeur Général", "", ""),
    ]),
    ("OPH", "Angers Loire Habitat", "Angers", "49", "https://www.angers-loire-habitat.fr", [
        ("Laurent Bordas", "Directeur Général", "", ""),
    ]),
    ("OPH", "Archipel Habitat (OPH Rennes Métropole)", "Rennes", "35", "https://www.archipel-habitat.fr", [
        ("Antoine Rousseau", "Directeur Général", "", ""),
    ]),
    ("OPH", "Partenord Habitat", "Villeneuve d'Ascq", "59", "https://www.partenordhabitat.fr", [
        ("Eric Cojon", "Directeur Général", "", ""),
        ("Matthieu Canda", "DRH", "", ""),
    ]),
    ("OPH", "Lille Métropole Habitat", "Lille", "59", "https://www.lmh.fr", [
        ("Emilie Lainard (Hakme)", "Directeur Général", "", ""),
    ]),
    ("OPH", "Pas-de-Calais Habitat", "Arras", "62", "https://www.pasdecalais-habitat.fr", [
        ("Bruno Fontalirand", "Directeur Général", "", ""),
    ]),
    ("OPH", "Habitat 76", "Rouen", "76", "https://habitat76.fr", [
        ("Eric Gimer", "Directeur Général", "", ""),
    ]),
    ("OPH", "Inolya (OPH Calvados)", "Caen", "14", "https://www.inolya.fr", [
        ("Christophe Bureau", "Directeur Général", "", ""),
    ]),
    ("OPH", "Meurthe-et-Moselle Habitat (MMH)", "Nancy", "54", "https://www.mmhabitat.fr", [
        ("Audrey Dony", "Directeur Général", "", ""),
    ]),
    ("OPH", "Vosgelis", "Épinal", "88", "https://www.vosgelis.fr", [
        ("Fabrice Barbe", "Directeur Général", "", ""),
        ("Lorinda Carreiras", "DRH", "", ""),
    ]),
    ("OPH", "Orvitis", "Dijon", "21", "https://www.orvitis.fr", [
        ("Christophe Bérion", "Directeur Général", "", ""),
        ("Josiane Corte", "DRH", "", ""),
    ]),
    ("OPH", "Dynacité", "Oyonnax", "01", "https://www.dynacite.fr", [
        ("Jean-Luc Triollet", "Directeur Général", "", ""),
        ("Nathalie Marotta", "DRH", "", ""),
    ]),
    ("OPH", "Allier Habitat", "Moulins", "03", "https://www.allier-habitat.fr", [
        ("Laurent Cot", "Directeur Général", "", ""),
    ]),
    ("OPH", "Hérault Logement", "Montpellier", "34", "https://www.herault-logement.fr", [
        ("Gilles Dupont", "Directeur Général", "", ""),
    ]),
    ("OPH", "Nantes Métropole Habitat", "Nantes", "44", "https://www.nmh.fr", []),
    ("OPH", "Saône-et-Loire Habitat", "Mâcon", "71", "https://www.sl-habitat.fr", []),
    ("OPH", "Yvelines Habitat", "Versailles", "78", "https://www.yvelineshabitat.fr", []),
    ("OPH", "Seine-et-Marne Habitat", "Dammarie-les-Lys", "77", "https://www.seineetmarnehabitat.fr", []),
    ("OPH", "Côte-d'Or Habitat", "Dijon", "21", "https://www.cotedorhabitat.fr", []),
    ("OPH", "Haute-Loire Habitat", "Le Puy-en-Velay", "43", "https://www.hauteloirehabitat.fr", []),
    ("OPH", "Puy-de-Dôme Habitat", "Clermont-Ferrand", "63", "https://www.puy-de-dome-habitat.fr", []),
    ("OPH", "Moselle Habitat", "Metz", "57", "https://www.mosellehabitat.fr", []),
    ("OPH", "Bas-Rhin Habitat", "Strasbourg", "67", "https://www.basrhinhabitat.fr", []),
    ("OPH", "Alsace Habitat", "Strasbourg", "67", "https://www.alsacehabitat.fr", []),
    ("OPH", "Nord Habitat", "Lille", "59", "https://www.nordhabitat.fr", []),
    ("OPH", "Côtes d'Armor Habitat", "Saint-Brieuc", "22", "https://www.cotesdarmor-habitat.fr", []),
    ("OPH", "Manche Habitat", "Saint-Lô", "50", "https://www.manchehabitat.fr", []),
    ("OPH", "Bretagne Sud Habitat / Morbihan Habitat", "Vannes", "56", "https://www.bretagne-sud-habitat.fr", []),
    ("OPH", "Bourgogne Habitat", "Dijon", "21", "https://www.bourgognehabitat.fr", []),
    ("OPH", "Habitat 13", "Marseille", "13", "https://www.habitat13.fr", []),
    ("OPH", "Nice Habitat", "Nice", "06", "https://www.nicehabitat.fr", []),
    ("OPH", "Deux Fleuves Loire Habitat (ex Loire Habitat)", "Saint-Étienne", "42", "https://www.rhonehabitat.fr", []),
    # ── ESH ──────────────────────────────────────────────────────────────────
    ("ESH", "Immobilière 3F", "Paris", "75", "https://www.groupe3f.fr", [
        ("Valérie Fournier", "Directeur Général", "", ""),
        ("Valérie Chung-Coquillet", "DRH", "", ""),
    ]),
    ("ESH", "ICF Habitat", "Paris", "75", "https://www.icfhabitat.fr", [
        ("Romain Dubois", "Directeur Général", "", ""),
        ("Valérie Bignon", "DRH", "", ""),
    ]),
    ("ESH", "RIVP", "Paris", "75", "https://www.rivp.fr", [
        ("Christine Laconde", "Directeur Général", "", ""),
    ]),
    ("ESH", "Efidis", "Paris", "75", "https://www.efidis.fr", []),
    ("ESH", "Domaxis", "Paris", "75", "https://www.domaxis.fr", [
        ("Bruno Hoang", "Directeur Général Adjoint", "", ""),
        ("Marie-Claude Gauthier", "DRH", "", ""),
    ]),
    ("ESH", "Vilogia", "Villeneuve d'Ascq", "59", "https://www.vilogia.fr", [
        ("Philippe Rémignon", "Président Directoire", "", ""),
    ]),
    ("ESH", "Habitat du Nord", "Villeneuve d'Ascq", "59", "https://www.habitatdunord.fr", [
        ("Franck Porier", "Président Directoire", "", ""),
    ]),
    ("ESH", "Partenord Habitat", "Villeneuve d'Ascq", "59", "https://www.partenord-legroupe.fr", []),
    ("ESH", "Batigère", "Metz", "57", "https://www.batigere.fr", [
        ("Jean-François Prevot", "Directeur Général Groupe", "", ""),
        ("Nathalie Mateos-Jorge", "Directeur Général Adjoint Groupe", "", ""),
        ("Sébastien Tilignac", "Directeur Général Batigère Grand Est", "", ""),
    ]),
    ("ESH", "Néolia", "Besançon", "25", "https://www.neolia.fr", [
        ("Jacques Ferrand", "Directeur Général", "", ""),
    ]),
    ("ESH", "Alliade Habitat", "Lyon", "69", "https://alliadehabitat.com", [
        ("Sofia Kada", "RH Business Partner", "", ""),
    ]),
    ("ESH", "Semcoda", "Bourg-en-Bresse", "01", "https://www.semcoda.com", [
        ("Bernard Perret", "Directeur Général", "", ""),
    ]),
    ("ESH", "Dynacité (ESH)", "Oyonnax", "01", "https://www.dynacite.fr", []),
    ("ESH", "Erilia", "Marseille", "13", "https://www.erilia.fr", [
        ("Frédéric Lavergne", "Directeur Général", "", ""),
        ("Fabienne Abecassis", "Directeur Général Délégué", "", ""),
        ("Antoine Jeandet", "Directeur Général Délégué", "", ""),
    ]),
    ("ESH", "Logirem", "Marseille", "13", "https://www.logirem.fr", [
        ("Fabienne Abecassis", "Directeur Général", "", ""),
        ("Frank Nicol", "Directeur Général Délégué", "", ""),
    ]),
    ("ESH", "Espacil Habitat", "Rennes", "35", "https://www.espacil-habitat.fr", [
        ("Julia Lagadec", "Directeur Général", "", ""),
    ]),
    ("ESH", "Aiguillon Construction", "Rennes", "35", "https://www.aiguillon-construction.fr", [
        ("Thierry Heyvang", "Directeur Général", "", ""),
        ("Thomas Duke", "Directeur Général Délégué", "", ""),
    ]),
    ("ESH", "Harmonie Habitat", "Saint-Herblain", "44", "https://www.harmoniehabitat.org", [
        ("Fabienne Delcambre", "Directeur Général", "", ""),
        ("Helena Riand", "Directeur Général Adjoint – Ressources", "", ""),
    ]),
    ("ESH", "Clairsienne", "Bordeaux", "33", "https://www.clairsienne.com", []),
    ("ESH", "Nouveau Logis", "Bordeaux", "33", "https://www.nouveaulogis.fr", []),
    ("ESH", "Vosgelis ESH", "Épinal", "88", "https://www.vosgelis.fr", []),
    ("ESH", "SCIC Habitat", "Paris", "75", "https://www.scic-habitat.fr", []),
    ("ESH", "France Habitation", "Paris", "75", "https://www.france-habitation.fr", []),
    ("ESH", "OGIF", "Paris", "75", "https://www.ogif.fr", []),
    ("ESH", "Orvitis ESH", "Dijon", "21", "https://www.orvitis.fr", []),
    ("ESH", "Logi-Ouest", "Brest", "29", "https://www.logiouest.fr", []),
    ("ESH", "Vendée Habitat ESH", "La Roche-sur-Yon", "85", "https://www.vendeehabitat.fr", []),
    ("ESH", "Sarthe Habitat", "Le Mans", "72", "https://www.sarthehabitat.fr", []),
    ("ESH", "Picardie Habitat", "Amiens", "80", "https://www.picardiehabitat.fr", []),
    ("ESH", "Aisne Habitat", "Laon", "02", "https://www.aisnehabitat.fr", []),
    ("ESH", "Habitat 62/59 Picardie", "Arras", "62", "https://www.habitat6259picardie.fr", []),
    ("ESH", "Néodyme", "Amiens", "80", "https://www.neodyme.org", []),
    ("ESH", "Habitat 80", "Amiens", "80", "https://www.habitat80.fr", []),
    ("ESH", "Haute-Saône Habitat", "Vesoul", "70", "https://www.hsh70.fr", []),
    ("ESH", "Nièvre Habitat", "Nevers", "58", "https://www.nievre-habitat.com", []),
    ("ESH", "Cher Habitat", "Bourges", "18", "https://www.cherhabitat.fr", []),
    ("ESH", "Indre Habitat", "Châteauroux", "36", "https://www.indrehabitat.fr", []),
    ("ESH", "Loir-et-Cher Habitat", "Blois", "41", "https://www.lchabitat.fr", []),
    ("ESH", "Loiret Habitat", "Orléans", "45", "https://www.loirethabitat.fr", []),
    ("ESH", "Eure-et-Loir Habitat", "Chartres", "28", "https://www.euretloir-habitat.fr", []),
    ("ESH", "Héritage et Traditions Habitat", "Lyon", "69", "https://www.ht-habitat.fr", []),
]


def split_name(full: str):
    parts = full.strip().split(" ", 1)
    return (parts[1], parts[0]) if len(parts) == 2 else (full, "")


def build_rows():
    rows = []
    for entry in DATA:
        type_, nom, ville, dept, site, contacts = entry
        base = {
            "type": type_,
            "nom_organisme": nom,
            "ville": ville,
            "departement": dept,
            "site_web": site,
            "source_url": "",
        }
        if contacts:
            for full_name, poste, email, tel in contacts:
                prenom, nom_fam = split_name(full_name)
                rows.append({
                    **base,
                    "nom_contact": nom_fam,
                    "prenom_contact": prenom,
                    "poste": poste,
                    "email": email,
                    "telephone": tel,
                })
        else:
            rows.append({
                **base,
                "nom_contact": "",
                "prenom_contact": "",
                "poste": "",
                "email": "",
                "telephone": "",
            })
    return rows


def main():
    rows = build_rows()
    path = "bailleurs_contacts.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    total_orgs = len(DATA)
    total_contacts = sum(len(e[5]) for e in DATA)
    print(f"✓ {path} – {total_orgs} organismes, {total_contacts} contacts")

    # Also write xlsx if openpyxl available
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Bailleurs"
        # Header style
        from openpyxl.styles import Font, PatternFill, Alignment
        header_fill = PatternFill("solid", fgColor="1F4E79")
        header_font = Font(color="FFFFFF", bold=True)
        ws.append(FIELDNAMES)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        for row in rows:
            ws.append([row.get(f, "") for f in FIELDNAMES])
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=0)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)
        xlsx_path = "bailleurs_contacts.xlsx"
        wb.save(xlsx_path)
        print(f"✓ {xlsx_path}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
