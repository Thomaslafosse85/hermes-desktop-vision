"""
Hermes Desktop Vision — Give your AI agent eyes and hands on Windows.

Pipelines:
    DesktopVision  — Screenshot → EasyOCR/YOLO → click/type/scroll/drag
    BrowserControl — Chrome automation (CDP + vision fallback)
    SystemControl  — Windows, processes, clipboard, volume, notifications

Usage:
    from hermes_desktop_vision import DesktopVision, BrowserControl, SystemControl

    # Desktop
    desktop = DesktopVision()
    desktop.open_desktop_item("Chrome")

    # Browser
    browser = BrowserControl(desktop_vision=desktop)
    browser.open("https://github.com")
    browser.fill("Search", "hermes-desktop-vision")
    browser.press_enter()

    # System
    sys = SystemControl()
    sys.focus_window("Chrome")
    sys.set_volume(50)
    sys.clipboard_copy("Hello World")
"""

__version__ = "1.1.0"
__author__ = "Thoma Lafosse & Gordias (starbottroopers)"
__license__ = "MIT"

from .desktop import DesktopVision, ScreenText, DetectedObject
from .browser import BrowserControl
from .system import SystemControl
from .safety import SafetyGuard, DANGEROUS_ACTIONS, PROTECTED_PROCESSES

__all__ = [
    "DesktopVision",
    "BrowserControl",
    "SystemControl",
    "SafetyGuard",
    "ScreenText",
    "DetectedObject",
    "DANGEROUS_ACTIONS",
    "PROTECTED_PROCESSES",
]
