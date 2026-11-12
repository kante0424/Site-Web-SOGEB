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
TEINTES = [np.array(c) for c in ([0.85, 1.0, 0.9], [0.25, 1.0, 0.5], [1.0, 0.72, 0.22], [0.6, 1.0, 0.75])]
POIDS = [0.38, 0.32, 0.18, 0.12]


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


def main(sortie):
    yy, xx = np.mgrid[0:H, 0:L]
    fond = np.zeros((H, L, 3))
    # fond très sombre, légèrement vert
    g = np.exp(-(((xx - L * 0.62) / (L * 0.55)) ** 2 + ((yy - H * 0.42) / (H * 0.6)) ** 2))
    fond += g[..., None] * np.array([0.002, 0.012, 0.007])

    plans = [np.zeros((H, L, 3)) for _ in range(NB_PLANS)]
    profondeurs = np.linspace(0.55, 1.7, NB_PLANS)
    pointes = []
    # origine du faisceau (gaine) en bas à gauche, hors champ
    ox, oy = -0.08 * L, 1.12 * H
    for i in range(190):
        z = rng.choice([rng.uniform(0.9, 1.1), rng.uniform(0.6, 1.6)], p=[0.45, 0.55])
        plan = int(np.argmin(np.abs(profondeurs - z)))
        ang = np.radians(rng.normal(-38, 11))
        long = rng.uniform(0.7, 1.25) * L / z ** 0.35
        ex, ey = ox + np.cos(ang) * long, oy + np.sin(ang) * long * 0.95
        # courbure : la fibre monte puis retombe légèrement
        cx = ox + np.cos(ang) * long * 0.55 + rng.normal(0, 40)
        cy = oy + np.sin(ang) * long * 0.75 - rng.uniform(40, 160)
        t = np.linspace(0, 1, 900)[:, None]
        pts = (1 - t) ** 2 * np.array([ox, oy]) + 2 * (1 - t) * t * np.array([cx, cy]) + t ** 2 * np.array([ex, ey])
        k = rng.choice(4, p=POIDS)
        coul = TEINTES[k] * rng.uniform(0.75, 1.1)
        # la gaine de la fibre diffuse un peu de lumière, davantage vers l'extrémité
        lum = (0.02 + 0.22 * t[:, 0] ** 3) * rng.uniform(0.5, 1.3) / max(z, 0.7)
        xs, ys = pts[:, 0].astype(int), pts[:, 1].astype(int)
        ok = (xs >= 0) & (xs < L) & (ys >= 0) & (ys < H)
        np.add.at(plans[plan], (ys[ok], xs[ok]), coul[None, :] * lum[ok, None])
        if 0 <= ex < L and 0 <= ey < H:
            pointes.append((ex, ey, z, coul, rng.uniform(0.6, 1.6)))

    img = fond.copy()
    for p, z in zip(plans, profondeurs):
        sigma = 0.5 + abs(z - FOCUS) * 7
        img += gaussian_filter(p, (sigma, sigma, 0))

    # extrémités : bokeh hors du plan net, point brillant dans le plan net
    for ex, ey, z, coul, e in pointes:
        r = 1.5 + abs(z - FOCUS) * 38
        disque(img, ex, ey, r, coul, e * 45)
        if abs(z - FOCUS) < 0.12:
            disque(img, ex, ey, 2.2, np.array([1.0, 1.0, 1.0]), e * 40)

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
    if len(sys.argv) > 3 and sys.argv[3] == "miroir":
        img = img[:, ::-1]
    im = Image.fromarray((img * 255).astype(np.uint8))
    im.save(sortie + ".webp", quality=80, method=6)
    im.save(sortie + ".jpg", quality=82, optimize=True, progressive=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fibre")
