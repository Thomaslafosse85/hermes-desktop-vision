---
name: hermes-desktop-vision
description: "Give Hermes eyes on Windows — find and click any UI element via EasyOCR + YOLOv8"
version: 1.2.0
platforms: [windows]
python: ">=3.10"
---

# Hermes Desktop Vision Skill

Donne à ton agent Hermes des **yeux sur Windows**. Screenshot → OCR/YOLO → Clic.

## Installation (automatique au premier usage)

```bash
pip install git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git#egg=hermes-desktop-vision[full]
```

Si YOLO ne t'intéresse pas (package plus léger) :
```bash
pip install git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git
```

## Utilisation

Une fois installé, ton agent peut :

```python
from desktop_vision import DesktopVision
vision = DesktopVision()

# Ouvrir un élément du bureau par son nom
vision.open_desktop_item("Chrome")
vision.open_desktop_item("VS Code")

# Trouver et cliquer n'importe quel texte visible à l'écran
vision.find_and_click("Submit")
vision.find_and_double_click("Rapport financier")

# Scanner tout le texte visible
texts = vision.scan_screen()
for t in texts:
    print(f"[{t.confidence:.2f}] '{t.text}'")

# Détection d'objets sans texte (YOLO)
vision.find_and_click_object("cell phone")
vision.detect_objects(classes=["person", "laptop"])

# Contrôle clavier
vision.hotkey("ctrl", "c")
vision.type_text("Hello World")
```

## Pipelines disponibles

| Pipeline | Usage | Méthode |
|----------|-------|---------|
| **EasyOCR** | Texte visible (icônes, boutons, menus) | `find_and_click("texte")` |
| **YOLOv8** | Objets sans texte (80 classes COCO) | `find_and_click_object("laptop")` |

## Exemples concrets

### "Ouvre mon fichier bonjour_thomas.txt"

```python
vision = DesktopVision()
vision.show_desktop()          # Win+D
vision.find_and_double_click("bonjour")  # Trouve le label, double-clic 45px au-dessus
```

### "Clique sur le bouton Submit dans cette fenêtre"

```python
vision = DesktopVision()
vision.find_and_click("Submit")  # Cherche le texte "Submit" et clique dessus
```

### "Montre-moi ce que tu vois" (debug)

```python
vision = DesktopVision()
vision.annotate_screenshot("ce_que_je_vois.png")  # Screenshot avec bounding boxes YOLO
```

## Prérequis

- Windows 10/11
- Python 3.10+
- GPU recommandé (RTX 4070 : ~8s scan 4K, CPU : ~30s)

## Dépannage

**"ImportError: No module named 'desktop_vision'"**
→ Relance `pip install git+https://...` (le package n'est pas installé)

**"YOLO support requires: pip install ultralytics..."**
→ Installe la version full : `pip install "...[full]"`

**L'OCR est lent**
→ Premier lancement = téléchargement du modèle (~400MB). Ensuite c'est rapide.
→ Vérifie que `gpu=True` (par défaut) et que CUDA est dispo.

**L'OCR ne trouve pas mon texte**
→ Vérifie que le thème n'est pas trop extrême (contraste suffisant)
→ Baisse `min_confidence` : `vision.find_text("cible", min_confidence=0.1)`
