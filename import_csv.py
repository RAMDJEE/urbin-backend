import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "urbin.settings")
django.setup()

from detection.models import ImageUpload, User

CSV_PATH = "Data/csv/df_fichiers_img.csv"

uploader = User.objects.first()
if not uploader:
    print("Aucun utilisateur trouvé. Création d'un utilisateur par défaut...")
    uploader = User.objects.create_user(username="default", password="default")

with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        lat = float(row["latitude"]) if row["latitude"] else None
        lon = float(row["longitude"]) if row["longitude"] else None
        classe = row["classe"].strip().lower()

        if classe == "clean":
            annotation = "vide"
        elif classe == "dirty":
            annotation = "pleine"
        else:
            annotation = "auto"

        img = ImageUpload.objects.create(
            uploader=uploader,
            image="uploads/fake.jpg",
            latitude=lat,
            longitude=lon,
            annotation=annotation,
            chemin=row["chemin"],
            type=row["type"],
            date_csv=row["date"],
            taille=row["taille"],
            hauteur=row["hauteur"],
            largeur=row["largeur"],
            pixels=row["pixels"],
        )
        count += 1
        if count % 100 == 0:
            print(f"{count} enregistrements importés...")

print("Import terminé!")
