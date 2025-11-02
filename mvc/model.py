import os
import io
import json
import uuid 
import logging
import pathlib
from zipfile import ZipFile, ZIP_DEFLATED
from typing import Dict, Any, Tuple, List, Optional

from PIL import Image

from utils import get_writable_path

# --- Configuration du logger ---
# Utilise get_writable_path pour que le fichier log soit toujours créé à côté de l'exécutable
LOG_FILE_PATH = get_writable_path("logs/application.log")

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=LOG_FILE_PATH, # ⬅️ UTILISATION DU CHEMIN FIABLE
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
# -----------------------------------------------------

class ApplicationModel:
    """
    Gère les données (images, chemins) et la logique de compression.
    Cette classe agit comme un service de données et de traitement,
    sans aucune interaction directe avec l'interface utilisateur (Tkinter/ttkbootstrap).
    """

    # Nom et chemin RELATIF du fichier de configuration pour la persistance
    CONFIG_FILE: str = "settings/export_folder.json"
    
    def __init__(self) -> None:
        # Dictionnaire pour stocker les informations et l'objet PIL de chaque image sélectionnée.
        # Structure: {id: {"old_path": str, "old_name": str, "old_size": int, "image_obj": Image.Image, ...}}
        self.data: Dict[int, Dict[str, Any]] = {} 
        
        # Le chemin de destination des fichiers exportés
        self.export_path: str = ""
        
        # Initialise le chemin d'exportation persistant ou utilise le chemin par défaut
        self.setup_export_path()

    # --- Persistance (lecture/écriture du chemin d'exportation) ---

    def _read_config(self) -> Optional[str]:
        """
        Lit le fichier de configuration et retourne le chemin d'exportation sauvegardé.

        Returns:
            Le chemin sauvegardé (str) ou None si le fichier n'existe pas ou est corrompu.
        """
        try:
            # ⬅️ CORRECTION : Obtient le chemin d'accès complet et fiable au fichier de configuration
            config_full_path: str = get_writable_path(self.CONFIG_FILE)

            # Ouverture du fichier en lecture avec gestion de l'encodage
            with io.open(file=config_full_path, mode="r", encoding="utf-8") as f:
                # Chargement des données JSON
                data_config: Any = json.load(f)
                # Vérification que les données lues sont bien une chaîne de caractères (le chemin)
                if isinstance(data_config, str):
                    return data_config
                return None 
        except (FileNotFoundError, json.JSONDecodeError):
            # Retourne None si le fichier n'existe pas ou si le JSON est invalide
            return None

    def write_config(self, path: str) -> None:
        """
        Écrit le chemin d'exportation dans le fichier de configuration et met à jour l'état interne.

        Args:
            path: Le chemin du répertoire à sauvegarder.
        """
        try:
            # ⬅️ CORRECTION : Obtient le chemin d'accès complet et fiable au fichier de configuration
            config_full_path: str = get_writable_path(self.CONFIG_FILE)

            # Ouverture du fichier en écriture
            with io.open(file=config_full_path, mode="w", encoding="utf-8") as f:
                # Écrit le chemin sous forme de chaîne JSON (ensure_ascii=False pour les chemins avec accents)
                json.dump(obj=path, fp=f, ensure_ascii=False)
            # Met à jour l'état interne du modèle
            self.export_path = path 
        except Exception as e:
            # Log de l'erreur en cas d'échec de l'écriture
            logger.error(f"Erreur lors de l'écriture de la configuration: {e}")
            
    def setup_export_path(self) -> None:
        """
        Détermine le chemin d'exportation à utiliser : le chemin sauvegardé, 
        le répertoire HOME par défaut, et s'assure qu'il est écrit en config.
        """
        # Tente de lire le chemin précédemment sauvegardé
        saved_path: Optional[str] = self._read_config()
        
        # Vérifie si le chemin sauvegardé est valide et est un répertoire existant
        if saved_path and os.path.isdir(saved_path):
            final_path: str = saved_path
        else:
            # Définit le répertoire HOME de l'utilisateur comme chemin par défaut
            default_path: str = str(pathlib.Path.home())
            final_path = default_path
            # Sauvegarde ce chemin par défaut dans le fichier de configuration
            self.write_config(default_path) 
            
        # Définit le chemin d'exportation interne du modèle
        self.export_path = final_path

    # --- Gestion des images (Importation et Réinitialisation) ---

    def load_images(self, files: List[str]) -> int:
        """
        Charge les fichiers images sélectionnés, stocke leurs métadonnées et 
        leurs objets PIL dans `self.data`.

        Args:
            files: Une liste des chemins d'accès absolus des fichiers à charger.

        Returns:
            Le nombre d'images chargées avec succès.
        """
        if not files:
            return 0
            
        # Vide les données précédentes pour commencer une nouvelle session
        self.data.clear() 
        loaded_files: int = 0
        
        # Parcourt la liste des fichiers et tente de les charger
        for i, file in enumerate(files, start=1):
            f: pathlib.Path = pathlib.Path(file)
            try:
                # Ouvre l'image avec Pillow (gestion des formats divers)
                img: Image.Image = Image.open(f)
                # Obtient la taille originale du fichier sur le disque
                old_size: int = os.path.getsize(file)
                
                # Stockage des informations dans le dictionnaire de données
                self.data[i] = {
                    "old_path": str(f),             # Chemin complet du fichier original
                    "old_name": f.stem,             # Nom du fichier sans extension
                    "old_suffix": f.suffix,         # Extension du fichier
                    "old_size": old_size,           # Taille initiale en octets
                    "new_size": 0,                  # Taille finale après compression (initialisé à 0)
                    "image_obj": img                # L'objet Image.Image de Pillow
                }
                loaded_files += 1
            except Exception as e:
                # Log de l'erreur si le fichier n'est pas une image valide ou ne peut être lu
                logger.error(f"Échec du chargement de l'image {file}: {e}")
                continue

        return loaded_files

    def reset_data(self) -> None:
        """
        Ferme proprement tous les objets PIL en mémoire pour libérer les ressources 
        et vide le dictionnaire de données.
        """
        # Parcourt toutes les entrées dans les données
        for item in self.data.values():
            try:
                # Tente de fermer l'objet PIL
                item["image_obj"].close()
            except:
                # Ignore l'erreur si l'objet est déjà fermé ou non valide
                pass
        
        # Vide le dictionnaire de données
        self.data.clear()
        
        # S'assure que le chemin d'exportation est à jour (au cas où il ait été perdu)
        self.setup_export_path()

    # --- Logique de Compression et Exportation ---

    def process_and_export(self, options: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Applique les transformations (redimensionnement, conversion, compression) 
        aux images et les exporte vers la destination choisie.

        Args:
            options: Dictionnaire des options de compression et d'exportation lues depuis la Vue.

        Returns:
            Un tuple contenant (nombre de succès, dictionnaire de statistiques et d'erreurs).
        """
        
        # Vérification de sécurité : si les données sont vides ou le chemin d'exportation est invalide
        if not self.data or not self.export_path or not os.path.isdir(self.export_path):
            return 0, {"error_msg": "Données manquantes ou chemin d'exportation invalide."} 
        
        # 1. Extraction et typage des options
        quality: int = options.get('quality', 80)
        resize_factor: float = options.get('resize_factor', 1.0)
        output_format: str = options.get('output_format', 'JPG').upper() 
        add_suffixe: bool = options.get('add_suffixe', False) 
        use_zip: bool = options.get('use_zip', False)
        delete_originals: bool = options.get('delete_originals', False)
        optimized_encoding: bool = options.get('optimized_encoding', False)
        progressive_loading: bool = options.get('progressive_loading', False)
        strip_metadata: bool = options.get('strip_metadata', False)

        # Détermine le format de sauvegarde interne de Pillow
        save_format_key: str
        if output_format in ["JPG", "JPEG"]:
            save_format_key = "jpeg" 
        elif output_format == "WEBP":
            save_format_key = "webp"
        else:
            # Si le format n'est pas supporté (sécurité)
            return 0, {"error_msg": f"Format de sortie non supporté: {output_format}"} 

        # 2. Préparation des statistiques et du fichier ZIP
        total_old_size: int = 0
        total_new_size: int = 0
        success_count: int = 0 
        zip_file: Optional[ZipFile] = None
        zip_path: Optional[pathlib.Path] = None
        
        # Initialisation du fichier ZIP si l'option est activée
        if use_zip:
            # Génère un nom de fichier ZIP unique
            zip_filename: str = f"{uuid.uuid4()}.zip" 
            # Chemin complet du fichier ZIP
            zip_path = pathlib.Path(self.export_path) / zip_filename
            try:
                 # Ouvre le fichier ZIP en mode écriture avec compression DEFLATE
                 zip_file = ZipFile(zip_path, 'w', ZIP_DEFLATED)
            except Exception as e:
                logger.error(f"Erreur lors de la création du fichier ZIP: {e}")
                # Retourne l'erreur et le chemin du zip
                return 0, {"error_msg": f"Erreur ZIP : {str(e)}", "zip_path": str(zip_path)}
        
        # 3. Traitement image par image
        for item in self.data.values():
            img: Image.Image = item["image_obj"]
            original_path: str = item["old_path"]
            temp_path: Optional[pathlib.Path] = None
            
            try:
                # Vérifie si l'objet PIL est toujours ouvert/valide avant de le traiter
                if getattr(img, 'fp', None) is None: 
                    img = Image.open(original_path)
                    item["image_obj"] = img 
                    
                # Ajout de la taille originale pour le calcul final
                total_old_size += item["old_size"]
                
                # --- Redimensionnement ---
                if resize_factor < 1.0 and resize_factor > 0:
                    # Calcul des nouvelles dimensions
                    new_width: int = int(img.width * resize_factor)
                    new_height: int = int(img.height * resize_factor)
                    
                    if new_width > 0 and new_height > 0:
                        # Redimensionnement avec l'algorithme de rééchantillonnage de haute qualité
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # --- Conversion de mode ---
                # Si le format est JPEG, les modes RGBA (transparence) ou P (palette) ne sont pas supportés
                if save_format_key == "jpeg" and img.mode in ('RGBA', 'P'):
                    # Convertit l'image au format RGB standard
                    img = img.convert('RGB')

                # --- Définition des chemins d'exportation ---
                new_name: str = item["old_name"]
                suffix: str = "_compressée" if add_suffixe else ""
                # Nom du fichier final avec le nouveau format
                export_filename: str = f"{new_name}{suffix}.{output_format.lower()}"
                # Chemin temporaire/final du fichier
                temp_path = pathlib.Path(self.export_path) / export_filename

                # --- Paramètres de sauvegarde de Pillow ---
                pillow_params: Dict[str, Any] = {'quality': quality}
                
                # Ajout des options d'optimisation
                if optimized_encoding:
                    pillow_params['optimize'] = True
                
                # Suppression des métadonnées (EXIF)
                if strip_metadata:
                    pillow_params['exif'] = b'' 
                
                # Affichage progressif (spécifique à JPEG)
                if progressive_loading and save_format_key == "jpeg":
                    pillow_params['progressive'] = True
                    
                # --- SAUVEGARDE SUR LE DISQUE ---
                img.save(temp_path, format=save_format_key, **pillow_params)
                
                # Lecture de la taille du nouveau fichier compressé
                new_size: int = os.path.getsize(temp_path)
                total_new_size += new_size
                success_count += 1

                # --- Gestion de l'exportation ZIP ---
                if use_zip and zip_file:
                    # Ajoute le fichier compressé au ZIP
                    zip_file.write(temp_path, export_filename)
                    # Supprime le fichier temporaire du disque (car il est maintenant dans le zip)
                    os.remove(temp_path) 
                    
                # --- Suppression de l'original ---
                if delete_originals:
                    item["image_obj"].close() # Fermeture explicite
                    os.remove(original_path)
                    logger.info(f"Original '{item["old_path"]}' supprimé")
            
            except Exception as e:
                logger.error(f"Erreur de traitement/exportation pour {item['old_path']}: {e}")
                
                # Tente de supprimer le fichier temporaire s'il a été créé avant l'erreur
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as cleanup_e:
                         logger.error(f"Erreur de nettoyage du fichier temporaire: {cleanup_e}")
                continue

        # 4. Finalisation du ZIP
        if zip_file:
            zip_file.close()
            # Si un ZIP a été créé, total_new_size doit refléter la taille du fichier ZIP lui-même
            if zip_path and os.path.exists(zip_path):
                 total_new_size = os.path.getsize(zip_path)


        # 5. Calcul des statistiques finales
        stats: Dict[str, Any] = {}
        if success_count > 0:
            # Conversion des octets en Mégaoctets (Mo)
            total_old_mo: float = round(total_old_size / 1000000, 2)
            total_new_mo: float = round(total_new_size / 1000000, 2)
            
            # Calcul du gain en pourcentage
            gain_bytes: int = total_old_size - total_new_size
            gain_percent: float = (gain_bytes / total_old_size) * 100 if total_old_size > 0 else 0
            
            # Remplissage du dictionnaire de statistiques
            stats = {
                "total_old_mo": total_old_mo,
                "total_new_mo": total_new_mo,
                "difference_mo": round(total_old_mo - total_new_mo, 2),
                "gain_percent": round(gain_percent, 1),
                "export_dir": self.export_path
            }
        
        # Retourne le nombre de succès et le dictionnaire de statistiques
        return success_count, stats
