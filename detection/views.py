from django.shortcuts import render, redirect
from .forms import ImageUploadForm, RegisterForm
from .models import ImageUpload
from detection.ai.feature_extractor import ImageFeatureExtractor, create_classification_rules
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import os
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
#from detection.gps_utils import extract_gps_from_image


@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.uploader = request.user
            instance.save()
            
            extractor = ImageFeatureExtractor()
            img_path = instance.image.path
            
            # Extraire coordonnées GPS si EXIF disponibles
            #gps = extract_gps_from_image(img_path)
            #if gps:
            #   instance.latitude, instance.longitude = gps

            try:
                features = extractor.extract_all_features(img_path)
                instance.file_size_kb = features.get('file_size_kb')
                instance.width = features.get('width')
                instance.height = features.get('height')
                instance.avg_r = features.get('mean_red')
                instance.avg_g = features.get('mean_green')
                instance.avg_b = features.get('mean_blue')
                instance.contrast = features.get('contrast_range')
                instance.contours = features.get('total_contours')
                instance.annotation = create_classification_rules(features)
            except Exception as e:
                print(f"Erreur d'extraction: {e}")

            instance.save()
            if instance.annotation == "pleine":
                profile = request.user.userprofile
                profile.points += 1
                profile.save()
            return redirect('image_success')
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_image')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload_image')
        else:
            return render(request, 'login.html', {'error': 'Identifiants invalides'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello from Django REST API!'})



@api_view(['POST'])
def register_user(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if User.objects.filter(username=email).exists():
        return Response({'error': 'Cet email est déjà utilisé.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    UserProfile.objects.create(user=user)  # Crée aussi le profil

    return Response({'message': 'Utilisateur créé avec succès.'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    user = authenticate(username=email, password=password)
    if user is not None:
        profile = UserProfile.objects.get(user=user)
        return Response({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'points': profile.points
        })
    else:
        return Response({'error': 'Identifiants invalides.'}, status=status.HTTP_401_UNAUTHORIZED)
