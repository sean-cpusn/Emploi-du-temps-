"""
ui/app.py
Fenêtre principale de l'application.
Architecture : sidebar de navigation + zone de contenu par onglet.
.
"""

import tkinter as tk
from tkinter import messagebox

from utils.theme import *
from models.repository import Repository
from ui.tableau_bord   import TableauBord
from ui.ressources     import PanneauRessources
from ui.planning       import PanneauPlanning
from ui.contraintes_ui import PanneauContraintes
from ui.sessions_ui    import PanneauSessions
from ui.export_ui      import PanneauExport


class Application:

    MENUS = [
        ("", "Tableau de Bord",  "tableau_bord"),
        ("", "Ressources",       "ressources"),
        ("", "Planning",         "planning"),
        ("", "Sessions",         "sessions"),
        ("", "Contraintes",      "contraintes"),
        ("", "Export",           "export"),
    ]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Emploi du Temps Universitaire")
        self.root.state("zoomed")          # Plein écran PyCharm-compatible
        self.root.configure(bg=COULEUR_FOND)
        self.root.minsize(1100, 680)

        try:
            self.root.iconbitmap("")
        except Exception:
            pass

        self.repo = Repository()
        self._panneaux = {}
        self._boutons_menu = {}
        self._panneau_actif = None

        self._construire_interface()
        self._naviguer("tableau_bord")

    # ──────────────────────────────────────────────────────────
    #  Construction de l'interface principale
    # ──────────────────────────────────────────────────────────

    def _construire_interface(self):
        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self.root, bg=COULEUR_PRIMAIRE, height=HAUTEUR_HEADER)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header,
                 text="🏛  Système de Génération des Emplois du Temps",
                 font=("Segoe UI", 14, "bold"),
                 fg=COULEUR_BLANC, bg=COULEUR_PRIMAIRE).pack(side="left", padx=20, pady=14)

        tk.Label(header,
                 text="",
                 font=FONT_SMALL, fg="#95a5a6",
                 bg=COULEUR_PRIMAIRE).pack(side="left", padx=4)

        # Bouton quitter
        tk.Button(header, text="✕  Quitter", command=self._quitter,
                  font=FONT_SMALL, bg="#e74c3c", fg=COULEUR_BLANC,
                  relief="flat", padx=10, pady=4,
                  cursor="hand2",
                  activebackground="#c0392b",
                  activeforeground=COULEUR_BLANC).pack(side="right", padx=16, pady=10)

        # Bouton aide
        tk.Button(header, text="Aide", command=self._aide,
                  font=FONT_SMALL, bg=COULEUR_SIDEBAR, fg=COULEUR_BLANC,
                  relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="right", padx=4, pady=10)

        # ── Corps (sidebar + contenu) ─────────────────────────
        corps = tk.Frame(self.root, bg=COULEUR_FOND)
        corps.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(corps, bg=COULEUR_SIDEBAR, width=LARGEUR_SIDEBAR)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="NAVIGATION", font=("Segoe UI", 9, "bold"),
                 fg="#7f8c8d", bg=COULEUR_SIDEBAR).pack(pady=(18, 6), padx=16, anchor="w")

        for icone, libelle, cle in self.MENUS:
            btn = tk.Button(
                sidebar,
                text=f"  {icone}  {libelle}",
                command=lambda k=cle: self._naviguer(k),
                font=FONT_NORMAL,
                fg=COULEUR_BLANC,
                bg=COULEUR_SIDEBAR,
                activebackground=COULEUR_SECONDAIRE,
                activeforeground=COULEUR_BLANC,
                relief="flat",
                anchor="w",
                padx=8,
                pady=10,
                cursor="hand2",
                bd=0,
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._boutons_menu[cle] = btn

        # Séparateur
        tk.Frame(sidebar, bg="#4a6278", height=1).pack(
            fill="x", padx=12, pady=12)

        # Info version
        tk.Label(sidebar, text="projet", font=FONT_SMALL,
                 fg="#7f8c8d", bg=COULEUR_SIDEBAR).pack(side="bottom", pady=10)
        tk.Label(sidebar, text="", font=FONT_SMALL,
                 fg="#7f8c8d", bg=COULEUR_SIDEBAR).pack(side="bottom")
        tk.Label(sidebar, text="", font=FONT_SMALL,
                 fg="#95a5a6", bg=COULEUR_SIDEBAR).pack(side="bottom")

        # Zone de contenu
        self.zone_contenu = tk.Frame(corps, bg=COULEUR_FOND)
        self.zone_contenu.pack(fill="both", expand=True)

        # ── Barre de statut ───────────────────────────────────
        barre_status = tk.Frame(self.root, bg=COULEUR_PRIMAIRE, height=24)
        barre_status.pack(fill="x", side="bottom")
        barre_status.pack_propagate(False)

        self.lbl_status = tk.Label(
            barre_status,
            text="✅ Application prête – Données chargées en mémoire",
            font=FONT_SMALL, fg="#95a5a6", bg=COULEUR_PRIMAIRE
        )
        self.lbl_status.pack(side="left", padx=12, pady=4)

        from datetime import datetime
        tk.Label(barre_status,
                 text=f"ISS •  {datetime.now().strftime('%d/%m/%Y')}",
                 font=FONT_SMALL, fg="#95a5a6",
                 bg=COULEUR_PRIMAIRE).pack(side="right", padx=12)

    # ──────────────────────────────────────────────────────────
    #  Navigation
    # ──────────────────────────────────────────────────────────

    def _naviguer(self, cle: str):
        # Réinitialiser la couleur des boutons
        for k, btn in self._boutons_menu.items():
            btn.config(bg=COULEUR_SIDEBAR if k != cle else COULEUR_SECONDAIRE)

        # Masquer le panneau actif
        if self._panneau_actif:
            self._panneau_actif.pack_forget()

        # Créer le panneau si nécessaire
        if cle not in self._panneaux:
            self._panneaux[cle] = self._creer_panneau(cle)

        panneau = self._panneaux[cle]
        panneau.pack(fill="both", expand=True)

        # Actualiser si le panneau expose la méthode
        if hasattr(panneau, "actualiser"):
            panneau.actualiser()

        self._panneau_actif = panneau
        self._mettre_a_jour_status(cle)

    def _creer_panneau(self, cle: str) -> tk.Frame:
        if cle == "tableau_bord":
            return TableauBord(self.zone_contenu, self.repo,
                               on_generation_terminee=self._on_generation)
        elif cle == "ressources":
            return PanneauRessources(self.zone_contenu, self.repo)
        elif cle == "planning":
            return PanneauPlanning(self.zone_contenu, self.repo)
        elif cle == "sessions":
            return PanneauSessions(self.zone_contenu, self.repo)
        elif cle == "contraintes":
            return PanneauContraintes(self.zone_contenu, self.repo)
        elif cle == "export":
            return PanneauExport(self.zone_contenu, self.repo)
        return tk.Frame(self.zone_contenu, bg=COULEUR_FOND)

    def _on_generation(self):
        """"""
        for cle in ["planning", "sessions", "export"]:
            if cle in self._panneaux:
                del self._panneaux[cle]

    def _mettre_a_jour_status(self, cle: str):
        labels = {
            "tableau_bord": "Tableau de Bord",
            "ressources":   "Gestion des Ressources",
            "planning":     "Visualisation de l'Emploi du Temps",
            "sessions":     "Gestion des Sessions",
            "contraintes":  "Contraintes & Conflits",
            "export":       "Export PDF / CSV",
        }
        self.lbl_status.config(
            text=f"📍 {labels.get(cle, cle)}")

    # ──────────────────────────────────────────────────────────

    def _aide(self):
        aide = tk.Toplevel(self.root)
        aide.title("Aide – Guide d'utilisation")
        aide.configure(bg=COULEUR_BLANC)
        aide.geometry("560x480")
        aide.resizable(False, False)

        tk.Label(aide, text="🏛  Guide d'utilisation", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_BLANC).pack(pady=(20, 8))
        tk.Frame(aide, bg=COULEUR_BORDURE, height=1).pack(fill="x", padx=20)

        texte = (
            "1. RESSOURCES\n"
            "   Saisissez les enseignants, matières, salles et filières.\n\n"
            "2. CONTRAINTES\n"
            "   Définissez les contraintes fortes (obligatoires) et faibles\n"
            "   (préférences). Déclarez les indisponibilités des enseignants.\n\n"
            "3. TABLEAU DE BORD\n"
            "   Sélectionnez la semaine et cliquez sur « Générer ».\n"
            "   L'algorithme placera automatiquement toutes les sessions\n"
            "   en respectant les contraintes fortes.\n\n"
            "4. PLANNING\n"
            "   Visualisez la grille hebdomadaire par filière, enseignant\n"
            "   ou salle. Survolez une session pour voir ses détails.\n\n"
            "5. SESSIONS\n"
            "   Modifiez manuellement les sessions, ajoutez-en,\n"
            "   ou lancez l'analyse des conflits.\n\n"
            "6. EXPORT\n"
            "   Exportez en CSV (données brutes) ou en PDF (planning\n"
            "   formaté imprimable), avec filtrage par filière ou enseignant."
        )

        txt = tk.Text(aide, font=FONT_NORMAL, bg=COULEUR_BLANC, fg=COULEUR_TEXTE,
                      relief="flat", padx=20, pady=10, wrap="word")
        txt.insert("1.0", texte)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(aide, text="Fermer", command=aide.destroy,
                  font=FONT_BOLD, bg=COULEUR_PRIMAIRE, fg=COULEUR_BLANC,
                  relief="flat", padx=16, pady=6).pack(pady=(0, 14))

    def _quitter(self):
        if messagebox.askyesno("Quitter",
                                "Êtes-vous sûr de vouloir quitter l'application ?\n"
                                "(Les données en mémoire seront perdues.)"):
            self.root.destroy()
