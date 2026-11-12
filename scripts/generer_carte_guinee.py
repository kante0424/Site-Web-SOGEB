"""
Génère templates/includes/carte_guinee.html : carte SVG simplifiée de la Guinée,
avec les chefs-lieux de préfecture et des liaisons stylisées du Backbone.

Les liaisons sont une représentation schématique (villes et axes), pas le tracé réel du réseau :
aucune coordonnée de site technique n'est publiée (cahier des charges, section 6.3).

Contour : Natural Earth 1:10m (domaine public), fichier ne_10m_admin_0_countries.geojson.
Usage : python scripts/generer_carte_guinee.py chemin/vers/ne_10m_admin_0_countries.geojson
"""
import json
import math
import sys
from pathlib import Path

# Chefs-lieux (latitude, longitude). « grande » = nom affiché sur la carte.
VILLES = {
    "Conakry": (9.51, -13.71, True), "Dubréka": (9.79, -13.52, False), "Coyah": (9.70, -13.38, False),
    "Forécariah": (9.43, -13.09, False), "Boffa": (10.18, -14.04, False), "Boké": (10.94, -14.30, True),
    "Fria": (10.37, -13.58, False), "Gaoual": (11.75, -13.20, False), "Koundara": (12.48, -13.30, False),
    "Kindia": (10.06, -12.86, True), "Télimélé": (10.90, -13.04, False), "Mamou": (10.38, -12.09, True),
    "Dalaba": (10.69, -12.25, False), "Pita": (11.06, -12.40, False), "Labé": (11.32, -12.29, True),
    "Lélouma": (11.42, -12.53, False), "Mali": (12.08, -12.30, False), "Tougué": (11.44, -11.66, False),
    "Koubia": (11.58, -11.89, False), "Dabola": (10.75, -11.11, False), "Dinguiraye": (11.30, -10.72, False),
    "Faranah": (10.04, -10.74, True), "Kouroussa": (10.65, -9.88, False), "Kankan": (10.39, -9.31, True),
    "Siguiri": (11.42, -9.17, True), "Mandiana": (10.62, -8.69, False), "Kérouané": (9.27, -9.01, False),
    "Kissidougou": (9.18, -10.10, False), "Guéckédou": (8.56, -10.13, False), "Macenta": (8.54, -9.47, False),
    "Beyla": (8.69, -8.66, False), "Nzérékoré": (7.75, -8.82, True), "Lola": (7.80, -8.53, False),
    "Yomou": (7.57, -9.25, False),
}

# Liaisons schématiques, dans l'ordre d'animation (depuis Conakry vers l'intérieur)
LIENS = [
    ("Conakry", "Dubréka"), ("Conakry", "Coyah"), ("Coyah", "Forécariah"), ("Coyah", "Kindia"),
    ("Dubréka", "Boffa"), ("Dubréka", "Fria"), ("Boffa", "Boké"), ("Kindia", "Mamou"), ("Kindia", "Télimélé"),
    ("Fria", "Télimélé"), ("Boké", "Gaoual"), ("Mamou", "Dalaba"), ("Mamou", "Dabola"), ("Mamou", "Faranah"),
    ("Télimélé", "Pita"), ("Gaoual", "Koundara"), ("Dalaba", "Pita"), ("Pita", "Labé"), ("Dabola", "Dinguiraye"),
    ("Dabola", "Kouroussa"), ("Faranah", "Kissidougou"), ("Labé", "Lélouma"), ("Lélouma", "Gaoual"),
    ("Labé", "Mali"), ("Labé", "Koubia"), ("Koubia", "Tougué"), ("Tougué", "Dinguiraye"),
    ("Kouroussa", "Kankan"), ("Kissidougou", "Guéckédou"), ("Kissidougou", "Kérouané"),
    ("Dinguiraye", "Siguiri"), ("Kankan", "Siguiri"), ("Kankan", "Mandiana"), ("Siguiri", "Mandiana"),
    ("Kankan", "Kérouané"), ("Guéckédou", "Macenta"), ("Kérouané", "Beyla"), ("Macenta", "Nzérékoré"),
    ("Beyla", "Nzérékoré"), ("Nzérékoré", "Lola"), ("Nzérékoré", "Yomou"), ("Macenta", "Yomou"),
]

# Interconnexions internationales : (ville de départ, libellé, décalage x, décalage y en pixels)
INTERNATIONAL = [
    ("Conakry", "Câble sous-marin", -70, 40), ("Koundara", "Sénégal", -10, -50), ("Gaoual", "Guinée-Bissau", -95, -10),
    ("Siguiri", "Mali", 30, -55), ("Mandiana", "Côte d'Ivoire", 70, 25), ("Lola", "Libéria", 20, 45),
    ("Forécariah", "Sierra Leone", 20, 60),
]

# Axes principaux parcourus par l'animation « flux de données »
FLUX = [
    ["Conakry", "Coyah", "Kindia", "Mamou", "Dabola", "Kouroussa", "Kankan", "Siguiri"],
    ["Mamou", "Faranah", "Kissidougou", "Guéckédou", "Macenta", "Nzérékoré", "Lola"],
    ["Kindia", "Télimélé", "Pita", "Labé", "Mali"],
    ["Conakry", "Dubréka", "Boffa", "Boké", "Gaoual", "Koundara"],
    ["Kankan", "Kérouané", "Beyla", "Nzérékoré"],
]

LARGEUR = 800
MARGE = 12


def simplifier(points, tolerance):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dmax, index = 0, 0
    for i in range(1, len(points) - 1):
        x0, y0 = points[i]
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = math.hypot(y2 - y1, x2 - x1) or 1
        if num / den > dmax:
            dmax, index = num / den, i
    if dmax > tolerance:
        return simplifier(points[: index + 1], tolerance)[:-1] + simplifier(points[index:], tolerance)
    return [points[0], points[-1]]


def main(chemin):
    data = json.loads(Path(chemin).read_text(encoding="utf-8"))
    pays = next(f for f in data["features"] if f["properties"].get("ADM0_A3") == "GIN")
    geom = pays["geometry"]
    polygones = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    anneaux = [p[0] for p in polygones]

    lons = [x for a in anneaux for x, _ in a]
    lats = [y for a in anneaux for _, y in a]
    lat0 = (min(lats) + max(lats)) / 2
    kx = math.cos(math.radians(lat0))
    echelle = (LARGEUR - 2 * MARGE) / ((max(lons) - min(lons)) * kx)
    hauteur = round((max(lats) - min(lats)) * echelle + 2 * MARGE)

    def proj(lon, lat):
        return (round(MARGE + (lon - min(lons)) * kx * echelle, 1), round(MARGE + (max(lats) - lat) * echelle, 1))

    chemins = []
    for anneau in anneaux:
        brut = [proj(x, y) for x, y in anneau]
        milieu = len(brut) // 2  # anneau fermé : simplifier en deux moitiés
        pts = simplifier(brut[: milieu + 1], 1.2)[:-1] + simplifier(brut[milieu:], 1.2)
        if len(pts) < 4:
            continue
        chemins.append("M" + "L".join(f"{x} {y}" for x, y in pts) + "Z")

    pos = {nom: proj(lon, lat) for nom, (lat, lon, _) in VILLES.items()}
    lignes = []
    for i, (a, b) in enumerate(LIENS):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        lignes.append(f'      <path d="M{x1} {y1}L{x2} {y2}" pathLength="1" style="--i:{i}"/>')
    flux = []
    for i, trajet in enumerate(FLUX):
        d = "M" + "L".join(f"{pos[v][0]} {pos[v][1]}" for v in trajet)
        flux.append(f'      <path d="{d}" style="--j:{i}"/>')
    inter, inter_noms = [], []
    for ville, libelle, dx, dy in INTERNATIONAL:
        x, y = pos[ville]
        x2, y2 = round(x + dx, 1), round(y + dy, 1)
        inter.append(f'      <path d="M{x} {y}L{x2} {y2}"/>')
        ancre = "end" if dx < 0 else "start"
        inter_noms.append(f'      <text x="{x2 + (-4 if dx < 0 else 4)}" y="{y2 + (14 if dy > 0 else -6)}" text-anchor="{ancre}">{libelle}</text>')
    points, noms = [], []
    for nom, (lat, lon, grande) in VILLES.items():
        x, y = pos[nom]
        classe = ' class="majeure"' if grande else ""
        if nom == "Conakry":
            classe = ' class="hub"'
        points.append(f'      <circle cx="{x}" cy="{y}" r="{9 if nom == "Conakry" else 6.5 if grande else 4.5}"{classe} style="--k:{len(points)}"><title>{nom}</title></circle>')
        if grande:
            dx = -10 if nom in ("Siguiri", "Kankan", "Nzérékoré") else 10
            ancre = "end" if dx < 0 else "start"
            noms.append(f'      <text x="{x + dx}" y="{y + 5}" text-anchor="{ancre}">{nom}</text>')

    svg = f"""{{# Fichier généré par scripts/generer_carte_guinee.py : ne pas modifier à la main. #}}
<svg class="carte-guinee" viewBox="-110 -70 {LARGEUR + 220} {hauteur + 140}" role="img" aria-labelledby="carte-titre carte-desc" focusable="false">
  <title id="carte-titre">Carte du Backbone national de Guinée</title>
  <desc id="carte-desc">Représentation simplifiée du réseau de fibre optique reliant Conakry et les {len(VILLES) - 1} préfectures du pays.</desc>
  <path class="carte-guinee__pays" d="{' '.join(chemins)}"/>
  <g class="carte-guinee__international">
{chr(10).join(inter)}
  </g>
  <g class="carte-guinee__international-noms" aria-hidden="true">
{chr(10).join(inter_noms)}
  </g>
  <g class="carte-guinee__liens">
{chr(10).join(lignes)}
  </g>
  <g class="carte-guinee__flux" aria-hidden="true">
{chr(10).join(flux)}
  </g>
  <g class="carte-guinee__villes">
{chr(10).join(points)}
  </g>
  <g class="carte-guinee__noms" aria-hidden="true">
{chr(10).join(noms)}
  </g>
</svg>
"""
    sortie = Path(__file__).resolve().parent.parent / "templates" / "includes" / "carte_guinee.html"
    sortie.write_text(svg, encoding="utf-8")
    print(f"Carte écrite : {sortie} ({len(svg) // 1024} Ko, {len(VILLES)} villes, {len(LIENS)} liaisons)")


if __name__ == "__main__":
    main(sys.argv[1])
