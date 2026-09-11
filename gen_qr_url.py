# -*- coding: utf-8 -*-
"""
QR du cartouche -> URL de la fiche installation.
Usage:  python gen_qr_url.py https://<votre-domaine>/tcn/
"""
import sys, segno

URL = sys.argv[1] if len(sys.argv) > 1 else "https://nadirzouaoui.github.io/tcn-armoire/"


def make(url=URL, error="q"):
    """ECC Q (25 %) : tolere une impression salie ou pliee en chantier."""
    return segno.make(url, error=error)


def draw_qr(ax, x0, y0, size, url=URL, error="q", quiet=4, color="black"):
    """QR vectoriel (rectangles matplotlib) dans le repere du plan.
    quiet=4 modules : zone silencieuse normative, indispensable au scan."""
    from matplotlib.patches import Rectangle
    qr = make(url, error)
    m = qr.matrix
    n = len(m)
    px = size / (n + 2 * quiet)
    ax.add_patch(Rectangle((x0, y0), size, size, facecolor="white", edgecolor="none", zorder=50))
    for r, row in enumerate(m):
        for c, bit in enumerate(row):
            if bit:
                ax.add_patch(Rectangle((x0 + (quiet + c) * px,
                                        y0 + (quiet + n - 1 - r) * px),
                                       px * 1.02, px * 1.02,
                                       facecolor=color, edgecolor="none", zorder=51))
    return n, qr.version


if __name__ == "__main__":
    qr = make()
    n = len(qr.matrix)
    print(f"URL     : {URL}")
    print(f"version : {qr.version}  matrice {n}x{n}  ECC {qr.error}")
    for mm in (25, 30, 40):
        print(f"  {mm} mm sur le plan -> {mm/(n+8):.2f} mm/module")
    qr.save("qr_fiche.svg", scale=10, border=4)
    qr.save("qr_fiche.png", scale=14, border=4)
