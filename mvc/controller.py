import tkinter as tk
from typing import Dict, Any, Tuple

from .model import ApplicationModel
from .view import ApplicationView


class ApplicationController:
    """
    Gère le flux de l'application, les interactions utilisateur, 
    et coordonne le Modèle et la Vue.
    """
    def __init__(self, master: tk.Tk) -> None:
        """
        Initialise le contrôleur, le modèle et la vue.

        Args:
            master: La fenêtre principale Tkinter.
        """
        self.master: tk.Tk = master
        # Initialisation du Modèle (logique et données)
        self.model: ApplicationModel = ApplicationModel()
        # Initialisation de la Vue (interface graphique)
        self.view: ApplicationView = ApplicationView(master)
        
        # Synchronisation initiale : Initialise le chemin d'exportation de la Vue avec la valeur du Modèle
        self.view.export_path_var.set(self.model.export_path)

        # Lie les méthodes du contrôleur aux événements des widgets de la vue
        self._attach_commands()
        
        # Initialise l'état des boutons au lancement de l'application
        self.view.update_state_buttons(import_enabled=True, export_enabled=False, reset_enabled=False)
        
    def _attach_commands(self) -> None:
        """Lie les méthodes du contrôleur (handlers) aux commandes des widgets interactifs de la vue."""
        
        # Récupère les références des widgets nécessaires
        widgets: Dict[str, Any] = self.view.widget_references
        
        # Liaison des commandes des boutons d'action principaux
        widgets['import_button'].configure(command=self.handle_import_images)
        widgets['export_final_button'].configure(command=self.handle_export_images)
        widgets['reset_button'].configure(command=self.handle_reset)
        
        # Liaison du bouton de sélection du chemin d'exportation
        widgets['export_path_button'].configure(command=self.handle_select_export_path)
        
        # Liaison du Checkbutton de bascule du mode optimisé
        widgets['optimized_storage_checkbutton'].configure(command=self.handle_optimized_storage_toggle)

    # --- Gestionnaires d'événements (Handlers) ---
    
    def handle_select_export_path(self) -> None:
        """Gère l'ouverture du dialogue de sélection de répertoire et la persistance du chemin."""
        # Ouvre la boîte de dialogue de sélection de répertoire
        chosen_path: str = self.view.open_directory_dialog()
        
        if chosen_path:
            # 1. Met à jour le Modèle et le rend persistant via la fonction de sauvegarde
            self.model.write_config(chosen_path)
            
            # 2. Met à jour l'affichage de la Vue
            self.view.export_path_var.set(chosen_path)
            self.view.update_status_label(
                f"Dossier de destination sélectionné et sauvegardé : {chosen_path}", "success"
            )
            
    def handle_import_images(self) -> None:
        """Gère l'importation des images, le chargement dans le Modèle et la mise à jour de la Vue."""
        # Ouvre la boîte de dialogue de sélection des fichiers images
        files: Tuple[str, ...] = self.view.open_files_dialog()
        
        # Si la sélection est annulée (tuple vide)
        if not files:
            self.view.update_status_label("Importation annulée. Aucune image sélectionnée.", "info")
            return

        # 1. Chargement des images dans le Modèle
        num_files: int = self.model.load_images(list(files)) # Conversion en liste pour le modèle
        
        # 2. Mise à jour de l'interface utilisateur
        if num_files > 0:
            # Affichage du succès et activation des boutons Export/Reset
            self.view.update_status_label(
                f"{num_files} image(s) sélectionnée(s) : Prêt pour l'export.", "success"
            )
            self.view.update_state_buttons(import_enabled=False, export_enabled=True, reset_enabled=True)
        else:
            # Affichage de l'échec
            self.view.update_status_label(
                "Échec de l'importation. Aucune image valide n'a été chargée.", "danger"
            )
            self.view.update_state_buttons(import_enabled=True, export_enabled=False, reset_enabled=False)

    def handle_optimized_storage_toggle(self) -> None:
        """Applique ou désactive les réglages pour le mode 'stockage optimisé' (réglages agressifs)."""
        
        # Vérifie l'état actuel de la variable de contrôle
        if self.view.optimized_storage_var.get():
            # --- Activation du mode optimisé ---
            self.view.set_meter_values(quality=50, resize=75)     # Qualité à 50%, Redimensionnement à 75%
            self.view.output_format_var.set("WEBP")               # Format de sortie en WEBP (meilleure compression)
            self.view.optimized_encoding_var.set(True)            # Encodage optimisé activé
            self.view.strip_metadata_var.set(True)                # Suppression des métadonnées
            self.view.progressive_loading_var.set(True)           # Affichage progressif (si compatible)
            
            self.view.update_status_label(
                "Mode Stockage Optimisé activé. Les réglages ont été ajustés.", "warning"
            )
        else:
            # --- Retour aux réglages par défaut ---
            self.view.set_meter_values(quality=80, resize=100)
            self.view.output_format_var.set("JPG")
            self.view.optimized_encoding_var.set(False)
            self.view.strip_metadata_var.set(False)
            self.view.progressive_loading_var.set(False)
            
            # Réinitialise le message seulement si aucune image n'est chargée
            if not self.model.data:
                 self.view.update_status_label("Aucune image n'a été sélectionnée", "info")

    def handle_export_images(self) -> None:
        """Collecte les options de la Vue, appelle le Modèle pour l'export, et affiche le résultat."""
        
        # Vérification préliminaire : y a-t-il des données à traiter ?
        if not self.model.data:
            self.view.update_status_label("Aucune image à exporter. Veuillez importer des fichiers.", "danger")
            return
        
        # 1. Collecte des options de la Vue
        options: Dict[str, Any]
        try:
            options = {
                # Récupère la valeur du Meter de qualité
                'quality': self.view.quality_meter.amountusedvar.get(),
                # Récupère la valeur du Meter de redimensionnement et la convertit en facteur (e.g., 75% -> 0.75)
                'resize_factor': self.view.resize_meter.amountusedvar.get() / 100.0,
                # Récupère les valeurs des variables de contrôle
                'output_format': self.view.output_format_var.get(),
                'add_suffixe': self.view.add_suffixe_var.get(),
                'use_zip': self.view.zip_export_var.get(),
                'delete_originals': self.view.delete_originals_var.get(),
                'optimized_encoding': self.view.optimized_encoding_var.get(),
                'progressive_loading': self.view.progressive_loading_var.get(),
                'strip_metadata': self.view.strip_metadata_var.get(),
            }
            
            # Validation simple des paramètres (la validation complète est faite dans le Modèle)
            if not (1 <= options['quality'] <= 100):
                self.view.update_status_label("Erreur: La qualité de compression doit être entre 1 et 100.", "danger")
                return

        except Exception as e:
            # Gestion d'une erreur de lecture des widgets
            self.view.update_status_label(f"Échec de la lecture des paramètres: {e}", "danger")
            return
            
        # Affiche le statut "En cours" et force l'actualisation de l'interface
        self.view.update_status_label("[EN COURS] Démarrage de la compression...", "warning")
        self.master.update_idletasks() # Assure que le message d'avertissement s'affiche immédiatement

        # 2. Appel au Modèle pour le traitement et l'exportation
        success_count: int
        stats: Dict[str, Any]
        success_count, stats = self.model.process_and_export(options)

        # 3. Mise à jour de la Vue avec les résultats
        if success_count == 0:
            # Gestion de l'échec de traitement (récupère un message d'erreur si disponible)
            error_msg: str = stats.get("error_msg", "Aucune image n'a été traitée avec succès.")
            self.view.update_status_label(f"Échec de l'exportation. {error_msg}", "danger")
        else:
            # Construction du message de succès détaillé avec les statistiques
            message: str = (
                f"Exportation terminée : {success_count} image(s) compressée(s) avec succès. "
                f"| {stats['total_old_mo']:.2f} Mo -> {stats['total_new_mo']:.2f} Mo | "
                f"Différence: {stats['difference_mo']:.2f} Mo ({stats['gain_percent']:.1f}%)"
            )
            self.view.update_status_label(message, "success")
            
            # Réactive le bouton d'importation et maintient le bouton de réinitialisation actif
            self.view.update_state_buttons(import_enabled=True, export_enabled=False, reset_enabled=True)

    def handle_reset(self) -> None:
        """Gère la réinitialisation complète de l'application (données et interface)."""
        
        # 1. Réinitialisation du Modèle (ferme les objets PIL, vide les données, réinitialise le chemin)
        self.model.reset_data()
        
        # 2. Réinitialisation des variables de la Vue aux valeurs par défaut
        self.view.set_meter_values(quality=80, resize=100) 
        self.view.optimized_storage_var.set(False)
        self.view.optimized_encoding_var.set(False)
        self.view.strip_metadata_var.set(False)
        self.view.progressive_loading_var.set(False)
        self.view.zip_export_var.set(False)
        self.view.delete_originals_var.set(False)
        self.view.add_suffixe_var.set(False) 
        self.view.output_format_var.set("JPG")
        
        # Met à jour le chemin d'exportation dans la vue avec la valeur réinitialisée du modèle
        self.view.export_path_var.set(self.model.export_path)
        
        # Mise à jour de l'état final de la vue
        self.view.update_status_label("Aucune image n'a été sélectionnée", "info")
        self.view.update_state_buttons(import_enabled=True, export_enabled=False, reset_enabled=False)
