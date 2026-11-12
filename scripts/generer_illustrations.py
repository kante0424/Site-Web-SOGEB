"""Génère les illustrations SVG du site (static/img/illustrations/).

Elles servent tant que les vraies photographies de la SOGEB ne sont pas fournies : dès qu'une image est choisie
dans l'administration, elle remplace l'illustration correspondante.

Usage : python scripts/generer_illustrations.py
"""
import math
import random
from pathlib import Path

SORTIE = Path(__file__).resolve().parent.parent / "static" / "img" / "illustrations"

VERT_900, VERT_800, VERT_700, VERT_600 = "#03341b", "#064d28", "#087236", "#0d9541"
OR, OR_CLAIR, VERT_LUMIERE = "#f6bd37", "#f9c64d", "#3ee07a"
L, H = 1200, 800


def entete(titre, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {L} {H}" role="img" aria-label="{titre}">\n'
        f"<defs>\n"
        f'<linearGradient id="fond" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VERT_900}"/>'
        f'<stop offset=".6" stop-color="{VERT_800}"/><stop offset="1" stop-color="{VERT_700}"/></linearGradient>\n'
        f'<radialGradient id="halo"><stop offset="0" stop-color="{OR}" stop-opacity=".45"/>'
        f'<stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>\n'
        f'<filter id="lueur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>\n'
        f'<pattern id="points" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="#fff" fill-opacity=".08"/></pattern>\n'
        f"{defs}</defs>\n"
        f'<rect width="{L}" height="{H}" fill="url(#fond)"/>\n<rect width="{L}" height="{H}" fill="url(#points)"/>\n'
    )


def bokeh(rnd, n, couleurs=("#fff", OR, VERT_LUMIERE)):
    sortie = []
    for _ in range(n):
        x, y, r = rnd.uniform(0, L), rnd.uniform(0, H), rnd.uniform(6, 38)
        sortie.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{rnd.choice(couleurs)}" '
                      f'fill-opacity="{rnd.uniform(.03, .1):.2f}"/>')
    return "\n".join(sortie) + "\n"


def fibre():
    rnd = random.Random(7)
    defs = "".join(
        f'<linearGradient id="brin{i}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c}" stop-opacity="0"/>'
        f'<stop offset=".55" stop-color="{c}" stop-opacity=".55"/><stop offset="1" stop-color="{c}"/></linearGradient>\n'
        for i, c in enumerate(["#ffffff", OR, VERT_LUMIERE, OR_CLAIR])
    )
    svg = [entete("Fibres optiques lumineuses", defs)]
    svg.append(f'<circle cx="820" cy="380" r="420" fill="url(#halo)"/>\n')
    svg.append(bokeh(rnd, 28))
    pointes = []
    for i in range(34):
        y0 = 560 + rnd.uniform(-30, 30)
        angle = math.radians(rnd.uniform(-58, 22))
        long = rnd.uniform(620, 980)
        x1, y1 = 40 + long * math.cos(angle), y0 + long * math.sin(angle) * .9
        c1 = (40 + long * .45, y0 + rnd.uniform(-40, 40))
        c2 = (x1 - long * .25, y1 + rnd.uniform(-60, 60))
        n = i % 4
        largeur = rnd.uniform(1.6, 4.2)
        svg.append(f'<path d="M-20 {y0:.0f}C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {x1:.0f} {y1:.0f}" '
                   f'fill="none" stroke="url(#brin{n})" stroke-width="{largeur:.1f}" stroke-linecap="round"/>\n')
        pointes.append((x1, y1, ["#ffffff", OR, VERT_LUMIERE, OR_CLAIR][n], largeur))
    for x, y, c, larg in pointes:
        r = larg * 2.2
        svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * 2.6:.1f}" fill="{c}" fill-opacity=".55" filter="url(#lueur)"/>'
                   f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * .7:.1f}" fill="#fff"/>\n')
    # Gaine du câble à gauche
    svg.append(f'<rect x="-40" y="520" width="90" height="80" rx="18" fill="{VERT_900}" stroke="{OR}" stroke-opacity=".5" stroke-width="2"/>\n')
    svg.append("</svg>\n")
    return "".join(svg)


def datacenter():
    rnd = random.Random(11)
    defs = (
        '<linearGradient id="baie" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f3a24"/>'
        '<stop offset="1" stop-color="#072315"/></linearGradient>\n'
        '<linearGradient id="sol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d9541" stop-opacity=".25"/>'
        '<stop offset="1" stop-color="#03341b" stop-opacity="0"/></linearGradient>\n'
        '<linearGradient id="plafond" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>\n'
    )
    svg = [entete("Salle informatique du data center", defs)]
    svg.append(f'<circle cx="600" cy="300" r="460" fill="url(#halo)" opacity=".7"/>\n')
    # Couloir en perspective : lignes de fuite au sol
    fx, fy = 600, 330
    for x in range(-600, 1801, 150):
        svg.append(f'<line x1="{fx}" y1="{fy}" x2="{x}" y2="{H}" stroke="#fff" stroke-opacity=".05"/>\n')
    for y in (420, 500, 600, 730):
        svg.append(f'<line x1="0" y1="{y}" x2="{L}" y2="{y}" stroke="#fff" stroke-opacity=".04"/>\n')
    svg.append(f'<polygon points="0,{H} {L},{H} {fx + 260},{fy + 150} {fx - 260},{fy + 150}" fill="url(#sol)"/>\n')
    # Rampes lumineuses au plafond
    for i, (x0, x1) in enumerate([(120, 470), (730, 1080)]):
        svg.append(f'<rect x="{x0}" y="40" width="{x1 - x0}" height="8" rx="4" fill="#fff" fill-opacity=".7"/>'
                   f'<rect x="{x0}" y="48" width="{x1 - x0}" height="120" fill="url(#plafond)"/>\n')

    def baie(x, y, larg, haut, echelle):
        out = [f'<rect x="{x:.0f}" y="{y:.0f}" width="{larg:.0f}" height="{haut:.0f}" rx="{6 * echelle:.0f}" '
               f'fill="url(#baie)" stroke="#2a6b45" stroke-width="{2 * echelle:.1f}"/>']
        nb = 12
        pas = (haut - 24 * echelle) / nb
        for u in range(nb):
            uy = y + 12 * echelle + u * pas
            out.append(f'<rect x="{x + 10 * echelle:.0f}" y="{uy:.0f}" width="{larg - 20 * echelle:.0f}" '
                       f'height="{pas - 4 * echelle:.1f}" rx="{2 * echelle:.0f}" fill="#0a2c1b" stroke="#1d5537" '
                       f'stroke-width="{echelle:.1f}"/>')
            for k in range(rnd.randint(1, 4)):
                c = rnd.choice([VERT_LUMIERE, VERT_LUMIERE, VERT_LUMIERE, OR, "#ffffff"])
                lx = x + larg - (22 + k * 12) * echelle
                ly = uy + (pas - 4 * echelle) / 2
                out.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="{2.6 * echelle:.1f}" fill="{c}"/>')
            if rnd.random() < .5:
                out.append(f'<rect x="{x + 18 * echelle:.0f}" y="{uy + (pas - 4 * echelle) / 2 - 1.5 * echelle:.0f}" '
                           f'width="{(larg - 90 * echelle) * rnd.uniform(.3, .8):.0f}" height="{3 * echelle:.1f}" '
                           f'rx="1" fill="#2f7a51"/>')
        return "\n".join(out) + "\n"

    # Rangées gauche et droite, de la plus lointaine à la plus proche
    for cote in (-1, 1):
        for i in range(5, -1, -1):
            e = .42 + i * .0  # échelle provisoire
            prof = i / 5
            e = 1.15 - prof * .75
            larg, haut = 150 * e, 430 * e
            centre = fx + cote * (190 + (1 - prof) * 330)
            x = centre - larg / 2 + cote * (1 - prof) * 40
            y = fy + 150 * (1 - prof) * .9 - haut * .62
            svg.append(baie(x, y, larg, haut, e))
    # Baie centrale au fond
    svg.append(baie(fx - 55, fy - 150, 110, 260, .55))
    svg.append(bokeh(rnd, 12, ("#fff", VERT_LUMIERE)))
    svg.append("</svg>\n")
    return "".join(svg)


def reseau():
    rnd = random.Random(3)
    svg = [entete("Réseau de données")]
    svg.append(f'<circle cx="600" cy="400" r="460" fill="url(#halo)" opacity=".6"/>\n')
    for r in (140, 260, 380):
        svg.append(f'<circle cx="600" cy="400" r="{r}" fill="none" stroke="#fff" stroke-opacity=".07" stroke-width="2"/>\n')
    noeuds = [(rnd.uniform(60, L - 60), rnd.uniform(60, H - 60)) for _ in range(46)]
    for i, (x, y) in enumerate(noeuds):
        voisins = sorted(noeuds, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)[1:4]
        for vx, vy in voisins:
            c = OR if (i % 3 == 0) else "#9cc4ad"
            svg.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{vx:.0f}" y2="{vy:.0f}" stroke="{c}" '
                       f'stroke-opacity=".45" stroke-width="1.6"/>\n')
    for i, (x, y) in enumerate(noeuds):
        grand = i % 6 == 0
        c = OR if grand else "#ffffff"
        if grand:
            svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="16" fill="{OR}" fill-opacity=".5" filter="url(#lueur)"/>\n')
        svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{7 if grand else 3.5}" fill="{c}" stroke="{VERT_600}" '
                   f'stroke-width="{2 if grand else 0}"/>\n')
    svg.append(bokeh(rnd, 16))
    svg.append("</svg>\n")
    return "".join(svg)


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    for nom, fonction in (("fibre", fibre), ("datacenter", datacenter), ("reseau", reseau)):
        (SORTIE / f"{nom}.svg").write_text(fonction(), encoding="utf-8")
        print(nom, (SORTIE / f"{nom}.svg").stat().st_size // 1024, "Ko")
