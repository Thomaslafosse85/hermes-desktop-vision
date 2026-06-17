# 🛡️ Self-Protection Guide for Hermes Agents

This guide explains how to configure your Hermes agent to **never** accidentally
damage your PC or servers. Apply these rules once, and your agent is safe forever.

## Quick Setup (copy-paste into your agent)

Tell your Hermes agent to add this to its memory:

```
SÉCURITÉ: shutdown/restart/lock/sleep/kill/SSH prod → confirmation obligatoire.
SystemControl+SafetyGuard obligatoire pour toute action système.
Protégés: processus système, C:\Windows, System32, /etc, /boot,
configs nginx/PG, clés SSH, .env, config.yaml Hermes.
Pas de rm/del/édition dans ces zones sans feu vert explicite.
```

## How it works

This package (`hermes-desktop-vision`) already includes `SafetyGuard` in `SystemControl`.
But your Hermes agent might call `os.system('shutdown')` directly, bypassing it.

**The memory rule prevents this** — it tells the agent to ALWAYS use the safe path.

## Three-layer protection

| Layer | What it does | Where |
|-------|-------------|-------|
| 🧠 **Memory rule** | Agent refuses to execute dangerous commands directly | Agent config |
| 📋 **Skill** | `desktop-control` skill documents safe patterns | `~/.hermes/skills/` |
| 🛡️ **SafetyGuard** | Python code blocks actions at runtime | This package |

## Testing your protection

Ask your agent to do something dangerous:

> "Shutdown my PC"

It should respond with something like:

> 🛡️ BLOCKED: 'shutdown' requires explicit permission.
> Use SystemControl with guard.allow('shutdown') if you really want this.

If it starts typing `os.system('shutdown /s')` — your memory rule isn't applied.

## Protected resources

### Never kill these processes
`explorer.exe`, `svchost.exe`, `csrss.exe`, `winlogon.exe`, `services.exe`,
`lsass.exe`, `smss.exe`, `System`, `wininit.exe`, `dwm.exe`, `hermes`

### Never modify these paths
**Windows:** `C:\Windows`, `C:\Windows\System32`, Hermes config (`.env`, `config.yaml`)
**Linux:** `/etc`, `/boot`, `/var/lib/docker`, nginx configs, PostgreSQL data, SSH keys

### Never run via SSH without approval
`rm -rf`, `shutdown`, `reboot`, `docker rm -f`, `DROP TABLE`, `ALTER TABLE`

---

Built by [starbottroopers](https://github.com/Thomaslafosse85) — because AI agents should be powerful, not dangerous.
