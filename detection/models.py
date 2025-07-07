from django.db import models
from django.contrib.auth.models import User

class ImageUpload(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/")
    upload_date = models.DateTimeField(auto_now_add=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    annotation = models.CharField(
        max_length=10,
        choices=[
            ("pleine", "Pleine"),
            ("vide", "Vide"),
            ("auto", "Auto"),
            ("non", "Non annotée")
        ],
        default="non"
    )
    chemin = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    date_csv = models.CharField(max_length=50, null=True, blank=True)
    taille = models.CharField(max_length=50, null=True, blank=True)
    hauteur = models.CharField(max_length=50, null=True, blank=True)
    largeur = models.CharField(max_length=50, null=True, blank=True)
    pixels = models.CharField(max_length=50, null=True, blank=True)

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    LANG_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
    ]
    THEME_CHOICES = [
        ('light', 'Clair'),
        ('dark', 'Sombre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    langue = models.CharField(max_length=10, choices=LANG_CHOICES, default='fr')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    points = models.PositiveIntegerField(default=0)  # 1 point par photo pleine

    def __str__(self):
        return f"Profil de {self.user.username}"
    
class CustomUser(AbstractUser):
    theme = models.CharField(max_length=10, default='light')