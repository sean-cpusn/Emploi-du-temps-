# Système de Génération des Emplois du Temps Universitaires
**ISAM – Institut Supérieur des Sciences Arts et Métiers**
Auteur : NKOA MVENG SEAN | Superviseur : M. NOAH

---

## 📁 Structure du Projet

```
emploi_du_temps/
│
├── main.py                        ← Point d'entrée (Run this file)
├── requirements.txt               ← Dépendances
│
├── models/
│   ├── entities.py                ← Entités métier (MCD/MLD)
│   └── repository.py              ← Dépôt en mémoire (remplace la BD)
│
├── services/
│   ├── contraintes.py             ← Validation contraintes fortes/faibles
│   └── generateur.py              ← Algorithme glouton de génération
│
├── ui/
│   ├── app.py                     ← Fenêtre principale + navigation sidebar
│   ├── tableau_bord.py            ← Écran Dashboard (stats + génération)
│   ├── ressources.py              ← Gestion Enseignants/Matières/Salles/Filières
│   ├── planning.py                ← Grille hebdomadaire (vue calendrier)
│   ├── sessions_ui.py             ← Liste et édition manuelle des sessions
│   ├── contraintes_ui.py          ← Gestion contraintes + détection conflits
│   └── export_ui.py               ← Export PDF / CSV
│
├── exports/
│   └── export_service.py          ← Service d'export multi-format
│
└── utils/
    ├── theme.py                   ← Palette couleurs, polices, constantes UI
    └── widgets.py                 ← Widgets Tkinter réutilisables
```

---

## 🚀 Lancement sous PyCharm

1. **Ouvrir le projet** : `File → Open` → sélectionner le dossier `emploi_du_temps`
2. **Configurer l'interpréteur** : `File → Settings → Project → Python Interpreter` (Python 3.8+)
3. **Installer les dépendances optionnelles** :
   ```
   pip install reportlab openpyxl
   ```
4. **Lancer l'application** : clic droit sur `main.py` → `Run 'main'`

> **Tkinter est inclus dans Python standard** – aucune installation requise.
> Sur Linux, si tkinter est absent : `sudo apt install python3-tk`

---

## 🎯 Fonctionnalités Implémentées

| Fonctionnalité | Statut |
|---|---|
| Gestion CRUD enseignants, matières, salles, filières | ✅ |
| Définition de contraintes fortes et faibles | ✅ |
| Indisponibilités des enseignants | ✅ |
| Algorithme glouton de génération automatique | ✅ |
| Validation en temps réel des contraintes | ✅ |
| Grille calendrier hebdomadaire (vue semaine) | ✅ |
| Filtrage par filière / enseignant / salle | ✅ |
| Édition manuelle des sessions | ✅ |
| Détection des conflits avec rapport | ✅ |
| Export CSV | ✅ |
| Export PDF (via reportlab ou texte formaté) | ✅ |
| Données d'exemple pré-chargées | ✅ |
| Architecture en couches (Modèle / Service / UI) | ✅ |

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────┐
│       Couche Présentation       │  ui/ + utils/
│   Tkinter – Fenêtres modales    │
│   Grille calendrier interactive │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│         Couche Métier           │  services/
│   Validation des contraintes    │
│   Algorithme de génération      │
│   Service d'export              │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│         Couche Données          │  models/
│   Repository en mémoire         │
│   (remplace la base de données) │
└─────────────────────────────────┘
```
