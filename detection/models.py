from django.db import models
from django.contrib.auth.models import User

class ImageUpload(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/")
    upload_date = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    annotation = models.CharField(max_length=10, choices=[("pleine", "Pleine"), ("vide", "Vide"), ("auto", "Auto"), ("non", "Non annotée")], default="non")
    # Features extraites
    file_size_kb = models.FloatField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    avg_r = models.FloatField(null=True, blank=True)
    avg_g = models.FloatField(null=True, blank=True)
    avg_b = models.FloatField(null=True, blank=True)
    contrast = models.FloatField(null=True, blank=True)
    contours = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.image.name} - {self.annotation}"
    


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