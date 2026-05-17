"""
utils/widgets.py
Widgets Tkinter réutilisables dans toute l'application.
"""

import tkinter as tk
from tkinter import ttk
from utils.theme import *


class BoutonPrincipal(tk.Button):
    """Bouton bleu arrondi"""
    def __init__(self, parent, texte, commande=None, couleur=COULEUR_SECONDAIRE, **kwargs):
        super().__init__(
            parent,
            text=texte,
            command=commande,
            bg=couleur,
            fg=COULEUR_BLANC,
            font=FONT_BOLD,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            activebackground=COULEUR_HOVER,
            activeforeground=COULEUR_BLANC,
            bd=0,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=COULEUR_HOVER))
        self.bind("<Leave>", lambda e: self.config(bg=couleur))


class BoutonDanger(BoutonPrincipal):
    def __init__(self, parent, texte, commande=None, **kwargs):
        super().__init__(parent, texte, commande, couleur=COULEUR_DANGER, **kwargs)


class BoutonSucces(BoutonPrincipal):
    def __init__(self, parent, texte, commande=None, **kwargs):
        super().__init__(parent, texte, commande, couleur=COULEUR_ACCENT, **kwargs)


class LabelTitre(tk.Label):
    def __init__(self, parent, texte, **kwargs):
        super().__init__(
            parent, text=texte, font=FONT_TITRE,
            fg=COULEUR_PRIMAIRE, bg=COULEUR_FOND, **kwargs
        )


class LabelSousTitre(tk.Label):
    def __init__(self, parent, texte, **kwargs):
        super().__init__(
            parent, text=texte, font=FONT_SOUS_TITRE,
            fg=COULEUR_PRIMAIRE, bg=COULEUR_BLANC, **kwargs
        )


class CarteStat(tk.Frame):
    """Carte de statistique du tableau de bord """
    def __init__(self, parent, titre, valeur, couleur=COULEUR_SECONDAIRE, **kwargs):
        super().__init__(parent, bg=COULEUR_BLANC, relief="ridge", bd=1, **kwargs)
        tk.Label(self, text=titre, font=FONT_SMALL, fg=COULEUR_TEXTE_CLAIR,
                 bg=COULEUR_BLANC).pack(pady=(10, 2))
        self.lbl_valeur = tk.Label(self, text=str(valeur), font=("Segoe UI", 22, "bold"),
                                   fg=couleur, bg=COULEUR_BLANC)
        self.lbl_valeur.pack(pady=(0, 10))

    def mettre_a_jour(self, valeur):
        self.lbl_valeur.config(text=str(valeur))


class TableauTrie(tk.Frame):
    """Treeview stylisé avec en-têtes cliquables pour tri."""
    def __init__(self, parent, colonnes, **kwargs):
        super().__init__(parent, bg=COULEUR_FOND, **kwargs)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=COULEUR_BLANC,
                        foreground=COULEUR_TEXTE,
                        rowheight=26,
                        fieldbackground=COULEUR_BLANC,
                        font=FONT_NORMAL)
        style.configure("Custom.Treeview.Heading",
                        background=COULEUR_PRIMAIRE,
                        foreground=COULEUR_BLANC,
                        font=FONT_BOLD,
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", COULEUR_SECONDAIRE)],
                  foreground=[("selected", COULEUR_BLANC)])

        scrollbar_v = ttk.Scrollbar(self, orient="vertical")
        scrollbar_h = ttk.Scrollbar(self, orient="horizontal")

        self.tree = ttk.Treeview(
            self,
            columns=colonnes,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar_v.set,
            xscrollcommand=scrollbar_h.set,
        )
        scrollbar_v.config(command=self.tree.yview)
        scrollbar_h.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for col in colonnes:
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._trier(c))
            self.tree.column(col, anchor="w", minwidth=80)

        self.tree.tag_configure("pair", background="#f8f9fa")
        self.tree.tag_configure("impair", background=COULEUR_BLANC)
        self.tree.tag_configure("conflit", background="#fde8e8",
                                foreground=COULEUR_DANGER)

    def _trier(self, colonne):
        items = [(self.tree.set(k, colonne), k) for k in self.tree.get_children()]
        items.sort()
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, "", idx)

    def vider(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def ajouter_ligne(self, valeurs, tag="", iid=None):
        nb = len(self.tree.get_children())
        t = tag if tag else ("pair" if nb % 2 == 0 else "impair")
        return self.tree.insert("", "end", values=valeurs, tags=(t,), iid=iid)


class BarreProgression(tk.Frame):
    """Barre de progression animée."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COULEUR_FOND, **kwargs)
        self.barre = ttk.Progressbar(self, orient="horizontal",
                                     mode="determinate", length=400)
        self.barre.pack(fill="x", padx=PAD, pady=PAD_SMALL)
        self.lbl = tk.Label(self, text="", font=FONT_SMALL,
                            fg=COULEUR_TEXTE_CLAIR, bg=COULEUR_FOND)
        self.lbl.pack()

    def mettre_a_jour(self, pct: int, message: str = ""):
        self.barre["value"] = pct
        self.lbl.config(text=message)
        self.update_idletasks()


class FormulaireModal(tk.Toplevel):
    """Fenêtre modale de base pour les formulaires de saisie."""
    def __init__(self, parent, titre: str, largeur=480, hauteur=420):
        super().__init__(parent)
        self.title(titre)
        self.resizable(False, False)
        self.configure(bg=COULEUR_BLANC)
        self.grab_set()
        self.result = None

        # Centrer la fenêtre
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - largeur)  // 2
        py = parent.winfo_y() + (parent.winfo_height() - hauteur) // 2
        self.geometry(f"{largeur}x{hauteur}+{px}+{py}")

        # En-tête
        header = tk.Frame(self, bg=COULEUR_PRIMAIRE, height=50)
        header.pack(fill="x")
        tk.Label(header, text=titre, font=FONT_SOUS_TITRE,
                 fg=COULEUR_BLANC, bg=COULEUR_PRIMAIRE).pack(pady=12)

        # Zone de contenu (à remplir par les sous-classes)
        self.corps = tk.Frame(self, bg=COULEUR_BLANC, padx=20, pady=15)
        self.corps.pack(fill="both", expand=True)

        # Barre de boutons
        self.barre_boutons = tk.Frame(self, bg=COULEUR_FOND, pady=8)
        self.barre_boutons.pack(fill="x", side="bottom")

    def _champ(self, libelle: str, valeur_defaut: str = "") -> tk.Entry:
        """Ajoute un label + entry et retourne l'Entry."""
        tk.Label(self.corps, text=libelle, font=FONT_BOLD,
                 bg=COULEUR_BLANC, anchor="w").pack(fill="x", pady=(6, 1))
        e = tk.Entry(self.corps, font=FONT_NORMAL, relief="solid", bd=1)
        e.pack(fill="x", ipady=4)
        if valeur_defaut:
            e.insert(0, valeur_defaut)
        return e

    def _combo(self, libelle: str, valeurs: list, defaut: str = "") -> ttk.Combobox:
        """Ajoute un label + combobox et retourne le Combobox."""
        tk.Label(self.corps, text=libelle, font=FONT_BOLD,
                 bg=COULEUR_BLANC, anchor="w").pack(fill="x", pady=(6, 1))
        cb = ttk.Combobox(self.corps, values=valeurs,
                          state="readonly", font=FONT_NORMAL)
        cb.pack(fill="x", ipady=2)
        if defaut in valeurs:
            cb.set(defaut)
        elif valeurs:
            cb.set(valeurs[0])
        return cb
