# Pictrim

Deux scripts Python indépendants basés sur [Pillow](https://pillow.readthedocs.io/) pour recadrer et redimensionner des images sans perte de qualité inutile :

| Script | Rôle |
|---|---|
| `crop_image.py` | Détecte automatiquement un contenu placé dans le coin supérieur gauche d'un fond blanc, et le recadre en garantissant une taille minimale (1500x1000 px par défaut). |
| `scale_image.py` | Redimensionne une image (agrandir ou réduire) en conservant le ratio d'aspect et la meilleure qualité possible. |

## Installation

Les deux scripts n'ont qu'une seule dépendance :

```bash
pip install pillow --break-system-packages
```

## `crop_image.py`

### Ce qu'il fait

1. Repère la zone non blanche de l'image (le contenu utile).
2. Ajoute une marge de sécurité autour.
3. Étend la zone de crop si besoin pour atteindre la taille minimale demandée, sans jamais dépasser les bords de l'image d'origine.

### Utilisation

```bash
python crop_image.py <image_entree> [image_sortie]
```

Si `image_sortie` n'est pas précisé, le script crée automatiquement `<nom>_crop.<extension>`.

### Exemple

```bash
python crop_image.py photo.jpg
python crop_image.py photo.jpg resultat.jpg
```

### Paramètres ajustables (dans le code)

- `min_width`, `min_height` : taille minimale du crop final (défaut 1500x1000).
- `margin` : marge en pixels autour du contenu détecté (défaut 40).
- `tolerance` : sensibilité de détection du "blanc" (défaut 245). À augmenter si le fond n'est pas parfaitement blanc (léger bruit JPEG, blanc cassé).

### Limite à connaître

Un crop ne peut jamais **agrandir** une image. Si l'image source est plus petite que la taille minimale demandée, le script lève une erreur explicite plutôt que de produire un résultat trompeur.

## `scale_image.py`

### Ce qu'il fait

Redimensionne l'image avec le filtre `LANCZOS` (le meilleur algorithme de rééchantillonnage classique disponible dans Pillow), en conservant toujours le ratio d'aspect d'origine.

### Utilisation

```bash
python scale_image.py <image_entree> --factor 2.0
python scale_image.py <image_entree> --width 1920
python scale_image.py <image_entree> --height 1080
```

Un seul de ces trois paramètres doit être précisé à la fois. La dimension non précisée est calculée automatiquement pour garder le ratio d'origine.

Pour choisir le nom du fichier de sortie, ajoute-le en dernier argument :

```bash
python scale_image.py photo.jpg --factor 2.0 resultat.jpg
```

### Limite à connaître

Réduire une image (downscale) perd très peu de qualité avec un bon algorithme. **Agrandir une image (upscale) ne peut pas inventer de l'information qui n'existait pas** : au-delà d'un facteur x1.5/x2 environ, le résultat peut paraître plus doux ou flou. C'est une limite mathématique du rééchantillonnage classique, pas un bug.

Pour un upscale "intelligent" qui génère de vrais détails plausibles, il faudrait un modèle d'IA dédié (Real-ESRGAN, Topaz Gigapixel...), ce qui sort du cadre de ce script.
