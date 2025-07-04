from django import forms
from .models import ImageUpload
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image', 'latitude', 'longitude']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]