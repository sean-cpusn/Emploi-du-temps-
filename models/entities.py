"""
models/entities.py
Couche Modèle – Entités métier du système de gestion des emplois du temps.
"""

from dataclasses import dataclass, field
from datetime import time
from typing import List, Optional
from enum import Enum
import uuid


# ──────────────────────────────────────────────────────────────
#  Énumérations
# ──────────────────────────────────────────────────────────────

class TypeSeance(Enum):
    CM = "CM"       # Cours Magistral
    TD = "TD"       # Travaux Dirigés
    TP = "TP"       # Travaux Pratiques


class TypeSalle(Enum):
    COURS = "cours"
    INFO  = "info"
    LABO  = "labo"


class TypeContrainte(Enum):
    FORTE  = "forte"
    FAIBLE = "faible"


class StatutSession(Enum):
    PLANIFIE = "planifie"
    CONFLIT  = "conflit"
    ANNULE   = "annule"


class NiveauFiliere(Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    M1 = "M1"
    M2 = "M2"


JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]


# ──────────────────────────────────────────────────────────────
#  Entités
# ──────────────────────────────────────────────────────────────

@dataclass
class Filiere:
    """Entité FILIERE """
    nom: str
    niveau: NiveauFiliere
    effectif: int
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return f"{self.nom} ({self.niveau.value})"


@dataclass
class Enseignant:
    """Entité ENSEIGNANT"""
    nom: str
    prenom: str
    email: str
    vol_max_heures: int = 20          # Volume horaire maximum par semaine
    matieres_ids: List[str] = field(default_factory=list)
    indisponibilites: List[str] = field(default_factory=list)  # ids de créneaux bloqués
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


@dataclass
class Matiere:
    """Entité MATIERE"""
    code: str
    intitule: str
    filiere_id: str
    credits: float
    heures_req: int
    type_seance: TypeSeance
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return f"{self.code} – {self.intitule}"


@dataclass
class Salle:
    """Entité SALLE """
    numero: str
    batiment: str
    capacite: int
    type_salle: TypeSalle = TypeSalle.COURS
    disponible: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return f"Salle {self.numero} – {self.batiment} (cap. {self.capacite})"


@dataclass
class Creneau:
    """Entité CRENEAU """
    jour: str
    heure_debut: time
    heure_fin: time
    semaine: int = 1
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return (f"{self.jour} {self.heure_debut.strftime('%H:%M')}"
                f"–{self.heure_fin.strftime('%H:%M')} (S{self.semaine})")

    def chevauche(self, autre: "Creneau") -> bool:
        """Vérifie si deux créneaux se chevauchent (même jour, mêmes semaine)."""
        if self.jour != autre.jour or self.semaine != autre.semaine:
            return False
        return self.heure_debut < autre.heure_fin and autre.heure_debut < self.heure_fin


@dataclass
class Contrainte:
    """Entité CONTRAINTE """
    type_contrainte: TypeContrainte
    description: str
    priorite: int = 1
    enseignant_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return f"[{self.type_contrainte.value.upper()}] {self.description}"


@dataclass
class Session:
    """
    Entité SESSION.
    Agrège les 4 ressources : enseignant, matière, salle, créneau.
    """
    enseignant_id: str
    matiere_id: str
    salle_id: str
    creneau_id: str
    statut: StatutSession = StatutSession.PLANIFIE
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __str__(self):
        return f"Session({self.id}) – statut={self.statut.value}"
