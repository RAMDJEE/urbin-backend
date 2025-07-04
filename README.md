# Urbin – Système intelligent de détection de l’état des poubelles

Projet backend Django développé dans le cadre du MasterCamp Data à l’EFREI.  
Ce projet permet à des utilisateurs de se connecter, d’envoyer des images de poubelles, de détecter automatiquement si elles sont pleines ou vides à l’aide d’un extracteur de caractéristiques, et d’obtenir des points lorsque des poubelles pleines sont détectées.

## Fonctionnalités principales

- Authentification :
  - Inscription, connexion, déconnexion
  - Middleware pour restreindre l’accès aux utilisateurs connectés

- Téléversement d’images :
  - Upload avec latitude / longitude (à remplir manuellement dans le formulaire)
  - Extraction automatique des caractéristiques (taille, contraste, couleurs, contours…)
  - Prédiction (pleine / vide / incertain)
  - Attribution de points en cas de détection de poubelle pleine

- Préférences utilisateur :
  - Chaque utilisateur a un profil avec : langue, thème, nombre de points
  - Formulaire pour modifier ses préférences

## Structure du projet

```
urbin/
├── smartbin/             # Configuration du projet Django
├── detection/            # App principale
│   ├── models.py         # Modèles ImageUpload, UserProfile
│   ├── forms.py          # Formulaires d’upload et inscription
│   ├── views.py          # Logique backend
│   ├── templates/        # HTML (upload, login, register, profile…)
│   └── ai/
│       └── feature_extractor.py
├── media/uploads/        # Dossier des images uploadées
└── db.sqlite3            # Base de données locale
```

## Installation locale (développement)

1. Cloner le projet
```bash
git clone <repo_url>
cd urbin
```

2. Créer un environnement virtuel
```bash
python -m venv env
source env/bin/activate   # ou .\env\Scripts\activate sur Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Appliquer les migrations
```bash
python manage.py migrate
```

5. Créer un superutilisateur (facultatif)
```bash
python manage.py createsuperuser
```

6. Lancer le serveur
```bash
python manage.py runserver
```

7. Accéder à l’application :
- http://127.0.0.1:8000/upload/ → Upload d’image
- http://127.0.0.1:8000/profile/ → Modifier ses préférences
- http://127.0.0.1:8000/admin/ → Interface admin (si activée)

## Dépendances principales

- Django 5.x
- Pillow
- OpenCV (cv2)
- NumPy

## Remarques

- Les images sont stockées dans le dossier media/uploads/
- La détection se base sur un extracteur fait maison dans detection/ai/feature_extractor.py
- La prédiction actuelle utilise des règles simples définies dans create_classification_rules()

## Auteur

- Kenza Braham (backend)