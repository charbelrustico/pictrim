"""
Script de redimensionnement (scale) d'image en préservant la qualité.

Point important à comprendre (ça sert pour la suite de ta carrière) :
--------------------------------------------------------------------
Il y a une différence fondamentale entre :

- REDUIRE une image (downscale) : on peut le faire avec une perte de
  qualité quasi nulle si on utilise un bon algorithme de rééchantillonnage
  (LANCZOS). On a "trop" d'information de départ, donc on peut la
  condenser proprement.

- AGRANDIR une image (upscale) : il est MATHEMATIQUEMENT IMPOSSIBLE de
  créer de la vraie information qui n'existait pas dans l'image d'origine.
  Un algorithme classique (LANCZOS, BICUBIC...) ne fait qu'interpoler,
  c'est-à-dire "deviner" les pixels manquants en lissant les pixels
  voisins. Résultat : ça reste correct visuellement jusqu'à un certain
  facteur (x1.5, x2), mais au-delà l'image devient floue/molle.

  Pour un vrai upscale "intelligent" (qui invente des détails plausibles),
  il faut un modèle d'IA dédié (ex: Real-ESRGAN, waifu2x, Topaz Gigapixel).
  Ce script fait le redimensionnement classique de haute qualité — pas
  de l'IA generative — donc c'est le meilleur résultat "sans magie".

Ce script :
1. Redimensionne en conservant le ratio d'aspect (pas de déformation).
2. Utilise LANCZOS, le meilleur filtre de rééchantillonnage de Pillow.
3. Peut cibler soit une taille précise, soit un facteur d'échelle.
4. Sauvegarde en PNG (sans perte) ou en JPEG haute qualité selon le besoin.

Dépendances : Pillow (pip install pillow --break-system-packages)
"""

from PIL import Image
import sys
import os


def scale_image(input_path, output_path=None, scale_factor=None,
                 target_width=None, target_height=None, quality=95):
    """
    Redimensionne une image en conservant le ratio d'aspect.

    Trois façons de spécifier la taille cible (une seule à la fois) :
    - scale_factor   : ex. 2.0 pour doubler la taille
    - target_width   : largeur cible en pixels (hauteur calculée automatiquement)
    - target_height  : hauteur cible en pixels (largeur calculée automatiquement)
    """
    img = Image.open(input_path)
    orig_w, orig_h = img.size

    if sum(x is not None for x in [scale_factor, target_width, target_height]) != 1:
        raise ValueError(
            "Précise exactement UN des paramètres : scale_factor, "
            "target_width ou target_height."
        )

    if scale_factor is not None:
        new_w = round(orig_w * scale_factor)
        new_h = round(orig_h * scale_factor)
    elif target_width is not None:
        ratio = target_width / orig_w
        new_w = target_width
        new_h = round(orig_h * ratio)
    else:  # target_height
        ratio = target_height / orig_h
        new_h = target_height
        new_w = round(orig_w * ratio)

    is_upscale = (new_w * new_h) > (orig_w * orig_h)

    # LANCZOS = meilleur filtre de rééchantillonnage disponible dans Pillow,
    # que ce soit pour réduire ou agrandir.
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_scaled{ext}"

    ext = os.path.splitext(output_path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        resized = resized.convert("RGB")
        resized.save(output_path, quality=quality, optimize=True)
    elif ext == ".png":
        resized.save(output_path, optimize=True)
    else:
        resized.save(output_path)

    print(f"Image source      : {orig_w}x{orig_h}")
    print(f"Image redimensionnée : {new_w}x{new_h}")
    print(f"Type d'opération   : {'AGRANDISSEMENT (upscale)' if is_upscale else 'RÉDUCTION (downscale)'}")
    if is_upscale:
        factor = (new_w * new_h) / (orig_w * orig_h)
        print(
            f"⚠️  Attention : agrandissement x{factor**0.5:.2f} environ. "
            f"Au-delà de x1.5/x2, l'image peut paraître plus douce/floue : "
            f"c'est une limite mathématique du rééchantillonnage classique, "
            f"pas un bug du script."
        )
    print(f"Sauvegardé dans    : {output_path}")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage :\n"
            "  python scale_image.py <image_entree> --factor 2.0\n"
            "  python scale_image.py <image_entree> --width 1920\n"
            "  python scale_image.py <image_entree> --height 1080\n"
            "  (ajoute [image_sortie] en dernier argument si tu veux choisir le nom)"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    args = sys.argv[2:]

    scale_factor = target_width = target_height = None
    output_path = None

    i = 0
    while i < len(args):
        if args[i] == "--factor":
            scale_factor = float(args[i + 1])
            i += 2
        elif args[i] == "--width":
            target_width = int(args[i + 1])
            i += 2
        elif args[i] == "--height":
            target_height = int(args[i + 1])
            i += 2
        else:
            output_path = args[i]
            i += 1

    scale_image(
        input_path,
        output_path=output_path,
        scale_factor=scale_factor,
        target_width=target_width,
        target_height=target_height,
    )
