"""
Scraper – Bailleurs sociaux France (OPH & ESH)
Cibles : Directeur Général, Responsable Formation, DRH, Responsable RH

Usage:
    # Avec ScrapeGraphAI (recommandé, nécessite une clé OpenAI ou Anthropic)
    OPENAI_API_KEY=sk-... python scrape_bailleurs.py

    # Sans clé API (scraping HTML classique)
    python scrape_bailleurs.py
"""

import os
import re
import csv
import time
import json
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ── optional deps ─────────────────────────────────────────────────────────────
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from scrapegraphai.graphs import SmartScraperGraph
    HAS_SCRAPEGRAPHAI = True
except ImportError:
    HAS_SCRAPEGRAPHAI = False

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scrape_bailleurs.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── config ────────────────────────────────────────────────────────────────────
OPENAI_KEY  = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OUTPUT_CSV  = "bailleurs_contacts.csv"
OUTPUT_XLSX = "bailleurs_contacts.xlsx"
DELAY       = 2          # seconds between requests
MAX_ORGS    = None       # set e.g. 20 for a quick test; None = all

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

FIELDNAMES = [
    "type", "nom_organisme", "ville", "departement", "site_web",
    "nom_contact", "prenom_contact", "poste", "email", "telephone",
    "source_url",
]

# Role keywords → normalized label
ROLE_MAP = {
    "Directeur Général": [
        "directeur général", "directrice générale",
        "directeur general", "directrice generale",
        "dg ", "pdg",
    ],
    "DRH": [
        "directeur des ressources humaines",
        "directrice des ressources humaines",
        "drh",
    ],
    "Responsable Formation": [
        "responsable de formation", "responsable formation",
        "chargé de formation", "chargée de formation",
        "responsable développement rh",
    ],
    "Responsable RH": [
        "responsable rh", "responsable des ressources humaines",
        "chargé rh", "chargée rh", "gestionnaire rh",
        "chargé de recrutement", "chargée de recrutement",
    ],
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+33\s?|0)[1-9](?:[\s.\-]?\d{2}){4}")

# ── known bailleur seed list (fallback if annuaire is unavailable) ─────────────
# Format: (type, nom, ville, site_web)
SEED_BAILLEURS = [
    # OPH
    ("OPH", "Paris Habitat OPH", "Paris", "https://www.parishabitat.fr"),
    ("OPH", "Opievoy", "Versailles", "https://www.opievoy.fr"),
    ("OPH", "Plaine Commune Habitat", "Saint-Denis", "https://www.plainecommunehabitat.fr"),
    ("OPH", "Seine-Saint-Denis Habitat", "Bobigny", "https://www.seine-saint-denis-habitat.fr"),
    ("OPH", "Val d'Oise Habitat", "Cergy", "https://www.valdoisehabitat.fr"),
    ("OPH", "Grand Paris Habitat", "Paris", "https://www.grandparishabitat.fr"),
    ("OPH", "OPAC du Rhône", "Lyon", "https://www.opac-du-rhone.fr"),
    ("OPH", "Lyon Métropole Habitat", "Lyon", "https://www.grandlyon-habitat.fr"),
    ("OPH", "Grenoble Alpes Habitat", "Grenoble", "https://www.grenoble-alpes-habitat.fr"),
    ("OPH", "Isère Habitat", "Grenoble", "https://www.isere-habitat.fr"),
    ("OPH", "OPAC de Savoie", "Aix-les-Bains", "https://www.opac-savoie.fr"),
    ("OPH", "Chambéry Alpes Habitat", "Chambéry", "https://www.chambery-alpes-habitat.fr"),
    ("OPH", "Allier Habitat", "Moulins", "https://www.allier-habitat.fr"),
    ("OPH", "Haute-Loire Habitat", "Le Puy-en-Velay", "https://www.hauteloirehabitat.fr"),
    ("OPH", "Puy-de-Dôme Habitat", "Clermont-Ferrand", "https://www.puy-de-dome-habitat.fr"),
    ("OPH", "Gironde Habitat", "Bordeaux", "https://www.gironde-habitat.fr"),
    ("OPH", "Bordeaux Métropole Habitat", "Bordeaux", "https://www.bordeaux-metropole-habitat.fr"),
    ("OPH", "Nantes Métropole Habitat", "Nantes", "https://www.nantesmetropolehabitat.fr"),
    ("OPH", "Toulouse Métropole Habitat", "Toulouse", "https://www.toulouse-metropole-habitat.fr"),
    ("OPH", "Marseille Habitat", "Marseille", "https://www.marseille-habitat.fr"),
    ("OPH", "Habitat 13", "Marseille", "https://www.habitat13.fr"),
    ("OPH", "Var Habitat", "Toulon", "https://www.varhabitat.fr"),
    ("OPH", "Nice Habitat", "Nice", "https://www.nicehabitat.fr"),
    ("OPH", "Montpellier Méditerranée Habitat", "Montpellier", "https://www.montpellier-mediterranee-habitat.fr"),
    ("OPH", "Hérault Habitat", "Montpellier", "https://www.herault-habitat.fr"),
    ("OPH", "Oise Habitat", "Beauvais", "https://www.oise-habitat.fr"),
    ("OPH", "Seine-et-Marne Habitat", "Dammarie-les-Lys", "https://www.seineetmarnehabitat.fr"),
    ("OPH", "Essonne Habitat", "Évry", "https://www.essonne-habitat.fr"),
    ("OPH", "Yvelines Habitat", "Versailles", "https://www.yvelineshabitat.fr"),
    ("OPH", "Hauts-de-Seine Habitat", "Nanterre", "https://www.92.fr"),
    ("OPH", "Val-de-Marne Habitat", "Créteil", "https://www.valdemarne-habitat.fr"),
    ("OPH", "Meurthe-et-Moselle Habitat", "Nancy", "https://www.meurthe-et-moselle-habitat.fr"),
    ("OPH", "Moselle Habitat", "Metz", "https://www.mosellehabitat.fr"),
    ("OPH", "Bas-Rhin Habitat", "Strasbourg", "https://www.basrhinhabitat.fr"),
    ("OPH", "Alsace Habitat", "Strasbourg", "https://www.alsacehabitat.fr"),
    ("OPH", "Nord-Pas-de-Calais Habitat", "Lille", "https://www.nordhabitat.fr"),
    ("OPH", "Lille Métropole Habitat", "Lille", "https://www.lillemetropolehabitat.fr"),
    ("OPH", "Pas-de-Calais Habitat", "Arras", "https://www.pasdecalaishabitat.fr"),
    ("OPH", "Normandie Habitat", "Rouen", "https://www.normandiehabitat.fr"),
    ("OPH", "Seine-Maritime Habitat", "Rouen", "https://www.seine-maritime-habitat.fr"),
    ("OPH", "Calvados Habitat", "Caen", "https://www.calvadoshabitat.fr"),
    ("OPH", "Manche Habitat", "Saint-Lô", "https://www.manchehabitat.fr"),
    ("OPH", "Bretagne Sud Habitat", "Vannes", "https://www.bsh56.fr"),
    ("OPH", "Côtes d'Armor Habitat", "Saint-Brieuc", "https://www.cotesdarmor-habitat.fr"),
    ("OPH", "Rennes Métropole Habitat", "Rennes", "https://www.rennesmh.fr"),
    ("OPH", "Nantes Métropole Habitat", "Nantes", "https://www.nantesmetropolehabitat.fr"),
    ("OPH", "Loire Habitat", "Saint-Étienne", "https://www.loirehabitat.fr"),
    ("OPH", "Saône-et-Loire Habitat", "Mâcon", "https://www.sl-habitat.fr"),
    ("OPH", "Bourgogne Habitat", "Dijon", "https://www.bourgognehabitat.fr"),
    ("OPH", "Côte-d'Or Habitat", "Dijon", "https://www.cotedorhabitat.fr"),
    # ESH
    ("ESH", "3F - Immobilière 3F", "Paris", "https://www.3f.fr"),
    ("ESH", "ICF Habitat", "Paris", "https://www.icf-habitat.fr"),
    ("ESH", "France Habitation", "Paris", "https://www.france-habitation.fr"),
    ("ESH", "RIVP", "Paris", "https://www.rivp.fr"),
    ("ESH", "Efidis", "Paris", "https://www.efidis.fr"),
    ("ESH", "OGIF", "Paris", "https://www.ogif.fr"),
    ("ESH", "Domaxis", "Paris", "https://www.domaxis.fr"),
    ("ESH", "Vilogia", "Villeneuve d'Ascq", "https://www.vilogia.fr"),
    ("ESH", "Valophis Habitat", "Créteil", "https://www.valophis.com"),
    ("ESH", "Batigère", "Metz", "https://www.batigere.fr"),
    ("ESH", "Habitat en Région", "Lyon", "https://www.habitatenregion.fr"),
    ("ESH", "Partenord Habitat", "Villeneuve d'Ascq", "https://www.partenord-habitat.fr"),
    ("ESH", "Habitat du Nord", "Villeneuve d'Ascq", "https://www.habitatdunord.fr"),
    ("ESH", "Logirem", "Marseille", "https://www.logirem.fr"),
    ("ESH", "Erilia", "Marseille", "https://www.erilia.fr"),
    ("ESH", "Nouveau Logis", "Bordeaux", "https://www.nouveaulogis.fr"),
    ("ESH", "Aquitanis", "Bordeaux", "https://www.aquitanis.fr"),
    ("ESH", "Néolia", "Besançon", "https://www.neolia.fr"),
    ("ESH", "Clairsienne", "Bordeaux", "https://www.clairsienne.com"),
    ("ESH", "Harmonie Habitat", "Tours", "https://www.harmoniehabitat.fr"),
    ("ESH", "Anjou Loire Habitat", "Angers", "https://www.anjouloirehabitat.fr"),
    ("ESH", "Sarthe Habitat", "Le Mans", "https://www.sarthehabitat.fr"),
    ("ESH", "Maine Coeur de Sarthe Habitat", "Le Mans", "https://www.mchsarthe.fr"),
    ("ESH", "Vendée Habitat", "La Roche-sur-Yon", "https://www.vendeehabitat.fr"),
    ("ESH", "Logi-Ouest", "Brest", "https://www.logiouest.fr"),
    ("ESH", "Aiguillon Construction", "Rennes", "https://www.aiguillon-construction.fr"),
    ("ESH", "Espacil Habitat", "Rennes", "https://www.espacil.com"),
    ("ESH", "Côte-d'Or Habitat ESH", "Dijon", "https://www.dijonhabitat.fr"),
    ("ESH", "Orvitis", "Dijon", "https://www.orvitis.fr"),
    ("ESH", "Dynacité", "Oyonnax", "https://www.dynacite.fr"),
    ("ESH", "Alliade Habitat", "Lyon", "https://www.alliadehabitat.fr"),
    ("ESH", "Semcoda", "Bourg-en-Bresse", "https://www.semcoda.fr"),
    ("ESH", "Héritage et Traditions", "Lyon", "https://www.ht-habitat.fr"),
    ("ESH", "SCIC Habitat", "Paris", "https://www.scic-habitat.fr"),
    ("ESH", "Vosgelis", "Épinal", "https://www.vosgelis.fr"),
    ("ESH", "Haute-Saône Habitat", "Vesoul", "https://www.hsh70.fr"),
    ("ESH", "Nièvre Habitat", "Nevers", "https://www.nievre-habitat.com"),
    ("ESH", "Cher Habitat", "Bourges", "https://www.cherhabitat.fr"),
    ("ESH", "Indre Habitat", "Châteauroux", "https://www.indrehabitat.fr"),
    ("ESH", "Loir-et-Cher Habitat", "Blois", "https://www.lchabitat.fr"),
    ("ESH", "Loiret Habitat", "Orléans", "https://www.loirethabitat.fr"),
    ("ESH", "Eure-et-Loir Habitat", "Chartres", "https://www.euretloir-habitat.fr"),
    ("ESH", "Néodyme", "Amiens", "https://www.neodyme.org"),
    ("ESH", "Habitat 80", "Amiens", "https://www.habitat80.fr"),
    ("ESH", "Picardie Habitat", "Amiens", "https://www.picardiehabitat.fr"),
    ("ESH", "Aisne Habitat", "Laon", "https://www.aisnehabitat.fr"),
    ("ESH", "Habitat 62/59 Picardie", "Arras", "https://www.habitat6259picardie.fr"),
]


# ── helpers ───────────────────────────────────────────────────────────────────

def session_factory():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def safe_get(session, url, timeout=20, retries=3):
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            if e.response.status_code in (403, 404, 410):
                return None
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return None


def classify_role(text: str) -> str | None:
    t = text.lower()
    for label, keywords in ROLE_MAP.items():
        if any(kw in t for kw in keywords):
            return label
    return None


def looks_like_name(text: str) -> bool:
    """Heuristic: 2-4 capitalized words, no digits, short enough."""
    text = text.strip()
    if not text or len(text) > 60 or any(c.isdigit() for c in text):
        return False
    words = text.split()
    return 2 <= len(words) <= 5 and sum(1 for w in words if w[0].isupper()) >= len(words) - 1


# ── USH annuaire scraping ────────────────────────────────────────────────────

USH_BASE = "https://annuaire.union-habitat.org"


def fetch_ush_page(session, page: int) -> list[dict]:
    """Scrape one page of the USH annuaire and return partial organism records."""
    url = f"{USH_BASE}/organismes?page={page}"
    r = safe_get(session, url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, "lxml")
    items = []

    # Try several CSS selector patterns (annuaire may be updated)
    for sel in [
        "a[href*='/organisme/']",
        ".organisme a",
        ".card a",
        "li.item a",
    ]:
        links = soup.select(sel)
        if links:
            for a in links:
                href = a.get("href", "")
                if not href:
                    continue
                full = href if href.startswith("http") else USH_BASE + href
                items.append({"detail_url": full, "nom_organisme": a.get_text(strip=True)})
            break

    return items


def fetch_ush_detail(session, detail_url: str) -> dict:
    """Scrape an organism detail page on the USH annuaire."""
    r = safe_get(session, detail_url)
    if not r:
        return {}
    soup = BeautifulSoup(r.text, "lxml")
    data: dict = {"source_url": detail_url, "contacts": []}

    # Name
    h1 = soup.select_one("h1")
    if h1:
        data["nom_organisme"] = h1.get_text(strip=True)

    # Type
    for el in soup.select(".type, .badge, .organisme-type, .tag"):
        t = el.get_text(strip=True).upper()
        if "OPH" in t:
            data["type"] = "OPH"
            break
        if "ESH" in t:
            data["type"] = "ESH"
            break

    # External website
    for a in soup.select("a[href]"):
        h = a.get("href", "")
        if h.startswith("http") and "union-habitat" not in h and "annuaire" not in h:
            data["site_web"] = h
            break

    # Contacts table / list
    for block in soup.select(".contact, .personne, .responsable, .dirigeant"):
        c: dict = {}
        for sel in [".fonction", ".role", ".poste", ".title"]:
            el = block.select_one(sel)
            if el:
                c["poste_raw"] = el.get_text(strip=True)
                c["poste"] = classify_role(c["poste_raw"]) or c["poste_raw"]
                break
        for sel in [".nom", ".name", "strong", "b"]:
            el = block.select_one(sel)
            if el and looks_like_name(el.get_text(strip=True)):
                c["nom_contact"] = el.get_text(strip=True)
                break
        email_a = block.select_one("a[href^='mailto:']")
        if email_a:
            c["email"] = email_a["href"].replace("mailto:", "")
        if c:
            data["contacts"].append(c)

    return data


def scrape_ush_annuaire(session) -> list[dict]:
    log.info("Fetching organism list from USH annuaire…")
    organisms = []
    for page in range(1, 200):
        items = fetch_ush_page(session, page)
        if not items:
            log.info(f"  No items on page {page}, stopping.")
            break
        organisms.extend(items)
        log.info(f"  Page {page}: +{len(items)} organisms (total {len(organisms)})")
        time.sleep(DELAY)
    return organisms


# ── Per-website contact scraping ─────────────────────────────────────────────

CONTACT_PATHS = [
    "", "/qui-sommes-nous", "/notre-organisation", "/equipe-dirigeante",
    "/equipe", "/direction", "/organigramme", "/gouvernance",
    "/contacts", "/contact", "/nous-contacter",
    "/presentation", "/a-propos", "/le-groupe",
    "/notre-equipe", "/notre-direction", "/nos-equipes",
    "/rh", "/ressources-humaines", "/recrutement",
]


def scrape_website(session, base_url: str) -> list[dict]:
    """Visit key pages of a bailleur website and extract target contacts."""
    if not base_url:
        return []

    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    visited: set[str] = set()
    contacts: list[dict] = []

    pages = [base_url] + [root + p for p in CONTACT_PATHS if p]

    for url in pages:
        if url in visited:
            continue
        visited.add(url)

        r = safe_get(session, url, timeout=15)
        if not r:
            continue

        soup = BeautifulSoup(r.text, "lxml")
        page_contacts = _extract_contacts_from_soup(soup, url)
        contacts.extend(page_contacts)

        # Follow internal links that look like team/contact pages
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            full = urljoin(url, href)
            if urlparse(full).netloc != parsed.netloc:
                continue
            text = a.get_text(" ", strip=True).lower()
            if any(kw in text or kw in href.lower() for kw in [
                "equipe", "direction", "organigramme", "gouvernance",
                "contact", "dirigeant", "responsable",
            ]):
                if full not in visited:
                    pages.append(full)

        time.sleep(DELAY)

    return _deduplicate(contacts)


def _extract_contacts_from_soup(soup: BeautifulSoup, source_url: str) -> list[dict]:
    contacts = []

    # Strategy 1: structured card/block elements
    for block in soup.find_all(["div", "article", "li", "section", "p"]):
        block_text = block.get_text(" ", strip=True)
        if len(block_text) > 800:
            continue
        role = classify_role(block_text)
        if not role:
            continue

        c: dict = {"poste": role, "source_url": source_url}

        # Name in child tags
        for tag in block.find_all(["strong", "b", "h2", "h3", "h4", "h5", "span", "p"], recursive=True):
            candidate = tag.get_text(strip=True)
            if looks_like_name(candidate) and candidate.lower() != role.lower():
                c["nom_contact"] = candidate
                break

        # Email / phone
        emails = EMAIL_RE.findall(block_text)
        if emails:
            c["email"] = emails[0]
        phones = PHONE_RE.findall(block_text)
        if phones:
            c["telephone"] = phones[0].strip()

        contacts.append(c)

    # Strategy 2: line-by-line scan
    text_lines = [ln.strip() for ln in soup.get_text("\n").split("\n") if ln.strip()]
    for i, line in enumerate(text_lines):
        role = classify_role(line)
        if not role:
            continue
        c: dict = {"poste": role, "source_url": source_url}
        for offset in range(-3, 4):
            idx = i + offset
            if offset == 0 or not (0 <= idx < len(text_lines)):
                continue
            candidate = text_lines[idx]
            if looks_like_name(candidate):
                c["nom_contact"] = candidate
                break
        contacts.append(c)

    return contacts


def _deduplicate(contacts: list[dict]) -> list[dict]:
    seen: set = set()
    out = []
    for c in contacts:
        key = (c.get("poste", ""), c.get("nom_contact", ""), c.get("email", ""))
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


# ── ScrapeGraphAI smart extraction ───────────────────────────────────────────

AI_PROMPT = """
Extrais les contacts suivants depuis cette page web d'un bailleur social :
- Directeur Général (ou Directrice Générale)
- DRH (Directeur / Directrice des Ressources Humaines)
- Responsable Formation (ou Responsable Développement RH)
- Responsable RH (ou Chargé(e) RH)

Pour chaque contact trouvé, retourne un objet JSON avec les champs :
  nom_contact, poste, email (si disponible), telephone (si disponible).

Si un contact n'est pas trouvé, ne l'inclus pas.
Retourne une liste JSON (array).
"""


def scrape_with_scrapegraphai(url: str) -> list[dict]:
    """Use SmartScraperGraph when an API key is available."""
    if not HAS_SCRAPEGRAPHAI:
        return []

    if OPENAI_KEY:
        graph_config = {
            "llm": {"api_key": OPENAI_KEY, "model": "gpt-4o-mini"},
            "verbose": False,
        }
    elif ANTHROPIC_KEY:
        graph_config = {
            "llm": {
                "api_key": ANTHROPIC_KEY,
                "model": "claude-haiku-4-5-20251001",
                "provider": "anthropic",
            },
            "verbose": False,
        }
    else:
        return []

    try:
        graph = SmartScraperGraph(
            prompt=AI_PROMPT,
            source=url,
            config=graph_config,
        )
        result = graph.run()
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            # may be wrapped {"contacts": [...]}
            for v in result.values():
                if isinstance(v, list):
                    return v
    except Exception as e:
        log.warning(f"ScrapeGraphAI failed for {url}: {e}")
    return []


# ── output helpers ────────────────────────────────────────────────────────────

def write_csv(rows: list[dict], path: str):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"CSV saved → {path}")


def write_xlsx(rows: list[dict], path: str):
    if not HAS_OPENPYXL:
        log.warning("openpyxl not installed – skipping XLSX output")
        return
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bailleurs"
    ws.append(FIELDNAMES)
    for row in rows:
        ws.append([row.get(f, "") for f in FIELDNAMES])
    # Auto-width
    for col in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in col), default=0)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
    wb.save(path)
    log.info(f"XLSX saved → {path}")


# ── main ──────────────────────────────────────────────────────────────────────

def build_organism_list(session) -> list[dict]:
    """Build the full list of bailleurs, trying live sources first."""
    organisms = []

    # 1. Try USH annuaire (live)
    try:
        organisms = scrape_ush_annuaire(session)
    except Exception as e:
        log.warning(f"USH annuaire scraping failed: {e}")

    # 2. Fallback to seed list
    if not organisms:
        log.info("Using built-in seed list of known bailleurs.")
        for entry in SEED_BAILLEURS:
            organisms.append({
                "type": entry[0],
                "nom_organisme": entry[1],
                "ville": entry[2],
                "site_web": entry[3],
            })

    return organisms


def process_organism(session, org: dict) -> list[dict]:
    """Extract contacts for a single organism; returns list of output rows."""
    nom = org.get("nom_organisme", org.get("nom", ""))
    site = org.get("site_web", "")
    detail_url = org.get("detail_url", "")

    # -- Fetch USH detail page if available --
    ush_contacts: list[dict] = []
    if detail_url:
        detail = fetch_ush_detail(session, detail_url)
        org = {**org, **detail}
        ush_contacts = detail.get("contacts", [])
        time.sleep(DELAY)

    # -- ScrapeGraphAI (AI-powered) --
    ai_contacts: list[dict] = []
    if site and (OPENAI_KEY or ANTHROPIC_KEY):
        log.info(f"  → ScrapeGraphAI: {site}")
        ai_contacts = scrape_with_scrapegraphai(site)

    # -- Classic HTML scraping --
    html_contacts: list[dict] = []
    if site and not ai_contacts:
        log.info(f"  → Classic scraping: {site}")
        html_contacts = scrape_website(session, site)

    all_contacts = _deduplicate(ush_contacts + ai_contacts + html_contacts)

    rows = []
    base = {
        "type": org.get("type", ""),
        "nom_organisme": nom,
        "ville": org.get("ville", ""),
        "departement": org.get("departement", ""),
        "site_web": site,
    }

    if all_contacts:
        for c in all_contacts:
            row = {**base, **c}
            row.setdefault("nom_contact", "")
            row.setdefault("prenom_contact", "")
            row.setdefault("poste", "")
            row.setdefault("email", "")
            row.setdefault("telephone", "")
            row.setdefault("source_url", detail_url or site)
            rows.append(row)
    else:
        rows.append({**base, "nom_contact": "", "prenom_contact": "",
                     "poste": "", "email": "", "telephone": "",
                     "source_url": detail_url or site})

    return rows


def run():
    session = session_factory()
    organisms = build_organism_list(session)

    if MAX_ORGS:
        organisms = organisms[:MAX_ORGS]

    log.info(f"\n{'='*60}")
    log.info(f"Processing {len(organisms)} organisms")
    log.info(f"ScrapeGraphAI: {'ON (OpenAI)' if OPENAI_KEY else 'ON (Anthropic)' if ANTHROPIC_KEY else 'OFF'}")
    log.info(f"{'='*60}\n")

    all_rows = []
    for i, org in enumerate(organisms, 1):
        nom = org.get("nom_organisme", org.get("nom", "?"))
        log.info(f"[{i}/{len(organisms)}] {nom}")
        try:
            rows = process_organism(session, org)
            all_rows.extend(rows)
            contact_count = sum(1 for r in rows if r.get("nom_contact"))
            log.info(f"  → {contact_count} contacts found")
        except Exception as e:
            log.warning(f"  Error: {e}")
            all_rows.append({f: org.get(f, "") for f in FIELDNAMES})

    write_csv(all_rows, OUTPUT_CSV)
    write_xlsx(all_rows, OUTPUT_XLSX)

    total_with_contacts = sum(1 for r in all_rows if r.get("nom_contact"))
    log.info(f"\nDone. {len(all_rows)} rows total, {total_with_contacts} with contacts.")
    log.info(f"Files: {OUTPUT_CSV}, {OUTPUT_XLSX}")


if __name__ == "__main__":
    run()
