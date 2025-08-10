from PIL import Image, ImageDraw, ImageFont

# Taille de l'image (largeur, hauteur)
img = Image.new('RGB', (600, 300), color=(255, 255, 255))

draw = ImageDraw.Draw(img)

# Texte à afficher
text = "💡 Pourquoi analyser ses données ?\n\n" \
       "- Prendre de meilleures décisions\n" \
       "- Mieux comprendre son activité\n" \
       "- Identifier ce qui fonctionne ou non\n" \
       "- Gagner en autonomie"

# Charger une police système
try:
    font = ImageFont.truetype("arial.ttf", 18)
except:
    font = ImageFont.load_default()

# Afficher le texte
draw.text((30, 40), text, fill=(0, 0, 0), font=font)

# Sauvegarder dans le dossier assets/
img.save("assets/info.png")
print("✅ Image info.png créée dans le dossier assets/")
