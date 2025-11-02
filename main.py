import ttkbootstrap as ttk

from mvc.controller import ApplicationController


if __name__ == '__main__':
    # Création de la fenêtre principale (Root Window)
    # Utilise le thème "darkly" de ttkbootstrap pour une apparence moderne
    app = ttk.Window(title="Compresseur de fichiers JPG/JPEG", themename="darkly") 
    app.geometry("1000x650")
    # Empêche le redimensionnement pour maintenir une disposition stable
    app.resizable(False, False)
    # Initialisation du Contrôleur
    # Le Contrôleur crée et lie le Modèle et la Vue
    controller = ApplicationController(app)
    # Lancement de la boucle principale de l'interface graphique
    app.mainloop()
