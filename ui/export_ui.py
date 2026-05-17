"""
ui/export_ui.py
Interface d'export PDF et CSV.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from utils.theme import *
from utils.widgets import BoutonPrincipal, BoutonSucces
from models.repository import Repository
from exports.export_service import ServiceExport


class PanneauExport(tk.Frame):

    def __init__(self, parent, repo: Repository):
        super().__init__(parent, bg=COULEUR_FOND)
        self.repo    = repo
        self.service = ServiceExport(repo)
        self._construire()

    def _construire(self):
        tk.Label(self, text="  Export & Partage", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_FOND).pack(
            anchor="w", padx=PAD * 2, pady=(18, 4))
        tk.Frame(self, bg=COULEUR_BORDURE, height=1).pack(
            fill="x", padx=PAD * 2, pady=(0, 12))

        corps = tk.Frame(self, bg=COULEUR_FOND)
        corps.pack(fill="both", expand=True, padx=PAD * 2)
        corps.columnconfigure(0, weight=1)
        corps.columnconfigure(1, weight=1)

        # ── Carte CSV ──────────────────────────────────────────
        carte_csv = self._carte(corps, "📊 Export CSV",
                                "Données brutes pour intégration dans d'autres outils.")
        carte_csv.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)
        self._corps_csv(carte_csv)

        # ── Carte PDF ──────────────────────────────────────────
        carte_pdf = self._carte(corps, "📄 Export PDF",
                                "Planning formaté imprimable par filière ou enseignant.")
        carte_pdf.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)
        self._corps_pdf(carte_pdf)

        # ── Aperçu sessions ────────────────────────────────────
        frame_ap = tk.LabelFrame(self, text=" Aperçu des sessions planifiées ",
                                  font=FONT_BOLD, bg=COULEUR_BLANC,
                                  fg=COULEUR_PRIMAIRE, relief="ridge", bd=1)
        frame_ap.pack(fill="both", expand=True,
                      padx=PAD * 2, pady=8)

        barre = tk.Frame(frame_ap, bg=COULEUR_BLANC, pady=6)
        barre.pack(fill="x")
        BoutonPrincipal(barre, "🔄 Actualiser l'aperçu",
                        self._actualiser_apercu,
                        couleur=COULEUR_SIDEBAR).pack(side="left", padx=PAD)
        self.lbl_nb = tk.Label(barre, text="", font=FONT_SMALL,
                                fg=COULEUR_TEXTE_CLAIR, bg=COULEUR_BLANC)
        self.lbl_nb.pack(side="left", padx=8)

        COLS = ("Jour", "Horaire", "Matière", "Code", "Type",
                "Enseignant", "Salle", "Filière", "Statut")
        self.tableau = tk.Frame(frame_ap, bg=COULEUR_BLANC)
        self.tableau.pack(fill="both", expand=True, padx=PAD, pady=4)

        style = ttk.Style()
        style.configure("Export.Treeview", rowheight=24, font=FONT_SMALL)
        style.configure("Export.Treeview.Heading", font=FONT_BOLD)

        scr = tk.Scrollbar(self.tableau, orient="vertical")
        scr_h = tk.Scrollbar(self.tableau, orient="horizontal")
        self.tree = ttk.Treeview(self.tableau, columns=COLS, show="headings",
                                  style="Export.Treeview",
                                  yscrollcommand=scr.set,
                                  xscrollcommand=scr_h.set)
        scr.config(command=self.tree.yview)
        scr_h.config(command=self.tree.xview)
        for col in COLS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=70)
        self.tree.column("Matière", width=160)
        self.tree.column("Enseignant", width=130)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scr.grid(row=0, column=1, sticky="ns")
        scr_h.grid(row=1, column=0, sticky="ew")
        self.tableau.rowconfigure(0, weight=1)
        self.tableau.columnconfigure(0, weight=1)

        self._actualiser_apercu()

    # ──────────────────────────────────────────────────────────

    def _carte(self, parent, titre, sous_titre):
        f = tk.LabelFrame(parent, text=f"  {titre}  ",
                          font=FONT_BOLD, bg=COULEUR_BLANC,
                          fg=COULEUR_PRIMAIRE, relief="ridge", bd=1,
                          padx=PAD, pady=PAD)
        tk.Label(f, text=sous_titre, font=FONT_SMALL,
                 fg=COULEUR_TEXTE_CLAIR, bg=COULEUR_BLANC,
                 wraplength=280).pack(anchor="w", pady=(2, 8))
        return f

    def _corps_csv(self, parent):
        tk.Label(parent, text="Filtrer par :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(anchor="w")
        self.var_filtre_csv = tk.StringVar(value="Tout")
        for opt in ("Tout", "Par filière", "Par enseignant"):
            tk.Radiobutton(parent, text=opt, variable=self.var_filtre_csv,
                           value=opt, font=FONT_NORMAL, bg=COULEUR_BLANC,
                           command=self._maj_selects_csv).pack(anchor="w")

        self.frame_csv_sel = tk.Frame(parent, bg=COULEUR_BLANC)
        self.frame_csv_sel.pack(fill="x", pady=4)
        self.cb_csv = ttk.Combobox(self.frame_csv_sel, state="readonly",
                                   font=FONT_NORMAL, width=26)
        self.cb_csv.pack(side="left", padx=4)

        BoutonSucces(parent, "⬇️  Exporter en CSV",
                     self._exporter_csv).pack(pady=10)

    def _corps_pdf(self, parent):
        tk.Label(parent, text="Filtrer par :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).pack(anchor="w")
        self.var_filtre_pdf = tk.StringVar(value="Tout")
        for opt in ("Tout", "Par filière", "Par enseignant"):
            tk.Radiobutton(parent, text=opt, variable=self.var_filtre_pdf,
                           value=opt, font=FONT_NORMAL, bg=COULEUR_BLANC,
                           command=self._maj_selects_pdf).pack(anchor="w")

        self.frame_pdf_sel = tk.Frame(parent, bg=COULEUR_BLANC)
        self.frame_pdf_sel.pack(fill="x", pady=4)
        self.cb_pdf = ttk.Combobox(self.frame_pdf_sel, state="readonly",
                                   font=FONT_NORMAL, width=26)
        self.cb_pdf.pack(side="left", padx=4)

        BoutonSucces(parent, "⬇️  Exporter en PDF",
                     self._exporter_pdf).pack(pady=10)

        tk.Label(parent,
                 text="ℹ️  Si reportlab n'est pas installé, un fichier .txt formaté sera généré.",
                 font=FONT_SMALL, fg=COULEUR_TEXTE_CLAIR, bg=COULEUR_BLANC,
                 wraplength=260, justify="left").pack(anchor="w", pady=2)

    # ── Sélecteurs dynamiques ─────────────────────────────────

    def _maj_selects_csv(self):
        self._maj_combo(self.cb_csv, self.var_filtre_csv.get())

    def _maj_selects_pdf(self):
        self._maj_combo(self.cb_pdf, self.var_filtre_pdf.get())

    def _maj_combo(self, cb, filtre):
        if filtre == "Par filière":
            cb["values"] = [str(f) for f in self.repo.liste_filieres()]
            self._ids_cb = [f.id for f in self.repo.liste_filieres()]
        elif filtre == "Par enseignant":
            cb["values"] = [str(e) for e in self.repo.liste_enseignants()]
            self._ids_cb = [e.id for e in self.repo.liste_enseignants()]
        else:
            cb["values"] = []
            self._ids_cb = []
        if cb["values"]:
            cb.set(cb["values"][0])

    # ── Export CSV ────────────────────────────────────────────

    def _exporter_csv(self):
        chemin = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Tous", "*.*")],
            title="Enregistrer le CSV"
        )
        if not chemin:
            return
        filiere_id, ens_id = self._lire_filtres(self.var_filtre_csv, self.cb_csv)
        try:
            f = self.service.exporter_csv(chemin, filiere_id, ens_id)
            messagebox.showinfo("Export réussi", f"Fichier CSV enregistré :\n{f}")
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    # ── Export PDF ────────────────────────────────────────────

    def _exporter_pdf(self):
        chemin = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Tous", "*.*")],
            title="Enregistrer le PDF"
        )
        if not chemin:
            return
        filiere_id, ens_id = self._lire_filtres(self.var_filtre_pdf, self.cb_pdf)
        try:
            f = self.service.exporter_pdf(chemin, filiere_id, ens_id)
            ext = os.path.splitext(f)[1].upper().lstrip(".")
            messagebox.showinfo("Export réussi",
                                f"Fichier {ext} enregistré :\n{f}")
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _lire_filtres(self, var_filtre, cb):
        filtre = var_filtre.get()
        if filtre == "Par filière":
            idx = cb.current()
            ids = [f.id for f in self.repo.liste_filieres()]
            return (ids[idx] if idx >= 0 and ids else None), None
        elif filtre == "Par enseignant":
            idx = cb.current()
            ids = [e.id for e in self.repo.liste_enseignants()]
            return None, (ids[idx] if idx >= 0 and ids else None)
        return None, None

    # ── Aperçu ────────────────────────────────────────────────

    def _actualiser_apercu(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sessions = self.repo.liste_sessions()
        self.lbl_nb.config(text=f"{len(sessions)} session(s) planifiée(s)")
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

        def cle_tri(s):
            c = self.repo.get_creneau(s.creneau_id)
            if not c:
                return (99, "")
            return (jours.index(c.jour) if c.jour in jours else 99,
                    c.heure_debut.strftime("%H:%M"))

        for i, s in enumerate(sorted(sessions, key=cle_tri)):
            c  = self.repo.get_creneau(s.creneau_id)
            m  = self.repo.get_matiere(s.matiere_id)
            e  = self.repo.get_enseignant(s.enseignant_id)
            sa = self.repo.get_salle(s.salle_id)
            fi = self.repo.get_filiere(m.filiere_id) if m else None
            vals = (
                c.jour if c else "",
                f"{c.heure_debut.strftime('%H:%M')}–{c.heure_fin.strftime('%H:%M')}" if c else "",
                m.intitule if m else "",
                m.code if m else "",
                m.type_seance.value if m else "",
                str(e) if e else "",
                sa.numero if sa else "",
                str(fi) if fi else "",
                s.statut.value
            )
            tag = "pair" if i % 2 == 0 else "impair"
            self.tree.insert("", "end", values=vals, tags=(tag,))

        self.tree.tag_configure("pair",   background="#f8f9fa")
        self.tree.tag_configure("impair", background=COULEUR_BLANC)

    def actualiser(self):
        self._actualiser_apercu()
