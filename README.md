# 🐭👀 Hermes Desktop Vision

> Give your AI agent **eyes on Windows**. Screenshot → OCR → Click.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GPU Recommended](https://img.shields.io/badge/GPU-Recommended-green.svg)]()

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

```bash
git clone https://github.com/Thomaslafosse85/hermes-desktop-vision.git
cd hermes-desktop-vision
pip install -r requirements.txt
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
| YOLO alone | COCO has no "desktop icon" class |
| Pixel diff | Dark theme makes selection invisible |
| Coordinate grid | Icons aren't alphabetically sorted |
| Template matching | Icons change with Windows updates |

**EasyOCR reads the text labels directly** — no training needed, works on any theme, any resolution.

---

## Integration with AI Agents

### Hermes Agent
```bash
pip install hermes-desktop-vision
```
Then in your Hermes skill:
```python
from desktop_vision import DesktopVision
vision = DesktopVision()
vision.open_desktop_item("target_file")
```

### Claude / GPT / Any Agent
Any agent that can run Python can use this:
```python
# Agent decides: "I need to click 'Submit'"
from desktop_vision import DesktopVision
DesktopVision().find_and_click("Submit")
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
