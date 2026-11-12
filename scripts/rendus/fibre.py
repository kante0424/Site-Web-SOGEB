"""Rendu réaliste d'un faisceau de fibres optiques éclairées (gros plan, faible profondeur de champ).

Image d'attente : elle sera remplacée par une vraie photographie du réseau de la SOGEB.
Nécessite numpy, scipy et Pillow (outil de conception, inutile au fonctionnement du site).
Usage : python scripts/rendus/fibre.py static/img/illustrations/fibre
        python scripts/rendus/fibre.py static/img/illustrations/reseau 5 miroir
"""
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

L, H = 1600, 1000
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
FOCUS = 1.0
NB_PLANS = 9
TEINTES = [np.array(c) for c in ([0.8, 1.0, 0.85], [0.18, 1.0, 0.45], [1.0, 0.74, 0.2], [0.45, 1.0, 0.62])]
POIDS = [0.26, 0.46, 0.12, 0.16]


def disque(img, cx, cy, r, couleur, energie):
    """Tache de flou (bokeh) : disque uniforme, bord un peu plus lumineux."""
    r = max(r, 0.8)
    x0, x1 = int(max(cx - r - 3, 0)), int(min(cx + r + 4, L))
    y0, y1 = int(max(cy - r - 3, 0)), int(min(cy + r + 4, H))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    profil = np.clip((1 - d) * r * 0.8, 0, 1)  # bord net mais lissé
    profil = profil * (0.8 + 0.35 * np.clip(d, 0, 1) ** 4)
    img[y0:y1, x0:x1] += profil[..., None] * couleur * energie / (np.pi * r * r)


def ecrire_etincelles(sortie, etincelles, miroir):
    """Gabarit SVG superposé à l'image : petites étincelles qui scintillent au bout des fibres."""
    from pathlib import Path

    nom = Path(sortie).name
    gabarit = Path(__file__).resolve().parents[2] / "templates" / "includes" / f"animation_{nom}.html"
    lignes = [f"{{# Généré par scripts/rendus/fibre.py : ne pas modifier à la main. #}}",
              f'<svg class="scintillement" viewBox="0 0 {L} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">']
    choix = rng.permutation(len(etincelles))[:42]
    for i in choix:
        x, y, c = etincelles[i]
        if miroir:
            x = L - x
        hexa = "#%02x%02x%02x" % tuple(int(min(1, v) * 255) for v in c)
        lignes.append(f'<g style="--d:{rng.uniform(0, 6):.2f}s;--t:{rng.uniform(2.2, 5.5):.2f}s">'
                      f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{hexa}" opacity=".35"/>'
                      f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3" fill="#fff"/></g>')
    lignes.append("</svg>")
    gabarit.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def main(sortie):
    yy, xx = np.mgrid[0:H, 0:L]
    fond = np.zeros((H, L, 3))
    # fond très sombre, légèrement vert
    g = np.exp(-(((xx - L * 0.62) / (L * 0.55)) ** 2 + ((yy - H * 0.42) / (H * 0.6)) ** 2))
    fond += g[..., None] * np.array([0.003, 0.03, 0.014])

    plans = [np.zeros((H, L, 3)) for _ in range(NB_PLANS)]
    profondeurs = np.linspace(0.55, 1.7, NB_PLANS)
    pointes = []
    # câble (gaine verte) qui entre par le bas à gauche ; les fibres sortent de son extrémité
    axe = np.radians(-36)
    ux, uy = np.cos(axe), np.sin(axe)
    ox, oy = 0.16 * L, 0.84 * H
    R = 58.0
    sx, sy = xx - ox, yy - oy
    s_ax = sx * ux + sy * uy          # position le long du câble (0 = extrémité)
    p_ax = -sx * uy + sy * ux         # distance à l'axe
    n = np.clip(p_ax / R, -1, 1)
    gaine = (s_ax < 0) & (np.abs(p_ax) < R)
    relief = np.sqrt(np.clip(1 - n ** 2, 0, 1))
    reflet = np.exp(-((n + 0.45) / 0.16) ** 2)
    teinte_gaine = np.array([0.02, 0.12, 0.055]) * (0.25 + 0.9 * relief[..., None]) + reflet[..., None] * np.array([0.06, 0.16, 0.09])
    # bord éclairé par les fibres, plus fort près de l'extrémité
    proche = np.exp(s_ax / 220)
    teinte_gaine += (np.abs(n) ** 6)[..., None] * proche[..., None] * np.array([0.05, 0.25, 0.12])
    # bague métallique de l'extrémité
    bague = gaine & (s_ax > -26)
    teinte_gaine[bague] = (np.array([0.1, 0.12, 0.11]) * (0.4 + relief[bague][..., None])
                           + reflet[bague][..., None] * np.array([0.25, 0.28, 0.26]))
    fond[gaine] = teinte_gaine[gaine]
    # lumière qui s'échappe de l'extrémité
    lueur = np.exp(-((s_ax - 6) / 14) ** 2 - (p_ax / (R * 0.8)) ** 2) * (s_ax > -8)
    fond += lueur[..., None] * np.array([0.5, 1.0, 0.65]) * 0.9
    etincelles = []
    for i in range(190):
        z = rng.choice([rng.uniform(0.9, 1.1), rng.uniform(0.6, 1.6)], p=[0.45, 0.55])
        plan = int(np.argmin(np.abs(profondeurs - z)))
        ang = np.radians(rng.normal(-36, 13))
        long = rng.uniform(0.55, 1.05) * L / z ** 0.35
        # départ dans la section du câble, d'abord dans l'axe, puis la fibre s'écarte
        dec = rng.uniform(-0.8, 0.8) * R
        ax0, ay0 = ox - uy * dec, oy + ux * dec
        ex, ey = ax0 + np.cos(ang) * long, ay0 + np.sin(ang) * long * 0.95
        c1x, c1y = ax0 + ux * long * 0.35, ay0 + uy * long * 0.35
        c2x, c2y = ax0 + np.cos(ang) * long * 0.7, ay0 + np.sin(ang) * long * 0.7 - rng.uniform(0, 90)
        t = np.linspace(0, 1, 1100)[:, None]
        pts = ((1 - t) ** 3 * np.array([ax0, ay0]) + 3 * (1 - t) ** 2 * t * np.array([c1x, c1y])
               + 3 * (1 - t) * t ** 2 * np.array([c2x, c2y]) + t ** 3 * np.array([ex, ey]))
        k = rng.choice(4, p=POIDS)
        coul = TEINTES[k] * rng.uniform(0.75, 1.1)
        # la gaine de la fibre diffuse un peu de lumière, davantage vers l'extrémité
        lum = (0.02 + 0.22 * t[:, 0] ** 3) * rng.uniform(0.5, 1.3) / max(z, 0.7)
        xs, ys = pts[:, 0].astype(int), pts[:, 1].astype(int)
        ok = (xs >= 0) & (xs < L) & (ys >= 0) & (ys < H)
        np.add.at(plans[plan], (ys[ok], xs[ok]), coul[None, :] * lum[ok, None])
        if 0 <= ex < L and 0 <= ey < H:
            pointes.append((ex, ey, z, coul, rng.uniform(0.6, 1.6)))
            if abs(z - FOCUS) < 0.3:
                etincelles.append((ex, ey, coul))

    img = fond.copy()
    for p, z in zip(plans, profondeurs):
        sigma = 0.5 + abs(z - FOCUS) * 7
        img += gaussian_filter(p, (sigma, sigma, 0))

    # extrémités : bokeh hors du plan net, point brillant dans le plan net
    for ex, ey, z, coul, e in pointes:
        r = 1.5 + abs(z - FOCUS) * 38
        disque(img, ex, ey, r, coul, e * 45)
        if abs(z - FOCUS) < 0.12:
            disque(img, ex, ey, 2.2, np.array([0.9, 1.0, 0.92]), e * 40)

    # halo
    lumineux = np.clip(img - 0.25, 0, None)
    img += sum(gaussian_filter(lumineux, (s, s, 0)) * w for s, w in ((4, .6), (14, .45), (40, .3)))
    img = img * 2.0
    img = img / (1 + img)
    img = img ** (1 / 1.55)
    vign = 1 - 0.45 * (((xx - L / 2) / (L / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.3
    img *= vign[..., None]
    img += rng.normal(0, 0.008, img.shape)
    img = np.clip(img, 0, 1)
    miroir = len(sys.argv) > 3 and sys.argv[3] == "miroir"
    if miroir:
        img = img[:, ::-1]
    ecrire_etincelles(sortie, etincelles, miroir)
    im = Image.fromarray((img * 255).astype(np.uint8))
    im.save(sortie + ".webp", quality=80, method=6)
    im.save(sortie + ".jpg", quality=82, optimize=True, progressive=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fibre")
