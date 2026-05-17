"""
exports/export_service.py
Service d'export multi-format (PDF, CSV) — §3.5 du cahier des charges.
"""

import csv
import os
from datetime import datetime
from typing import List, Optional
from models.entities import Session
from models.repository import Repository


class ServiceExport:
    """Génère les  PDF et CSV"""

    def __init__(self, repo: Repository):
        self.repo = repo

    # ──────────────────────────────────────────────────────────
    #  CSV
    # ──────────────────────────────────────────────────────────

    def exporter_csv(self, chemin: str,
                     filiere_id: Optional[str] = None,
                     enseignant_id: Optional[str] = None) -> str:
        """
        Exporte les sessions planifiées en CSV.
        Filtrage optionnel par filière ou par enseignant.
        """
        sessions = self._filtrer_sessions(filiere_id, enseignant_id)

        entetes = [
            "Jour", "Heure Début", "Heure Fin", "Semaine",
            "Matière", "Code", "Type",
            "Enseignant",
            "Salle", "Bâtiment", "Capacité",
            "Filière", "Niveau", "Effectif",
            "Statut"
        ]

        with open(chemin, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(entetes)
            for s in sessions:
                row = self._session_vers_ligne(s)
                writer.writerow(row)

        return chemin

    # ──────────────────────────────────────────────────────────
    #  PDF
    # ──────────────────────────────────────────────────────────

    def exporter_pdf(self, chemin: str,
                     filiere_id: Optional[str] = None,
                     enseignant_id: Optional[str] = None) -> str:
        """
        Tente un export PDF via reportlab.

        """
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                            Paragraph, Spacer)
            from reportlab.lib.styles import getSampleStyleSheet
            return self._pdf_reportlab(chemin, filiere_id, enseignant_id)
        except ImportError:
            return self._pdf_texte(chemin, filiere_id, enseignant_id)

    def _pdf_reportlab(self, chemin: str,
                       filiere_id: Optional[str],
                       enseignant_id: Optional[str]) -> str:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer)
        from reportlab.lib.styles import getSampleStyleSheet

        sessions = self._filtrer_sessions(filiere_id, enseignant_id)
        styles   = getSampleStyleSheet()
        doc      = SimpleDocTemplate(chemin, pagesize=landscape(A4))
        elements = []

        titre = "Emploi du Temps"
        if filiere_id:
            f = self.repo.get_filiere(filiere_id)
            titre += f" | {f}" if f else ""
        if enseignant_id:
            e = self.repo.get_enseignant(enseignant_id)
            titre += f" | {e}" if e else ""

        elements.append(Paragraph(titre, styles["Title"]))
        elements.append(Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 0.5 * cm))

        entetes = ["Jour", "Horaire", "Matière", "Enseignant", "Salle", "Filière"]
        data = [entetes]
        for s in sessions:
            c = self.repo.get_creneau(s.creneau_id)
            m = self.repo.get_matiere(s.matiere_id)
            e = self.repo.get_enseignant(s.enseignant_id)
            sa = self.repo.get_salle(s.salle_id)
            fi = self.repo.get_filiere(m.filiere_id) if m else None
            data.append([
                c.jour if c else "",
                f"{c.heure_debut.strftime('%H:%M')}–{c.heure_fin.strftime('%H:%M')}" if c else "",
                str(m) if m else "",
                str(e) if e else "",
                sa.numero if sa else "",
                str(fi) if fi else "",
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        doc.build(elements)
        return chemin

    def _pdf_texte(self, chemin: str,
                   filiere_id: Optional[str],
                   enseignant_id: Optional[str]) -> str:

        sessions = self._filtrer_sessions(filiere_id, enseignant_id)
        lignes   = [
            "=" * 80,
            "EMPLOI DU TEMPS ",
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            "=" * 80, ""
        ]

        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        for jour in jours:
            sessions_jour = [
                s for s in sessions
                if (c := self.repo.get_creneau(s.creneau_id)) and c.jour == jour
            ]
            if not sessions_jour:
                continue
            lignes.append(f"\n── {jour.upper()} ──")
            sessions_jour.sort(key=lambda s: self.repo.get_creneau(s.creneau_id).heure_debut)
            for s in sessions_jour:
                c  = self.repo.get_creneau(s.creneau_id)
                m  = self.repo.get_matiere(s.matiere_id)
                e  = self.repo.get_enseignant(s.enseignant_id)
                sa = self.repo.get_salle(s.salle_id)
                fi = self.repo.get_filiere(m.filiere_id) if m else None
                lignes.append(
                    f"  {c.heure_debut.strftime('%H:%M')}-{c.heure_fin.strftime('%H:%M')}"
                    f"  {str(m):<35}  {str(e):<25}  {sa.numero if sa else '?':>6}"
                    f"  [{str(fi) if fi else '?'}]"
                )

        chemin_txt = chemin.replace(".pdf", ".txt")
        with open(chemin_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(lignes))
        return chemin_txt

    # ──────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────

    def _filtrer_sessions(self, filiere_id, enseignant_id) -> List[Session]:
        sessions = self.repo.liste_sessions()
        if filiere_id:
            sessions = [
                s for s in sessions
                if (m := self.repo.get_matiere(s.matiere_id)) and m.filiere_id == filiere_id
            ]
        if enseignant_id:
            sessions = [s for s in sessions if s.enseignant_id == enseignant_id]
        # Tri par jour puis heure
        def cle(s):
            jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
            c = self.repo.get_creneau(s.creneau_id)
            if not c:
                return (99, "00:00")
            return (jours.index(c.jour) if c.jour in jours else 99,
                    c.heure_debut.strftime("%H:%M"))
        sessions.sort(key=cle)
        return sessions

    def _session_vers_ligne(self, s: Session) -> list:
        c  = self.repo.get_creneau(s.creneau_id)
        m  = self.repo.get_matiere(s.matiere_id)
        e  = self.repo.get_enseignant(s.enseignant_id)
        sa = self.repo.get_salle(s.salle_id)
        fi = self.repo.get_filiere(m.filiere_id) if m else None
        return [
            c.jour if c else "",
            c.heure_debut.strftime("%H:%M") if c else "",
            c.heure_fin.strftime("%H:%M") if c else "",
            str(c.semaine) if c else "",
            m.intitule if m else "",
            m.code if m else "",
            m.type_seance.value if m else "",
            str(e) if e else "",
            sa.numero if sa else "",
            sa.batiment if sa else "",
            str(sa.capacite) if sa else "",
            fi.nom if fi else "",
            fi.niveau.value if fi else "",
            str(fi.effectif) if fi else "",
            s.statut.value,
        ]
