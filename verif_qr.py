# -*- coding: utf-8 -*-
"""
Relit les QR produits et verifie qu'ils rendent bien l'URL attendue.

Un QR habille qui "fait joli" mais ne se lit pas est un dechet imprime :
ce script existe pour qu'aucun style ne parte a l'impression sans preuve
de relecture.

On simule la chaine reelle -- rasterisation a la resolution d'impression,
flou (encre qui bave, mise au point approximative), reduction (photo prise
de loin) -- et on relit avec deux moteurs :

  zxing-cpp : le moteur de Google Lens / Android. C'est la reference, la
              plus proche de ce que fera un telephone sur le chantier.
  OpenCV    : moteur plus rustique, mauvais avec les modules non carres.
              Il echoue sur beaucoup de QR habilles pourtant lisibles en
              vrai ; on l'affiche a titre indicatif, pas comme verdict.

Usage:  python verif_qr.py [URL]
Sortie : code de retour non nul si zxing-cpp echoue quelque part.
"""
import glob
import io
import sys

import cairosvg
import cv2
import numpy as np
import zxingcpp
from PIL import Image, ImageFilter

URL = sys.argv[1] if len(sys.argv) > 1 else "https://nadirzouaoui.github.io/tcn-armoire/"


def read_zxing(pil):
    res = zxingcpp.read_barcode(pil.convert("L"))
    return res.text if res else ""


def read_opencv(pil):
    img = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    try:
        return cv2.QRCodeDetector().detectAndDecode(img)[0]
    except cv2.error:
        return ""


def conditions(path, mm):
    """(libelle, image) pour chaque condition de lecture simulee."""
    for dpi in (600, 300, 200):
        px = round(mm / 25.4 * dpi)
        raw = cairosvg.svg2png(url=path, output_width=px, output_height=px,
                               background_color="white")
        base = Image.open(io.BytesIO(raw))
        yield f"{dpi}dpi/net", base
        yield f"{dpi}dpi/flou1px", base.filter(ImageFilter.GaussianBlur(1.0))
        yield f"{dpi}dpi/flou2px", base.filter(ImageFilter.GaussianBlur(2.0))
        small = max(80, px // 4)
        yield f"{dpi}dpi/photo-de-loin", base.resize((small, small), Image.LANCZOS)


def main():
    failed = False
    for path in sorted(glob.glob("qr_dve_*.svg")) + sorted(glob.glob("qr_fiche_*.svg")):
        mm = float(path.split("_")[-1].replace("mm.svg", ""))
        zx_ko, cv_ko, total = [], [], 0
        for label, img in conditions(path, mm):
            total += 1
            if read_zxing(img) != URL:
                zx_ko.append(label)
            if read_opencv(img) != URL:
                cv_ko.append(label)
        verdict = "OK" if not zx_ko else "ECHEC " + ", ".join(zx_ko)
        failed = failed or bool(zx_ko)
        print(f"{path:22} zxing {total - len(zx_ko):2}/{total} {verdict:10}"
              f"   (opencv {total - len(cv_ko):2}/{total}, indicatif)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
