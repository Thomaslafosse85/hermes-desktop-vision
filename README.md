# Hermes Desktop Vision v1.1

> **Full PC control for AI agents** — Desktop, Browser, System. Safe by default.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Code: 1800+ lines](https://img.shields.io/badge/Code-1800+-lines-9cf.svg)](hermes_desktop_vision/)

---

AI agents are **blind and powerless** on Windows. This package gives them eyes and hands.

```python
from hermes_desktop_vision import DesktopVision, BrowserControl, SystemControl

# See and click
DesktopVision().open_desktop_item("Chrome")

# Browser automation
browser = BrowserControl()
browser.open("https://github.com")
browser.fill("Search", "hermes-desktop-vision", press_enter=True)

# System control (safe by default)
sys = SystemControl()
sys.focus_window("VS Code")
sys.clipboard_copy("Hello from your agent!")
```

---

## Install

```bash
pip install git+https://github.com/Thomaslafosse85/hermes-desktop-vision.git#egg=hermes-desktop-vision[full]
```

Or for Hermes Agent users: copy [`SKILL.md`](SKILL.md) into `~/.hermes/skills/` — auto-installs on first use.

---

## Modules

| Module | What it does | File |
|--------|-------------|------|
| 🖥️ **DesktopVision** | See screen (OCR + YOLO), click, scroll, drag, wait | [`desktop.py`](hermes_desktop_vision/desktop.py) |
| 🌐 **BrowserControl** | Chrome automation via CDP + vision fallback | [`browser.py`](hermes_desktop_vision/browser.py) |
| ⚙️ **SystemControl** | Windows, processes, clipboard, volume | [`system.py`](hermes_desktop_vision/system.py) |
| 🛡️ **SafetyGuard** | Blocks dangerous actions by default | [`safety.py`](hermes_desktop_vision/safety.py) |

---

## Quick examples

### Desktop — see and click

```python
vision = DesktopVision()

vision.open_desktop_item("Chrome")       # Win+D → find → double-click
vision.find_and_click("Submit")          # Click any visible text
vision.wait_and_click("Loading...")      # Wait for async UI
vision.scroll_to_and_click("Settings")   # Scroll until found
vision.drag_item("file.txt", "Folder")   # Drag and drop
```

### Browser — Chrome automation

```python
browser = BrowserControl(desktop_vision=vision)

browser.open("https://example.com")
browser.navigate("https://github.com")
text = browser.extract_text()
browser.screenshot("page.png")
browser.new_tab("https://news.ycombinator.com")
browser.go_back()
```

### System — Windows control

```python
sys = SystemControl()

sys.focus_window("Chrome")
sys.resize_window(1200, 800)
sys.list_processes(sort_by="memory")
sys.set_volume(50)
sys.clipboard_copy("Copied!")
sys.send_notification("Done!", "Task complete.")
```

---

## 🛡️ Safety — blocked by default

All destructive actions require **explicit opt-in**. Your agent CANNOT accidentally:

- `shutdown()` / `restart()` — CRITICAL, blocked
- `kill_process("explorer.exe")` — protected, blocked forever
- `lock()` / `sleep()` — CRITICAL, blocked
- SSH to production — blocked without approval
- Modify system files (`C:\Windows`, `/etc`) — blocked

```python
sys.guard.allow("kill_process")         # Opt-in
sys.kill_process("notepad.exe")         # ✅ Allowed
sys.kill_process("explorer.exe")        # 🛡️ STILL BLOCKED
```

👉 **[Full safety documentation →](docs/SELF_PROTECTION.md)**

---

## Requirements

- Windows 10/11 · Python 3.10+
- GPU recommended (RTX 4070: ~8s 4K scan)
- Optional: `[full]` install includes YOLO + CDP + system tools

---

## Why this exists

Built by [Thoma Lafosse](https://github.com/Thomaslafosse85) & **Gordias** (AI co-CEO of [starbottroopers](https://starbottroopers.com)).

One day our AI agent needed to open a file on the desktop. It couldn't see the screen. We fixed that. Then we added browser control. Then system control. Then safety guards.

**"We didn't solve computer vision. We just gave our AI eyes and hands on Windows."**

MIT License — use it, fork it, build on it.
