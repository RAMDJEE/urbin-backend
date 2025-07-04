import cv2
import numpy as np
import os
import json

def load_rules(json_path="rules.json"):
    try:
        with open(json_path, "r") as f:
            rules = json.load(f)
    except Exception as e:
        print("⚠️ Impossible de charger les règles, utilisation des valeurs par défaut.")
        print("Erreur :", e)
        rules = {
            "mean_color_threshold": 100,
            "area_threshold": 5000,
            "edge_density_threshold": 0.05,
            "texture_variance_threshold": 500,
            "dark_pixels_ratio_threshold": 0.4,
            "saturation_threshold": 30,
            "debris_contour_count": 10,
            "fullness_score_threshold": 0.6
        }
    return rules

def extract_features(image_path):
    original_img = cv2.imread(image_path)
    if original_img is None:
        raise ValueError(f"Image invalide ou format non supporté: {image_path}")
    img = extract_ground_patch(original_img)
    # Conversion en différents espaces colorimétriques
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Caractéristiques de base
    mean_color = np.mean(img)
    
    # 1. Analyse des contours et de la densité des bords
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    # 2. Analyse de la texture (variance locale)
    kernel = np.ones((5,5), np.float32) / 25
    texture_filtered = cv2.filter2D(gray, -1, kernel)
    texture_variance = np.var(texture_filtered)
    
    # 3. Analyse des pixels sombres (déchets souvent plus sombres)
    dark_threshold = 80
    dark_pixels = np.sum(gray < dark_threshold)
    dark_pixels_ratio = dark_pixels / (gray.shape[0] * gray.shape[1])
    
    # 4. Analyse de la saturation (déchets colorés vs fond neutre)
    saturation = hsv[:,:,1]
    mean_saturation = np.mean(saturation)
    
    # 5. Détection de contours multiples (débris/objets)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrer les petits contours (bruit)
    significant_contours = [c for c in contours if cv2.contourArea(c) > 100]
    debris_contour_count = len(significant_contours)
    
    total_area = sum(cv2.contourArea(c) for c in significant_contours)
    
    # 6. Analyse de l'uniformité (poubelle vide = plus uniforme)
    histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
    histogram_variance = np.var(histogram)
    
    # 7. Détection de formes irrégulières
    irregular_shapes = 0
    for contour in significant_contours:
        if cv2.contourArea(contour) > 500:
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * cv2.contourArea(contour) / (perimeter * perimeter)
                if circularity < 0.5:  # Forme très irrégulière
                    irregular_shapes += 1
    
    return {
        "mean_color": mean_color,
        "area": total_area,
        "edge_density": edge_density,
        "texture_variance": texture_variance,
        "dark_pixels_ratio": dark_pixels_ratio,
        "mean_saturation": mean_saturation,
        "debris_contour_count": debris_contour_count,
        "histogram_variance": histogram_variance,
        "irregular_shapes": irregular_shapes,
        "shape": img.shape[:2]
    }

def calculate_fullness_score(features, rules):
    """Calcule un score de remplissage basé sur plusieurs critères avec pondération"""
    score = 0.0
    
    # Critères FORTS (poids 2.0) - Très indicatifs de poubelle pleine
    strong_criteria = 0
    
    # Critère FORT 1: Beaucoup de contours significatifs ET densité des bords élevée
    if (features['debris_contour_count'] > rules["debris_contour_count"] and 
        features['edge_density'] > rules["edge_density_threshold"]):
        score += 2.0
        strong_criteria += 1
    
    # Critère FORT 2: Texture très complexe ET pixels sombres nombreux
    if (features['texture_variance'] > rules["texture_variance_threshold"] and 
        features['dark_pixels_ratio'] > rules["dark_pixels_ratio_threshold"]):
        score += 2.0
        strong_criteria += 1
    
    # Critères MOYENS (poids 1.0) - Indicatifs mais pas décisifs seuls
    medium_criteria = 0
    
    # Critère moyen 1: Saturation élevée (objets colorés)
    if features['mean_saturation'] > rules["saturation_threshold"]:
        score += 1.0
        medium_criteria += 1
    
    # Critère moyen 2: Histogram très non-uniforme
    if features['histogram_variance'] > rules.get("histogram_variance_threshold", 2000):
        score += 1.0
        medium_criteria += 1
    
    # Critère moyen 3: Formes irrégulières présentes
    if features['irregular_shapes'] > rules.get("irregular_shapes_threshold", 3):
        score += 1.0
        medium_criteria += 1
    
    # Critères FAIBLES (poids 0.5) - Supportent la décision
    weak_criteria = 0
    
    # Aire totale importante
    if features['area'] > rules["area_threshold"]:
        score += 0.5
        weak_criteria += 1
    
    # Couleur moyenne sombre
    if features['mean_color'] < rules["mean_color_threshold"]:
        score += 0.5
        weak_criteria += 1
    
    # Score maximum possible: 2*2 + 1*3 + 0.5*2 = 8.0
    max_score = 8.0
    normalized_score = score / max_score
    
    # RÈGLE STRICTE: Au moins 1 critère fort OU 2 critères moyens requis
    if strong_criteria == 0 and medium_criteria < 2:
        normalized_score *= 0.3  # Pénalité sévère
    
    return normalized_score

def classify_image(features, rules):
    # Nouvelle méthode stricte basée sur le score pondéré
    fullness_score = calculate_fullness_score(features, rules)
    
    # Seuils adaptatifs basés sur la combinaison de critères
    strict_threshold = rules.get("strict_fullness_threshold", 0.4)
    medium_threshold = rules.get("medium_fullness_threshold", 0.6)
    
    # Classification avec niveaux de confiance
    if fullness_score >= medium_threshold:
        classification = "Poubelle pleine"
        confidence = "Élevée"
    elif fullness_score >= strict_threshold:
        # Vérification supplémentaire pour éviter les faux positifs
        validation_checks = 0
        
        # Check 1: Au moins 8 contours significatifs
        if features['debris_contour_count'] >= 8:
            validation_checks += 1
            
        # Check 2: Densité des bords > seuil strict
        if features['edge_density'] > rules["edge_density_threshold"] * 1.5:
            validation_checks += 1
            
        # Check 3: Variance de texture significative
        if features['texture_variance'] > rules["texture_variance_threshold"] * 1.2:
            validation_checks += 1
        
        if validation_checks >= 2:
            classification = "Poubelle pleine"
            confidence = "Moyenne"
        else:
            classification = "Poubelle vide"
            confidence = "Moyenne"
    else:
        classification = "Poubelle vide"
        confidence = "Élevée"
    
    # Méthode classique pour comparaison
    mean_color = features['mean_color']
    area = features['area']
    classic_result = "Poubelle pleine" if (mean_color < rules["mean_color_threshold"] and area > rules["area_threshold"]) else "Poubelle vide"
    
    return {
        "classification": classification,
        "confidence": confidence,
        "fullness_score": fullness_score,
        "classic_method": classic_result,
        "validation_details": {
            "contours_count": features['debris_contour_count'],
            "edge_density": features['edge_density'],
            "texture_variance": features['texture_variance'],
            "dark_ratio": features['dark_pixels_ratio']
        }
    }

def demo_extraction(image_path, rules_path="rules.json"):
    if not os.path.exists(image_path):
        print(f"❌ Fichier introuvable : {image_path}")
        return

    try:
        print(f"🔍 Analyse de l'image : {image_path}")
        print("=" * 50)
        
        features = extract_features(image_path)
        print("📊 Caractéristiques extraites :")
        for key, value in features.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        
        print("\n" + "=" * 50)
        
        rules = load_rules(rules_path)
        result = classify_image(features, rules)
        
        print("🧪 Résultats de la classification :")
        print(f"   Classification finale: {result['classification']}")
        print(f"   Confiance: {result['confidence']}")
        print(f"   Score de remplissage: {result['fullness_score']:.2f}")
        print(f"   Méthode classique: {result['classic_method']}")
        print(f"   Validation par critères multiples: {result['validation_details']}")

    except Exception as e:
        print("❌ Erreur lors du traitement de l'image :", e)

def create_default_rules_file(rules_path="rules.json"):
    """Crée un fichier de règles avec des valeurs optimisées"""
    default_rules = {
        "mean_color_threshold": 100,
        "area_threshold": 5000,
        "edge_density_threshold": 0.05,
        "texture_variance_threshold": 500,
        "dark_pixels_ratio_threshold": 0.4,
        "saturation_threshold": 30,
        "debris_contour_count": 10,
        "fullness_score_threshold": 0.6,
        "description": {
            "mean_color_threshold": "Seuil couleur moyenne (plus bas = plus sombre)",
            "area_threshold": "Aire minimale des contours",
            "edge_density_threshold": "Densité minimale des bords",
            "texture_variance_threshold": "Variance de texture minimale",
            "dark_pixels_ratio_threshold": "Ratio minimal de pixels sombres",
            "saturation_threshold": "Saturation moyenne minimale",
            "debris_contour_count": "Nombre minimal de contours significatifs",
            "fullness_score_threshold": "Score minimal pour 'poubelle pleine' (0-1)"
        }
    }
    
    with open(rules_path, "w") as f:
        json.dump(default_rules, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Fichier de règles créé : {rules_path}")

def extract_ground_patch(img):
    """Extrait une bande devant la base de la poubelle pour éviter les fausses détections"""
    h, w = img.shape[:2]
    top = int(h * 0.60)
    bottom = int(h * 0.85)
    left = int(w * 0.25)
    right = int(w * 0.75)
    return img[top:bottom, left:right]



# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le fichier de règles s'il n'é pas
    rules_path = "rules.json"
    if not os.path.exists(rules_path):
        create_default_rules_file(rules_path)
    
    image_path = "Data/train/with_label/dirty/00511_01.jpg"
    demo_extraction(image_path, rules_path)