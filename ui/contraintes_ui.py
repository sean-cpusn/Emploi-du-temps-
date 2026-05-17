"""
ui/contraintes_ui.py
Interface de gestion des contraintes et détection des conflits.
"""

import tkinter as tk
from tkinter import messagebox

from utils.theme import *
from utils.widgets import (BoutonPrincipal, BoutonDanger, BoutonSucces,
                            TableauTrie, FormulaireModal)
from models.repository import Repository
from models.entities import Contrainte, TypeContrainte
from services.contraintes import ServiceContraintes


class PanneauContraintes(tk.Frame):

    def __init__(self, parent, repo: Repository):
        super().__init__(parent, bg=COULEUR_FOND)
        self.repo = repo
        self.svc  = ServiceContraintes(repo)
        self._construire()

    def _construire(self):
        tk.Label(self, text="⚙️  Gestion des Contraintes", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_FOND).pack(
            anchor="w", padx=PAD * 2, pady=(18, 4))
        tk.Frame(self, bg=COULEUR_BORDURE, height=1).pack(fill="x", padx=PAD * 2, pady=(0, 8))

        corps = tk.Frame(self, bg=COULEUR_FOND)
        corps.pack(fill="both", expand=True, padx=PAD * 2)
        corps.columnconfigure(0, weight=1)
        corps.columnconfigure(1, weight=1)
        corps.rowconfigure(0, weight=1)

        # ── Colonne gauche : liste des contraintes ────────────
        frame_gauche = tk.LabelFrame(corps, text=" Contraintes définies ",
                                     font=FONT_BOLD, bg=COULEUR_BLANC,
                                     fg=COULEUR_PRIMAIRE, relief="ridge", bd=1)
        frame_gauche.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)

        barre = tk.Frame(frame_gauche, bg=COULEUR_BLANC, pady=6)
        barre.pack(fill="x")
        BoutonSucces(barre, "➕ Ajouter", self._ajouter).pack(side="left", padx=PAD)
        BoutonDanger(barre, "🗑 Supprimer", self._supprimer).pack(side="left", padx=4)

        COLS_C = ("ID", "Type", "Priorité", "Description")
        self.tableau = TableauTrie(frame_gauche, COLS_C)
        self.tableau.pack(fill="both", expand=True, padx=PAD, pady=4)
        self.tableau.tree.column("ID", width=60)
        self.tableau.tree.column("Type", width=70)
        self.tableau.tree.column("Priorité", width=60)
        self.tableau.tree.tag_configure("forte",
                                        foreground=COULEUR_DANGER,
                                        font=FONT_BOLD)
        self.tableau.tree.tag_configure("faible",
                                        foreground=COULEUR_WARNING)
        self._actualiser_contraintes()

        # ── Colonne droite : détection des conflits ───────────
        frame_droite = tk.LabelFrame(corps, text=" Détection des Conflits ",
                                     font=FONT_BOLD, bg=COULEUR_BLANC,
                                     fg=COULEUR_PRIMAIRE, relief="ridge", bd=1)
        frame_droite.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)

        barre2 = tk.Frame(frame_droite, bg=COULEUR_BLANC, pady=6)
        barre2.pack(fill="x")
        BoutonPrincipal(barre2, "🔍 Analyser les conflits",
                        self._analyser_conflits,
                        couleur=COULEUR_DANGER).pack(side="left", padx=PAD)

        self.lbl_resume = tk.Label(frame_droite, text="Aucune analyse effectuée.",
                                    font=FONT_SMALL, fg=COULEUR_TEXTE_CLAIR,
                                    bg=COULEUR_BLANC)
        self.lbl_resume.pack(anchor="w", padx=PAD)

        COLS_CON = ("Session ID", "Problème détecté")
        self.tableau_conflits = TableauTrie(frame_droite, COLS_CON)
        self.tableau_conflits.pack(fill="both", expand=True, padx=PAD, pady=4)
        self.tableau_conflits.tree.column("Session ID", width=90)

        # ── Bas : indisponibilités enseignants ────────────────
        frame_indisp = tk.LabelFrame(self, text=" Indisponibilités des Enseignants ",
                                      font=FONT_BOLD, bg=COULEUR_BLANC,
                                      fg=COULEUR_PRIMAIRE, relief="ridge", bd=1)
        frame_indisp.pack(fill="x", padx=PAD * 2, pady=8, ipady=4)

        tk.Label(frame_indisp,
                 text="Sélectionnez un enseignant et cochez les créneaux indisponibles :",
                 font=FONT_SMALL, fg=COULEUR_TEXTE_CLAIR,
                 bg=COULEUR_BLANC).pack(anchor="w", padx=PAD, pady=(4, 2))

        frame_indisp_ctrl = tk.Frame(frame_indisp, bg=COULEUR_BLANC)
        frame_indisp_ctrl.pack(fill="x", padx=PAD)

        tk.Label(frame_indisp_ctrl, text="Enseignant :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(side="left")
        self._ids_ens = [e.id for e in self.repo.liste_enseignants()]
        noms_ens = [str(e) for e in self.repo.liste_enseignants()]
        import tkinter.ttk as ttk
        self.cb_ens = ttk.Combobox(frame_indisp_ctrl, values=noms_ens,
                                   state="readonly", font=FONT_NORMAL, width=25)
        if noms_ens:
            self.cb_ens.set(noms_ens[0])
        self.cb_ens.pack(side="left", padx=8)
        self.cb_ens.bind("<<ComboboxSelected>>", lambda e: self._afficher_indisp())

        tk.Label(frame_indisp_ctrl, text="Créneau bloqué :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(side="left", padx=(16, 4))
        creneaux = self.repo.liste_creneaux(semaine=1)
        noms_cren = [str(c) for c in creneaux]
        self._ids_cren = [c.id for c in creneaux]
        self.cb_cren = ttk.Combobox(frame_indisp_ctrl, values=noms_cren,
                                    state="readonly", font=FONT_NORMAL, width=30)
        if noms_cren:
            self.cb_cren.set(noms_cren[0])
        self.cb_cren.pack(side="left", padx=4)

        BoutonDanger(frame_indisp_ctrl, "🚫 Bloquer ce créneau",
                     self._bloquer_creneau).pack(side="left", padx=8)
        BoutonSucces(frame_indisp_ctrl, "✅ Débloquer",
                     self._debloquer_creneau).pack(side="left", padx=4)

        self.lbl_indisp = tk.Label(frame_indisp,
                                    text="", font=FONT_SMALL,
                                    fg=COULEUR_DANGER, bg=COULEUR_BLANC)
        self.lbl_indisp.pack(anchor="w", padx=PAD, pady=(2, 6))

    # ──────────────────────────────────────────────────────────

    def _actualiser_contraintes(self):
        self.tableau.vider()
        for c in self.repo.liste_contraintes():
            tag = "forte" if c.type_contrainte == TypeContrainte.FORTE else "faible"
            self.tableau.ajouter_ligne(
                (c.id, c.type_contrainte.value, c.priorite, c.description),
                tag=tag, iid=c.id
            )

    def _ajouter(self):
        dlg = DialogueContrainte(self, self.repo)
        self.wait_window(dlg)
        self._actualiser_contraintes()

    def _supprimer(self):
        sel = self.tableau.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une contrainte.")
            return
        if messagebox.askyesno("Confirmer", "Supprimer cette contrainte ?"):
            self.repo.supprimer_contrainte(sel[0])
            self._actualiser_contraintes()

    def _analyser_conflits(self):
        self.tableau_conflits.vider()
        conflits = self.svc.detecter_tous_conflits()
        if not conflits:
            self.lbl_resume.config(
                text="✅ Aucun conflit détecté. Planning cohérent.",
                fg=COULEUR_ACCENT)
        else:
            self.lbl_resume.config(
                text=f"⚠️ {len(conflits)} conflit(s) détecté(s) :",
                fg=COULEUR_DANGER)
            for session, erreurs in conflits:
                for err in erreurs:
                    self.tableau_conflits.ajouter_ligne(
                        (session.id, err), tag="conflit"
                    )

    def _afficher_indisp(self):
        idx = self.cb_ens.current()
        if idx < 0:
            return
        ens = self.repo.get_enseignant(self._ids_ens[idx])
        if ens:
            nb = len(ens.indisponibilites)
            self.lbl_indisp.config(
                text=f"{nb} créneau(x) bloqué(s) pour {ens}.")

    def _bloquer_creneau(self):
        idx_e = self.cb_ens.current()
        idx_c = self.cb_cren.current()
        if idx_e < 0 or idx_c < 0:
            return
        ens = self.repo.get_enseignant(self._ids_ens[idx_e])
        cren_id = self._ids_cren[idx_c]
        if ens and cren_id not in ens.indisponibilites:
            ens.indisponibilites.append(cren_id)
            self.repo.modifier_enseignant(ens)
        self._afficher_indisp()

    def _debloquer_creneau(self):
        idx_e = self.cb_ens.current()
        idx_c = self.cb_cren.current()
        if idx_e < 0 or idx_c < 0:
            return
        ens = self.repo.get_enseignant(self._ids_ens[idx_e])
        cren_id = self._ids_cren[idx_c]
        if ens and cren_id in ens.indisponibilites:
            ens.indisponibilites.remove(cren_id)
            self.repo.modifier_enseignant(ens)
        self._afficher_indisp()

    def actualiser(self):
        self._actualiser_contraintes()


# ── Dialogue Contrainte ──────────────────────────────────────

class DialogueContrainte(FormulaireModal):
    def __init__(self, parent, repo):
        super().__init__(parent, "Ajouter une contrainte", largeur=480, hauteur=340)
        self.repo = repo

        self.cb_type = self._combo("Type *",
                                   [t.value for t in TypeContrainte], "forte")
        self.e_desc  = self._champ("Description *", "")
        self.e_prio  = self._champ("Priorité (1 = max) *", "1")

        BoutonSucces(self.barre_boutons, "💾  Enregistrer", self._enregistrer).pack(
            side="right", padx=PAD)
        BoutonDanger(self.barre_boutons, "Annuler", self.destroy).pack(side="right", padx=4)

    def _enregistrer(self):
        desc = self.e_desc.get().strip()
        try:
            prio = int(self.e_prio.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "La priorité doit être un entier.", parent=self)
            return
        if not desc:
            messagebox.showerror("Erreur", "La description est obligatoire.", parent=self)
            return
        type_c = TypeContrainte(self.cb_type.get())
        self.repo.ajouter_contrainte(Contrainte(type_c, desc, prio))
        self.destroy()
