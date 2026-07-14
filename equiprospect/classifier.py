"""Module 2 — Détection du signal « cavalier » (le cœur de l'outil).

Deux moteurs :
- `classifier_llm`       : un profil → un appel Claude (sortie JSON structurée)
- `classifier_llm_batch` : N profils → Message Batches API (−50 % de coût,
  idéal pour qualifier des centaines de profils d'un coup)
- `classifier_heuristique` : repli hors-ligne par mots-clés (aucune clé API),
  utile pour tester le pipeline et pré-trier avant de payer des appels LLM.

Le prompt reprend celui du brief : réponse JSON
{cavalier: oui/non/incertain, indice: "citation", confiance: 0-100},
en ignorant homonymies (nom "Cheval"/"Cavalier") et mentions purement
professionnelles (moniteur, vendeur de selles… ≠ passion personnelle).
"""

from __future__ import annotations

import json
import re
import time
import unicodedata

MODELE_DEFAUT = "claude-opus-4-8"
# Pour de très gros lots où le coût prime, l'utilisateur peut choisir
# claude-haiku-4-5 via --model (5x moins cher, classification simple).

SCHEMA_CLASSIFICATION = {
    "type": "object",
    "properties": {
        "cavalier": {"type": "string", "enum": ["oui", "non", "incertain"]},
        "indice": {
            "type": "string",
            "description": "Citation exacte du texte qui prouve (ou non) le lien équestre personnel",
        },
        "confiance": {"type": "integer", "description": "0 à 100"},
        "type_signal": {
            "type": "string",
            "enum": [
                "cavalier_pratiquant",
                "proprietaire_chevaux",
                "affinite_cheval",
                "mention_professionnelle_seulement",
                "homonymie_ou_bruit",
                "aucun",
            ],
        },
    },
    "required": ["cavalier", "indice", "confiance", "type_signal"],
    "additionalProperties": False,
}

PROMPT_SYSTEME = """Tu es un classifieur pour une prospection B2B très ciblée.
On te donne le contenu public d'un profil LinkedIn (ou un extrait de presse) concernant une personne.
Question : cette personne pratique-t-elle l'équitation ou est-elle passionnée de chevaux À TITRE PERSONNEL ?

Règles :
- Ignore les homonymies (noms de famille "Cheval", "Cavalier", "Chevallier", entreprise "Cheval Blanc"...).
- Ignore les mentions purement professionnelles sans passion personnelle (RH d'un centre équestre,
  commercial en sellerie, organisateur d'événements) SAUF si le texte montre une pratique personnelle.
- "propriétaire d'écurie de course / haras" = signal fort (proprietaire_chevaux) même sans pratique en selle.
- Participation à un séminaire d'équicoaching = affinite_cheval (signal plus faible mais réel).
- Cite l'indice EXACT (extrait du texte) qui justifie ta réponse."""


def _client():
    import anthropic

    return anthropic.Anthropic()


def _extraire_json(texte: str) -> dict:
    try:
        return json.loads(texte)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", texte, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


def classifier_llm(texte_profil: str, modele: str = MODELE_DEFAUT) -> dict:
    """Classifie un profil via l'API Claude (sortie JSON garantie par schéma)."""
    client = _client()
    response = client.messages.create(
        model=modele,
        max_tokens=1024,
        system=PROMPT_SYSTEME,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA_CLASSIFICATION}},
        messages=[
            {
                "role": "user",
                "content": f"Voici le contenu du profil :\n\n{texte_profil[:15000]}",
            }
        ],
    )
    texte = next(b.text for b in response.content if b.type == "text")
    return _extraire_json(texte)


def classifier_llm_batch(
    profils: dict[str, str],
    modele: str = MODELE_DEFAUT,
    attente_s: int = 30,
) -> dict[str, dict]:
    """Classifie un lot de profils via la Message Batches API (−50 % de coût).

    `profils` : {identifiant: texte_du_profil}. Retourne {identifiant: résultat}.
    La plupart des lots terminent en moins d'une heure.
    """
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = _client()
    requests = [
        Request(
            custom_id=cid,
            params=MessageCreateParamsNonStreaming(
                model=modele,
                max_tokens=1024,
                system=PROMPT_SYSTEME,
                output_config={
                    "format": {"type": "json_schema", "schema": SCHEMA_CLASSIFICATION}
                },
                messages=[
                    {
                        "role": "user",
                        "content": f"Voici le contenu du profil :\n\n{texte[:15000]}",
                    }
                ],
            ),
        )
        for cid, texte in profils.items()
    ]
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch créé : {batch.id} ({len(requests)} profils)")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        print(f"  … en cours ({batch.request_counts.processing} restants)")
        time.sleep(attente_s)

    resultats: dict[str, dict] = {}
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            msg = result.result.message
            texte = next((b.text for b in msg.content if b.type == "text"), "")
            try:
                resultats[result.custom_id] = _extraire_json(texte)
            except json.JSONDecodeError:
                resultats[result.custom_id] = {
                    "cavalier": "incertain",
                    "indice": "réponse non parsable",
                    "confiance": 0,
                    "type_signal": "aucun",
                }
        else:
            resultats[result.custom_id] = {
                "cavalier": "incertain",
                "indice": f"erreur batch: {result.result.type}",
                "confiance": 0,
                "type_signal": "aucun",
            }
    return resultats


# ---------------------------------------------------------------------------
# Heuristique hors-ligne (pré-tri / tests sans clé API)
# ---------------------------------------------------------------------------

_FORTS = [
    "cavalier international", "cavaliere internationale", "cavalier de concours",
    "concours complet", "championnat de france amateur", "csi", "cso",
    "dressage", "jumping", "polo", "gentleman rider", "cadre noir",
    "cavaliere depuis", "cavalier depuis", "passionnee d'equitation",
    "passionne d'equitation", "monte a cheval", "mon cheval", "mes chevaux",
]
_PROPRIETAIRE = [
    "proprietaire de chevaux", "ecurie de course", "haras", "trotteur",
    "galopeur", "poulinieres", "elevage de chevaux", "prix d'amerique",
    "prix du jockey club", "arc de triomphe", "france galop", "etalon",
]
_AFFINITE = ["equicoaching", "equi-coaching", "seminaire equestre", "coaching par le cheval"]
_BRUIT = ["monitrice", "moniteur d'equitation", "bpjeps", "sellerie", "centre equestre employe"]


def _normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def classifier_heuristique(texte_profil: str) -> dict:
    """Classification par mots-clés — rapide, gratuite, moins précise que le LLM."""
    t = _normaliser(texte_profil)

    def _trouve(mots: list[str]) -> str | None:
        return next((m for m in mots if m in t), None)

    if m := _trouve(_FORTS):
        return {"cavalier": "oui", "indice": m, "confiance": 70, "type_signal": "cavalier_pratiquant"}
    if m := _trouve(_PROPRIETAIRE):
        return {"cavalier": "oui", "indice": m, "confiance": 65, "type_signal": "proprietaire_chevaux"}
    if m := _trouve(_AFFINITE):
        return {"cavalier": "incertain", "indice": m, "confiance": 45, "type_signal": "affinite_cheval"}
    if m := _trouve(_BRUIT):
        return {"cavalier": "non", "indice": m, "confiance": 30, "type_signal": "mention_professionnelle_seulement"}
    if "equitation" in t or "cheval" in t or "chevaux" in t:
        return {"cavalier": "incertain", "indice": "mention équestre générique", "confiance": 35, "type_signal": "affinite_cheval"}
    return {"cavalier": "non", "indice": "", "confiance": 10, "type_signal": "aucun"}
