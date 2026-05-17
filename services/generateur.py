"""
services/generateur.py
Algorithme glouton de génération des emplois du temps (couche Métier).
"""

from typing import List, Tuple, Optional
from models.entities import Session, StatutSession
from models.repository import Repository
from services.contraintes import ServiceContraintes
import random


class ResultatGeneration:
    """Résultat après une génération."""
    def __init__(self):
        self.sessions_planifiees: List[Session] = []
        self.conflits: List[Tuple[str, str]] = []   # (matiere, message)
        self.nb_placements_reussis: int = 0
        self.nb_echecs: int = 0
        self.taux_completion: float = 0.0

    def __str__(self):
        return (
            f"Génération terminée : {self.nb_placements_reussis} sessions planifiées, "
            f"{self.nb_echecs} échec(s). Taux : {self.taux_completion:.0%}"
        )


class GenerateurEmploiDuTemps:


    def __init__(self, repo: Repository):
        self.repo = repo
        self.svc_contraintes = ServiceContraintes(repo)

    def generer(self, semaine: int = 1,
                callback_progression=None) -> ResultatGeneration:

        self.repo.vider_sessions()

        matieres     = self.repo.liste_matieres()
        salles       = self.repo.liste_salles()
        creneaux     = [c for c in self.repo.liste_creneaux() if c.semaine == semaine]
        enseignants  = self.repo.liste_enseignants()

        resultat = ResultatGeneration()
        sessions_courantes: List[Session] = []

        total = len(matieres)
        if total == 0:
            return resultat

        for idx, matiere in enumerate(matieres):

            if callback_progression:
                pct = int((idx / total) * 100)
                callback_progression(pct)

            # Trouver l'enseignant référent de cette matière
            enseignant = self._trouver_enseignant(matiere.id, enseignants)
            if not enseignant:
                resultat.conflits.append((
                    str(matiere),
                    f"Aucun enseignant associé à la matière {matiere.code}"
                ))
                resultat.nb_echecs += 1
                continue

            # Salles compatibles (capacité suffisante)
            filiere = self.repo.get_filiere(matiere.filiere_id)
            effectif = filiere.effectif if filiere else 0
            salles_ok = [s for s in salles if s.capacite >= effectif]

            if not salles_ok:
                resultat.conflits.append((
                    str(matiere),
                    f"Aucune salle avec capacité ≥ {effectif} pour {matiere.code}"
                ))
                resultat.nb_echecs += 1
                continue


            meilleure_session: Optional[Session] = None
            meilleur_score: int = -1

            candidats = [(s, c) for s in salles_ok for c in creneaux]
            random.shuffle(candidats)   # évite les biais de l'ordre

            for salle, creneau in candidats:
                candidate = Session(
                    enseignant_id=enseignant.id,
                    matiere_id=matiere.id,
                    salle_id=salle.id,
                    creneau_id=creneau.id,
                    statut=StatutSession.PLANIFIE,
                )
                valide, _ = self.svc_contraintes.valider_session(
                    candidate, sessions_courantes
                )
                if valide:
                    score = self.svc_contraintes.score_contraintes_faibles(
                        candidate, sessions_courantes
                    )
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleure_session = candidate

            if meilleure_session:
                sessions_courantes.append(meilleure_session)
                self.repo.ajouter_session(meilleure_session)
                resultat.sessions_planifiees.append(meilleure_session)
                resultat.nb_placements_reussis += 1
            else:
                resultat.conflits.append((
                    str(matiere),
                    f"Impossible de placer {matiere.code} : "
                    f"tous les créneaux/salles sont en conflit"
                ))
                resultat.nb_echecs += 1

        if callback_progression:
            callback_progression(100)

        total_tente = resultat.nb_placements_reussis + resultat.nb_echecs
        resultat.taux_completion = (
            resultat.nb_placements_reussis / total_tente if total_tente else 0.0
        )
        return resultat

    # ──────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────

    def _trouver_enseignant(self, matiere_id: str, enseignants):
        """Retourne le premier enseignant qui enseigne cette matière."""
        for e in enseignants:
            if matiere_id in e.matieres_ids:
                return e
        return None
