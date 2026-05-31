"""
Generates bailleurs_contacts.csv from all data collected via web search.
Run: python generate_csv.py
"""

import csv

FIELDNAMES = [
    "type", "nom_organisme", "ville", "departement", "site_web",
    "nom_contact", "prenom_contact", "poste", "email", "telephone",
    "telephone_mobile", "linkedin_url", "source_url",
]

# ─────────────────────────────────────────────────────────────────────────────
# DATA collected via web search (May 2026)
# Each entry: (type, nom, ville, dept, site, contacts)
# contacts: list of (nom_complet, poste, email, tel, linkedin_url)
# ─────────────────────────────────────────────────────────────────────────────
DATA = [
    # ── OPH ──────────────────────────────────────────────────────────────────
    ("OPH", "Paris Habitat OPH", "Paris", "75", "https://www.parishabitat.fr", [
        ("Cécile Belard du Plantys", "Directeur Général", "", "", "", "https://fr.linkedin.com/posts/paris-habitat_cécile-belard-du-plantys-nouvelle-directrice-activity-6900366200384159744-f5z2"),
        ("Christophe Argoud", "DRH", "", "", "06 46 19 07 56", "https://fr.linkedin.com/in/christopheargouddrh"),
    ]),
    ("OPH", "Seine-Saint-Denis Habitat", "Bobigny", "93", "https://www.seinesaintdenishabitat.fr", [
        ("Bertrand Prade", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Val d'Oise Habitat", "Cergy", "95", "https://www.valdoisehabitat.fr", [
        ("Séverine Leplus", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/severine-leplus-095b0944"),
    ]),
    ("OPH", "Plaine Commune Habitat", "Saint-Denis", "93", "https://www.plainecommunehabitat.fr", [
        ("Olivier Rougier", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Valophis Habitat", "Créteil", "94", "https://www.groupevalophis.fr", [
        ("Christian Harcouët", "Directeur Général (intérimaire)", "", "", "", ""),
    ]),
    ("OPH", "Hauts-de-Seine Habitat", "Nanterre", "92", "https://www.hautsdeseinehabitat.fr", [
        ("Yann Chevalier", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Essonne Habitat", "Ris-Orangis", "91", "https://www.essonne-habitat.fr", [
        ("Céline Lanctuit", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Versailles Habitat", "Versailles", "78", "https://versailles-habitat.fr", [
        ("Éric Le Coz", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Oise Habitat", "Creil", "60", "https://oisehabitat.fr", [
        ("Benjamin André", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Lyon Métropole Habitat", "Lyon", "69", "https://www.lmhabitat.fr", [
        ("Vincent Cristia", "Directeur Général", "", "", "", ""),
        ("Isabelle Scapin", "DRH", "", "", "", "https://fr.linkedin.com/in/isabelle-scapin-28964265"),
    ]),
    ("OPH", "Deux Fleuves Rhône Habitat (ex OPAC du Rhône)", "Lyon", "69", "https://www.rhonehabitat.fr", [
        ("Guillaume Rio", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Alpes Isère Habitat", "Grenoble", "38", "https://alpeshabitat.fr", [
        ("Laurent Droulez", "Directeur Général", "", "", "", ""),
        ("Cécile May", "Responsable Formation", "", "", "", "https://www.linkedin.com/in/c%C3%A9cile-may-84b57690/"),
    ]),
    ("OPH", "OPAC Savoie", "Chambéry", "73", "https://www.opac-savoie.fr", [
        ("David Jonnard", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Toulouse Métropole Habitat", "Toulouse", "31", "https://www.toulouse-metropole-habitat.fr", [
        ("Luc Laventure", "Directeur Général", "", "", "", "https://www.linkedin.com/in/luc-laventure-a16554195/"),
    ]),
    ("OPH", "Marseille Habitat", "Marseille", "13", "https://www.marseillehabitat.fr", [
        ("Frédéric Pâris", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Provence Métropole Logement (ex HMP)", "Marseille", "13", "https://www.habitat-marseille-provence.fr", [
        ("Jean-Bernard Dambier", "Directeur Général", "", "", "", "https://www.linkedin.com/in/jean-bernard-dambier-44536b148/"),
    ]),
    ("OPH", "Var Habitat", "Toulon", "83", "https://www.varhabitat.com", [
        ("Martial Aubry", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Gironde Habitat", "Bordeaux", "33", "https://www.gironde-habitat.fr", [
        ("Sigrid Monnier", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/sigrid-monnier-62b45a24"),
    ]),
    ("OPH", "Aquitanis (OPH Bordeaux Métropole)", "Bordeaux", "33", "https://www.aquitanis.fr", [
        ("Jean-Luc Gorce", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Vendée Habitat", "La Roche-sur-Yon", "85", "https://www.vendeehabitat.fr", [
        ("Laurent Saussaye", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/laurent-saussaye-86118513a"),
    ]),
    ("OPH", "Angers Loire Habitat", "Angers", "49", "https://www.angers-loire-habitat.fr", [
        ("Laurent Bordas", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Archipel Habitat (OPH Rennes Métropole)", "Rennes", "35", "https://www.archipel-habitat.fr", [
        ("Antoine Rousseau", "Directeur Général", "", "", "", "https://rocketreach.co/antoine-rousseau-email_67702980"),
    ]),
    ("OPH", "Partenord Habitat", "Villeneuve d'Ascq", "59", "https://www.partenordhabitat.fr", [
        ("Eric Cojon", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/eric-cojon-95a382181"),
        ("Matthieu Canda", "DRH", "", "", "", "https://www.linkedin.com/in/matthieu-canda-4aa78853/"),
    ]),
    ("OPH", "Lille Métropole Habitat", "Lille", "59", "https://www.lmh.fr", [
        ("Emilie Lainard (Hakme)", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Pas-de-Calais Habitat", "Arras", "62", "https://www.pasdecalais-habitat.fr", [
        ("Bruno Fontalirand", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Habitat 76", "Rouen", "76", "https://habitat76.fr", [
        ("Eric Gimer", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Inolya (OPH Calvados)", "Caen", "14", "https://www.inolya.fr", [
        ("Christophe Bureau", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Meurthe-et-Moselle Habitat (MMH)", "Nancy", "54", "https://www.mmhabitat.fr", [
        ("Audrey Dony", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Vosgelis", "Épinal", "88", "https://www.vosgelis.fr", [
        ("Fabrice Barbe", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/fabrice-barbe"),
        ("Lorinda Carreiras", "DRH", "", "", "", ""),
    ]),
    ("OPH", "Orvitis", "Dijon", "21", "https://www.orvitis.fr", [
        ("Christophe Bérion", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/christophe-berion-76611558"),
        ("Josiane Corte", "DRH", "", "", "", "https://www.linkedin.com/in/josiane-corte-87108090"),
    ]),
    ("OPH", "Dynacité", "Oyonnax", "01", "https://www.dynacite.fr", [
        ("Jean-Luc Triollet", "Directeur Général", "", "", "", ""),
        ("Nathalie Marotta", "DRH", "", "", "", ""),
    ]),
    ("OPH", "Allier Habitat", "Moulins", "03", "https://www.allier-habitat.fr", [
        ("Laurent Cot", "Directeur Général", "", "", "", ""),
    ]),
    ("OPH", "Hérault Logement", "Montpellier", "34", "https://www.herault-logement.fr", [
        ("Gilles Dupont", "Directeur Général", "", "", "", ""),
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
    ("OPH", "Morbihan Habitat (ex Bretagne Sud Habitat)", "Vannes", "56", "https://www.morbihan-habitat.fr", []),
    ("OPH", "Bourgogne Habitat", "Dijon", "21", "https://www.bourgognehabitat.fr", []),
    ("OPH", "Habitat 13", "Marseille", "13", "https://www.habitat13.fr", []),
    ("OPH", "Nice Habitat", "Nice", "06", "https://www.nicehabitat.fr", []),
    ("OPH", "Deux Fleuves Loire Habitat (ex Loire Habitat)", "Saint-Étienne", "42", "https://www.deuxfleuvesloirehabitat.fr", []),
    # ── ESH ──────────────────────────────────────────────────────────────────
    ("ESH", "Immobilière 3F", "Paris", "75", "https://www.groupe3f.fr", [
        ("Valérie Fournier", "Directeur Général", "", "", "", ""),
        ("Valérie Chung-Coquillet", "DRH", "", "", "", "https://www.linkedin.com/in/val%C3%A9rie-chung-coquillet-2b2500121/"),
    ]),
    ("ESH", "ICF Habitat", "Paris", "75", "https://www.icfhabitat.fr", [
        ("Romain Dubois", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/romain-dubois-26964521"),
        ("Valérie Bignon", "DRH", "", "", "", "https://fr.linkedin.com/in/val%C3%A9rie-bignon-86ab9330"),
    ]),
    ("ESH", "RIVP", "Paris", "75", "https://www.rivp.fr", [
        ("Christine Laconde", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/christine-laconde-4452a0269"),
    ]),
    ("ESH", "Efidis (CDC Habitat Social)", "Paris", "75", "https://www.efidis.fr", []),
    ("ESH", "Domaxis", "Paris", "75", "https://www.domaxis.fr", [
        ("Bruno Hoang", "Directeur Général Adjoint", "", "", "", ""),
        ("Marie-Claude Gauthier", "DRH", "", "", "", "https://fr.linkedin.com/in/marie-claude-gauthier-03091436"),
    ]),
    ("ESH", "Vilogia", "Villeneuve d'Ascq", "59", "https://www.vilogia.fr", [
        ("Philippe Rémignon", "Président Directoire", "", "", "", ""),
    ]),
    ("ESH", "Habitat du Nord", "Villeneuve d'Ascq", "59", "https://www.habitatdunord.fr", [
        ("Franck Porier", "Président Directoire", "", "", "", ""),
    ]),
    ("ESH", "Batigère", "Metz", "57", "https://www.batigere.fr", [
        ("Jean-François Prevot", "Directeur Général Groupe", "", "", "", ""),
        ("Nathalie Mateos-Jorge", "Directeur Général Adjoint Groupe", "", "", "", ""),
        ("Sébastien Tilignac", "Directeur Général Batigère Grand Est", "", "", "", ""),
    ]),
    ("ESH", "Néolia", "Besançon", "25", "https://www.neolia.fr", [
        ("Jacques Ferrand", "Directeur Général", "", "", "", ""),
    ]),
    ("ESH", "Alliade Habitat", "Lyon", "69", "https://alliadehabitat.com", []),
    ("ESH", "Semcoda", "Bourg-en-Bresse", "01", "https://www.semcoda.com", [
        ("Bernard Perret", "Directeur Général", "", "", "", "https://www.linkedin.com/in/bernard-perret-729057263/"),
    ]),
    ("ESH", "Erilia", "Marseille", "13", "https://www.erilia.fr", [
        ("Frédéric Lavergne", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/fr%C3%A9d%C3%A9ric-lavergne-5617508"),
        ("Fabienne Abecassis", "Directeur Général Délégué", "", "", "", "https://fr.linkedin.com/in/fabienne-abecassis-34b01830"),
        ("Antoine Jeandet", "Directeur Général Délégué", "", "", "", ""),
    ]),
    ("ESH", "Logirem", "Marseille", "13", "https://www.logirem.fr", [
        ("Fabienne Abecassis", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/fabienne-abecassis-34b01830"),
        ("Frank Nicol", "Directeur Général Délégué", "", "", "", ""),
    ]),
    ("ESH", "Espacil Habitat", "Rennes", "35", "https://www.espacil-habitat.fr", [
        ("Julia Lagadec", "Directeur Général", "", "", "", ""),
    ]),
    ("ESH", "Aiguillon Construction", "Rennes", "35", "https://www.aiguillon-construction.fr", [
        ("Thierry Heyvang", "Directeur Général", "", "", "", "https://www.linkedin.com/in/thierry-heyvang-b952bb26/"),
        ("Thomas Duke", "Directeur Général Délégué", "", "", "", ""),
    ]),
    ("ESH", "Harmonie Habitat", "Saint-Herblain", "44", "https://www.harmoniehabitat.org", [
        ("Fabienne Delcambre", "Directeur Général", "", "", "", "https://fr.linkedin.com/in/fabienne-delcambre-38aab8145"),
        ("Helena Riand", "Directeur Général Adjoint – Ressources", "", "", "", ""),
    ]),
    ("ESH", "Clairsienne", "Bordeaux", "33", "https://www.clairsienne.com", []),
    ("ESH", "Nouveau Logis", "Bordeaux", "33", "https://www.nouveaulogis.fr", []),
    ("ESH", "SCIC Habitat", "Paris", "75", "https://www.scic-habitat.fr", []),
    ("ESH", "France Habitation", "Paris", "75", "https://www.france-habitation.fr", []),
    ("ESH", "OGIF", "Paris", "75", "https://www.ogif.fr", []),
    ("ESH", "Logi-Ouest", "Brest", "29", "https://www.logiouest.fr", []),
    ("ESH", "Sarthe Habitat", "Le Mans", "72", "https://www.sarthehabitat.fr", []),
    ("ESH", "Picardie Habitat", "Amiens", "80", "https://www.picardiehabitat.fr", []),
    ("ESH", "Aisne Habitat", "Laon", "02", "https://www.aisnehabitat.fr", []),
    ("ESH", "Habitat 62/59 Picardie", "Arras", "62", "https://www.habitat6259picardie.fr", []),
    ("ESH", "Néodyme", "Amiens", "80", "https://www.neodyme.org", []),
    ("ESH", "Haute-Saône Habitat", "Vesoul", "70", "https://www.hsh70.fr", []),
    ("ESH", "Nièvre Habitat", "Nevers", "58", "https://www.nievre-habitat.com", []),
    ("ESH", "Cher Habitat", "Bourges", "18", "https://www.cherhabitat.fr", []),
    ("ESH", "Indre Habitat", "Châteauroux", "36", "https://www.indrehabitat.fr", []),
    ("ESH", "Loir-et-Cher Habitat", "Blois", "41", "https://www.lchabitat.fr", []),
    ("ESH", "Loiret Habitat", "Orléans", "45", "https://www.loirethabitat.fr", []),
    ("ESH", "Eure-et-Loir Habitat", "Chartres", "28", "https://www.euretloir-habitat.fr", []),
    ("ESH", "Héritage et Traditions Habitat", "Lyon", "69", "https://www.ht-habitat.fr", []),
    ("ESH", "Habitat 80", "Amiens", "80", "https://www.habitat80.fr", []),
    ("ESH", "Haute-Saône Habitat", "Vesoul", "70", "https://www.hsh70.fr", []),
]


def split_name(full: str):
    parts = full.strip().split(" ", 1)
    return (parts[1], parts[0]) if len(parts) == 2 else (full, "")


def build_rows():
    rows = []
    seen_orgs = set()
    for entry in DATA:
        type_, nom, ville, dept, site, contacts = entry
        # Deduplicate org rows with no contacts
        base = {
            "type": type_,
            "nom_organisme": nom,
            "ville": ville,
            "departement": dept,
            "site_web": site,
            "source_url": "",
        }
        if contacts:
            for contact_tuple in contacts:
                full_name, poste, email, tel, mobile, linkedin = contact_tuple
                prenom, nom_fam = split_name(full_name)
                rows.append({
                    **base,
                    "nom_contact": nom_fam,
                    "prenom_contact": prenom,
                    "poste": poste,
                    "email": email,
                    "telephone": tel,
                    "telephone_mobile": mobile,
                    "linkedin_url": linkedin,
                })
        else:
            key = (type_, nom)
            if key not in seen_orgs:
                seen_orgs.add(key)
                rows.append({
                    **base,
                    "nom_contact": "",
                    "prenom_contact": "",
                    "poste": "",
                    "email": "",
                    "telephone": "",
                    "telephone_mobile": "",
                    "linkedin_url": "",
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
    with_linkedin = sum(1 for r in rows if r.get("linkedin_url"))
    print(f"✓ {path} – {total_orgs} organismes, {total_contacts} contacts, {with_linkedin} profils LinkedIn")

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Bailleurs"
        header_fill = PatternFill("solid", fgColor="1F4E79")
        header_font = Font(color="FFFFFF", bold=True)
        ws.append(FIELDNAMES)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        for row in rows:
            ws.append([row.get(f, "") for f in FIELDNAMES])
        # Make LinkedIn URLs clickable
        for row_cells in ws.iter_rows(min_row=2):
            li_col = FIELDNAMES.index("linkedin_url")
            cell = row_cells[li_col]
            if cell.value:
                cell.hyperlink = cell.value
                cell.font = Font(color="0563C1", underline="single")
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=0)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 55)
        xlsx_path = "bailleurs_contacts.xlsx"
        wb.save(xlsx_path)
        print(f"✓ {xlsx_path}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
