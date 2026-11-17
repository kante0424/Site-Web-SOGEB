"""Rendu réaliste d'une allée de data center (baies informatiques), en lancer de rayons simple.

Image d'attente : elle sera remplacée par une vraie photographie du data center de la SOGEB.
Nécessite numpy, scipy et Pillow (outil de conception, inutile au fonctionnement du site).
Usage : python scripts/rendus/datacenter.py static/img/illustrations/datacenter
"""
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

L, H, SUR = 1600, 1000, 2  # taille finale et suréchantillonnage
W, HH = L * SUR, H * SUR
rng = np.random.default_rng(4)

A = 0.92        # demi-largeur de l'allée (faces avant des baies)
HAUT = 3.1      # plafond
H_BAIE = 2.15
PROF = 26.0     # mur du fond
LARG_BAIE = 0.62
LUMIERES = [(x, HAUT - 0.02, z) for z in np.arange(0.6, PROF, 1.5) for x in (-0.45, 0.45)]


def hash2(a, b, graine=0):
    """Nombre pseudo-aléatoire stable dans [0, 1) pour des indices entiers."""
    x = (a * 73856093) ^ (b * 19349663) ^ (graine * 83492791)
    x = (x ^ (x >> 13)) * 1274126177
    return ((x ^ (x >> 16)) & 0xFFFFFF) / float(0x1000000)


def eclairage(px, py, pz, nx, ny, nz):
    total = np.zeros_like(px)
    for lx, ly, lz in LUMIERES:
        dx, dy, dz = lx - px, ly - py, lz - pz
        d2 = dx * dx + dy * dy + dz * dz
        d = np.sqrt(d2)
        cos = np.clip((dx * nx + dy * ny + dz * nz) / d, 0, 1)
        # le luminaire éclaire surtout vers le bas
        cos_l = np.clip(-dy / d, 0, 1) ** 0.8
        total += 1.9 * cos * cos_l / (d2 + 0.5)
    return total + 0.09


def face_baie(z, y, cote):
    """Couleur et émission de la face avant des baies (côté -1 gauche, +1 droite)."""
    idx = np.floor(z / LARG_BAIE).astype(np.int64)
    u = z / LARG_BAIE - idx  # position horizontale dans la baie (0..1)
    graine = 1 if cote < 0 else 2
    couleur = np.zeros(z.shape + (3,))
    emission = np.zeros(z.shape + (3,))
    base = np.array([0.045, 0.05, 0.05])
    couleur[:] = base

    dans = (y > 0.05) & (y < H_BAIE)
    # montants verticaux de la baie
    montant = (u < 0.06) | (u > 0.94)
    # unités de 1U
    U = 0.0445
    iu = np.floor((y - 0.12) / U).astype(np.int64)
    v = (y - 0.12) / U - iu
    # chaque baie : suite d'équipements de 1U, 2U ou vides, déterminée par hash
    h_equip = hash2(idx, iu // 2, graine)
    h_type = hash2(idx, iu // 2, graine + 7)
    vide = h_equip < 0.18
    gris = 0.09 + 0.12 * h_type
    equip = dans & ~montant & (iu >= 0) & (iu < 44) & ~vide
    couleur[equip] = np.stack([gris[equip] * 0.95, gris[equip], gris[equip] * 1.02], -1)
    # rainures entre les unités
    rainure = equip & ((v < 0.06) | ((iu % 2 == 1) & (v > 0.94)))
    couleur[rainure] *= 0.35
    lisere = equip & (iu % 2 == 0) & (v > 0.06) & (v < 0.16)
    couleur[lisere] = couleur[lisere] * 1.7 + 0.04
    poignee = equip & (((u > 0.07) & (u < 0.1)) | ((u > 0.9) & (u < 0.93))) & (iu % 2 == 0)
    couleur[poignee] = [0.32, 0.33, 0.34]
    # façades perforées (aération)
    perfo = equip & (h_type > 0.45) & (u > 0.12) & (u < 0.74)
    trame = (np.sin(z * 900) * np.sin(y * 900)) > 0.3
    couleur[perfo & trame] *= 0.55
    # baies vides : plaque d'obturation noire
    couleur[dans & ~montant & vide] = [0.02, 0.022, 0.022]
    couleur[dans & montant] = [0.03, 0.033, 0.033]

    # diodes : 1 à 3 par équipement, près du bord droit
    for k in range(3):
        present = equip & (hash2(idx, iu // 2, graine + 20 + k) < [0.85, 0.55, 0.25][k])
        cu = 0.86 - k * 0.035
        cv = 0.55
        du = (u - cu) * LARG_BAIE
        dv = ((iu % 2) + v - 0.5) * U
        dist = np.sqrt((du / 0.0032) ** 2 + (dv / 0.0032) ** 2)
        allume = present & (dist < 1.0) & (hash2(idx, iu, graine + 40 + k) < 0.9)
        t = hash2(idx, iu // 2, graine + 60 + k)
        teinte = np.where(t[..., None] < 0.82, [0.12, 1.0, 0.38],
                          np.where(t[..., None] < 0.92, [1.0, 0.72, 0.1], [0.25, 0.6, 1.0]))
        emission[allume] = teinte[allume] * 6.0

    # au-dessus des baies : chemin de câbles jaune puis mur sombre
    haut = y >= H_BAIE
    couleur[haut] = [0.03, 0.032, 0.03]
    chemin = (y > 2.42) & (y < 2.52)
    couleur[chemin] = [0.55, 0.42, 0.05]
    bord_chemin = (y > 2.52) & (y < 2.535)
    couleur[bord_chemin] = [0.2, 0.16, 0.03]
    # plinthe
    couleur[y <= 0.05] = [0.015, 0.015, 0.015]
    # liseré lumineux vert au pied des baies
    emission[(y > 0.012) & (y <= 0.03)] = [0.05, 0.75, 0.3]
    return couleur, emission


def sol(x, z):
    tx, tz = np.floor(x / 0.6), np.floor(z / 0.6)
    fx, fz = x / 0.6 - tx, z / 0.6 - tz
    var = hash2(tx.astype(np.int64) + 100, tz.astype(np.int64), 3)
    c = 0.52 + 0.06 * var
    couleur = np.stack([c, c * 1.01, c * 1.02], -1)
    joint = (fx < 0.012) | (fx > 0.988) | (fz < 0.012) | (fz > 0.988)
    couleur[joint] *= 0.45
    # dalles perforées dans l'allée froide
    perforee = (np.abs(x) < 0.6) & (tz.astype(np.int64) % 2 == 0)
    trous = perforee & ((np.sin(x * 260) * np.sin(z * 260)) > 0.55)
    couleur[trous] *= 0.4
    return couleur


def plafond(x, z):
    couleur = np.full(x.shape + (3,), 0.16)
    emission = np.zeros(x.shape + (3,))
    zz = np.mod(z, 3.0)
    lum = (np.abs(np.abs(x) - 0.45) < 0.035) & (zz < 2.85)
    emission[lum] = [3.9, 4.7, 4.3]
    cadre = (np.abs(np.abs(x) - 0.45) < 0.055) & ~lum
    couleur[cadre] = 0.25
    # dalles de plafond
    joint = (np.mod(x, 0.6) < 0.01) | (np.mod(z, 0.6) < 0.01)
    couleur[joint & ~lum] *= 0.5
    return couleur, emission


def tracer(ox, oy, oz, dx, dy, dz, profondeur=0):
    inf = np.full(dx.shape, np.inf)
    t_g = np.where(dx < -1e-6, (-A - ox) / np.where(dx == 0, 1, dx), inf)
    t_d = np.where(dx > 1e-6, (A - ox) / np.where(dx == 0, 1, dx), inf)
    t_sol = np.where(dy < -1e-6, (0 - oy) / np.where(dy == 0, 1, dy), inf)
    t_pl = np.where(dy > 1e-6, (HAUT - oy) / np.where(dy == 0, 1, dy), inf)
    t_fond = np.where(dz > 1e-6, (PROF - oz) / np.where(dz == 0, 1, dz), inf)
    ts = np.stack([t_g, t_d, t_sol, t_pl, t_fond])
    quoi = np.argmin(ts, 0)
    t = np.min(ts, 0)
    px, py, pz = ox + dx * t, oy + dy * t, oz + dz * t
    couleur = np.zeros(dx.shape + (3,))
    emission = np.zeros(dx.shape + (3,))
    led = np.zeros(dx.shape + (3,))
    n = [np.zeros_like(dx) for _ in range(3)]

    for cote, k in ((-1, 0), (1, 1)):
        m = quoi == k
        if m.any():
            c, e = face_baie(pz[m], py[m], cote)
            couleur[m], emission[m] = c, e
            led[m] = e
            n[0][m] = -cote
    m = quoi == 2
    couleur[m] = sol(px[m], pz[m])
    n[1][m] = 1
    m = quoi == 3
    c, e = plafond(px[m], pz[m])
    couleur[m], emission[m] = c, e
    n[1][m] = -1
    m = quoi == 4
    couleur[m] = [0.04, 0.045, 0.045]
    porte = m & (np.abs(px) < 0.45) & (py < 2.1)
    couleur[porte] = [0.08, 0.09, 0.09]
    n[2][m] = -1

    lum = eclairage(px, py, pz, n[0], n[1], n[2])
    rendu = couleur * lum[..., None] + emission
    # brouillard léger
    brume = 1 - np.exp(-t / 40)
    rendu = rendu * (1 - brume[..., None]) + np.array([0.05, 0.1, 0.075]) * brume[..., None]

    if profondeur == 0:
        reflet = np.zeros_like(rendu)
        m = quoi == 2
        if m.any():
            r = tracer(px[m], py[m] + 1e-4, pz[m], dx[m], -dy[m], dz[m], 1)
            fresnel = 0.1 + 0.35 * (1 - np.clip(-dy[m] * 4, 0, 1)) ** 3
            rendu[m] = rendu[m] * (1 - fresnel[..., None] * 0.4)
            reflet[m] = r * fresnel[..., None]
        brume_led = np.exp(-t / 30)[..., None]
        return rendu, reflet, led * brume_led
    return rendu


def ecrire_voyants(sortie, led):
    """Gabarit SVG superposé à l'image : quelques voyants des baies qui clignotent."""
    from pathlib import Path

    from scipy.ndimage import center_of_mass, label

    lum = led.max(-1)
    zones, nb = label(lum > 0.6)
    centres = center_of_mass(lum, zones, range(1, nb + 1))
    voyants = []
    for i, (cy, cx) in enumerate(centres):
        y, x = int(cy), int(cx)
        if 0 < x < L and 0 < y < H:
            taille = (zones == i + 1).sum() if nb < 4000 else 4
            voyants.append((cx, cy, led[y, x] / max(led[y, x].max(), 1e-6), taille))
    rng.shuffle(voyants)
    nom = Path(sortie).name
    gabarit = Path(__file__).resolve().parents[2] / "templates" / "includes" / f"animation_{nom}.html"
    lignes = ["{# Généré par scripts/rendus/datacenter.py : ne pas modifier à la main. #}",
              f'<svg class="voyants" viewBox="0 0 {L} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">']
    for cx, cy, c, taille in voyants[:70]:
        r = float(np.clip(np.sqrt(taille) * 0.9, 1.6, 5))
        hexa = "#%02x%02x%02x" % tuple(int(min(1, v) * 255) for v in c)
        lignes.append(f'<g style="--d:{rng.uniform(0, 8):.2f}s;--t:{rng.uniform(1.4, 4.5):.2f}s">'
                      f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r * 3:.1f}" fill="{hexa}" opacity=".3"/>'
                      f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="{hexa}"/></g>')
    lignes.append("</svg>")
    gabarit.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def main(sortie):
    camx, camy, camz = 0.18, 1.5, -0.6
    lacet, tangage = np.radians(-3.0), np.radians(-1.5)
    fov = np.radians(64)
    xs = (np.arange(W) + 0.5) / W * 2 - 1
    ys = 1 - (np.arange(HH) + 0.5) / HH * 2
    X, Y = np.meshgrid(xs * np.tan(fov / 2), ys * np.tan(fov / 2) * HH / W)
    dx, dy, dz = X, Y, np.ones_like(X)
    # tangage puis lacet
    dy, dz = dy * np.cos(tangage) - dz * np.sin(tangage), dy * np.sin(tangage) + dz * np.cos(tangage)
    dx, dz = dx * np.cos(lacet) + dz * np.sin(lacet), -dx * np.sin(lacet) + dz * np.cos(lacet)
    nrm = np.sqrt(dx * dx + dy * dy + dz * dz)
    img, reflet, led = tracer(np.full_like(dx, camx), np.full_like(dx, camy), np.full_like(dx, camz),
                         dx / nrm, dy / nrm, dz / nrm)

    # réduction (anti-crénelage), puis reflet du sol légèrement flou (sol satiné)
    img = img.reshape(H, SUR, L, SUR, 3).mean((1, 3))
    reflet = reflet.reshape(H, SUR, L, SUR, 3).mean((1, 3))
    led = led.reshape(H, SUR, L, SUR, 3).mean((1, 3))
    ecrire_voyants(sortie, led)
    img = img + gaussian_filter(reflet, (5, 2.5, 0))
    # halo lumineux des sources
    lumineux = np.clip(img - 0.9, 0, None)
    halo = sum(gaussian_filter(lumineux, (s, s, 0)) * p for s, p in ((3, .5), (10, .35), (35, .25)))
    img = img + halo
    # profondeur de champ légère au loin (haut du centre)
    yy, xx = np.mgrid[0:H, 0:L]
    flou = gaussian_filter(img, (1.6, 1.6, 0))
    centre = np.exp(-(((xx - L * 0.49) / (L * 0.12)) ** 2 + ((yy - H * 0.47) / (H * 0.15)) ** 2))
    img = img * (1 - centre[..., None] * 0.7) + flou * centre[..., None] * 0.7
    # exposition, courbe filmique, légère teinte froide-verte
    img *= 1.5
    img = img / (1 + img)
    img = img ** (1 / 1.9)
    img *= np.array([0.86, 1.04, 0.92])
    # vignettage et grain
    vign = 1 - 0.38 * (((xx - L / 2) / (L / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4
    img *= vign[..., None]
    img += rng.normal(0, 0.012, img.shape)
    img = np.clip(img, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8))
    im.save(sortie + ".webp", quality=80, method=6)
    im.save(sortie + ".jpg", quality=82, optimize=True, progressive=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datacenter")
