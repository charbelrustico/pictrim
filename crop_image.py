"""
Script de crop automatique.

Contexte : la photo contient un grand fond blanc, et le contenu utile
se trouve dans le coin supérieur gauche. Ce script :

1. Détecte automatiquement la zone "non blanche" (le contenu).
2. Ajoute une marge de sécurité autour de cette zone.
3. Agrandit le crop si besoin pour respecter une taille minimale
   (1500 x 1000 px par défaut) — un crop ne peut jamais AUGMENTER
   la taille d'origine, donc si l'image de base est plus petite que
   la taille minimale demandée, le script préviendra au lieu de
   produire un résultat trompeur.

Dépendances : Pillow (pip install pillow --break-system-packages)
"""

from PIL import Image, ImageChops
import sys
import os


def find_content_bbox(img: Image.Image, tolerance: int = 245):
    """
    Trouve la boîte englobante (bounding box) du contenu non-blanc.
    tolerance : en dessous de cette valeur (0-255) un pixel est considéré
    comme "contenu" plutôt que "fond blanc". Augmente-la si le fond
    n'est pas parfaitement blanc (ex: blanc cassé, léger bruit JPEG).
    """
    gray = img.convert("L")  # niveaux de gris, plus simple à seuiller
    # Crée une image de référence toute blanche, puis calcule la différence
    bg = Image.new("L", gray.size, 255)
    diff = ImageChops.difference(gray, bg)
    # Seuillage : tout pixel dont la différence dépasse (255 - tolerance)
    # est considéré comme du contenu
    threshold = 255 - tolerance
    mask = diff.point(lambda p: 255 if p > threshold else 0)
    bbox = mask.getbbox()  # (left, upper, right, lower) ou None si tout blanc
    return bbox


def expand_bbox_to_min_size(bbox, img_size, min_width=1500, min_height=1000, margin=40):
    """
    Prend la bbox du contenu détecté, ajoute une marge, puis l'étend
    (sans dépasser les bords de l'image) pour respecter min_width x min_height.
    """
    img_w, img_h = img_size
    left, upper, right, lower = bbox

    # Ajout d'une marge autour du contenu détecté
    left = max(0, left - margin)
    upper = max(0, upper - margin)
    right = min(img_w, right + margin)
    lower = min(img_h, lower + margin)

    # Vérifie si l'image source est assez grande pour atteindre le minimum
    if img_w < min_width or img_h < min_height:
        raise ValueError(
            f"Image source trop petite ({img_w}x{img_h}) pour garantir "
            f"un crop de {min_width}x{min_height}. Un crop ne peut pas "
            f"agrandir l'image — il faudrait upscaler (perte de qualité)."
        )

    cur_w = right - left
    cur_h = lower - upper

    # Si la largeur du crop est trop petite, on l'étend symétriquement
    if cur_w < min_width:
        deficit = min_width - cur_w
        left -= deficit // 2
        right += deficit - deficit // 2
        # Recale si on sort des bords de l'image
        if left < 0:
            right -= left  # décale à droite
            left = 0
        if right > img_w:
            left -= (right - img_w)
            right = img_w
            left = max(0, left)

    # Même logique pour la hauteur
    if cur_h < min_height:
        deficit = min_height - cur_h
        upper -= deficit // 2
        lower += deficit - deficit // 2
        if upper < 0:
            lower -= upper
            upper = 0
        if lower > img_h:
            upper -= (lower - img_h)
            lower = img_h
            upper = max(0, upper)

    return (int(left), int(upper), int(right), int(lower))


def crop_image(input_path, output_path, min_width=1500, min_height=1000,
                margin=40, tolerance=245):
    img = Image.open(input_path)
    img = img.convert("RGB")  # évite les soucis de mode (RGBA, CMYK, etc.)

    bbox = find_content_bbox(img, tolerance=tolerance)
    if bbox is None:
        raise ValueError("Aucun contenu détecté : l'image semble entièrement blanche.")

    final_bbox = expand_bbox_to_min_size(
        bbox, img.size, min_width=min_width, min_height=min_height, margin=margin
    )

    cropped = img.crop(final_bbox)
    cropped.save(output_path)

    print(f"Image source     : {img.size[0]}x{img.size[1]}")
    print(f"Contenu détecté  : {bbox}")
    print(f"Zone finale crop : {final_bbox}")
    print(f"Taille du résultat : {cropped.size[0]}x{cropped.size[1]}")
    print(f"Sauvegardé dans  : {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python crop_image.py <chemin_image_entree> [chemin_image_sortie]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_crop{ext}"

    crop_image(input_path, output_path)
