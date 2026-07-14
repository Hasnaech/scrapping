"""EquiProspect — génération de prospects équicoaching.

Croise deux signaux qui ne coexistent que sur les profils individuels :
1. le pouvoir de décision (DRH, DG, fondateur, responsable formation…)
2. la passion équestre (cavalier, propriétaire, affinité cheval)

Modules (cf. brief) :
- M1 sourcing   : equiprospect.xray      (requêtes X-ray LinkedIn/Google)
- M2 signal     : equiprospect.classifier (classifieur LLM Claude + heuristique)
- M3 scoring    : equiprospect.scoring
- M4 enrichissement : equiprospect.enrich (Dropcontact)
- M5 export     : equiprospect.export
"""

__version__ = "0.1.0"
