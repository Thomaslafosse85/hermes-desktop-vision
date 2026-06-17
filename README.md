# 🐭👀 Hermes Desktop Vision v3.0

> **Full PC control for AI agents** — Desktop, Browser & System.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GPU Recommended](https://img.shields.io/badge/GPU-Recommended-green.svg)]()
[![Code: 1200+ lines](https://img.shields.io/badge/Code-1200+-lines-9cf.svg)](hermes_desktop_vision/)

👉 **Package:** `hermes_desktop_vision/` — [`desktop.py`](hermes_desktop_vision/desktop.py) · [`browser.py`](hermes_desktop_vision/browser.py) · [`system.py`](hermes_desktop_vision/system.py)  
👉 **Skill Hermes:** [`SKILL.md`](SKILL.md) — copier dans `~/.hermes/skills/`

---

## What is this?

AI agents are blind and powerless on Windows. This toolkit gives them:

| Module | Power | Lines |
|--------|-------|-------|
| 🖥️ **DesktopVision** | See screen (OCR+YOLO), click, scroll, drag, type | 500 |
| 🌐 **BrowserControl** | Chrome automation via CDP + vision fallback | 280 |
| ⚙️ **SystemControl** | Windows, processes, clipboard, volume, notifications | 350 |

**Total: 1200+ lines of pure agent empowerment.**

**AI agents are blind on Windows.** They can't see your desktop, read icon labels, or click buttons. This toolkit gives them vision — enabling autonomous desktop control through EasyOCR + pyautogui.

Built for [Hermes Agent](https://github.com/NousResearch/hermes-agent) but works with **any** AI agent (Claude, GPT, local LLMs).

---

## The Problem

Your AI agent wants to open a file on your desktop. It tries:

| Approach | Result |
|----------|--------|
| "Just guess coordinates" | ❌ Clicks random apps |
| "Pixel diff analysis" | ❌ Dark theme makes it invisible |
| "Scan 160 positions blindly" | ❌ 2 minutes, opens everything |

**Without vision, desktop automation is guesswork.**

## The Solution

```
Screenshot → EasyOCR (reads all text) → pyautogui (clicks the right spot)
```

✅ **Real-world tested**: 54 texts scanned on a 4K dark-theme desktop, "bonjour_thomas.txt" found at confidence 0.77, double-clicked accurately.

---

## Installation

### One-command (recommended for Hermes Agent users)

```bash
pip install git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git
```

Or with YOLO support (larger install):
```bash
pip install "git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git#egg=hermes-desktop-vision[full]"
```

### Manual install

```bash
git clone https://github.com/Thomaslafosse85/hermes-desktop-vision.git
cd hermes-desktop-vision
pip install -e .        # core only
pip install -e ".[full]" # with YOLO
```

**Requirements:**
- Windows 10/11
- Python 3.10+
- GPU recommended (RTX 4070: ~8s scan, CPU: ~30s)

## Quick Start

```python
from desktop_vision import DesktopVision

vision = DesktopVision()

# Open any desktop item by name
vision.open_desktop_item("Chrome")      # Opens Google Chrome
vision.open_desktop_item("bonjour")      # Opens bonjour_thomas.txt

# Find and click anything visible on screen
vision.find_and_click("Submit")          # Click a button
vision.find_and_double_click("Reports")  # Open a folder

# Get all visible text
texts = vision.scan_screen()
for t in texts:
    print(f"[{t.confidence:.2f}] '{t.text}' at ({t.center_x}, {t.center_y})")
```

---

## API Reference

### `DesktopVision(languages=['fr', 'en'], gpu=True)`

Initialize the vision system. First run downloads OCR models (~400MB, cached).

### Screen Control

| Method | Description |
|--------|-------------|
| `screenshot(path=None)` | Take a full-screen screenshot |
| `show_desktop()` | Win+D to show the desktop |
| `scan_screen(path=None)` | OCR-scan and return all text elements |

### Find & Click

| Method | Description |
|--------|-------------|
| `find_text(search, min_confidence=0.3)` | Find first matching text on screen |
| `find_all_text(search, min_confidence=0.3)` | Find all matching texts |
| `find_and_click(search, double=False)` | Find text and click its icon (45px offset) |
| `find_and_double_click(search)` | Find text and double-click its icon |
| `open_desktop_item(name)` | Win+D → find → double-click desktop item |

### Keyboard & System

| Method | Description |
|--------|-------------|
| `type_text(text)` | Type text at cursor position |
| `press_key(key)` | Press a single key |
| `hotkey(*keys)` | Press a key combo (e.g., `hotkey('ctrl', 'c')`) |
| `open_folder(path)` | Open a folder in Explorer |
| `open_app(app_name)` | Launch an application |

### Return Type: `ScreenText`

```python
@dataclass
class ScreenText:
    text: str          # The recognized text
    confidence: float   # OCR confidence (0-1)
    center_x: int      # Center X coordinate
    center_y: int      # Center Y coordinate
    bbox: List         # Full bounding box
```

---

## Real-World Example

This is how we locate and open `bonjour_thomas.txt` on a 4K desktop with 40+ icons:

```python
vision = DesktopVision()
vision.show_desktop()

# Scan finds 54 text elements
texts = vision.scan_screen()

# EasyOCR output:
#   [0.77] "bonjour_thoma_" at (211, 2021)
#   [0.99] "Chrome" at (120, 345)
#   [0.95] "VS Code" at (250, 560)
#   ...

# Click 45px above the text (where the icon is)
vision.find_and_double_click("bonjour")
# → Sublime Text opens with bonjour_thomas.txt ✅
```

---

## Why This Works

| Other approaches | Why they fail |
|-----------------|---------------|
| YOLO alone (COCO) | No "desktop icon" class |
| Pixel diff | Dark theme makes selection invisible |
| Coordinate grid | Icons aren't alphabetically sorted |
| Template matching | Icons change with Windows updates |

**Two complementary pipelines:**
- **EasyOCR** reads text labels → finds icons, buttons, files by name
- **YOLOv8** detects objects (80 COCO classes) → finds non-text UI elements, people, devices

Together they cover everything: text-based and object-based UI elements.

---

## Object Detection with YOLOv8

For non-text UI elements (icons without labels, buttons, images):

```python
vision = DesktopVision()

# Detect everything on screen
objects = vision.detect_objects()
for obj in objects:
    print(f"[{obj.confidence:.2f}] {obj.class_name} at ({obj.center_x}, {obj.center_y})")

# Find and click a specific object
vision.find_and_click_object("cell phone")     # Click on a phone icon
vision.find_and_click_object("laptop")         # Click on a laptop icon
vision.find_and_click_object("book")           # Click on a book/document

# Use custom YOLO models
vision.detect_objects(model="yolov8s.pt")                     # More accurate
vision.detect_objects(model="path/to/custom_model.pt")        # Your fine-tuned model

# Debug: see what YOLO sees
vision.annotate_screenshot(output_path="debug.png")
```

**Available YOLO models:** `yolov8n.pt` (nano, fast), `yolov8s.pt` (small), `yolov8m.pt` (medium), `yolov8l.pt` (large), `yolov8x.pt` (extra large). First run downloads ~6-136MB.

**80 COCO classes** include: person, laptop, cell phone, book, chair, bottle, mouse, keyboard, tv, clock, and more.

### YOLO + EasyOCR = Complete Vision

```python
vision = DesktopVision()

# Strategy 1: Try text first (most reliable)
if not vision.find_and_click("Settings"):
    # Strategy 2: Fall back to object detection
    vision.find_and_click_object("tv")  # Maybe settings is a gear icon
```

---

## Integration with AI Agents

### Hermes Agent

**One-command install** (from your Hermes terminal):
```bash
pip install git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git#egg=hermes-desktop-vision[full]
```

Then in any Hermes skill or conversation:
```python
from desktop_vision import DesktopVision
vision = DesktopVision()

# Text-based
vision.open_desktop_item("target_file")

# Object-based
vision.find_and_click_object("laptop")

# Debug what the agent sees
vision.annotate_screenshot("what_i_see.png")
```

**No skill configuration needed** — the package installs as a standard Python module.
Just tell your Hermes agent: "Use DesktopVision to click on X" and it works.

**Even simpler — use it as a Hermes Skill:**
1. Copy [`SKILL.md`](SKILL.md) into your Hermes skills folder (`~/.hermes/skills/hermes-desktop-vision/`)
2. The skill auto-installs the package on first use
3. Hermes now has vision — zero manual config

```bash
# One-time setup (or let the skill auto-install)
mkdir -p ~/.hermes/skills/hermes-desktop-vision
cp SKILL.md ~/.hermes/skills/hermes-desktop-vision/
```

**Integration with existing Hermes skills:**
The [`hermes-vision`](https://github.com/NousResearch/hermes-agent) and
`desktop-control` skills already document the EasyOCR + YOLO pipeline.
This package is the reference implementation.

### Claude / GPT / Any Agent
Any agent that can run Python can use this. For agents without GPU access,
use the CPU-only install (skip YOLO for speed):
```bash
pip install easyocr pyautogui pillow pygetwindow numpy
```

---

## Browser Control with Chrome

Full Chrome automation — navigate, fill forms, extract text, screenshots.

```python
from hermes_desktop_vision import BrowserControl, DesktopVision

desktop = DesktopVision()
browser = BrowserControl(desktop_vision=desktop)

browser.open("https://github.com")
browser.fill("Search", "hermes-desktop-vision", press_enter=True)
text = browser.extract_text()
browser.screenshot("github.png")
browser.new_tab("https://news.ycombinator.com")
```

**Two modes:** CDP (Chrome DevTools Protocol) or DesktopVision fallback.

---

## System Control

Full Windows management — windows, processes, clipboard, volume.

```python
from hermes_desktop_vision import SystemControl

sys = SystemControl()
sys.focus_window("Chrome")
sys.resize_window(1200, 800)
sys.list_processes(sort_by="memory")
sys.kill_process("notepad.exe")
sys.set_volume(50)
sys.clipboard_copy("Hello from your agent!")
sys.send_notification("Done!", "Task complete.")
sys.lock()  # Win+L
```

---

## 🛡️ Safety First

**All destructive actions are BLOCKED by default.** Your agent can't accidentally
shutdown your PC, kill system processes, or access protected files.

### Protected by default

| Category | What's blocked | How to allow |
|----------|---------------|--------------|
| 🔌 **System** | `shutdown()`, `restart()`, `sleep()`, `lock()` | `guard.allow('shutdown')` |
| 🔫 **Processes** | Killing system processes (`explorer.exe`, `svchost`, `lsass`, `hermes`...) | `guard.allow('kill_process')` — system processes still blocked |
| 📁 **Local files** | `C:\Windows`, `System32`, Hermes config (`.env`, `config.yaml`) | Explicit approval required |
| 🌐 **SSH** | Production connections, destructive commands (`rm -rf`, `shutdown`, `docker rm -f`, `DROP TABLE`) | Explicit approval required |
| 📁 **Server files** | `/etc`, `/boot`, Docker volumes, nginx/PostgreSQL configs, SSH keys | Explicit approval required |
| 🔊 **User experience** | `set_volume()`, `mute()`, `send_notification()` | `guard.allow('set_volume')` |

```python
from hermes_desktop_vision import SystemControl

sys = SystemControl()  # safe_mode=True by default

# BLOCKED by default:
sys.shutdown()                      # 🛡️ CRITICAL — blocked
sys.kill_process("explorer.exe")    # 🛡️ Protected process — blocked
sys.kill_process("notepad.exe")     # 🛡️ DESTRUCTIVE — blocked
sys.lock()                          # 🛡️ CRITICAL — blocked

# Opt-in for specific actions:
sys.guard.allow("kill_process")
sys.kill_process("notepad.exe")     # ✅ Allowed

# System processes STAY protected even with opt-in:
sys.kill_process("explorer.exe")    # 🛡️ STILL BLOCKED

# Check safety status:
print(sys.guard.summary())
# SafetyGuard: safe_mode=ON
#   Blocked: 5 actions
#   Allowed: 1 action (kill_process)
#   Dry run: OFF
#   Protected processes: 12

# Dry-run mode: see what would happen without executing
sys.guard.set_dry_run(True)
sys.shutdown()  # [DRY RUN] Would execute: shutdown (risk=critical)
```

### Risk levels

| Level | Examples | Safe mode behavior |
|-------|----------|-------------------|
| `SAFE` | `list_processes()`, `get_screen_resolution()` | ✅ Always allowed |
| `MODERATE` | `set_volume()`, `clipboard_copy()`, `resize_window()` | 🛡️ Blocked (opt-in) |
| `DESTRUCTIVE` | `kill_process()` (non-system), `close_window()` | 🛡️ Blocked (opt-in) |
| `CRITICAL` | `shutdown()`, `restart()`, `lock()`, `sleep()` | 🛡️ Blocked (explicit opt-in only) |

### Protected processes (can NEVER be killed)

`explorer.exe` · `svchost.exe` · `csrss.exe` · `winlogon.exe` · `services.exe` · `lsass.exe` · `smss.exe` · `System` · `wininit.exe` · `dwm.exe` · `hermes`

### Protected paths (local + SSH)

**Windows:** `C:\Windows` · `C:\Windows\System32` · `C:\Program Files` · Hermes config  
**Linux servers:** `/etc` · `/boot` · `/var/lib/docker` · nginx configs · PostgreSQL data · SSH keys

👉 **[Full self-protection guide for Hermes agents →](SELF_PROTECTION.md)**

### Disabling safety (⚠️ use with caution)

```python
sys.guard.allow_all()    # Disable ALL safety checks
sys = SystemControl(safe_mode=False)  # Start without safety
```

---

## Performance

| Resolution | GPU (RTX 4070) | CPU |
|-----------|----------------|-----|
| 1080p | ~4s | ~15s |
| 4K (3840×2160) | ~8s | ~30s |

First run includes model download (~400MB). Subsequent runs use cached models.

---

## Roadmap

- [ ] Multi-monitor support
- [ ] YOLO integration for non-text UI elements (buttons, icons without labels)
- [ ] Webcam-based gesture control
- [ ] Cross-platform (Linux/macOS) via different screenshot backends

---

## Credits

Built by **Thoma Lafosse** & **Gordias** (the AI co-CEO of [starbottroopers](https://starbottroopers.com)) — the world's first humanoid robot marketplace.

This toolkit emerged from a real need: our AI agent couldn't see the desktop, and we were tired of it opening random apps.

**"We didn't solve computer vision. We just gave our AI eyes on Windows."**

---

## License

MIT — use it, fork it, build on it. If you make something cool, let us know!
