"""
Application de Génération d'Emplois du Temps Universitaires
– Développé en Python
Auteur : NKOA MVENG SEAN
"""

import tkinter as tk
from ui.app import Application


def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
