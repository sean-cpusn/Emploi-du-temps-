"""
services/contraintes.py
Service de validation des contraintes fortes et faibles.
"""

from typing import List, Tuple
from models.entities import Session, StatutSession
from models.repository import Repository


class ServiceContraintes:
    """
    Vérifie les contraintes fortes (obligatoires) et faibles (préférences).
    Une contrainte forte bloquée → la session est marquée CONFLIT.
    """

    def __init__(self, repo: Repository):
        self.repo = repo

    # ──────────────────────────────────────────────────────────
    #  API publique
    # ──────────────────────────────────────────────────────────

    def valider_session(self, session: Session,
                        sessions_existantes: List[Session]
                        ) -> Tuple[bool, List[str]]:
        """
        Valide une session candidate contre les contraintes fortes.
        Retourne (valide: bool, liste_erreurs: List[str]).
        """
        erreurs = []
        erreurs += self._conflit_enseignant(session, sessions_existantes)
        erreurs += self._conflit_salle(session, sessions_existantes)
        erreurs += self._conflit_filiere(session, sessions_existantes)
        erreurs += self._capacite_salle(session)
        erreurs += self._indisponibilite_enseignant(session)
        erreurs += self._volume_horaire_enseignant(session, sessions_existantes)
        return len(erreurs) == 0, erreurs

    def score_contraintes_faibles(self, session: Session,
                                   sessions_existantes: List[Session]) -> int:
        """
        Calcule un score de qualité (plus il est élevé, mieux c'est).
        Utilisé par l'algorithme glouton pour choisir le meilleur placement.
        """
        score = 0
        score += self._score_regroupement_filiere(session, sessions_existantes)
        score += self._score_equilibrage_charge(session, sessions_existantes)
        return score

    def detecter_tous_conflits(self) -> List[Tuple[Session, List[str]]]:
        """Parcourt toutes les sessions planifiées et retourne les conflits."""
        sessions = self.repo.liste_sessions()
        conflits = []
        for i, s in enumerate(sessions):
            autres = [x for j, x in enumerate(sessions) if j != i]
            ok, erreurs = self.valider_session(s, autres)
            if not ok:
                conflits.append((s, erreurs))
        return conflits

    # ──────────────────────────────────────────────────────────
    #  Contraintes fortes
    # ──────────────────────────────────────────────────────────

    def _conflit_enseignant(self, session: Session,
                            existantes: List[Session]) -> List[str]:
        """Un enseignant ne peut pas assurer deux cours simultanément."""
        creneau = self.repo.get_creneau(session.creneau_id)
        if not creneau:
            return []
        for s in existantes:
            if s.enseignant_id != session.enseignant_id:
                continue
            c2 = self.repo.get_creneau(s.creneau_id)
            if c2 and creneau.chevauche(c2):
                ens = self.repo.get_enseignant(session.enseignant_id)
                return [f"Conflit enseignant : {ens} déjà occupé sur {creneau}"]
        return []

    def _conflit_salle(self, session: Session,
                       existantes: List[Session]) -> List[str]:
        """Une salle ne peut accueillir qu'un seul cours à la fois."""
        creneau = self.repo.get_creneau(session.creneau_id)
        if not creneau:
            return []
        for s in existantes:
            if s.salle_id != session.salle_id:
                continue
            c2 = self.repo.get_creneau(s.creneau_id)
            if c2 and creneau.chevauche(c2):
                salle = self.repo.get_salle(session.salle_id)
                return [f"Conflit salle : {salle} déjà réservée sur {creneau}"]
        return []

    def _conflit_filiere(self, session: Session,
                          existantes: List[Session]) -> List[str]:
        """Un groupe d'étudiants (filière) ne peut pas avoir deux cours simultanément."""
        matiere = self.repo.get_matiere(session.matiere_id)
        if not matiere:
            return []
        creneau = self.repo.get_creneau(session.creneau_id)
        if not creneau:
            return []
        for s in existantes:
            m2 = self.repo.get_matiere(s.matiere_id)
            if not m2 or m2.filiere_id != matiere.filiere_id:
                continue
            c2 = self.repo.get_creneau(s.creneau_id)
            if c2 and creneau.chevauche(c2):
                filiere = self.repo.get_filiere(matiere.filiere_id)
                return [f"Conflit filière : {filiere} a déjà un cours sur {creneau}"]
        return []

    def _capacite_salle(self, session: Session) -> List[str]:
        """La capacité de la salle >= effectifs de la filière."""
        salle = self.repo.get_salle(session.salle_id)
        matiere = self.repo.get_matiere(session.matiere_id)
        if not salle or not matiere:
            return []
        filiere = self.repo.get_filiere(matiere.filiere_id)
        if filiere and salle.capacite < filiere.effectif:
            return [
                f"Capacité insuffisante : salle {salle.numero} ({salle.capacite} places)"
                f" < effectif {filiere} ({filiere.effectif} étudiants)"
            ]
        return []

    def _indisponibilite_enseignant(self, session: Session) -> List[str]:
        """Respect des indisponibilités déclarées par l'enseignant."""
        ens = self.repo.get_enseignant(session.enseignant_id)
        if not ens:
            return []
        if session.creneau_id in ens.indisponibilites:
            creneau = self.repo.get_creneau(session.creneau_id)
            return [f"Indisponibilité : {ens} n'est pas disponible sur {creneau}"]
        return []

    def _volume_horaire_enseignant(self, session: Session,
                                    existantes: List[Session]) -> List[str]:
        """Vérification du volume horaire maximal hebdomadaire de l'enseignant."""
        ens = self.repo.get_enseignant(session.enseignant_id)
        if not ens:
            return []
        creneau_new = self.repo.get_creneau(session.creneau_id)
        if not creneau_new:
            return []

        heures_planifiees = 0
        for s in existantes:
            if s.enseignant_id != session.enseignant_id:
                continue
            c = self.repo.get_creneau(s.creneau_id)
            if c and c.semaine == creneau_new.semaine:
                duree = (c.heure_fin.hour * 60 + c.heure_fin.minute
                         - c.heure_debut.hour * 60 - c.heure_debut.minute) / 60
                heures_planifiees += duree

        duree_nouvelle = (
            creneau_new.heure_fin.hour * 60 + creneau_new.heure_fin.minute
            - creneau_new.heure_debut.hour * 60 - creneau_new.heure_debut.minute
        ) / 60

        if heures_planifiees + duree_nouvelle > ens.vol_max_heures:
            return [
                f"Volume horaire dépassé : {ens} aurait "
                f"{heures_planifiees + duree_nouvelle:.1f}h > max {ens.vol_max_heures}h"
            ]
        return []

    # ──────────────────────────────────────────────────────────
    #  Contraintes faibles (score de qualité)
    # ──────────────────────────────────────────────────────────

    def _score_regroupement_filiere(self, session: Session,
                                     existantes: List[Session]) -> int:
        """
        +2 points si d'autres cours de la même filière sont déjà
        planifiés sur le même jour (favorise les journées continues).
        """
        matiere = self.repo.get_matiere(session.matiere_id)
        creneau = self.repo.get_creneau(session.creneau_id)
        if not matiere or not creneau:
            return 0
        for s in existantes:
            m2 = self.repo.get_matiere(s.matiere_id)
            c2 = self.repo.get_creneau(s.creneau_id)
            if m2 and c2 and m2.filiere_id == matiere.filiere_id and c2.jour == creneau.jour:
                return 2
        return 0

    def _score_equilibrage_charge(self, session: Session,
                                   existantes: List[Session]) -> int:
        """
        +1 point si l'enseignant a encore de la marge horaire
        (favorise l'équilibrage de la charge hebdomadaire).
        """
        ens = self.repo.get_enseignant(session.enseignant_id)
        creneau = self.repo.get_creneau(session.creneau_id)
        if not ens or not creneau:
            return 0
        heures = sum(
            (self.repo.get_creneau(s.creneau_id).heure_fin.hour -
             self.repo.get_creneau(s.creneau_id).heure_debut.hour)
            for s in existantes
            if s.enseignant_id == ens.id
            and self.repo.get_creneau(s.creneau_id)
            and self.repo.get_creneau(s.creneau_id).semaine == creneau.semaine
        )
        marge = ens.vol_max_heures - heures
        return 1 if marge > 4 else 0
