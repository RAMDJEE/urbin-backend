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
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from detection.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ImageUpload
from .ai.demo_extraction import extract_features, classify_image, load_rules
from django.conf import settings
import uuid


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
@csrf_exempt
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
@csrf_exempt
def login_user(request):
    print("login_user a bien été appelé", request.method)
    data = request.data
    email = data.get('email')
    password = data.get('password')

    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user)  # <- Ce login crée une session côté Django
        profile = UserProfile.objects.get(user=user)
        return Response({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'points': profile.points,
            'theme': profile.theme,
            "langue": profile.langue,
        })
    else:
        return Response({'error': 'Identifiants invalides.'}, status=status.HTTP_401_UNAUTHORIZED)

    

@api_view(['GET'])
def bins_data(request):
    bins = ImageUpload.objects.all()

    stats = {
        "total": bins.count(),
        "pleine": bins.filter(annotation="pleine").count(),
        "vide": bins.filter(annotation="vide").count(),
        "inconnu": bins.filter(annotation="auto").count(),
    }

    bins_list = []
    for b in bins:
        bins_list.append({
            "id": b.id,
            "chemin": b.chemin,
            "type": b.type,
            "date": b.date_csv,
            "taille": b.taille,
            "hauteur": b.hauteur,
            "largeur": b.largeur,
            "pixels": b.pixels,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "classe": b.annotation,
        })

    return Response({"stats": stats, "bins": bins_list})

class UpdateUserView(APIView):
    def patch(self, request):
        theme = request.data.get('theme')

        if not theme:
            return Response({'error': 'Missing theme'}, status=400)

        try:
            if not request.user or request.user.is_anonymous:
                return Response({'error': 'Utilisateur non connecté'}, status=401)

            profile = UserProfile.objects.get(user=request.user)
            profile.theme = theme
            profile.save()
            return Response({'status': 'theme updated', 'theme': theme})
        except Exception as e:
            print("Erreur update-user:", e)
            return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    profile = user.userprofile
    return Response({
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "points": profile.points,
        "theme": profile.theme,
        "langue": profile.langue,
    })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    profile = request.user.userprofile
    theme = request.data.get("theme")
    langue = request.data.get("langue")  
    points = request.data.get("points")  

    updated = {}

    if theme in ['dark', 'light']:
        profile.theme = theme
        updated['theme'] = theme

    if langue in ['fr', 'en']:
        profile.langue = langue
        updated['langue'] = langue

    if points is not None:
        try:
            profile.points += int(points)  
            updated['points'] = profile.points
        except Exception as e:
            return Response({"error": "points doit être un nombre"}, status=400)

    if updated:
        profile.save()
        return Response({"message": "Updated", **updated})

    return Response({"error": "No valid fields to update"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_image_api(request):
    # On suppose que tu envoies bien tous les champs dans le FormData JS
    try:
        image_file = request.FILES.get('image')

        if not image_file:
            return Response({'error': 'Image manquante.'}, status=400)

        # Tu crées l'objet manuellement :
        obj = ImageUpload()
        obj.uploader = request.user
        obj.image = image_file
        obj.annotation = request.POST.get('annotation')
        obj.latitude = request.POST.get('latitude')
        obj.longitude = request.POST.get('longitude')
        obj.taille = request.POST.get('taille')
        obj.largeur = request.POST.get('largeur')
        obj.hauteur = request.POST.get('hauteur')
        obj.pixels = request.POST.get('pixels')
        obj.type = request.POST.get('type')
        # Tu ajoutes ici tous les champs utiles

        obj.save()

        return Response({'status': 'success'}, status=201)

    except Exception as e:
        print("Erreur upload_image_api:", e)
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def analyze_image_api(request):
    image_file = request.FILES.get('image')

    if not image_file:
        return Response({'error': 'Image manquante.'}, status=400)

    # Sauvegarder temporairement l’image
    temp_filename = f"{uuid.uuid4()}.jpg"
    temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)

    try:
        # Analyse de l’image
        features = extract_features(temp_path)
        rules = load_rules()
        classification_result = classify_image(features, rules)

        # Supprimer le fichier temporaire
        os.remove(temp_path)

        # Retourner le résultat
        return Response({
            "status": "pleine" if classification_result['classification'] == "Poubelle pleine" else "vide",
            "score": classification_result['fullness_score'],
            "details": classification_result['validation_details']
        })

    except Exception as e:
        print("Erreur classification:", e)
        return Response({'error': str(e)}, status=500)