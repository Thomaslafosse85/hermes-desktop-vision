"""
System control for Hermes Desktop Vision.

Full Windows system control — windows, processes, clipboard,
volume, notifications, session management.

Requirements (optional):
    psutil>=5.9      # process management
    pyperclip>=1.8   # clipboard (faster than PowerShell fallback)
"""

import subprocess
import time
import os
import ctypes
from typing import Optional, List, Tuple

try:
    from .safety import SafetyGuard
except ImportError:
    SafetyGuard = None


class SystemControl:
    """
    Full Windows system control with built-in safety.

    Safe by default: destructive actions (shutdown, kill_process, lock)
    require explicit opt-in via guard.allow('action').

    Usage:
        sys = SystemControl()
        sys.guard.allow("kill_process")  # Opt-in for this session
        sys.kill_process("notepad.exe")
        sys.guard.summary()  # Check what's been blocked
    """

    def __init__(self, safe_mode: bool = True):
        """
        Initialize system control.

        Args:
            safe_mode: Enable safety guard (default: True)
        """
        self.guard = SafetyGuard(safe_mode=safe_mode) if SafetyGuard else None

    # ── Window Management ────────────────────────────────────────────────

    def focus_window(self, title_contains: str) -> bool:
        """
        Bring a window to the foreground by partial title match.

        Args:
            title_contains: Part of the window title (case-insensitive)

        Returns:
            True if window was found and focused
        """
        try:
            import pygetwindow as gw
            matches = [w for w in gw.getAllWindows()
                       if title_contains.lower() in w.title.lower()
                       and w.width > 100]
            if matches:
                matches[0].activate()
                return True
        except ImportError:
            pass

        # PowerShell fallback
        script = (
            f"Add-Type -AssemblyName Microsoft.VisualBasic; "
            f"$wshell = New-Object -ComObject wscript.shell; "
            f"$wshell.AppActivate('{title_contains}')"
        )
        subprocess.run(["powershell", "-Command", script],
                       capture_output=True, timeout=5)
        return True

    def list_windows(self) -> List[dict]:
        """
        List all visible windows.

        Returns:
            List of dicts with 'title', 'width', 'height', 'x', 'y'
        """
        try:
            import pygetwindow as gw
            return [
                {
                    "title": w.title,
                    "width": w.width,
                    "height": w.height,
                    "x": w.left,
                    "y": w.top,
                }
                for w in gw.getAllWindows()
                if w.title.strip() and w.width > 50
            ]
        except ImportError:
            return []

    def resize_window(self, width: int, height: int,
                      title_contains: str = None) -> bool:
        """
        Resize the active or specified window.

        Args:
            width: New width in pixels
            height: New height in pixels
            title_contains: Window to resize (active window if None)

        Returns:
            True if successful
        """
        try:
            import pygetwindow as gw

            if title_contains:
                matches = [w for w in gw.getAllWindows()
                           if title_contains.lower() in w.title.lower()]
                if matches:
                    matches[0].resizeTo(width, height)
                    return True
            else:
                # Active window
                import pyautogui
                win = gw.getActiveWindow()
                if win:
                    win.resizeTo(width, height)
                    return True
        except ImportError:
            pass
        return False

    def move_window(self, x: int, y: int,
                    title_contains: str = None) -> bool:
        """
        Move a window to a specific position.

        Args:
            x, y: New position
            title_contains: Window to move (active if None)

        Returns:
            True if successful
        """
        try:
            import pygetwindow as gw
            if title_contains:
                matches = [w for w in gw.getAllWindows()
                           if title_contains.lower() in w.title.lower()]
                if matches:
                    matches[0].moveTo(x, y)
                    return True
            else:
                win = gw.getActiveWindow()
                if win:
                    win.moveTo(x, y)
                    return True
        except ImportError:
            pass
        return False

    def minimize_window(self, title_contains: str = None) -> bool:
        """Minimize a window."""
        try:
            import pygetwindow as gw
            if title_contains:
                matches = [w for w in gw.getAllWindows()
                           if title_contains.lower() in w.title.lower()]
                if matches:
                    matches[0].minimize()
                    return True
            else:
                win = gw.getActiveWindow()
                if win:
                    win.minimize()
                    return True
        except ImportError:
            pass
        return False

    def maximize_window(self, title_contains: str = None) -> bool:
        """Maximize a window."""
        try:
            import pygetwindow as gw
            if title_contains:
                matches = [w for w in gw.getAllWindows()
                           if title_contains.lower() in w.title.lower()]
                if matches:
                    matches[0].maximize()
                    return True
            else:
                win = gw.getActiveWindow()
                if win:
                    win.maximize()
                    return True
        except ImportError:
            pass
        return False

    def close_window(self, title_contains: str = None) -> bool:
        """
        Close a window gracefully (Alt+F4).

        Args:
            title_contains: Window to close (active if None)

        Returns:
            True if successful
        """
        if title_contains:
            self.focus_window(title_contains)
            time.sleep(0.3)
        import pyautogui
        pyautogui.hotkey("alt", "f4")
        return True

    # ── Process Management ───────────────────────────────────────────────

    def list_processes(self, filter_name: str = None,
                       sort_by: str = "memory") -> List[dict]:
        """
        List running processes.

        Args:
            filter_name: Filter by process name (partial match)
            sort_by: 'memory', 'cpu', or 'name'

        Returns:
            List of process dicts with name, pid, memory_mb
        """
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(["name", "pid", "memory_info"]):
                try:
                    info = proc.info
                    name = info["name"] or ""
                    if filter_name and filter_name.lower() not in name.lower():
                        continue
                    mem = info["memory_info"]
                    processes.append({
                        "name": name,
                        "pid": info["pid"],
                        "memory_mb": round(mem.rss / 1024 / 1024, 1) if mem else 0,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if sort_by == "memory":
                processes.sort(key=lambda p: -p["memory_mb"])
            elif sort_by == "name":
                processes.sort(key=lambda p: p["name"])
            return processes[:50]
        except ImportError:
            # Fallback: tasklist
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=10
            )
            processes = []
            for line in result.stdout.strip().split("\n"):
                parts = line.replace('"', "").split(",")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    if filter_name and filter_name.lower() not in name.lower():
                        continue
                    processes.append({
                        "name": name,
                        "pid": int(parts[1].strip()),
                        "memory_mb": 0,
                    })
            return processes[:50]

    def kill_process(self, name: str, force: bool = False) -> int:
        """
        Kill a process by name. Requires guard.allow('kill_process').

        Args:
            name: Process name (e.g., 'notepad.exe', 'chrome')
            force: Use /F (force kill)

        Returns:
            Number of processes killed (0 if blocked by safety)
        """
        # Safety check
        if self.guard and not self.guard.check("kill_process", process_name=name):
            return 0

        killed = 0
        try:
            import psutil
            for proc in psutil.process_iter(["name"]):
                try:
                    if name.lower() in (proc.info["name"] or "").lower():
                        proc.kill() if force else proc.terminate()
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            flag = "/F" if force else ""
            result = subprocess.run(
                ["taskkill", f"/IM", name, flag],
                capture_output=True, text=True, timeout=10
            )
            if "SUCCESS" in result.stdout:
                killed = result.stdout.count("SUCCESS")

        return killed

    def is_process_running(self, name: str) -> bool:
        """Check if a process is running by name."""
        try:
            import psutil
            for proc in psutil.process_iter(["name"]):
                try:
                    if name.lower() in (proc.info["name"] or "").lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except ImportError:
            result = subprocess.run(
                ["tasklist", "/fi", f"IMAGENAME eq {name}", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=5
            )
            return name.lower() in result.stdout.lower()

    # ── Clipboard ────────────────────────────────────────────────────────

    def clipboard_copy(self, text: str = None) -> str:
        """
        Copy selected text to clipboard, or set clipboard content.

        If text is provided, sets clipboard to that text.
        Otherwise, performs Ctrl+C to copy current selection.

        Args:
            text: Text to put on clipboard (optional)

        Returns:
            Current clipboard content
        """
        if text is not None:
            try:
                import pyperclip
                pyperclip.copy(text)
                return text
            except ImportError:
                subprocess.run(
                    ["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
                    capture_output=True, timeout=5
                )
                return text
        else:
            import pyautogui
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.2)
            return self.clipboard_paste()

    def clipboard_paste(self) -> str:
        """
        Get current clipboard content.

        Returns:
            Clipboard text
        """
        try:
            import pyperclip
            return pyperclip.paste()
        except ImportError:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()

    # ── Audio ────────────────────────────────────────────────────────────

    def set_volume(self, level: int) -> bool:
        """
        Set system volume (Windows).

        Args:
            level: Volume level 0-100

        Returns:
            True if successful
        """
        try:
            # Use pyautogui to press volume keys
            import pyautogui
            # First mute to get a baseline, then adjust
            for _ in range(50):  # press volume down many times
                pyautogui.press("volumedown")
            time.sleep(0.3)
            # Press volume up the right number of times
            presses = int(level / 2)  # 2% per press
            for _ in range(presses):
                pyautogui.press("volumeup")
                time.sleep(0.02)
            return True
        except Exception:
            pass
        return False

    def mute(self) -> bool:
        """Toggle mute."""
        import pyautogui
        pyautogui.press("volumemute")
        return True

    # ── System ───────────────────────────────────────────────────────────

    def lock(self):
        """Lock the workstation (Win+L). Requires guard.allow('lock')."""
        if self.guard and not self.guard.check("lock"):
            return
        import pyautogui
        pyautogui.hotkey("win", "l")

    def sleep(self):
        """Put the computer to sleep. Requires guard.allow('sleep')."""
        if self.guard and not self.guard.check("sleep"):
            return
        subprocess.run(
            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
            capture_output=True, timeout=5
        )

    def shutdown(self, force: bool = False, timeout: int = 60):
        """
        Shutdown the computer. Requires guard.allow('shutdown').

        Args:
            force: Force close applications
            timeout: Seconds before shutdown
        """
        if self.guard and not self.guard.check("shutdown"):
            return
        flag = "/f" if force else ""
        os.system(f"shutdown /s {flag} /t {timeout}")

    def restart(self, force: bool = False, timeout: int = 60):
        """
        Restart the computer. Requires guard.allow('restart').

        Args:
            force: Force close applications
            timeout: Seconds before restart
        """
        if self.guard and not self.guard.check("restart"):
            return
        flag = "/f" if force else ""
        os.system(f"shutdown /r {flag} /t {timeout}")

    def abort_shutdown(self):
        """Cancel a pending shutdown/restart."""
        os.system("shutdown /a")

    def open_start_menu(self):
        """Open the Windows Start menu."""
        import pyautogui
        pyautogui.press("win")

    def open_run_dialog(self):
        """Open the Run dialog (Win+R)."""
        import pyautogui
        pyautogui.hotkey("win", "r")

    def open_task_manager(self):
        """Open Task Manager."""
        import pyautogui
        pyautogui.hotkey("ctrl", "shift", "esc")

    def send_notification(self, title: str, message: str):
        """
        Show a Windows toast notification.

        Args:
            title: Notification title
            message: Notification body
        """
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(
            [Windows.UI.Notifications.ToastTemplateType]::ToastText02
        )
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(
            "Hermes Desktop Vision"
        ).Show($toast)
        """
        subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, timeout=5
        )

    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get primary monitor resolution."""
        import pyautogui
        size = pyautogui.size()
        return (size.width, size.height)
