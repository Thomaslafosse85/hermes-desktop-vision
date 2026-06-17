"""
Browser control for Hermes Desktop Vision.

Control Google Chrome — navigate, fill forms, click, extract text.
Uses Chrome DevTools Protocol (CDP) for reliable automation,
with desktop-vision fallback when CDP is unavailable.

Requirements (optional):
    websocket-client>=1.6  # for full CDP control
    Without it: falls back to desktop vision (pyautogui-based)
"""

import subprocess
import time
import json
import os
from typing import Optional, List, Dict, Any
from urllib.request import urlopen, Request
from urllib.error import URLError


class BrowserControl:
    """
    Control Google Chrome programmatically.

    Two modes:
    - CDP mode (recommended): Chrome DevTools Protocol via --remote-debugging-port
    - Fallback mode: Uses DesktopVision to click/type on visible Chrome windows

    Usage:
        browser = BrowserControl()
        browser.open("https://github.com")
        browser.fill("search-input", "hermes-desktop-vision")
        browser.press_enter()
        text = browser.extract_text()
    """

    CDP_PORT = 9222

    def __init__(self, chrome_path: str = None, desktop_vision=None):
        """
        Initialize browser control.

        Args:
            chrome_path: Path to chrome.exe (auto-detect if None)
            desktop_vision: DesktopVision instance for fallback mode
        """
        self.chrome_path = chrome_path or self._find_chrome()
        self._desktop_vision = desktop_vision
        self._cdp_available = False
        self._ws = None

    # ── Chrome lifecycle ─────────────────────────────────────────────────

    @staticmethod
    def _find_chrome() -> str:
        """Auto-detect Chrome installation path."""
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return "chrome"  # fallback: hope it's in PATH

    def _start_chrome_cdp(self, url: str = "about:blank") -> bool:
        """Start Chrome with remote debugging enabled."""
        try:
            subprocess.Popen(
                [self.chrome_path, f"--remote-debugging-port={self.CDP_PORT}", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(1.5)
            # Check if CDP is responding
            tabs = self._cdp_list_tabs()
            return len(tabs) > 0
        except Exception:
            return False

    def _cdp_list_tabs(self) -> List[dict]:
        """List open Chrome tabs via CDP HTTP API."""
        try:
            with urlopen(f"http://localhost:{self.CDP_PORT}/json", timeout=3) as resp:
                return json.loads(resp.read().decode())
        except (URLError, OSError, json.JSONDecodeError):
            return []

    def _cdp_send(self, tab_id: str, method: str, params: dict = None) -> dict:
        """Send a CDP command via WebSocket (requires websocket-client)."""
        try:
            from websocket import create_connection
        except ImportError:
            raise ImportError(
                "CDP WebSocket requires: pip install websocket-client\n"
                "Fallback mode will be used instead."
            )

        ws_url = tab_id.replace("ws://", "").replace("/devtools/page/", "")
        ws = create_connection(f"ws://localhost:{self.CDP_PORT}/devtools/page/{ws_url}",
                               timeout=5)

        msg = {"id": 1, "method": method}
        if params:
            msg["params"] = params
        ws.send(json.dumps(msg))

        response = json.loads(ws.recv())
        ws.close()
        return response

    def _get_active_tab(self) -> Optional[dict]:
        """Get the currently active Chrome tab."""
        tabs = self._cdp_list_tabs()
        for tab in tabs:
            if tab.get("type") == "page":
                return tab
        return None

    # ── Public API ───────────────────────────────────────────────────────

    def open(self, url: str, new_tab: bool = False) -> bool:
        """
        Open a URL in Chrome.

        Args:
            url: The URL to navigate to
            new_tab: Open in new tab (default: reuse existing)

        Returns:
            True if successful
        """
        # Try CDP first
        if self._start_chrome_cdp(url if not new_tab else "about:blank"):
            if new_tab:
                # Create new tab via CDP
                try:
                    self._cdp_send(
                        self._get_active_tab()["id"],
                        "Target.createTarget",
                        {"url": url}
                    )
                except Exception:
                    pass
            return True

        # Fallback: open via start command
        os.system(f'start {self.chrome_path} "{url}"')
        return True

    def navigate(self, url: str) -> bool:
        """Navigate the active tab to a URL."""
        tab = self._get_active_tab()
        if tab:
            try:
                self._cdp_send(tab["id"], "Page.navigate", {"url": url})
                return True
            except Exception:
                pass

        # Fallback: Ctrl+L, type URL, Enter
        if self._desktop_vision:
            self._desktop_vision.hotkey("ctrl", "l")
            time.sleep(0.2)
            self._desktop_vision.type_text(url)
            time.sleep(0.1)
            self._desktop_vision.press_key("enter")
            return True
        return False

    def new_tab(self, url: str = "about:blank") -> bool:
        """Open a new tab."""
        tab = self._get_active_tab()
        if tab:
            try:
                self._cdp_send(tab["id"], "Target.createTarget", {"url": url})
                return True
            except Exception:
                pass
        # Fallback
        self.open(url, new_tab=True)
        return True

    def close_tab(self) -> bool:
        """Close the active tab (keeps Chrome open if other tabs exist)."""
        tab = self._get_active_tab()
        if tab:
            try:
                self._cdp_send(tab["id"], "Page.close")
                return True
            except Exception:
                pass
        if self._desktop_vision:
            self._desktop_vision.hotkey("ctrl", "w")
            return True
        return False

    def fill(self, placeholder_or_label: str, text: str,
             press_enter: bool = False) -> bool:
        """
        Fill a form field found by placeholder text or label.

        Uses desktop vision to find and click the field, then type.

        Args:
            placeholder_or_label: Text near the input field
            text: Text to type
            press_enter: Submit the form after typing

        Returns:
            True if field was found and filled
        """
        if self._desktop_vision is None:
            return False

        # Find and click the input
        if not self._desktop_vision.find_and_click(placeholder_or_label,
                                                    icon_offset_y=0):
            return False

        time.sleep(0.2)

        # Select all existing text and replace
        self._desktop_vision.hotkey("ctrl", "a")
        time.sleep(0.1)
        self._desktop_vision.type_text(text)

        if press_enter:
            time.sleep(0.1)
            self._desktop_vision.press_key("enter")

        return True

    def press_enter(self):
        """Press Enter (submit form, follow link, etc.)."""
        if self._desktop_vision:
            self._desktop_vision.press_key("enter")

    def extract_text(self) -> str:
        """
        Extract all visible text from the active browser tab.

        Uses CDP DOM.getDocument + DOM.getOuterHTML then strips tags,
        or falls back to Ctrl+A, Ctrl+C on the page.

        Returns:
            Visible text content
        """
        tab = self._get_active_tab()
        if tab:
            try:
                # Get page HTML via CDP
                result = self._cdp_send(
                    tab["id"],
                    "Runtime.evaluate",
                    {"expression": "document.body.innerText"}
                )
                if "result" in result and "value" in result["result"]:
                    return result["result"]["value"]
            except Exception:
                pass

        # Fallback: select all + copy
        if self._desktop_vision:
            self._desktop_vision.hotkey("ctrl", "a")
            time.sleep(0.2)
            self._desktop_vision.hotkey("ctrl", "c")
            time.sleep(0.2)
            return self._get_clipboard()
        return ""

    def _get_clipboard(self) -> str:
        """Get clipboard text."""
        try:
            import pyperclip
            return pyperclip.paste()
        except ImportError:
            # Slow fallback via subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()

    def screenshot(self, path: str = None) -> Optional[str]:
        """
        Take a screenshot of the browser viewport via CDP.

        Args:
            path: Save path (auto-generated if None)

        Returns:
            Path to screenshot, or None on failure
        """
        tab = self._get_active_tab()
        if tab:
            try:
                result = self._cdp_send(
                    tab["id"],
                    "Page.captureScreenshot",
                    {"format": "png"}
                )
                import base64
                data = base64.b64decode(result["result"]["data"])

                if path is None:
                    path = os.path.join(
                        os.environ.get("TEMP", os.path.expanduser("~")),
                        "browser_screenshot.png"
                    )
                with open(path, "wb") as f:
                    f.write(data)
                return path
            except Exception:
                pass
        return None

    def scroll_page(self, direction: str = "down", amount: int = 500):
        """
        Scroll the page.

        Args:
            direction: 'up' or 'down'
            amount: Pixels to scroll
        """
        tab = self._get_active_tab()
        if tab:
            try:
                sign = -1 if direction == "down" else 1
                self._cdp_send(
                    tab["id"],
                    "Runtime.evaluate",
                    {"expression": f"window.scrollBy(0, {sign * amount})"}
                )
                return
            except Exception:
                pass
        # Fallback
        if self._desktop_vision:
            import pyautogui
            pyautogui.scroll(-amount if direction == "down" else amount)

    def go_back(self):
        """Navigate back in history."""
        if self._desktop_vision:
            self._desktop_vision.hotkey("alt", "left")

    def go_forward(self):
        """Navigate forward in history."""
        if self._desktop_vision:
            self._desktop_vision.hotkey("alt", "right")

    def refresh(self):
        """Refresh the page."""
        if self._desktop_vision:
            self._desktop_vision.press_key("f5")

    @property
    def cdp_available(self) -> bool:
        """Check if CDP (Chrome DevTools Protocol) is available."""
        return len(self._cdp_list_tabs()) > 0
