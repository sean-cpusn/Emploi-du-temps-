"""
models/repository.py
Couche Données.
"""

from typing import Dict, List, Optional
from models.entities import (
    Enseignant, Matiere, Filiere, Salle, Creneau, Session, Contrainte,
    TypeSeance, TypeSalle, TypeContrainte, StatutSession, NiveauFiliere
)
from datetime import time


class Repository:
    """Dépôt en mémoire."""

    def __init__(self):
        self._enseignants: Dict[str, Enseignant] = {}
        self._matieres:    Dict[str, Matiere]    = {}
        self._filieres:    Dict[str, Filiere]    = {}
        self._salles:      Dict[str, Salle]      = {}
        self._creneaux:    Dict[str, Creneau]    = {}
        self._sessions:    Dict[str, Session]    = {}
        self._contraintes: Dict[str, Contrainte] = {}
        self._charger_donnees_exemple()

    # ──────────────────────────────────────────────────────────
    #  Données d'exemple (remplace les fixtures SQL)
    # ──────────────────────────────────────────────────────────

    def _charger_donnees_exemple(self):
        """Pré-charge des données réalistes pour la démonstration."""

        # Filières
        f1 = Filiere("Génie Logiciel", NiveauFiliere.L1, 24)
        f2 = Filiere("Réseaux & Télécoms", NiveauFiliere.L2, 32)
        f3 = Filiere("Batiment", NiveauFiliere.M1, 20)
        for f in [f1, f2, f3]:
            self.ajouter_filiere(f)

        # Salles
        salles = [
            Salle("A10", "Bâtiment A", 50, TypeSalle.COURS),
            Salle("A12", "Bâtiment A", 40, TypeSalle.COURS),
            Salle("B21", "Bâtiment B", 30, TypeSalle.INFO),
            Salle("B23", "Bâtiment B", 25, TypeSalle.INFO),
            Salle("C14", "Bâtiment C", 20, TypeSalle.LABO),
        ]
        for s in salles:
            self.ajouter_salle(s)

        # Enseignants
        e1 = Enseignant("NOAH", "", "noah@gmail.com", 18)
        e2 = Enseignant("AZEGUE", "", "AD@gmail.com", 16)
        e3 = Enseignant("DOMNGANG", "", "Dom@gmail.com", 20)
        e4 = Enseignant("Tankeu", "", "Htankeu@gmail.com", 14)
        for e in [e1, e2, e3, e4]:
            self.ajouter_enseignant(e)

        # Matières
        ids_f = list(self._filieres.keys())
        ids_e = list(self._enseignants.keys())

        matieres = [
            Matiere("INF301", "Analyse mathématiques II",       ids_f[0], 4.0, 45, TypeSeance.CM),
            Matiere("INF302", "Génie Logiciel",            ids_f[0], 3.0, 30, TypeSeance.TD),
            Matiere("INF303", "Introduction Aux Bases de Données",          ids_f[0], 4.0, 45, TypeSeance.TP),
            Matiere("RES201", "Programmation évènementielle",        ids_f[1], 4.0, 45, TypeSeance.CM),
            Matiere("RES202", "Programmation Structurée",   ids_f[1], 3.0, 30, TypeSeance.TP),
            Matiere("SYS401", "Economie",   ids_f[2], 5.0, 60, TypeSeance.CM),
            Matiere("SYS402", "Système d'information II",     ids_f[2], 4.0, 45, TypeSeance.TD),
        ]
        for m in matieres:
            self.ajouter_matiere(m)

        # Association enseignants <-> matières
        ids_m = list(self._matieres.keys())
        self._enseignants[ids_e[0]].matieres_ids = [ids_m[0], ids_m[1]]
        self._enseignants[ids_e[1]].matieres_ids = [ids_m[2], ids_m[3]]
        self._enseignants[ids_e[2]].matieres_ids = [ids_m[4], ids_m[5]]
        self._enseignants[ids_e[3]].matieres_ids = [ids_m[6]]

        # Créneaux horaires standard (semaine 1)
        horaires = [
            ("07:30", "09:30"), ("09:45", "11:45"),
            ("12:00", "14:00"), ("14:15", "16:15"), ("16:30", "18:30"),
        ]
        for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
            for h_debut, h_fin in horaires:
                hd = time(*map(int, h_debut.split(":")))
                hf = time(*map(int, h_fin.split(":")))
                self.ajouter_creneau(Creneau(jour, hd, hf, semaine=1))

        # Contraintes exemples
        self.ajouter_contrainte(Contrainte(
            TypeContrainte.FORTE,
            "Un enseignant ne peut assurer deux cours simultanément", 1
        ))
        self.ajouter_contrainte(Contrainte(
            TypeContrainte.FORTE,
            "Une salle ne peut accueillir qu'un seul cours à la fois", 1
        ))
        self.ajouter_contrainte(Contrainte(
            TypeContrainte.FAIBLE,
            "Regrouper les cours d'une même filière sur des journées complètes", 2
        ))

    # ──────────────────────────────────────────────────────────
    #  ENSEIGNANTS
    # ──────────────────────────────────────────────────────────

    def ajouter_enseignant(self, e: Enseignant) -> Enseignant:
        self._enseignants[e.id] = e
        return e

    def modifier_enseignant(self, e: Enseignant) -> Enseignant:
        if e.id not in self._enseignants:
            raise KeyError(f"Enseignant {e.id} introuvable.")
        self._enseignants[e.id] = e
        return e

    def supprimer_enseignant(self, eid: str):
        if eid not in self._enseignants:
            raise KeyError(f"Enseignant {eid} introuvable.")
        del self._enseignants[eid]

    def get_enseignant(self, eid: str) -> Optional[Enseignant]:
        return self._enseignants.get(eid)

    def liste_enseignants(self) -> List[Enseignant]:
        return list(self._enseignants.values())

    # ──────────────────────────────────────────────────────────
    #  MATIÈRES
    # ──────────────────────────────────────────────────────────

    def ajouter_matiere(self, m: Matiere) -> Matiere:
        self._matieres[m.id] = m
        return m

    def modifier_matiere(self, m: Matiere) -> Matiere:
        if m.id not in self._matieres:
            raise KeyError(f"Matière {m.id} introuvable.")
        self._matieres[m.id] = m
        return m

    def supprimer_matiere(self, mid: str):
        del self._matieres[mid]

    def get_matiere(self, mid: str) -> Optional[Matiere]:
        return self._matieres.get(mid)

    def liste_matieres(self, filiere_id: Optional[str] = None) -> List[Matiere]:
        matieres = list(self._matieres.values())
        if filiere_id:
            matieres = [m for m in matieres if m.filiere_id == filiere_id]
        return matieres

    # ──────────────────────────────────────────────────────────
    #  FILIÈRES
    # ──────────────────────────────────────────────────────────

    def ajouter_filiere(self, f: Filiere) -> Filiere:
        self._filieres[f.id] = f
        return f

    def modifier_filiere(self, f: Filiere) -> Filiere:
        self._filieres[f.id] = f
        return f

    def supprimer_filiere(self, fid: str):
        del self._filieres[fid]

    def get_filiere(self, fid: str) -> Optional[Filiere]:
        return self._filieres.get(fid)

    def liste_filieres(self) -> List[Filiere]:
        return list(self._filieres.values())

    # ──────────────────────────────────────────────────────────
    #  SALLES
    # ──────────────────────────────────────────────────────────

    def ajouter_salle(self, s: Salle) -> Salle:
        self._salles[s.id] = s
        return s

    def modifier_salle(self, s: Salle) -> Salle:
        self._salles[s.id] = s
        return s

    def supprimer_salle(self, sid: str):
        del self._salles[sid]

    def get_salle(self, sid: str) -> Optional[Salle]:
        return self._salles.get(sid)

    def liste_salles(self) -> List[Salle]:
        return list(self._salles.values())

    # ──────────────────────────────────────────────────────────
    #  CRÉNEAUX
    # ──────────────────────────────────────────────────────────

    def ajouter_creneau(self, c: Creneau) -> Creneau:
        self._creneaux[c.id] = c
        return c

    def get_creneau(self, cid: str) -> Optional[Creneau]:
        return self._creneaux.get(cid)

    def liste_creneaux(self, semaine: Optional[int] = None) -> List[Creneau]:
        creneaux = list(self._creneaux.values())
        if semaine is not None:
            creneaux = [c for c in creneaux if c.semaine == semaine]
        return creneaux

    # ──────────────────────────────────────────────────────────
    #  SESSIONS
    # ──────────────────────────────────────────────────────────

    def ajouter_session(self, s: Session) -> Session:
        self._sessions[s.id] = s
        return s

    def modifier_session(self, s: Session) -> Session:
        self._sessions[s.id] = s
        return s

    def supprimer_session(self, sid: str):
        if sid in self._sessions:
            del self._sessions[sid]

    def get_session(self, sid: str) -> Optional[Session]:
        return self._sessions.get(sid)

    def liste_sessions(self) -> List[Session]:
        return list(self._sessions.values())

    def vider_sessions(self):
        self._sessions.clear()

    # ──────────────────────────────────────────────────────────
    #  CONTRAINTES
    # ──────────────────────────────────────────────────────────

    def ajouter_contrainte(self, c: Contrainte) -> Contrainte:
        self._contraintes[c.id] = c
        return c

    def supprimer_contrainte(self, cid: str):
        if cid in self._contraintes:
            del self._contraintes[cid]

    def liste_contraintes(self) -> List[Contrainte]:
        return list(self._contraintes.values())
