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
| `qr_fiche.svg` / `.png` | QR pointant vers l'URL de production. Le SVG est le fichier à placer sur l'étiquette. |
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

Viser **35 mm de côté** pour tenir la marge de ~0,8 mm par module sur une porte
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
