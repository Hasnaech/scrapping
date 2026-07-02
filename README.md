# Prospection équicoaching — Base de 100 décideurs « signal cheval »

Base de données construite **manuellement par recherche en sources ouvertes** (OSINT), en préfiguration de l'outil
automatisé décrit dans le brief (sourcing décideurs × détection du signal « cavalier » × scoring × enrichissement × export).

📄 **Fichier : [`data/prospects.csv`](data/prospects.csv)** — 100 personnes, encodage UTF-8, séparateur virgule.

## Ce que contient la base

Chaque ligne = une personne réelle, identifiée pendant la phase de recherche, avec **la source publique qui documente
son lien avec les chevaux**. Aucune ligne n'est inventée : quand un signal n'a pas pu être confirmé, c'est écrit
explicitement dans les colonnes `niveau_preuve` / `preuve` / `confiance_0_100`.

### Niveaux de preuve (colonne `niveau_preuve`)

| Niveau | Nb | Définition |
|---|---|---|
| **A-presse** | 28 | Lien cheval **vérifié** par un article de presse / une fiche officielle (propriétaire d'écurie ou de haras, cavalier de concours, joueur de polo…) — dont 3 célébrités-dirigeants signalées |
| **A-témoignage équicoaching** | 17 | Décideur **nommé publiquement** comme participant/commanditaire d'un séminaire d'équicoaching (signal d'affinité fort, mais ≠ cavalier personnel) |
| **A-registre+presse** | 1 | Croisement registre d'entreprises (mandats) + presse |
| **B-profil LinkedIn à qualifier** | 43 | Profil LinkedIn réel **remonté par Google sur une requête croisant fonction + mot-clé équestre** (« DRH » + « équitation », « cavalière » + « dirigeante »…). L'indice figure dans l'index Google mais doit être **confirmé en ouvrant le profil** — c'est exactement le travail du Module 2 de l'outil |
| **B-registre / presse à qualifier** | 11 | Personne réelle avec un des deux signaux confirmé (ex. dirigeant cumulant un mandat de haras + une SAS commerciale via Pappers), l'autre à qualifier |

### Colonnes

`id, niveau_preuve, nom, poste, entreprise, ville_region, linkedin, email, type_signal_cheval, preuve, source_url, confiance_0_100`

- **linkedin** : URL directe du profil quand elle a été trouvée ; sinon une **URL de recherche LinkedIn pré-remplie**
  (`/search/results/people/?keywords=…`) — un clic donne le profil. Aucune URL de profil n'a été devinée.
- **email** : volontairement vide — à remplir via Dropcontact/Kaspr/Hunter (Module 4), je n'invente pas d'emails.
- **source_url** : la preuve du lien cheval (article, fiche propriétaire, page témoignage, profil LinkedIn, fiche Pappers).
- **confiance_0_100** : ma confiance dans le couple (décideur ✕ signal cheval). ≥80 = très solide, 60-79 = solide,
  <60 = à qualifier avant toute prospection.

## Typologie des signaux trouvés (utile pour cibler le discours commercial)

1. **Cavaliers pratiquants** (le signal idéal) : É. de Rothschild, S. Fegaier, G. Canet, J. Courbet, N. Canteloup, G. Mégret…
2. **Joueurs de polo dirigeants** : É. Carmignac, J.-F. Decaux, P. Guerrand-Hermès, famille Strom…
3. **Propriétaires d'écuries/haras** (courses & sport) : X. Marie, J.-L. Bouchard, Wertheimer (Chanel), J.-P. Barjon, T. Parker, K. Chehboub…
4. **Décideurs ayant déjà acheté/vécu de l'équicoaching** (affinité prouvée + budget formation validé) :
   DGRH Savencia, CODIR Casden, présidente Clarins Fragrance, DRH Châteauform', Ring Capital… ⚠️ déjà exposés à des prestataires concurrents.
5. **Profils LinkedIn décideur + mot-clé équestre** (niveau B) : le vivier à qualifier en premier par l'outil.

## Méthode utilisée (reproductible = spécification de l'outil)

1. **X-ray LinkedIn via Google** : `site:fr.linkedin.com/in "passionnée d'équitation" (DRH OR directrice OR fondatrice)`
   et variantes (« cavalière depuis », « cavalier amateur », dressage/CSO + titres). → candidats niveau B.
2. **Presse équestre & éco** (GrandPrix.info, L'Éperon, Studforlife, Equidia, zone-turf, presse éco) : portraits de
   propriétaires/mécènes/cavaliers amateurs mentionnant la fonction. → niveau A.
3. **Témoignages des prestataires d'équicoaching** (equicoaching-events, Cabalys, Alter Horse, Visions for Leaders,
   coaching-par-le-cheval…) : décideurs nommés avec fonction + entreprise. → niveau A (affinité).
4. **Croisement de mandats société** (Pappers / annuaire-entreprises) : une même personne dirigeant une société
   « haras/écurie » **et** une société commerciale = propriétaire de chevaux à pouvoir de décision. → niveaux A/B.
5. **Polo & courses** : listes de patrons d'équipes (Chantilly, Deauville, Sainte-Mesme), fiches propriétaires
   France Galop / LeTrot. → niveau A.

### Limites connues (à traiter par l'outil)
- Les entrées **niveau B** reposent sur le snippet/l'indexation Google : il faut ouvrir chaque profil (session LinkedIn
  authentifiée ou scraping conforme) pour confirmer la citation exacte — c'est le rôle du classifieur LLM (Module 2).
- Les témoignages équicoaching prouvent l'**affinité**, pas la pratique équestre personnelle.
- Deux entrées sont signalées à risque (homonymie « Cavallari », faux positif possible Roux de Bézieux).
- `recherche-entreprises.api.gouv.fr` et la plupart des sites de classements étaient bloqués par la politique réseau de
  cet environnement ; en local, ces sources permettront d'industrialiser le point 4 (l'API est gratuite et sans clé).

## Prochaine étape : l'outil (5 modules du brief)

- **M1 Sourcing** : requêtes X-ray ci-dessus + Pappers API (mandats) + Apollo/Kaspr pour les titres RH/L&D.
- **M2 Signal cavalier** : récupération du texte public du profil → classifieur LLM (prompt JSON du brief) + renfort FFE Compet (moteur de résultats par nom) et Instagram.
- **M3 Scoring** : `pouvoir de décision × confiance signal × taille entreprise × géo` — la colonne `confiance_0_100` amorce déjà ce score.
- **M4 Enrichissement** : Dropcontact (RGPD-friendly) pour remplir `email`.
- **M5 Export** : ce CSV est déjà au format cible ; ajout Google Sheet/Airtable trivial.
