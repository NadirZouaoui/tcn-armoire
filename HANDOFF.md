# Armoire d'injection Tetra Canette — fiche QR

## Objet
Étiquette QR à coller sur l'armoire d'injection. Le QR pointe vers une page HTML
mobile qui affiche les caractéristiques de l'installation. Pas de table des
matières, pas de cartouche de plan : c'est une fiche d'armoire, pas un plan.

## Pourquoi une URL et pas du texte brut
Un QR à charge utile texte ne déclenche rien sur l'appareil photo iOS (aucune
bannière, aucun geste possible). Seule une URL `https://` donne une action
cliquable sur iOS et Android. Les URI `data:text/html;base64,…` sont bloquées
par les navigateurs mobiles en navigation de premier niveau — cette voie est
définitivement fermée, l'hébergement est obligatoire.

## Fichiers
| Fichier | Rôle |
|---|---|
| `index.html` | La fiche. Autonome, ~6 ko, mobile-first, mode sombre inclus. À la racine : c'est elle que sert l'URL du QR. |
| `qr_fiche.svg` / `.png` | QR pointant vers l'URL de production, sans dimension physique imposée. |
| `qr_fiche_30mm.svg`, `_35mm`, `_40mm` | Le même QR, mais dimensionné en mm : le carré complet (code + zone silencieuse) mesure exactement 30, 35 ou 40 mm. **Ce sont ces fichiers-là qu'on envoie à l'imprimeur** — aucune mise à l'échelle à refaire. |
| `qr_fiche_600dpi.png` | Version raster 600 dpi, pour un flux d'impression qui refuse le vectoriel. |
| `qr_dve_35mm.svg`, `_40mm` | **QR habille DV** : modules fusionnes en gouttes, degrade bleu du logo, coeurs de reperage ronds, logo au centre. C'est la version a coller sur l'armoire. |
| `logo_dve.png` | Le logo, embarque en base64 dans les SVG habilles. |
| `gen_qr_style.py` | Genere les QR habilles. |
| `verif_qr.py` | Relit tous les QR produits et echoue si l'un d'eux ne rend pas l'URL. |
| `gen_qr_url.py` | Régénère le QR. `python gen_qr_url.py <URL>` (dépend de `segno` ; `matplotlib` seulement pour `draw_qr`, importé à la demande). |
| `.nojekyll` | Désactive Jekyll sur Pages : le HTML est servi tel quel. |

## Déploiement (GitHub Pages)
Dépôt public, `index.html` à la racine, Pages sur `main` / `(root)`.

URL de production :

    https://nadirzouaoui.github.io/tcn-armoire/

Après tout changement d'URL, régénérer le QR :

    python gen_qr_url.py https://nadirzouaoui.github.io/tcn-armoire/

### Taille d'impression
Cette URL sort en **version 4 (33 × 33 modules)**, ECC Q :

| Côté imprimé | mm / module |
|---|---|
| 25 mm | 0,61 |
| 30 mm | 0,73 |
| 35 mm | 0,85 |
| 40 mm | 0,98 |

Utiliser `qr_fiche_35mm.svg`. Viser **35 mm de côté** pour tenir la marge de ~0,8 mm par module sur une porte
d'armoire empoussiérée ; 30 mm reste scannable sur une étiquette propre. Zone
silencieuse blanche de 4 modules conservée — ne pas rogner.

## Intégration CAD (si le QR va aussi sur le plan)
`gen_qr_url.draw_qr(ax, x0, y0, size, url)` dessine la matrice en `Rectangle`
matplotlib : le PDF reste vectoriel, et le rendu est correct sous
`ax.invert_yaxis()`. Recouvrement de 2 % par module pour éviter les traits
blancs à l'impression.

## Points ouverts (à trancher avant impression)
- **Puissance AC 600 kVA** : suppose 4 × SUN2000-150K-MG0. Le plan ne nomme ni
  le modèle ni la puissance AC. À confirmer.
- **Stockage** : puissance et capacité inconnues. Seule donnée : 3 arrivées 250 A.
- **Les deux départs 800 A** : en parallèle sur un même jeu de barres, ou
  séparés (PV d'un côté, stockage de l'autre) ? Change le libellé de la fiche.
- **Injection simultanée** : PV ≈ 866 A sous 400 V. Vérifier PV + BESS en
  simultané contre 2 × 800 A et contre la puissance souscrite au PDL.
- **Couleurs onduleur** : les quatre pastilles de la fiche sont arbitraires.
  Les aligner sur le repérage couleur du plan de calepinage indice K.
- **Confidentialité** : un repo public rend la page publique (client, puissance,
  calibres d'armoire). Envisager le domaine DVE si c'est un sujet.

## QR habille : ce qu'il a fallu respecter

Le style n'est pas gratuit, deux contraintes sont sorties de la mesure et
non de l'oeil.

**Les motifs de reperage ne supportent pas d'etre trop arrondis.** Le carre
noir EXTERIEUR de 7x7 cesse d'etre reconnu au-dela d'environ 1,1 module de
rayon : a 1,5 le QR devient totalement illisible, alors qu'il reste superbe
a l'ecran. Le code est donc fixe a `R_FINDER_OUT = 0.9`. En revanche le
carre blanc median et le coeur central tolerent l'arrondi complet : c'est
le coeur rond qui donne le style, et il ne coute rien.

**ECC H au lieu de Q**, parce que la plaque du logo masque des modules. Le
QR passe en version 5 (37x37) : plus dense que la version 4 du QR simple,
d'ou une taille d'impression minimale plus grande.

| | QR simple | QR habille |
|---|---|---|
| Version | 4 (33x33), ECC Q | 5 (37x37), ECC H |
| Taille mini | 30 mm | **35 mm** |
| mm/module a 35 mm | 0,854 | 0,778 |

30 mm n'est volontairement pas genere pour la version habillee : a cette
taille elle commence a echouer aux relectures degradees, la ou le QR simple
passe encore.

## Verification avant impression
    python verif_qr.py

Le script rasterise chaque SVG a 600/300/200 dpi, applique un flou et une
reduction (encre qui bave, photo prise de loin), et relit tout avec
**zxing-cpp**, le moteur de Google Lens et d'Android. Il rend un code de
retour non nul au premier echec. Etat actuel : 12/12 pour chaque fichier.

Le script affiche aussi le score OpenCV, beaucoup plus bas sur les QR
habilles (5/12). Ce n'est **pas** un signal d'alarme : le detecteur
d'OpenCV gere mal les modules non carres et echoue sur des codes que tout
telephone lit sans hesiter. Il est la comme garde-fou pessimiste.

Dependances : `segno`, `pillow` pour generer ; `cairosvg`, `zxing-cpp`,
`opencv-python-headless`, `numpy` pour verifier.
