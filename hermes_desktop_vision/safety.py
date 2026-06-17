"""
Safety guard for Hermes Desktop Vision.

Prevents AI agents from doing dangerous things to your PC.
Safe by default — destructive actions require explicit opt-in.

Usage:
    from hermes_desktop_vision.safety import SafetyGuard, DANGEROUS_ACTIONS
"""

from typing import Set, Optional, Callable
from enum import Enum


class ActionRisk(Enum):
    """Risk level for system actions."""
    SAFE = "safe"           # Can run anytime
    MODERATE = "moderate"    # Affects user experience
    DESTRUCTIVE = "destructive"  # Data loss or system impact
    CRITICAL = "critical"    # Can brick the system


# ── Action classification ────────────────────────────────────────────────

DANGEROUS_ACTIONS: dict = {
    # System-level (CRITICAL)
    "shutdown": ActionRisk.CRITICAL,
    "restart": ActionRisk.CRITICAL,
    "sleep": ActionRisk.CRITICAL,
    "lock": ActionRisk.CRITICAL,

    # Process-level (DESTRUCTIVE)
    "kill_process": ActionRisk.DESTRUCTIVE,
    "kill_system_process": ActionRisk.DESTRUCTIVE,
    "close_window": ActionRisk.MODERATE,

    # User experience (MODERATE)
    "mute": ActionRisk.MODERATE,
    "set_volume": ActionRisk.MODERATE,
    "send_notification": ActionRisk.MODERATE,
    "minimize_window": ActionRisk.MODERATE,
    "maximize_window": ActionRisk.MODERATE,
    "resize_window": ActionRisk.MODERATE,
    "move_window": ActionRisk.MODERATE,

    # Clipboard (MODERATE — can overwrite user data)
    "clipboard_copy": ActionRisk.MODERATE,
}

# Processes that should NEVER be killed
PROTECTED_PROCESSES: Set[str] = {
    "explorer.exe",
    "svchost.exe",
    "csrss.exe",
    "winlogon.exe",
    "services.exe",
    "lsass.exe",
    "smss.exe",
    "System",
    "System Idle Process",
    "wininit.exe",
    "dwm.exe",
    "hermes",  # Don't kill yourself!
}


class SafetyGuard:
    """
    Safety layer for desktop automation.

    Default: SAFE_MODE=True — blocks CRITICAL and DESTRUCTIVE actions.
    The user must explicitly opt in for dangerous operations.

    Usage:
        guard = SafetyGuard()
        guard.allow("shutdown")  # Opt-in for this session
        guard.check("shutdown")   # Returns True if allowed
    """

    def __init__(self, safe_mode: bool = True):
        """
        Initialize safety guard.

        Args:
            safe_mode: If True, blocks dangerous actions (default: True)
        """
        self.safe_mode = safe_mode
        self._allowed: Set[str] = set()
        self._blocked_count: int = 0
        self._dry_run: bool = False
        self._confirm_callback: Optional[Callable] = None

    @property
    def blocked_count(self) -> int:
        """Number of actions blocked in this session."""
        return self._blocked_count

    def set_dry_run(self, enabled: bool = True):
        """
        Enable dry-run mode: logs what would happen without executing.

        Args:
            enabled: True to enable dry-run
        """
        self._dry_run = enabled

    def set_confirm_callback(self, callback: Callable[[str, ActionRisk], bool]):
        """
        Set a callback for user confirmation.

        The callback receives (action_name, risk_level) and should return
        True to allow or False to block. Useful for GUI confirmations.

        Args:
            callback: Function that returns bool
        """
        self._confirm_callback = callback

    def allow(self, action: str):
        """
        Allow a specific dangerous action for this session.

        Args:
            action: Action name to allow (e.g., 'shutdown', 'kill_process')
        """
        self._allowed.add(action)

    def deny(self, action: str):
        """Revoke permission for an action."""
        self._allowed.discard(action)

    def allow_all(self):
        """⚠️ Allow ALL actions (including CRITICAL). Use with caution."""
        self.safe_mode = False

    def check(self, action: str,
              process_name: str = None) -> bool:
        """
        Check if an action is allowed.

        Args:
            action: Action name (must be in DANGEROUS_ACTIONS)
            process_name: Process name for kill_process checks

        Returns:
            True if action is safe to execute
        """
        risk = DANGEROUS_ACTIONS.get(action, ActionRisk.SAFE)

        # SAFE actions always pass
        if risk == ActionRisk.SAFE:
            return True

        # Explicitly allowed
        if action in self._allowed:
            return True

        # Dry run: log but don't block
        if self._dry_run:
            print(f"[DRY RUN] Would execute: {action} (risk={risk.value})")
            return True

        # Protected processes can never be killed
        if action == "kill_process" and process_name:
            if process_name.lower() in PROTECTED_PROCESSES:
                self._blocked_count += 1
                print(f"🛡️ BLOCKED: Cannot kill protected process '{process_name}'")
                return False

        # In safe mode, block MODERATE+ actions
        if self.safe_mode and risk in (ActionRisk.MODERATE, ActionRisk.DESTRUCTIVE, ActionRisk.CRITICAL):
            # Ask for confirmation if callback is set
            if self._confirm_callback:
                if self._confirm_callback(action, risk):
                    self._allowed.add(action)
                    return True

            self._blocked_count += 1
            print(f"🛡️ BLOCKED: '{action}' requires explicit permission "
                  f"(risk={risk.value}). Use guard.allow('{action}') to enable.")
            return False

        # CRITICAL always blocked unless safe_mode disabled or explicitly allowed
        if risk == ActionRisk.CRITICAL and self.safe_mode:
            self._blocked_count += 1
            print(f"🛡️ BLOCKED: '{action}' is CRITICAL. "
                  f"Use guard.allow('{action}') or guard.allow_all() to disable safety.")
            return False

        return True

    def is_protected_process(self, process_name: str) -> bool:
        """Check if a process is in the protected list."""
        return process_name.lower() in PROTECTED_PROCESSES

    def summary(self) -> str:
        """Get a summary of safety status."""
        lines = [
            f"SafetyGuard: safe_mode={'ON' if self.safe_mode else '⚠️ OFF'}",
            f"  Blocked: {self._blocked_count} actions",
            f"  Allowed: {len(self._allowed)} actions ({', '.join(sorted(self._allowed)) if self._allowed else 'none'})",
            f"  Dry run: {'ON' if self._dry_run else 'OFF'}",
            f"  Protected processes: {len(PROTECTED_PROCESSES)}",
        ]
        return "\n".join(lines)


# ── Global safety instance ──────────────────────────────────────────────

# Import this to get the default safety guard
_default_guard = SafetyGuard()


def is_safe(action: str, process_name: str = None) -> bool:
    """Quick check using the global safety guard."""
    return _default_guard.check(action, process_name)


def allow_action(action: str):
    """Quick allow using the global safety guard."""
    _default_guard.allow(action)
