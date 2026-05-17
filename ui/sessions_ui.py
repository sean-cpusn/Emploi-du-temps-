"""
ui/sessions_ui.py
Liste complète des sessions avec édition manuelle et détection de conflits.

"""

import tkinter as tk
from tkinter import messagebox, ttk

from utils.theme import *
from utils.widgets import (BoutonPrincipal, BoutonDanger, BoutonSucces,
                            TableauTrie, FormulaireModal)
from models.repository import Repository
from models.entities import Session, StatutSession
from services.contraintes import ServiceContraintes


class PanneauSessions(tk.Frame):

    def __init__(self, parent, repo: Repository):
        super().__init__(parent, bg=COULEUR_FOND)
        self.repo = repo
        self.svc  = ServiceContraintes(repo)
        self._construire()

    def _construire(self):
        # En-tête
        entete = tk.Frame(self, bg=COULEUR_FOND)
        entete.pack(fill="x", padx=PAD * 2, pady=(18, 4))
        tk.Label(entete, text="🗂  Sessions Planifiées", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_FOND).pack(side="left")

        tk.Frame(self, bg=COULEUR_BORDURE, height=1).pack(
            fill="x", padx=PAD * 2, pady=(0, 6))

        # Barre d'outils
        barre = tk.Frame(self, bg=COULEUR_FOND, pady=6)
        barre.pack(fill="x", padx=PAD * 2)

        BoutonSucces(barre, "➕ Ajouter manuellement",
                     self._ajouter).pack(side="left", padx=(0, 6))
        BoutonPrincipal(barre, "✏️ Modifier",
                        self._modifier, couleur=COULEUR_WARNING).pack(side="left", padx=4)
        BoutonDanger(barre, "🗑 Supprimer",
                     self._supprimer).pack(side="left", padx=4)
        BoutonPrincipal(barre, "🔍 Analyser conflits",
                        self._analyser, couleur=COULEUR_DANGER).pack(side="left", padx=16)
        BoutonPrincipal(barre, "🔄 Actualiser",
                        self.actualiser, couleur=COULEUR_SIDEBAR).pack(side="left", padx=4)

        # Filtre rapide
        tk.Label(barre, text="Filtre :", font=FONT_SMALL,
                 bg=COULEUR_FOND).pack(side="left", padx=(20, 4))
        self.var_filtre = tk.StringVar()
        tk.Entry(barre, textvariable=self.var_filtre, font=FONT_NORMAL,
                 relief="solid", bd=1, width=20).pack(side="left")
        self.var_filtre.trace("w", lambda *_: self.actualiser())

        # Légende statuts
        for statut, couleur in [("planifie", COULEUR_ACCENT),
                                  ("conflit", COULEUR_DANGER),
                                  ("annule", COULEUR_TEXTE_CLAIR)]:
            tk.Label(barre, text=f"  {statut}  ", bg=couleur,
                     fg=COULEUR_BLANC, font=FONT_SMALL,
                     relief="flat").pack(side="right", padx=2)
        tk.Label(barre, text="Statuts :", font=FONT_SMALL,
                 bg=COULEUR_FOND).pack(side="right", padx=8)

        # Tableau
        COLS = ("ID", "Jour", "Horaire", "Matière", "Enseignant",
                "Salle", "Filière", "Statut")
        self.tableau = TableauTrie(self, COLS)
        self.tableau.pack(fill="both", expand=True, padx=PAD * 2, pady=4)
        self.tableau.tree.column("ID", width=70)
        self.tableau.tree.column("Jour", width=80)
        self.tableau.tree.column("Horaire", width=110)
        self.tableau.tree.column("Matière", width=180)
        self.tableau.tree.column("Enseignant", width=150)
        self.tableau.tree.column("Salle", width=70)
        self.tableau.tree.column("Filière", width=160)
        self.tableau.tree.column("Statut", width=80)

        self.tableau.tree.tag_configure("conflit",
                                        background="#fde8e8",
                                        foreground=COULEUR_DANGER)
        self.tableau.tree.tag_configure("annule",
                                        background="#f0f0f0",
                                        foreground=COULEUR_TEXTE_CLAIR)

        # Barre de statut
        self.lbl_status = tk.Label(self, text="", font=FONT_SMALL,
                                    fg=COULEUR_TEXTE_CLAIR, bg=COULEUR_FOND)
        self.lbl_status.pack(anchor="w", padx=PAD * 2, pady=4)

        self.actualiser()

    # ──────────────────────────────────────────────────────────

    def actualiser(self):
        filtre = self.var_filtre.get().lower()
        self.tableau.vider()
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

        sessions = self.repo.liste_sessions()
        sessions.sort(key=lambda s: (
            jours.index(c.jour) if (c := self.repo.get_creneau(s.creneau_id))
            and c.jour in jours else 99,
            self.repo.get_creneau(s.creneau_id).heure_debut.strftime("%H:%M")
            if self.repo.get_creneau(s.creneau_id) else ""
        ))

        for s in sessions:
            c  = self.repo.get_creneau(s.creneau_id)
            m  = self.repo.get_matiere(s.matiere_id)
            e  = self.repo.get_enseignant(s.enseignant_id)
            sa = self.repo.get_salle(s.salle_id)
            fi = self.repo.get_filiere(m.filiere_id) if m else None

            horaire = (f"{c.heure_debut.strftime('%H:%M')}–"
                       f"{c.heure_fin.strftime('%H:%M')}") if c else "?"
            vals = (
                s.id,
                c.jour if c else "?",
                horaire,
                m.intitule if m else "?",
                str(e) if e else "?",
                sa.numero if sa else "?",
                str(fi) if fi else "?",
                s.statut.value
            )
            if filtre and filtre not in " ".join(str(v).lower() for v in vals):
                continue

            tag = s.statut.value if s.statut != StatutSession.PLANIFIE else ""
            self.tableau.ajouter_ligne(vals, tag=tag, iid=s.id)

        nb = len(self.repo.liste_sessions())
        self.lbl_status.config(text=f"Total : {nb} session(s) planifiée(s).")

    def _item_selectionne(self):
        sel = self.tableau.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une session.")
            return None
        return self.repo.get_session(sel[0])

    def _ajouter(self):
        dlg = DialogueSession(self, self.repo, self.svc)
        self.wait_window(dlg)
        self.actualiser()

    def _modifier(self):
        s = self._item_selectionne()
        if s:
            dlg = DialogueSession(self, self.repo, self.svc, s)
            self.wait_window(dlg)
            self.actualiser()

    def _supprimer(self):
        s = self._item_selectionne()
        if s and messagebox.askyesno("Confirmer", "Supprimer cette session ?"):
            self.repo.supprimer_session(s.id)
            self.actualiser()

    def _analyser(self):
        conflits = self.svc.detecter_tous_conflits()
        # Marquer les sessions en conflit
        for s in self.repo.liste_sessions():
            s.statut = StatutSession.PLANIFIE
        for session, _ in conflits:
            session.statut = StatutSession.CONFLIT
            self.repo.modifier_session(session)
        self.actualiser()
        if conflits:
            messagebox.showwarning("Conflits détectés",
                                   f"{len(conflits)} conflit(s) détecté(s).\n"
                                   f"Les sessions concernées sont surlignées en rouge.")
        else:
            messagebox.showinfo("Analyse terminée",
                                "✅ Aucun conflit détecté. Planning cohérent !")


# ── Dialogue Session ─────────────────────────────────────────

class DialogueSession(FormulaireModal):
    def __init__(self, parent, repo, svc, session: Session = None):
        super().__init__(parent,
                         "Ajouter une session" if not session else "Modifier la session",
                         largeur=500, hauteur=500)
        self.repo    = repo
        self.svc     = svc
        self.session = session

        # Enseignants
        ens_list    = repo.liste_enseignants()
        noms_ens    = [str(e) for e in ens_list]
        self._ids_e = [e.id for e in ens_list]
        defaut_e    = str(repo.get_enseignant(session.enseignant_id)) if session else ""
        self.cb_ens = self._combo("Enseignant *", noms_ens, defaut_e)

        # Matières
        mat_list    = repo.liste_matieres()
        noms_mat    = [f"{m.code} – {m.intitule}" for m in mat_list]
        self._ids_m = [m.id for m in mat_list]
        defaut_m    = ""
        if session:
            m = repo.get_matiere(session.matiere_id)
            defaut_m = f"{m.code} – {m.intitule}" if m else ""
        self.cb_mat = self._combo("Matière *", noms_mat, defaut_m)

        # Salles
        sal_list    = repo.liste_salles()
        noms_sal    = [str(s) for s in sal_list]
        self._ids_s = [s.id for s in sal_list]
        defaut_s    = str(repo.get_salle(session.salle_id)) if session else ""
        self.cb_sal = self._combo("Salle *", noms_sal, defaut_s)

        # Créneaux
        cren_list   = repo.liste_creneaux(semaine=1)
        noms_cren   = [str(c) for c in cren_list]
        self._ids_c = [c.id for c in cren_list]
        defaut_c    = str(repo.get_creneau(session.creneau_id)) if session else ""
        self.cb_cren = self._combo("Créneau *", noms_cren, defaut_c)

        # Statut
        self.cb_stat = self._combo("Statut",
                                   [s.value for s in StatutSession],
                                   session.statut.value if session else "planifie")

        # Boutons
        BoutonSucces(self.barre_boutons, "💾  Enregistrer",
                     self._enregistrer).pack(side="right", padx=PAD)
        BoutonDanger(self.barre_boutons, "Annuler",
                     self.destroy).pack(side="right", padx=4)

    def _enregistrer(self):
        idx_e = self.cb_ens.current()
        idx_m = self.cb_mat.current()
        idx_s = self.cb_sal.current()
        idx_c = self.cb_cren.current()
        if any(i < 0 for i in [idx_e, idx_m, idx_s, idx_c]):
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.", parent=self)
            return

        ens_id  = self._ids_e[idx_e]
        mat_id  = self._ids_m[idx_m]
        sal_id  = self._ids_s[idx_s]
        cren_id = self._ids_c[idx_c]
        statut  = StatutSession(self.cb_stat.get())

        if self.session:
            s = self.session
            s.enseignant_id = ens_id
            s.matiere_id    = mat_id
            s.salle_id      = sal_id
            s.creneau_id    = cren_id
            s.statut        = statut
        else:
            s = Session(ens_id, mat_id, sal_id, cren_id, statut)

        # Validation des contraintes fortes
        autres = [x for x in self.repo.liste_sessions()
                  if not self.session or x.id != self.session.id]
        ok, erreurs = self.svc.valider_session(s, autres)
        if not ok:
            msg = "\n".join(f"• {e}" for e in erreurs)
            rep = messagebox.askyesno(
                "Contrainte violée",
                f"Cette session viole des contraintes fortes :\n\n{msg}\n\n"
                f"Enregistrer quand même (statut CONFLIT) ?",
                parent=self
            )
            if not rep:
                return
            s.statut = StatutSession.CONFLIT

        if self.session:
            self.repo.modifier_session(s)
        else:
            self.repo.ajouter_session(s)
        self.destroy()
