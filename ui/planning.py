"""
ui/planning.py
Visualisation de l'emploi du temps sous forme de grille hebdomadaire.

"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from utils.theme import *
from models.repository import Repository
from models.entities import Session, JOURS_SEMAINE


# ──────────────────────────────────────────────────────────────
#  Constantes de la grille
# ──────────────────────────────────────────────────────────────
HEURE_DEBUT = 7       # 07h
HEURE_FIN   = 17     # 17h
NB_HEURES   = HEURE_FIN - HEURE_DEBUT
PIXELS_PAR_HEURE = 70
LARGEUR_HEURE    = 60   # colonne des heures
LARGEUR_JOUR     = 160  # colonne de chaque jour
HAUTEUR_ENTETE   = 36


class PanneauPlanning(tk.Frame):

    def __init__(self, parent, repo: Repository):
        super().__init__(parent, bg=COULEUR_FOND)
        self.repo = repo
        self._construire()

    def _construire(self):
        # ── Barre de filtres ─────────────────────────────────
        barre = tk.Frame(self, bg=COULEUR_BLANC, relief="ridge", bd=1)
        barre.pack(fill="x", padx=PAD * 2, pady=(18, 6))

        tk.Label(barre, text="📅  Emploi du Temps", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_BLANC).pack(
            side="left", padx=16, pady=10)

        # Filtre type de vue
        tk.Label(barre, text="Voir par :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(side="left", padx=(20, 4))
        self.var_vue = tk.StringVar(value="Filière")
        for opt in ("Filière", "Enseignant", "Salle"):
            tk.Radiobutton(barre, text=opt, variable=self.var_vue, value=opt,
                           font=FONT_NORMAL, bg=COULEUR_BLANC,
                           command=self._on_changement_vue).pack(side="left", padx=4)

        # Sélecteur de ressource
        tk.Label(barre, text="Sélection :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(side="left", padx=(16, 4))
        self.cb_selection = ttk.Combobox(barre, state="readonly",
                                         font=FONT_NORMAL, width=28)
        self.cb_selection.pack(side="left", padx=4, pady=8)
        self.cb_selection.bind("<<ComboboxSelected>>", lambda e: self._afficher())

        # Semaine
        tk.Label(barre, text="Semaine :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(side="left", padx=(16, 4))
        self.spin_sem = tk.Spinbox(barre, from_=1, to=52, width=4,
                                   font=FONT_NORMAL, relief="solid", bd=1,
                                   command=self._afficher)
        self.spin_sem.pack(side="left", padx=4)

        tk.Button(barre, text="🔄 Rafraîchir", command=self._afficher,
                  font=FONT_BOLD, bg=COULEUR_SECONDAIRE, fg=COULEUR_BLANC,
                  relief="flat", padx=10, cursor="hand2").pack(side="right", padx=12, pady=8)

        # Légende types
        frame_leg = tk.Frame(barre, bg=COULEUR_BLANC)
        frame_leg.pack(side="right", padx=12)
        for type_s, couleur in COULEURS_SEANCE.items():
            tk.Label(frame_leg, text=f"  {type_s} ", bg=couleur,
                     fg=COULEUR_BLANC, font=FONT_SMALL,
                     relief="flat", padx=4).pack(side="left", padx=2)

        # ── Canvas de la grille ──────────────────────────────
        self.frame_canvas = tk.Frame(self, bg=COULEUR_FOND)
        self.frame_canvas.pack(fill="both", expand=True, padx=PAD * 2, pady=4)

        self.canvas = tk.Canvas(self.frame_canvas, bg=COULEUR_BLANC,
                                highlightthickness=0)
        scr_v = tk.Scrollbar(self.frame_canvas, orient="vertical",
                              command=self.canvas.yview)
        scr_h = tk.Scrollbar(self.frame_canvas, orient="horizontal",
                              command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scr_v.set, xscrollcommand=scr_h.set)

        scr_v.pack(side="right", fill="y")
        scr_h.pack(side="bottom", fill="x")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._on_changement_vue()

    # ──────────────────────────────────────────────────────────

    def _on_changement_vue(self):
        vue = self.var_vue.get()
        if vue == "Filière":
            items = [str(f) for f in self.repo.liste_filieres()]
            self._ids = [f.id for f in self.repo.liste_filieres()]
        elif vue == "Enseignant":
            items = [str(e) for e in self.repo.liste_enseignants()]
            self._ids = [e.id for e in self.repo.liste_enseignants()]
        else:
            items = [str(s) for s in self.repo.liste_salles()]
            self._ids = [s.id for s in self.repo.liste_salles()]

        self.cb_selection["values"] = items
        if items:
            self.cb_selection.set(items[0])
        self._afficher()

    def _afficher(self):
        self.canvas.delete("all")
        if not self._ids:
            return
        idx = self.cb_selection.current()
        if idx < 0:
            idx = 0
        res_id = self._ids[idx]
        try:
            semaine = int(self.spin_sem.get())
        except ValueError:
            semaine = 1

        sessions = self._filtrer_sessions(res_id, semaine)
        self._dessiner_grille()
        self._dessiner_sessions(sessions)

        largeur_tot = LARGEUR_HEURE + len(JOURS_SEMAINE) * LARGEUR_JOUR + 20
        hauteur_tot = HAUTEUR_ENTETE + NB_HEURES * PIXELS_PAR_HEURE + 20
        self.canvas.config(scrollregion=(0, 0, largeur_tot, hauteur_tot))

    def _filtrer_sessions(self, res_id: str, semaine: int):
        vue = self.var_vue.get()
        sessions = self.repo.liste_sessions()
        result = []
        for s in sessions:
            c = self.repo.get_creneau(s.creneau_id)
            if not c or c.semaine != semaine:
                continue
            if vue == "Filière":
                m = self.repo.get_matiere(s.matiere_id)
                if m and m.filiere_id == res_id:
                    result.append(s)
            elif vue == "Enseignant":
                if s.enseignant_id == res_id:
                    result.append(s)
            else:
                if s.salle_id == res_id:
                    result.append(s)
        return result

    # ── Dessin de la grille ───────────────────────────────────

    def _dessiner_grille(self):
        c = self.canvas
        # En-têtes des jours
        for j, jour in enumerate(JOURS_SEMAINE):
            x = LARGEUR_HEURE + j * LARGEUR_JOUR
            c.create_rectangle(x, 0, x + LARGEUR_JOUR, HAUTEUR_ENTETE,
                                fill=COULEUR_PRIMAIRE, outline="")
            c.create_text(x + LARGEUR_JOUR // 2, HAUTEUR_ENTETE // 2,
                          text=jour, fill=COULEUR_BLANC,
                          font=FONT_BOLD)

        # Lignes horaires
        for h in range(NB_HEURES + 1):
            y = HAUTEUR_ENTETE + h * PIXELS_PAR_HEURE
            heure_label = f"{HEURE_DEBUT + h:02d}:00"
            c.create_text(LARGEUR_HEURE - 6, y + 2, text=heure_label,
                          anchor="e", font=FONT_SMALL,
                          fill=COULEUR_TEXTE_CLAIR)
            c.create_line(LARGEUR_HEURE, y,
                          LARGEUR_HEURE + len(JOURS_SEMAINE) * LARGEUR_JOUR, y,
                          fill=COULEUR_BORDURE, dash=(3, 3))

        # Colonnes jours
        for j in range(len(JOURS_SEMAINE) + 1):
            x = LARGEUR_HEURE + j * LARGEUR_JOUR
            c.create_line(x, 0, x,
                          HAUTEUR_ENTETE + NB_HEURES * PIXELS_PAR_HEURE,
                          fill=COULEUR_BORDURE)

    def _dessiner_sessions(self, sessions):
        c = self.canvas
        jours_idx = {j: i for i, j in enumerate(JOURS_SEMAINE)}
        couleurs_fi = {}

        for s in sessions:
            creneau  = self.repo.get_creneau(s.creneau_id)
            matiere  = self.repo.get_matiere(s.matiere_id)
            ens      = self.repo.get_enseignant(s.enseignant_id)
            salle    = self.repo.get_salle(s.salle_id)
            if not creneau or creneau.jour not in jours_idx:
                continue

            j_idx = jours_idx[creneau.jour]
            h_deb = creneau.heure_debut.hour + creneau.heure_debut.minute / 60
            h_fin = creneau.heure_fin.hour   + creneau.heure_fin.minute   / 60
            y1 = HAUTEUR_ENTETE + (h_deb - HEURE_DEBUT) * PIXELS_PAR_HEURE
            y2 = HAUTEUR_ENTETE + (h_fin - HEURE_DEBUT) * PIXELS_PAR_HEURE
            x1 = LARGEUR_HEURE + j_idx * LARGEUR_JOUR + 3
            x2 = x1 + LARGEUR_JOUR - 6

            # Couleur selon type de séance ou filière
            type_s = matiere.type_seance.value if matiere else "CM"
            couleur = COULEURS_SEANCE.get(type_s, COULEUR_SECONDAIRE)

            if matiere and matiere.filiere_id not in couleurs_fi:
                idx_fi = len(couleurs_fi) % len(PALETTE_FILIERES)
                couleurs_fi[matiere.filiere_id] = PALETTE_FILIERES[idx_fi]

            # Dessin de la carte session
            c.create_rectangle(x1, y1, x2, y2,
                                fill=couleur, outline=COULEUR_BLANC, width=2)
            # Bande type séance
            c.create_rectangle(x1, y1, x1 + 6, y2,
                                fill=COULEUR_BLANC, outline="")

            # Texte de la session
            texte_mat = matiere.code if matiere else "?"
            texte_ens = str(ens) if ens else "?"
            texte_sal = salle.numero if salle else "?"
            horaire   = (f"{creneau.heure_debut.strftime('%H:%M')}"
                         f"–{creneau.heure_fin.strftime('%H:%M')}")

            milieu_y = (y1 + y2) / 2
            hauteur_bloc = y2 - y1

            if hauteur_bloc > 60:
                c.create_text(x1 + 12, y1 + 10, text=texte_mat,
                              anchor="nw", fill=COULEUR_BLANC, font=FONT_BOLD)
                c.create_text(x1 + 12, y1 + 26, text=texte_ens,
                              anchor="nw", fill=COULEUR_BLANC, font=FONT_SMALL)
                c.create_text(x1 + 12, y1 + 40, text=f"🚪 {texte_sal}  ⏰ {horaire}",
                              anchor="nw", fill=COULEUR_BLANC, font=FONT_SMALL)
            else:
                c.create_text((x1 + x2) / 2, milieu_y,
                              text=f"{texte_mat} | {texte_sal}",
                              fill=COULEUR_BLANC, font=FONT_SMALL)

            # Tooltip au survol
            rect_id = c.create_rectangle(x1, y1, x2, y2, outline="", fill="")
            tooltip_txt = (f"{matiere}\nEnseignant : {ens}\n"
                           f"Salle : {salle}\n{horaire}")
            c.tag_bind(rect_id, "<Enter>",
                       lambda e, t=tooltip_txt: self._montrer_tooltip(e, t))
            c.tag_bind(rect_id, "<Leave>", self._cacher_tooltip)

    def _montrer_tooltip(self, event, texte):
        self._cacher_tooltip(None)
        self._tooltip = tk.Toplevel(self)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{event.x_root + 12}+{event.y_root + 12}")
        tk.Label(self._tooltip, text=texte, font=FONT_SMALL,
                 bg="#2c3e50", fg="white", relief="flat",
                 padx=8, pady=6, justify="left").pack()

    def _cacher_tooltip(self, event):
        if hasattr(self, "_tooltip") and self._tooltip:
            try:
                self._tooltip.destroy()
            except Exception:
                pass
            self._tooltip = None

    def actualiser(self):
        self._on_changement_vue()
