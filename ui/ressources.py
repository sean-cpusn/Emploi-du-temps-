"""
ui/ressources.py
Gestion des ressources : Enseignants, Matières, Filières, Salles.

"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils.theme import *
from utils.widgets import (BoutonPrincipal, BoutonDanger, BoutonSucces,
                            TableauTrie, FormulaireModal)
from models.repository import Repository
from models.entities import (Enseignant, Matiere, Salle, Filiere,
                              TypeSeance, TypeSalle, NiveauFiliere)


# ══════════════════════════════════════════════════════════════
#  Panneau Ressources (onglets)
# ══════════════════════════════════════════════════════════════

class PanneauRessources(tk.Frame):

    def __init__(self, parent, repo: Repository):
        super().__init__(parent, bg=COULEUR_FOND)
        self.repo = repo
        self._construire()

    def _construire(self):
        tk.Label(self, text="📦  Gestion des Ressources", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_FOND).pack(
            anchor="w", padx=PAD * 2, pady=(18, 4))
        tk.Frame(self, bg=COULEUR_BORDURE, height=1).pack(fill="x", padx=PAD * 2, pady=(0, 8))

        style = ttk.Style()
        style.configure("Res.TNotebook.Tab", font=FONT_BOLD, padding=[12, 6])

        nb = ttk.Notebook(self, style="Res.TNotebook")
        nb.pack(fill="both", expand=True, padx=PAD * 2, pady=4)

        # Onglets
        self.tab_ens = OngletEnseignants(nb, self.repo)
        self.tab_mat = OngletMatieres(nb, self.repo)
        self.tab_sal = OngletSalles(nb, self.repo)
        self.tab_fil = OngletFilieres(nb, self.repo)

        nb.add(self.tab_ens, text="👨‍🏫  Enseignants")
        nb.add(self.tab_mat, text="📚  Matières")
        nb.add(self.tab_sal, text="🏫  Salles")
        nb.add(self.tab_fil, text="🎓  Filières")

    def actualiser(self):
        self.tab_ens.actualiser()
        self.tab_mat.actualiser()
        self.tab_sal.actualiser()
        self.tab_fil.actualiser()


# ══════════════════════════════════════════════════════════════
#  Mixin : barre de recherche + boutons CRUD
# ══════════════════════════════════════════════════════════════

class OngletBase(tk.Frame):

    def __init__(self, parent, repo: Repository):
        super().__init__(parent, bg=COULEUR_BLANC)
        self.repo = repo

    def _barre_outils(self, frame, cb_ajouter, cb_modifier, cb_supprimer):
        barre = tk.Frame(frame, bg=COULEUR_FOND, pady=6)
        barre.pack(fill="x")

        BoutonSucces(barre, "➕  Ajouter", cb_ajouter).pack(side="left", padx=(PAD, 4))
        BoutonPrincipal(barre, "✏️  Modifier", cb_modifier,
                        couleur=COULEUR_WARNING).pack(side="left", padx=4)
        BoutonDanger(barre, "🗑  Supprimer", cb_supprimer).pack(side="left", padx=4)

        tk.Label(barre, text="Recherche :", font=FONT_SMALL,
                 bg=COULEUR_FOND).pack(side="left", padx=(20, 4))
        self.var_recherche = tk.StringVar()
        e = tk.Entry(barre, textvariable=self.var_recherche, font=FONT_NORMAL,
                     relief="solid", bd=1, width=22)
        e.pack(side="left")
        self.var_recherche.trace("w", lambda *_: self.actualiser())

    def _item_selectionne(self, tableau):
        sel = tableau.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un élément.")
            return None
        return tableau.tree.item(sel[0])["values"]


# ══════════════════════════════════════════════════════════════
#  Onglet Enseignants
# ══════════════════════════════════════════════════════════════

class OngletEnseignants(OngletBase):

    COLONNES = ("ID", "Nom", "Prénom", "Email", "Vol. max (h)", "Matières")

    def __init__(self, parent, repo):
        super().__init__(parent, repo)
        self._construire()

    def _construire(self):
        self._barre_outils(self, self._ajouter, self._modifier, self._supprimer)
        self.tableau = TableauTrie(self, self.COLONNES)
        self.tableau.pack(fill="both", expand=True, padx=PAD, pady=4)
        self.tableau.tree.column("ID", width=60, minwidth=60)
        self.tableau.tree.column("Email", width=180)
        self.actualiser()

    def actualiser(self):
        filtre = getattr(self, "var_recherche", None)
        q = filtre.get().lower() if filtre else ""
        self.tableau.vider()
        for e in self.repo.liste_enseignants():
            nb_mat = len(e.matieres_ids)
            vals = (e.id, e.nom, e.prenom, e.email, e.vol_max_heures, nb_mat)
            if q and q not in " ".join(str(v).lower() for v in vals):
                continue
            self.tableau.ajouter_ligne(vals, iid=e.id)

    def _ajouter(self):
        dlg = DialogueEnseignant(self, self.repo)
        self.wait_window(dlg)
        self.actualiser()

    def _modifier(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        ens = self.repo.get_enseignant(vals[0])
        if ens:
            dlg = DialogueEnseignant(self, self.repo, ens)
            self.wait_window(dlg)
            self.actualiser()

    def _supprimer(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        if messagebox.askyesno("Confirmer", f"Supprimer l'enseignant {vals[1]} {vals[2]} ?"):
            self.repo.supprimer_enseignant(vals[0])
            self.actualiser()


# ── Dialogue Enseignant ──────────────────────────────────────

class DialogueEnseignant(FormulaireModal):
    def __init__(self, parent, repo, enseignant: Enseignant = None):
        super().__init__(parent, "Ajouter un enseignant" if not enseignant
                         else "Modifier l'enseignant", largeur=460, hauteur=420)
        self.repo = repo
        self.enseignant = enseignant

        self.e_nom    = self._champ("Nom *", enseignant.nom if enseignant else "")
        self.e_prenom = self._champ("Prénom *", enseignant.prenom if enseignant else "")
        self.e_email  = self._champ("Email *", enseignant.email if enseignant else "")
        self.e_vol    = self._champ("Volume horaire max (h/semaine) *",
                                    str(enseignant.vol_max_heures) if enseignant else "18")

        BoutonSucces(self.barre_boutons, "💾  Enregistrer", self._enregistrer).pack(
            side="right", padx=PAD)
        BoutonDanger(self.barre_boutons, "Annuler", self.destroy).pack(
            side="right", padx=4)

    def _enregistrer(self):
        nom    = self.e_nom.get().strip()
        prenom = self.e_prenom.get().strip()
        email  = self.e_email.get().strip()
        try:
            vol = int(self.e_vol.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "Volume horaire doit être un entier.", parent=self)
            return
        if not all([nom, prenom, email]):
            messagebox.showerror("Erreur", "Tous les champs marqués * sont obligatoires.",
                                 parent=self)
            return
        if self.enseignant:
            self.enseignant.nom = nom
            self.enseignant.prenom = prenom
            self.enseignant.email = email
            self.enseignant.vol_max_heures = vol
            self.repo.modifier_enseignant(self.enseignant)
        else:
            self.repo.ajouter_enseignant(Enseignant(nom, prenom, email, vol))
        self.destroy()


# ══════════════════════════════════════════════════════════════
#  Onglet Matières
# ══════════════════════════════════════════════════════════════

class OngletMatieres(OngletBase):

    COLONNES = ("ID", "Code", "Intitulé", "Filière", "Crédits", "Heures", "Type")

    def __init__(self, parent, repo):
        super().__init__(parent, repo)
        self._construire()

    def _construire(self):
        self._barre_outils(self, self._ajouter, self._modifier, self._supprimer)
        self.tableau = TableauTrie(self, self.COLONNES)
        self.tableau.pack(fill="both", expand=True, padx=PAD, pady=4)
        self.tableau.tree.column("ID", width=60)
        self.tableau.tree.column("Code", width=80)
        self.actualiser()

    def actualiser(self):
        q = getattr(self, "var_recherche", None)
        filtre = q.get().lower() if q else ""
        self.tableau.vider()
        for m in self.repo.liste_matieres():
            fi = self.repo.get_filiere(m.filiere_id)
            vals = (m.id, m.code, m.intitule,
                    str(fi) if fi else "—",
                    m.credits, m.heures_req, m.type_seance.value)
            if filtre and filtre not in " ".join(str(v).lower() for v in vals):
                continue
            self.tableau.ajouter_ligne(vals, iid=m.id)

    def _ajouter(self):
        dlg = DialogueMatiere(self, self.repo)
        self.wait_window(dlg)
        self.actualiser()

    def _modifier(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        mat = self.repo.get_matiere(vals[0])
        if mat:
            dlg = DialogueMatiere(self, self.repo, mat)
            self.wait_window(dlg)
            self.actualiser()

    def _supprimer(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        if messagebox.askyesno("Confirmer", f"Supprimer la matière {vals[2]} ?"):
            self.repo.supprimer_matiere(vals[0])
            self.actualiser()


class DialogueMatiere(FormulaireModal):
    def __init__(self, parent, repo, matiere: Matiere = None):
        super().__init__(parent, "Ajouter une matière" if not matiere
                         else "Modifier la matière", largeur=460, hauteur=500)
        self.repo = repo
        self.matiere = matiere

        filieres = self.repo.liste_filieres()
        noms_fil = [str(f) for f in filieres]
        self._ids_fil = [f.id for f in filieres]

        defaut_fil = ""
        if matiere:
            fi = repo.get_filiere(matiere.filiere_id)
            defaut_fil = str(fi) if fi else ""

        self.e_code    = self._champ("Code *", matiere.code if matiere else "")
        self.e_intit   = self._champ("Intitulé *", matiere.intitule if matiere else "")
        self.cb_fil    = self._combo("Filière *", noms_fil, defaut_fil)
        self.e_credits = self._champ("Crédits ECTS *", str(matiere.credits) if matiere else "3")
        self.e_heures  = self._champ("Heures requises *", str(matiere.heures_req) if matiere else "30")
        self.cb_type   = self._combo("Type de séance *",
                                     [t.value for t in TypeSeance],
                                     matiere.type_seance.value if matiere else "CM")

        BoutonSucces(self.barre_boutons, "💾  Enregistrer", self._enregistrer).pack(
            side="right", padx=PAD)
        BoutonDanger(self.barre_boutons, "Annuler", self.destroy).pack(side="right", padx=4)

    def _enregistrer(self):
        code   = self.e_code.get().strip()
        intit  = self.e_intit.get().strip()
        idx_fi = self.cb_fil.current()
        try:
            cred  = float(self.e_credits.get().strip())
            heures = int(self.e_heures.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "Crédits et heures doivent être numériques.", parent=self)
            return
        if not all([code, intit]) or idx_fi < 0:
            messagebox.showerror("Erreur", "Tous les champs * sont obligatoires.", parent=self)
            return
        fil_id = self._ids_fil[idx_fi]
        type_s = TypeSeance(self.cb_type.get())
        if self.matiere:
            self.matiere.code = code; self.matiere.intitule = intit
            self.matiere.filiere_id = fil_id; self.matiere.credits = cred
            self.matiere.heures_req = heures; self.matiere.type_seance = type_s
            self.repo.modifier_matiere(self.matiere)
        else:
            self.repo.ajouter_matiere(Matiere(code, intit, fil_id, cred, heures, type_s))
        self.destroy()


# ══════════════════════════════════════════════════════════════
#  Onglet Salles
# ══════════════════════════════════════════════════════════════

class OngletSalles(OngletBase):

    COLONNES = ("ID", "Numéro", "Bâtiment", "Capacité", "Type", "Disponible")

    def __init__(self, parent, repo):
        super().__init__(parent, repo)
        self._construire()

    def _construire(self):
        self._barre_outils(self, self._ajouter, self._modifier, self._supprimer)
        self.tableau = TableauTrie(self, self.COLONNES)
        self.tableau.pack(fill="both", expand=True, padx=PAD, pady=4)
        self.tableau.tree.column("ID", width=60)
        self.actualiser()

    def actualiser(self):
        q = getattr(self, "var_recherche", None)
        filtre = q.get().lower() if q else ""
        self.tableau.vider()
        for s in self.repo.liste_salles():
            vals = (s.id, s.numero, s.batiment, s.capacite,
                    s.type_salle.value, "Oui" if s.disponible else "Non")
            if filtre and filtre not in " ".join(str(v).lower() for v in vals):
                continue
            self.tableau.ajouter_ligne(vals, iid=s.id)

    def _ajouter(self):
        dlg = DialogueSalle(self, self.repo)
        self.wait_window(dlg)
        self.actualiser()

    def _modifier(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        salle = self.repo.get_salle(vals[0])
        if salle:
            dlg = DialogueSalle(self, self.repo, salle)
            self.wait_window(dlg)
            self.actualiser()

    def _supprimer(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        if messagebox.askyesno("Confirmer", f"Supprimer la salle {vals[1]} ?"):
            self.repo.supprimer_salle(vals[0])
            self.actualiser()


class DialogueSalle(FormulaireModal):
    def __init__(self, parent, repo, salle: Salle = None):
        super().__init__(parent, "Ajouter une salle" if not salle
                         else "Modifier la salle", largeur=440, hauteur=420)
        self.repo = repo
        self.salle = salle

        self.e_num  = self._champ("Numéro *", salle.numero if salle else "")
        self.e_bat  = self._champ("Bâtiment *", salle.batiment if salle else "")
        self.e_cap  = self._champ("Capacité *", str(salle.capacite) if salle else "")
        self.cb_type = self._combo("Type *",
                                   [t.value for t in TypeSalle],
                                   salle.type_salle.value if salle else "cours")
        self.var_dispo = tk.BooleanVar(value=salle.disponible if salle else True)
        tk.Checkbutton(self.corps, text="Salle disponible", variable=self.var_dispo,
                       font=FONT_NORMAL, bg=COULEUR_BLANC).pack(anchor="w", pady=4)

        BoutonSucces(self.barre_boutons, "💾  Enregistrer", self._enregistrer).pack(
            side="right", padx=PAD)
        BoutonDanger(self.barre_boutons, "Annuler", self.destroy).pack(side="right", padx=4)

    def _enregistrer(self):
        num = self.e_num.get().strip()
        bat = self.e_bat.get().strip()
        try:
            cap = int(self.e_cap.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "La capacité doit être un entier.", parent=self)
            return
        if not all([num, bat]):
            messagebox.showerror("Erreur", "Tous les champs * sont obligatoires.", parent=self)
            return
        type_s = TypeSalle(self.cb_type.get())
        if self.salle:
            self.salle.numero = num; self.salle.batiment = bat
            self.salle.capacite = cap; self.salle.type_salle = type_s
            self.salle.disponible = self.var_dispo.get()
            self.repo.modifier_salle(self.salle)
        else:
            self.repo.ajouter_salle(Salle(num, bat, cap, type_s, self.var_dispo.get()))
        self.destroy()


# ══════════════════════════════════════════════════════════════
#  Onglet Filières
# ══════════════════════════════════════════════════════════════

class OngletFilieres(OngletBase):

    COLONNES = ("ID", "Nom", "Niveau", "Effectif")

    def __init__(self, parent, repo):
        super().__init__(parent, repo)
        self._construire()

    def _construire(self):
        self._barre_outils(self, self._ajouter, self._modifier, self._supprimer)
        self.tableau = TableauTrie(self, self.COLONNES)
        self.tableau.pack(fill="both", expand=True, padx=PAD, pady=4)
        self.tableau.tree.column("ID", width=60)
        self.actualiser()

    def actualiser(self):
        q = getattr(self, "var_recherche", None)
        filtre = q.get().lower() if q else ""
        self.tableau.vider()
        for f in self.repo.liste_filieres():
            vals = (f.id, f.nom, f.niveau.value, f.effectif)
            if filtre and filtre not in " ".join(str(v).lower() for v in vals):
                continue
            self.tableau.ajouter_ligne(vals, iid=f.id)

    def _ajouter(self):
        dlg = DialogueFiliere(self, self.repo)
        self.wait_window(dlg)
        self.actualiser()

    def _modifier(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        fil = self.repo.get_filiere(vals[0])
        if fil:
            dlg = DialogueFiliere(self, self.repo, fil)
            self.wait_window(dlg)
            self.actualiser()

    def _supprimer(self):
        vals = self._item_selectionne(self.tableau)
        if not vals:
            return
        if messagebox.askyesno("Confirmer", f"Supprimer la filière {vals[1]} ?"):
            self.repo.supprimer_filiere(vals[0])
            self.actualiser()


class DialogueFiliere(FormulaireModal):
    def __init__(self, parent, repo, filiere: Filiere = None):
        super().__init__(parent, "Ajouter une filière" if not filiere
                         else "Modifier la filière", largeur=420, hauteur=340)
        self.repo = repo
        self.filiere = filiere

        self.e_nom = self._champ("Nom *", filiere.nom if filiere else "")
        self.cb_niv = self._combo("Niveau *",
                                  [n.value for n in NiveauFiliere],
                                  filiere.niveau.value if filiere else "L1")
        self.e_eff = self._champ("Effectif *", str(filiere.effectif) if filiere else "")

        BoutonSucces(self.barre_boutons, "💾  Enregistrer", self._enregistrer).pack(
            side="right", padx=PAD)
        BoutonDanger(self.barre_boutons, "Annuler", self.destroy).pack(side="right", padx=4)

    def _enregistrer(self):
        nom = self.e_nom.get().strip()
        try:
            eff = int(self.e_eff.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "L'effectif doit être un entier.", parent=self)
            return
        if not nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire.", parent=self)
            return
        niv = NiveauFiliere(self.cb_niv.get())
        if self.filiere:
            self.filiere.nom = nom; self.filiere.niveau = niv; self.filiere.effectif = eff
            self.repo.modifier_filiere(self.filiere)
        else:
            self.repo.ajouter_filiere(Filiere(nom, niv, eff))
        self.destroy()
