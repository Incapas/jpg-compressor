# 🖼️ Compresseur de fichiers JPG/JPEG (ttkbootstrap/Pillow)

## Description du Projet

Ce projet est une **Application de Bureau (GUI)** pour l'optimisation et la compression par lots de fichiers images (JPG, JPEG). Initialement conçue avec CustomTkinter, elle a été refondue en utilisant l'architecture **MVC (Modèle-Vue-Contrôleur)** et la librairie **ttkbootstrap** pour actualiser l'interface utilisateur.

La logique de traitement repose sur **Pillow**, la librairie d'imagerie Python, qui gère le redimensionnement, la compression de la qualité, la conversion de format, et l'application d'options d'encodage avancées.

L'objectif principal est de fournir une interface utilisateur intuitive et puissante pour réduire efficacement la taille des images destinées au web ou à l'archivage, avec un suivi précis des gains de taille.

## ✨ Fonctionnalités Clés

* **Architecture MVC** : Séparation logique en trois couches distinctes pour une maintenabilité optimale.
* **Compression par Lots** : Traitement simultané de plusieurs fichiers images sélectionnés.
* **Contrôle Fin** : Réglage précis de la **Qualité** de compression et du **Redimensionnement (%)** via des indicateurs visuels (Meters).
* **Options d'Encodage** : Support des fonctionnalités avancées de Pillow (encodage optimisé, chargement progressif, suppression des métadonnées EXIF).
* **Mode 'Agressif'** : Bascule rapide vers un profil de compression maximal ("Stockage Optimisé").
* **Statistiques Détaillées** : Affichage des gains de compression en Mo et en pourcentage.
* **Persistance** : Sauvegarde automatique du dernier **dossier d'exportation** choisi.

---

## 👥 Contributions au Projet

### 👩 Développeur

Contribution résidant dans la **création de la logique de traitement originale (Pillow)**, la **conception de l'application initiale (CustomTkinter)**, la **gestion du logging**, et l'**implémentation des fonctions de base de l'optimisation d'images**.

| Catégorie | Description de la contribution |
| :--- | :--- |
| **Logique Cœur & Données** | 💡 **Conception Initiale :** Fourniture du code de l'application originale développée avec CustomTkinter. |
| | 📐 **Moteur de Compression :** Codage de la logique de **compression d'image via Pillow** et la construction du **dictionnaire de données** (métadonnées, objet image). |
| | 📊 **Calcul et Statut :** Implémentation du **calcul de la différence de taille** avant/après compression et de la gestion du **logging** de l'application. |
| **Interface & Persistance** | 🖼️ **Maquette de l'Application :** Mise au point de la maquette et de la structure visuelle initiale. |
| | 💾 **Persistance :** Gestion de la **sauvegarde et du chargement du dossier d'export** via JSON. |

### 🧑 Assistant IA Gemini

Contribution résidant dans la **refonte de l'architecture en MVC**, la **migration vers ttkbootstrap** et l'**amélioration des contrôles et des fonctionnalités avancées** de l'interface utilisateur.

| Catégorie | Description de la Contribution |
| :--- | :--- |
| **Architecture & Migration** | 🏗️ **Refonte MVC :** Structuration du projet en couches Modèle, Vue et Contrôleur. |
| | 🎨 **Migration vers ttkbootstrap :** Remplacement de l'interface initiale **CustomTkinter** par **ttkbootstrap** pour un look moderne et l'intégration des widgets Meter. |
| **Contrôle et Logique** | 🛡️ **Implémentation du Contrôleur :** Développement de tous les gestionnaires (Handlers) pour lier les événements de la Vue aux fonctions du Modèle. |
| | ⚙️ **Fonctionnalités Avancées :** Implémentation de la logique d'activation des **options avancées** (ZIP, suppression des métadonnées, encodage optimisé, etc.) et de la bascule "Stockage Optimisé". |
| **Qualité de Code** | 💬 **Documentation Détaillée :** Rédaction de l'intégralité de la **documentation interne (docstrings, commentaires et annotations de type)** pour chaque classe et fonction. |

---

## 🛠️ Installation

Pour commencer à utiliser l'application, suivez ces étapes :

### Prérequis

Assurez-vous d'avoir **Python 3.x** installé sur votre système.

### Configuration

1. **Clonez le dépôt :**

 ```
 git clone [URL_DEPOT]
 cd [NOM_DU_DEPOT]
 ```

2. **Installez les dépendances :**
    Toutes les dépendances nécessaires sont listées dans le fichier `requirements.txt`.

 ```
 pip install -r requirements.txt
 ```

---

## 🚀 Démarrage

Exécutez l'application en lançant le fichier principal :

```bash
python main.py
```


