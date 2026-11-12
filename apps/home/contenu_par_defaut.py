"""Textes par défaut de la page d'accueil, partagés entre la commande initialiser_sogeb et les migrations."""

ACCROCHE = "Le réseau qui *relie* la Guinée"
ANCIENNE_ACCROCHE = "L'infrastructure numérique nationale au service de la connectivité de la Guinée"

MISSIONS = [
    ("reglages", "Gérer", "Assurer la gestion du Backbone national à fibre optique, infrastructure publique de l'État."),
    ("activite", "Exploiter", "Exploiter et maintenir le réseau et le data center pour garantir leur disponibilité."),
    ("poignee", "Commercialiser", "Proposer les capacités du réseau aux opérateurs, FAI, entreprises et institutions."),
    ("globe", "Connecter", "Relier les régions de Guinée entre elles et aux pays voisins par la fibre optique."),
]


def missions_stream():
    return [("mission", {"icone": i, "titre": t, "texte": x}) for i, t, x in MISSIONS]
