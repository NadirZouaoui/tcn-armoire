# -*- coding: utf-8 -*-
"""
QR habille aux couleurs DV Energy Solutions, logo au centre.

Usage:  python gen_qr_style.py [URL]

Sortie : qr_dve_<taille>mm.svg (vectoriel, cote en mm hors tout) + un PNG
600 dpi de controle. Le SVG est le fichier d'impression.

Deux choix techniques qui ne sont pas cosmetiques :
  - ECC H (30 % de redondance) parce que la plaque du logo masque des
    modules. Le QR reste lisible tant que la plaque reste petite.
  - zone silencieuse de 4 modules conservee : sans elle, beaucoup de
    lecteurs ne trouvent pas le code du tout.
"""
import base64, pathlib, sys
import segno

URL = sys.argv[1] if len(sys.argv) > 1 else "https://nadirzouaoui.github.io/tcn-armoire/"

QUIET = 4                 # modules de zone silencieuse
INK = "#0E1A33"           # navy du cartouche de la fiche
GRAD_FROM = "#2A7FBE"     # bleu du V du logo, assombri pour tenir 4:1 sur blanc
GRAD_TO = "#0E1A33"
LOGO = pathlib.Path(__file__).with_name("logo_dve.png")

DOT = 0.92                # diametre du module, en fraction du pas

# Rayons d'arrondi des motifs de reperage, en modules. Mesure faite au
# decodeur (voir verif_qr.py) : au-dela de ~1,1 module sur le carre
# EXTERIEUR de 7x7, le motif cesse d'etre reconnu et le QR devient
# illisible. Le carre blanc median et le coeur, eux, tolerent l'arrondi
# complet -- d'ou le coeur rond, qui fait tout le style, pour zero risque.
R_FINDER_OUT = 0.9        # plafond mesure : 1.1
R_FINDER_MID = 0.7
R_FINDER_IN = 1.5         # 1.5 sur un carre de 3 modules = disque
PLATE_W = 10.4            # plaque blanche du logo, en modules
LOGO_PAD = 0.7            # marge blanche autour du logo, en modules
CARVE = 0.55              # modules retires en plus autour de la plaque : un
                          # module dont le centre est hors plaque deborde
                          # quand meme dessus avec son disque, et vient
                          # mordre le logo.


def contrast_on_white(hex_color):
    """Rapport de contraste WCAG sur fond blanc. En dessous de ~3:1 un
    lecteur de QR commence a confondre module clair et module sombre."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
    return 1.05 / (lum + 0.05)


def finder_cells(n):
    """Les 3 x 49 modules des motifs de reperage, rendus a part."""
    out = set()
    for oy, ox in ((0, 0), (0, n - 7), (n - 7, 0)):
        for dy in range(7):
            for dx in range(7):
                out.add((oy + dy, ox + dx))
    return out


def build_svg(url, mm, error="h"):
    qr = segno.make(url, error=error)
    m = [list(row) for row in qr.matrix]
    n = len(m)
    total = n + 2 * QUIET
    step = mm / total                     # mm par module
    skip = finder_cells(n)

    # Plaque du logo : rectangle centre, dimensionne sur le ratio du logo.
    from PIL import Image
    with Image.open(LOGO) as im:
        ratio = im.size[0] / im.size[1]
    logo_w = PLATE_W - 2 * LOGO_PAD
    plate_h = logo_w / ratio + 2 * LOGO_PAD
    cx, cy = n / 2, n / 2
    px0, px1 = cx - PLATE_W / 2, cx + PLATE_W / 2
    py0, py1 = cy - plate_h / 2, cy + plate_h / 2

    def under_plate(r, c):
        return (px0 - 0.5 - CARVE <= c <= px1 - 0.5 + CARVE
                and py0 - 0.5 - CARVE <= r <= py1 - 0.5 + CARVE)

    def dark(r, c):
        return (0 <= r < n and 0 <= c < n and m[r][c]
                and (r, c) not in skip and not under_plate(r, c))

    def X(c):  # centre du module -> mm
        return (QUIET + c + 0.5) * step

    parts = []
    rr = DOT * step / 2

    # Modules de donnees : un disque par module, plus un pont vers le voisin
    # de droite et du bas quand il est sombre. Les modules voisins fusionnent
    # donc en gouttes arrondies, sans casser la grille que lit le decodeur.
    for r in range(n):
        for c in range(n):
            if not dark(r, c):
                continue
            parts.append(f'<circle cx="{X(c):.4f}" cy="{X(r):.4f}" r="{rr:.4f}"/>')
            if dark(r, c + 1):
                parts.append(
                    f'<rect x="{X(c):.4f}" y="{X(r) - rr:.4f}" '
                    f'width="{step:.4f}" height="{2 * rr:.4f}"/>')
            if dark(r + 1, c):
                parts.append(
                    f'<rect x="{X(c) - rr:.4f}" y="{X(r):.4f}" '
                    f'width="{2 * rr:.4f}" height="{step:.4f}"/>')
            # Bloc plein 2x2 : les deux ponts se croisent sans couvrir le
            # centre, ce qui laissait un losange blanc au milieu des aplats.
            if dark(r, c + 1) and dark(r + 1, c) and dark(r + 1, c + 1):
                parts.append(
                    f'<rect x="{X(c):.4f}" y="{X(r):.4f}" '
                    f'width="{step:.4f}" height="{step:.4f}"/>')
    dots = "\n".join(parts)

    # Motifs de reperage : anneau exterieur 7x7, blanc 5x5, coeur 3x3.
    finders = []
    for oy, ox in ((0, 0), (0, n - 7), (n - 7, 0)):
        x0, y0 = (QUIET + ox) * step, (QUIET + oy) * step
        s = 7 * step
        finders.append(
            f'<rect x="{x0:.4f}" y="{y0:.4f}" width="{s:.4f}" height="{s:.4f}" '
            f'rx="{R_FINDER_OUT * step:.4f}" fill="{INK}"/>'
            f'<rect x="{x0 + step:.4f}" y="{y0 + step:.4f}" '
            f'width="{5 * step:.4f}" height="{5 * step:.4f}" '
            f'rx="{R_FINDER_MID * step:.4f}" fill="#fff"/>'
            f'<rect x="{x0 + 2 * step:.4f}" y="{y0 + 2 * step:.4f}" '
            f'width="{3 * step:.4f}" height="{3 * step:.4f}" '
            f'rx="{R_FINDER_IN * step:.4f}" fill="{INK}"/>')

    b64 = base64.b64encode(LOGO.read_bytes()).decode()
    lx, ly = (QUIET + px0) * step, (QUIET + py0) * step
    plate = (
        f'<rect x="{lx:.4f}" y="{ly:.4f}" width="{PLATE_W * step:.4f}" '
        f'height="{plate_h * step:.4f}" rx="{1.1 * step:.4f}" fill="#fff"/>'
        f'<image x="{lx + LOGO_PAD * step:.4f}" y="{ly + LOGO_PAD * step:.4f}" '
        f'width="{logo_w * step:.4f}" height="{logo_w / ratio * step:.4f}" '
        f'href="data:image/png;base64,{b64}"/>')

    svg = f'''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{mm}mm" height="{mm}mm" viewBox="0 0 {mm} {mm}">
  <defs>
    <linearGradient id="dve" x1="0" y1="0" x2="{mm}" y2="{mm}"
                    gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{GRAD_FROM}"/>
      <stop offset="1" stop-color="{GRAD_TO}"/>
    </linearGradient>
  </defs>
  <rect width="{mm}" height="{mm}" fill="#fff"/>
  <g fill="url(#dve)">
{dots}
  </g>
  {"".join(finders)}
  {plate}
</svg>
'''
    return svg, qr, n


if __name__ == "__main__":
    print(f"contraste du bleu clair sur blanc : {contrast_on_white(GRAD_FROM):.2f}:1")
    # 30 mm n'est volontairement pas produit : a cette taille le QR habille
    # commence a echouer aux relectures degradees (voir verif_qr.py), la ou
    # le QR simple passe encore. Le style coute de la marge, on la reprend
    # en surface.
    for mm in (35, 40):
        svg, qr, n = build_svg(URL, mm)
        out = pathlib.Path(f"qr_dve_{mm}mm.svg")
        out.write_text(svg, encoding="utf-8")
        print(f"{out}  version {qr.version}  {n}x{n}  ECC {qr.error}  "
              f"{mm / (n + 2 * QUIET):.3f} mm/module")
