---
name: hermes-desktop-vision
description: "Full PC control for Hermes — Desktop (OCR+YOLO), Browser (Chrome CDP), System (Windows), Safety"
version: 1.1.0
platforms: [windows]
python: ">=3.10"
---

# Hermes Desktop Vision v1.1

Donne à ton agent Hermes le **contrôle total du PC** — voir, cliquer, naviguer, contrôler Windows. Sécurisé par défaut.

## Installation (automatique au premier usage)

```bash
pip install git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git#egg=hermes-desktop-vision[full]
```

## Utilisation

```python
from hermes_desktop_vision import DesktopVision, BrowserControl, SystemControl

# 🖥️ Desktop — voir l'écran et cliquer
vision = DesktopVision()
vision.open_desktop_item("Chrome")
vision.find_and_click("Submit")
vision.wait_and_click("Loading...", timeout=30)
vision.scroll_to_and_click("Settings")
vision.drag_item("file.txt", "Folder")

# 🌐 Browser — contrôler Chrome
browser = BrowserControl(desktop_vision=vision)
browser.open("https://github.com")
browser.fill("Search", "query", press_enter=True)
text = browser.extract_text()
browser.screenshot("page.png")
browser.new_tab("https://example.com")

# ⚙️ System — contrôler Windows
sys = SystemControl()
sys.focus_window("Chrome")
sys.resize_window(1200, 800)
sys.list_processes(sort_by="memory")
sys.clipboard_copy("Hello!")
sys.set_volume(50)
sys.send_notification("Done!", "Task complete.")
```

## 🛡️ Sécurité

Toutes les actions destructrices sont **bloquées par défaut** :

```python
sys.shutdown()                      # 🛡️ CRITICAL — bloqué
sys.kill_process("explorer.exe")    # 🛡️ Process protégé — bloqué
sys.lock()                          # 🛡️ CRITICAL — bloqué

# Opt-in explicite requis :
sys.guard.allow("kill_process")
sys.kill_process("notepad.exe")     # ✅ OK
```

**Protégés en permanence :** shutdown, restart, lock, kill de processus système,
connexions SSH prod, modification de C:\Windows, System32, /etc.

👉 [Guide complet de sécurité →](https://github.com/Thomaslafosse85/hermes-desktop-vision/blob/master/docs/SELF_PROTECTION.md)

## Pipelines disponibles

| Pipeline | Usage | Méthode |
|----------|-------|---------|
| **EasyOCR** | Texte visible (icônes, boutons, menus) | `find_and_click("texte")` |
| **YOLOv8** | Objets sans texte (80 classes COCO) | `find_and_click_object("laptop")` |
| **CDP** | Automatisation Chrome native | `browser.open()`, `browser.fill()` |

## Dépannage

**"ImportError: hermes_desktop_vision"**
→ Relance `pip install git+https://...` (package pas installé)

**"YOLO support requires..."**
→ Installe la version full : `pip install "...[full]"`

**L'OCR est lent au premier lancement**
→ Téléchargement du modèle (~400MB). Ensuite c'est rapide.

**Action bloquée par sécurité**
→ Ajoute `sys.guard.allow('action')` avant d'appeler la méthode.
