import os
import cv2
import numpy as np
from PIL import Image, ImageStat
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

class ImageFeatureExtractor:
    """
    Classe pour extraire automatiquement les caractéristiques d'images de poubelles.
    Optimisée pour la détection d'état (pleine/vide) avec approche Green IT.
    """
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def extract_all_features(self, image_path: str, include_advanced: bool = True) -> Dict[str, Any]:
        """
        Extrait toutes les caractéristiques d'une image.
        
        Args:
            image_path (str): Chemin vers l'image
            include_advanced (bool): Inclure les caractéristiques avancées (plus coûteuses)
        
        Returns:
            Dict: Dictionnaire contenant toutes les caractéristiques
        """
        if not self._validate_image(image_path):
            raise ValueError(f"Image invalide ou format non supporté: {image_path}")
        
        features = {}
        
        # Informations de base
        features.update(self._extract_basic_info(image_path))
        
        # Caractéristiques visuelles de base
        features.update(self._extract_color_features(image_path))
        features.update(self._extract_brightness_contrast(image_path))
        
        # Caractéristiques avancées (optionnelles pour performance)
        if include_advanced:
            features.update(self._extract_texture_features(image_path))
            features.update(self._extract_shape_features(image_path))
            features.update(self._extract_histogram_features(image_path))
        
        # Métadonnées temporelles
        features['extraction_timestamp'] = datetime.now().isoformat()
        
        return features
    
    def _validate_image(self, image_path: str) -> bool:
        """Valide que le fichier est une image supportée."""
        if not os.path.exists(image_path):
            return False
        
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.supported_formats:
            return False
        
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except:
            return False
    
    def _extract_basic_info(self, image_path: str) -> Dict[str, Any]:
        """Extrait les informations de base du fichier."""
        features = {}
        
        # Taille du fichier
        file_size_bytes = os.path.getsize(image_path)
        features['file_size_bytes'] = file_size_bytes
        features['file_size_kb'] = round(file_size_bytes / 1024, 2)
        features['file_size_mb'] = round(file_size_bytes / (1024 * 1024), 3)
        
        # Dimensions
        with Image.open(image_path) as img:
            width, height = img.size
            features['width'] = width
            features['height'] = height
            features['aspect_ratio'] = round(width / height, 3)
            features['total_pixels'] = width * height
            features['megapixels'] = round((width * height) / 1_000_000, 2)
        
        # Format et mode
        with Image.open(image_path) as img:
            features['format'] = img.format
            features['mode'] = img.mode
            
        return features
    
    def _extract_color_features(self, image_path: str) -> Dict[str, Any]:
        """Extrait les caractéristiques de couleur."""
        features = {}
        
        with Image.open(image_path) as img:
            # Conversion en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Couleur moyenne
            stat = ImageStat.Stat(img)
            features['mean_red'] = round(stat.mean[0], 2)
            features['mean_green'] = round(stat.mean[1], 2)
            features['mean_blue'] = round(stat.mean[2], 2)
            features['overall_brightness'] = round(sum(stat.mean) / 3, 2)
            
            # Écart-type des couleurs (variation)
            features['std_red'] = round(stat.stddev[0], 2)
            features['std_green'] = round(stat.stddev[1], 2)
            features['std_blue'] = round(stat.stddev[2], 2)
            features['color_variation'] = round(sum(stat.stddev) / 3, 2)
            
            # Dominance de couleur
            rgb_values = [stat.mean[0], stat.mean[1], stat.mean[2]]
            dominant_color_idx = rgb_values.index(max(rgb_values))
            color_names = ['red', 'green', 'blue']
            features['dominant_color'] = color_names[dominant_color_idx]
            features['dominant_color_value'] = round(max(rgb_values), 2)
            
        return features
    
    def _extract_brightness_contrast(self, image_path: str) -> Dict[str, Any]:
        """Extrait les caractéristiques de luminance et contraste."""
        features = {}
        
        # Utilisation d'OpenCV pour plus de précision
        img = cv2.imread(image_path)
        if img is None:
            return features
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Luminance
        features['luminance_mean'] = round(np.mean(gray), 2)
        features['luminance_std'] = round(np.std(gray), 2)
        features['luminance_min'] = int(np.min(gray))
        features['luminance_max'] = int(np.max(gray))
        
        # Contraste (différence max-min)
        features['contrast_range'] = int(np.max(gray) - np.min(gray))
        features['contrast_rms'] = round(np.sqrt(np.mean((gray - np.mean(gray)) ** 2)), 2)
        
        # Classification de luminosité
        if features['luminance_mean'] < 85:
            features['brightness_category'] = 'dark'
        elif features['luminance_mean'] < 170:
            features['brightness_category'] = 'medium'
        else:
            features['brightness_category'] = 'bright'
        
        return features
    
    def _extract_histogram_features(self, image_path: str) -> Dict[str, Any]:
        """Extrait les caractéristiques d'histogramme."""
        features = {}
        
        img = cv2.imread(image_path)
        if img is None:
            return features
        
        # Histogramme des niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # Statistiques de l'histogramme
        features['hist_peak'] = int(np.argmax(hist))  # Valeur la plus fréquente
        features['hist_peak_count'] = int(np.max(hist))
        
        # Distribution des pixels (quartiles)
        cumsum = np.cumsum(hist)
        total_pixels = cumsum[-1]
        
        # Percentiles
        features['hist_q1'] = int(np.where(cumsum >= total_pixels * 0.25)[0][0])
        features['hist_median'] = int(np.where(cumsum >= total_pixels * 0.5)[0][0])
        features['hist_q3'] = int(np.where(cumsum >= total_pixels * 0.75)[0][0])
        
        # Entropie (mesure de la complexité)
        hist_norm = hist / np.sum(hist)
        hist_norm = hist_norm[hist_norm > 0]  # Éviter log(0)
        features['histogram_entropy'] = round(-np.sum(hist_norm * np.log2(hist_norm)), 3)
        
        return features
    
    def _extract_texture_features(self, image_path: str) -> Dict[str, Any]:
        """Extrait les caractéristiques de texture et contours."""
        features = {}
        
        img = cv2.imread(image_path)
        if img is None:
            return features
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Détection de contours avec Canny
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = round(np.sum(edges > 0) / edges.size, 4)
        features['total_edges'] = int(np.sum(edges > 0))
        
        # Gradient (variation locale)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        features['gradient_mean'] = round(np.mean(gradient_magnitude), 2)
        features['gradient_std'] = round(np.std(gradient_magnitude), 2)
        
        # Texture (variance locale)
        kernel = np.ones((5,5), np.float32) / 25
        mean_local = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        variance_local = cv2.filter2D((gray.astype(np.float32) - mean_local)**2, -1, kernel)
        features['texture_mean'] = round(np.mean(variance_local), 2)
        
        return features
    
    def _extract_shape_features(self, image_path: str) -> Dict[str, Any]:
        """Extrait les caractéristiques de forme basiques."""
        features = {}
        
        img = cv2.imread(image_path)
        if img is None:
            return features
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Binarisation simple pour analyser les formes
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Contours principaux
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Plus grand contour
            largest_contour = max(contours, key=cv2.contourArea)
            features['largest_contour_area'] = int(cv2.contourArea(largest_contour))
            features['largest_contour_perimeter'] = round(cv2.arcLength(largest_contour, True), 2)
            
            # Compacité (circularité)
            if features['largest_contour_perimeter'] > 0:
                compactness = 4 * np.pi * features['largest_contour_area'] / (features['largest_contour_perimeter'] ** 2)
                features['shape_compactness'] = round(compactness, 4)
            
            features['total_contours'] = len(contours)
        else:
            features['largest_contour_area'] = 0
            features['total_contours'] = 0
        
        return features
    
    def extract_for_classification(self, image_path: str) -> Dict[str, float]:
        """
        Extrait uniquement les caractéristiques essentielles pour la classification pleine/vide.
        Version optimisée pour les performances.
        """
        features = {}
        
        # Informations de base
        basic = self._extract_basic_info(image_path)
        features['file_size_mb'] = basic['file_size_mb']
        features['aspect_ratio'] = basic['aspect_ratio']
        
        # Couleurs et luminosité (indicateurs clés)
        color = self._extract_color_features(image_path)
        features['overall_brightness'] = color['overall_brightness']
        features['color_variation'] = color['color_variation']
        
        # Contraste (important pour distinguer plein/vide)
        brightness = self._extract_brightness_contrast(image_path)
        features['contrast_range'] = brightness['contrast_range']
        features['luminance_mean'] = brightness['luminance_mean']
        
        return features
    
    def save_features_to_json(self, features: Dict[str, Any], output_path: str) -> None:
        """Sauvegarde les caractéristiques en JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(features, f, indent=2, ensure_ascii=False)
    
    def batch_extract(self, image_directory: str, output_directory: str = None) -> List[Dict[str, Any]]:
        """
        Traite un lot d'images.
        
        Args:
            image_directory (str): Dossier contenant les images
            output_directory (str): Dossier pour sauvegarder les résultats JSON
        
        Returns:
            List[Dict]: Liste des caractéristiques de chaque image
        """
        results = []
        
        if not os.path.exists(image_directory):
            raise ValueError(f"Dossier introuvable: {image_directory}")
        
        # Créer le dossier de sortie si spécifié
        if output_directory and not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        # Traiter chaque image
        for filename in os.listdir(image_directory):
            file_path = os.path.join(image_directory, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            ext = os.path.splitext(filename)[1].lower()
            if ext not in self.supported_formats:
                continue
            
            try:
                print(f"Traitement de {filename}...")
                features = self.extract_all_features(file_path)
                features['filename'] = filename
                features['file_path'] = file_path
                
                results.append(features)
                
                # Sauvegarder individuellement si demandé
                if output_directory:
                    json_filename = os.path.splitext(filename)[0] + '_features.json'
                    json_path = os.path.join(output_directory, json_filename)
                    self.save_features_to_json(features, json_path)
                
            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {str(e)}")
                continue
        
        return results


# Exemple d'utilisation et fonctions utilitaires
def create_classification_rules(features: Dict[str, float]) -> str:
    """
    Exemple de règles de classification basées sur les caractéristiques.
    À adapter selon vos observations.
    """
    # Règles simples basées sur l'hypothèse que les poubelles pleines sont :
    # - Plus sombres (débordement, ombres)
    # - Plus de variation de couleur (déchets variés)
    # - Contraste plus élevé
    
    score = 0
    
    # Critère 1: Luminosité
    if features.get('overall_brightness', 128) < 100:
        score += 2  # Plus sombre = plus susceptible d'être pleine
    
    # Critère 2: Variation de couleur
    if features.get('color_variation', 0) > 50:
        score += 2  # Plus de variation = déchets visibles
    
    # Critère 3: Contraste
    if features.get('contrast_range', 0) > 150:
        score += 1  # Contraste élevé = éléments distincts
    
    # Critère 4: Taille de fichier (plus de détails = pleine)
    if features.get('file_size_mb', 0) > 2.0:
        score += 1
    
    # Classification finale
    if score >= 4:
        return "pleine"
    elif score <= 1:
        return "vide"
    else:
        return "incertain"


def demo_extraction():
    """Fonction de démonstration."""
    extractor = ImageFeatureExtractor()
    
    # Test sur une image unique
    image_path = "Data/test/1080.full.jpeg"  # Remplacer le chemin en fonction de l'image à tester
    if not os.path.exists(image_path):
        print(f"Image non trouvée: {image_path}")
        return
    
    try:
        print("=== Extraction complète ===")
        features = extractor.extract_all_features(image_path)
        
        print(f"Taille: {features.get('file_size_mb', 0)} MB")
        print(f"Dimensions: {features.get('width', 0)}x{features.get('height', 0)}")
        print(f"Luminosité moyenne: {features.get('overall_brightness', 0)}")
        print(f"Contraste: {features.get('contrast_range', 0)}")
        
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    demo_extraction()