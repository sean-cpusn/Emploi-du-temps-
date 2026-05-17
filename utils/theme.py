"""
utils/theme.py
Constantes visuelles et palette de couleurs de l'application.
"""

# ── Palette principale ──────────────────────────────────────────
COULEUR_PRIMAIRE   = "#2c3e50"   # Bleu nuit (header / sidebar)
COULEUR_SECONDAIRE = "#3498db"   # Bleu clair (boutons principaux)
COULEUR_ACCENT     = "#27ae60"   # Vert (succès, planifié)
COULEUR_DANGER     = "#e74c3c"   # Rouge (conflit, erreur)
COULEUR_WARNING    = "#f39c12"   # Orange (avertissement)
COULEUR_FOND       = "#ecf0f1"   # Gris très clair (fond général)
COULEUR_BLANC      = "#ffffff"
COULEUR_TEXTE      = "#2c3e50"
COULEUR_TEXTE_CLAIR = "#7f8c8d"
COULEUR_BORDURE    = "#bdc3c7"
COULEUR_HOVER      = "#2980b9"
COULEUR_SIDEBAR    = "#34495e"
COULEUR_HEADER_ROW = "#dfe6e9"

# ── Couleurs par type de séance ─────────────────────────────────
COULEURS_SEANCE = {
    "CM": "#3498db",   # Cours Magistral → bleu
    "TD": "#27ae60",   # Travaux Dirigés → vert
    "TP": "#e67e22",   # Travaux Pratiques → orange
}

# ── Couleurs par filière (rotation) ────────────────────────────
PALETTE_FILIERES = [
    "#8e44ad", "#16a085", "#d35400", "#2980b9",
    "#c0392b", "#1abc9c", "#f39c12", "#7f8c8d",
]

# ── Polices ─────────────────────────────────────────────────────
FONT_TITRE   = ("Segoe UI", 18, "bold")
FONT_SOUS_TITRE = ("Segoe UI", 13, "bold")
FONT_NORMAL  = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_BOLD    = ("Segoe UI", 10, "bold")
FONT_MONO    = ("Courier New", 9)

# ── Dimensions ──────────────────────────────────────────────────
LARGEUR_SIDEBAR   = 200
HAUTEUR_HEADER    = 60
PAD               = 10
PAD_SMALL         = 5
RAYON_BOUTON      = 4

# ── Jours / horaires ────────────────────────────────────────────
JOURS   = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
HEURE_DEBUT_GRILLE = 7    # 07h
HEURE_FIN_GRILLE   = 17  # 17h
