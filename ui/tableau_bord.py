"""
ui/tableau_bord.py
Écran principal – Tableau de Bord (§7.1 du cahier des charges).
Affiche les indicateurs de statut et le bouton de génération.
"""

import tkinter as tk
from tkinter import messagebox
import threading

from utils.theme import *
from utils.widgets import (BoutonPrincipal, BoutonSucces, CarteStat,
                            BarreProgression, LabelTitre)
from models.repository import Repository
from services.generateur import GenerateurEmploiDuTemps
from services.contraintes import ServiceContraintes


class TableauBord(tk.Frame):

    def __init__(self, parent, repo: Repository, on_generation_terminee=None):
        super().__init__(parent, bg=COULEUR_FOND)
        self.repo = repo
        self.on_generation_terminee = on_generation_terminee
        self.generateur = GenerateurEmploiDuTemps(repo)
        self._construire()

    def _construire(self):
        # ── Titre ────────────────────────────────────────────
        entete = tk.Frame(self, bg=COULEUR_FOND)
        entete.pack(fill="x", padx=PAD * 2, pady=(20, 5))
        tk.Label(entete, text="🏛  Tableau de Bord", font=FONT_TITRE,
                 fg=COULEUR_PRIMAIRE, bg=COULEUR_FOND).pack(side="left")
        tk.Label(entete, text="SGET – Système de génération des emplois du temps",
                 font=FONT_SMALL, fg=COULEUR_TEXTE_CLAIR, bg=COULEUR_FOND).pack(
            side="left", padx=12, pady=6)

        tk.Frame(self, bg=COULEUR_BORDURE, height=1).pack(fill="x", padx=PAD * 2)

        # ── Cartes de statistiques ───────────────────────────
        frame_stats = tk.Frame(self, bg=COULEUR_FOND)
        frame_stats.pack(fill="x", padx=PAD * 2, pady=18)

        self.carte_enseignants = CarteStat(frame_stats, "👨‍🏫 Enseignants",
                                           len(self.repo.liste_enseignants()),
                                           COULEUR_SECONDAIRE)
        self.carte_matieres    = CarteStat(frame_stats, "📚 Matières",
                                           len(self.repo.liste_matieres()),
                                           "#8e44ad")
        self.carte_salles      = CarteStat(frame_stats, "🏫 Salles",
                                           len(self.repo.liste_salles()),
                                           COULEUR_WARNING)
        self.carte_sessions    = CarteStat(frame_stats, "📅 Sessions planifiées",
                                           len(self.repo.liste_sessions()),
                                           COULEUR_ACCENT)
        self.carte_conflits    = CarteStat(frame_stats, "⚠️  Conflits",
                                           0, COULEUR_DANGER)

        for i, c in enumerate([self.carte_enseignants, self.carte_matieres,
                                self.carte_salles, self.carte_sessions,
                                self.carte_conflits]):
            c.grid(row=0, column=i, padx=8, pady=4, ipadx=12, ipady=4,
                   in_=frame_stats, sticky="nsew")
            frame_stats.columnconfigure(i, weight=1)

        # ── Panneau de génération ────────────────────────────
        frame_gen = tk.Frame(self, bg=COULEUR_BLANC, relief="ridge", bd=1)
        frame_gen.pack(fill="x", padx=PAD * 2, pady=8, ipady=10)

        tk.Label(frame_gen, text="⚙️  Génération Automatique",
                 font=FONT_SOUS_TITRE, fg=COULEUR_PRIMAIRE,
                 bg=COULEUR_BLANC).pack(pady=(12, 4))
        tk.Label(frame_gen,
                 text="Sélectionnez la semaine et lancez l'algorithme d'optimisation.",
                 font=FONT_SMALL, fg=COULEUR_TEXTE_CLAIR,
                 bg=COULEUR_BLANC).pack()

        frame_ctrl = tk.Frame(frame_gen, bg=COULEUR_BLANC)
        frame_ctrl.pack(pady=10)

        tk.Label(frame_ctrl, text="Semaine :", font=FONT_BOLD,
                 bg=COULEUR_BLANC).grid(row=0, column=0, padx=6)
        self.spin_semaine = tk.Spinbox(frame_ctrl, from_=1, to=52, width=5,
                                       font=FONT_NORMAL, relief="solid", bd=1)
        self.spin_semaine.grid(row=0, column=1, padx=6)

        BoutonSucces(frame_ctrl, "▶  Générer l'emploi du temps",
                     self._lancer_generation).grid(row=0, column=2, padx=14)
        BoutonPrincipal(frame_ctrl, "🔄 Actualiser stats",
                        self.actualiser, couleur=COULEUR_SIDEBAR).grid(row=0, column=3, padx=4)

        self.barre = BarreProgression(frame_gen)
        self.barre.pack(fill="x", padx=PAD * 2, pady=4)

        # ── Journal de génération ────────────────────────────
        frame_journal = tk.Frame(self, bg=COULEUR_BLANC, relief="ridge", bd=1)
        frame_journal.pack(fill="both", expand=True, padx=PAD * 2, pady=8)

        tk.Label(frame_journal, text="📋 Journal des opérations",
                 font=FONT_BOLD, bg=COULEUR_BLANC,
                 fg=COULEUR_PRIMAIRE).pack(anchor="w", padx=PAD, pady=(8, 2))

        self.txt_journal = tk.Text(frame_journal, font=FONT_MONO, height=12,
                                    bg="#1e272e", fg="#dfe6e9",
                                    relief="flat", padx=8, pady=6,
                                    state="disabled")
        scr = tk.Scrollbar(frame_journal, command=self.txt_journal.yview)
        self.txt_journal.config(yscrollcommand=scr.set)
        self.txt_journal.pack(side="left", fill="both", expand=True, padx=(PAD, 0))
        scr.pack(side="right", fill="y")

        self._log("✅ Application démarrée. Données pré-chargées en mémoire.")
        self._log(f"   • {len(self.repo.liste_enseignants())} enseignants")
        self._log(f"   • {len(self.repo.liste_matieres())} matières")
        self._log(f"   • {len(self.repo.liste_salles())} salles")
        self._log(f"   • {len(self.repo.liste_creneaux())} créneaux disponibles")
        self._log("─" * 55)

    # ──────────────────────────────────────────────────────────

    def _lancer_generation(self):
        try:
            semaine = int(self.spin_semaine.get())
        except ValueError:
            messagebox.showerror("Erreur", "Numéro de semaine invalide.")
            return

        self._log(f"\n🚀 Lancement de la génération – Semaine {semaine}...")
        self.barre.mettre_a_jour(0, "Initialisation...")

        def progression(pct):
            self.barre.mettre_a_jour(pct, f"Traitement... {pct}%")

        def tache():
            resultat = self.generateur.generer(semaine, progression)
            self.after(0, lambda: self._afficher_resultat(resultat))

        threading.Thread(target=tache, daemon=True).start()

    def _afficher_resultat(self, resultat):
        self._log(f"✅ {resultat.nb_placements_reussis} sessions planifiées avec succès.")
        if resultat.nb_echecs:
            self._log(f"⚠️  {resultat.nb_echecs} matière(s) non placée(s) :")
            for mat, msg in resultat.conflits:
                self._log(f"   → {mat} : {msg}")
        self._log(f"   Taux de complétion : {resultat.taux_completion:.0%}")
        self.barre.mettre_a_jour(100, f"Terminé – {resultat.taux_completion:.0%} de complétion")

        # Conflits restants
        svc = ServiceContraintes(self.repo)
        conflits = svc.detecter_tous_conflits()
        self.carte_conflits.mettre_a_jour(len(conflits))

        self.actualiser()
        if self.on_generation_terminee:
            self.on_generation_terminee()

    def actualiser(self):
        self.carte_enseignants.mettre_a_jour(len(self.repo.liste_enseignants()))
        self.carte_matieres.mettre_a_jour(len(self.repo.liste_matieres()))
        self.carte_salles.mettre_a_jour(len(self.repo.liste_salles()))
        self.carte_sessions.mettre_a_jour(len(self.repo.liste_sessions()))

    def _log(self, message: str):
        self.txt_journal.config(state="normal")
        self.txt_journal.insert("end", message + "\n")
        self.txt_journal.see("end")
        self.txt_journal.config(state="disabled")
