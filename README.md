# Système de Génération des Emplois du Temps Universitaires
Auteur : NKOA MVENG SEAN | Superviseur : M. NOAH

---

## Structure du Projet

```
emploi_du_temps/
│
├── main.py                        
├── requirements.txt               
│
├── models/
│   ├── entities.py                
│   └── repository.py              ← Dépôt en mémoire 
│
├── services/
│   ├── contraintes.py             ← Validation contraintes fortes/faibles
│   └── generateur.py              ← Algorithme glouton de génération
│
├── ui/
│   ├── app.py                     ← Fenêtre principale + navigation sidebar
│   ├── tableau_bord.py            ← Écran Dashboard 
│   ├── ressources.py              ← Gestion Enseignants/Matières/Salles/Filières
│   ├── planning.py                ← Grille hebdomadaire 
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
2. **Configurer l'interpréteur** : `File → Settings → Project → Python Interpreter` (Python 3)
3. **Installer les dépendances optionnelles** :
   ```
   pip install reportlab openpyxl
   ```
4. **Lancer l'application** : clic droit sur `main.py` 

> **Tkinter est inclus dans Python standard** .

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


