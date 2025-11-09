# UWPLauncher — Game Booster for Microsoft Store / Xbox Game Pass Titles

UWPLauncher starts your UWP games and then **forces CPU affinity and/or High Priority** on the real game EXE so you can squeeze more performance out of sandboxed titles. It also supports optional **Discord Rich Presence**.

> TL;DR: Pick a game, click **Launch**. UWPLauncher calls **UWPHook.exe** to start the UWP app, waits until the *real* game process appears, and then applies your affinity/priority settings.

---

## What you need

- **Windows 10/11**
- **UWPHook.exe** (required). Place it anywhere and tell UWPLauncher where it is the first time.
- (Optional) **Discord** running if you want Rich Presence.

> **Do I need a Steam shortcut?**  
> **No.** UWPLauncher calls `UWPHook.exe` directly, so a Steam shortcut is **not required**. You can still make a Steam shortcut with UWPHook if you want Steam overlay/time tracking — it won’t affect the launcher either way.

---

## Quick Start

1. **Put `UWPHook.exe` on disk.** First run will ask you for its path if the built‑in default is wrong.
2. **Open UWPLauncher** and click **Games ▸ Sync UWP Apps** to pull the installed UWP titles (uses PowerShell Get‑StartApps).
3. Select a game and click **Add Selected**, then edit settings:
   - **AUMID / UWP ID** — the activation ID of the app.
   - **Game EXE (process)** — the *actual* process name the game runs (e.g., `Gears5_EAC.exe`).
   - **Flags** — optional launch flags forwarded to UWPHook.
   - **Affinity Mask (HEX)** — blank = auto (all CPUs except CPU0). Or set your own hex mask.
   - **High Priority / Apply Affinity** — toggles for what to enforce.
4. Hit **Launch**.

### What happens when you click Launch

1. We build: `[UWPHook.exe, <AUMID>, <exe_name>] + <flags>`  
2. UWPHook activates the UWP app and Windows starts the **real EXE**.
3. We watch for the EXE by name; when found, we call Windows APIs to set:
   - **CPU Affinity** (`SetProcessAffinityMask`)
   - **Priority** (`SetPriorityClass`)
4. (Optional) We push a Discord Rich Presence line that includes whether High Priority and Affinity are enabled and what flags you used.

See the architecture diagram for a visual overview.

---

## Discord Rich Presence (optional)

- Toggle via **Settings ▸ Discord RPC**.
- You can change the **Details** and **State** templates. Fields: `{name}`, `{high}`, `{aff}`, `{flags}`.

---

## Tips

- **Affinity mask**: Hex string. Example `FF` uses the lowest 8 CPUs; `FFFF` uses 16 CPUs. Leaving it blank uses all CPUs except CPU0.
- **Finding the EXE name**: Use Task Manager once the game is running, or check known process names for your title.
- **Steam Overlay**: If you want it, create a Steam shortcut using UWPHook. It’s optional and independent of this app.

---

## Known Limitations

- UWPHook **must** exist and be reachable. If it doesn’t, launch will fail and you’ll be prompted to fix the path.
- We wait up to ~45 seconds for the real game EXE to appear before timing out.
- Some anti-cheat / protected processes may block priority/affinity changes.

---

## Credits

- UWPHook by Brian Lima.
- Discord RPC via pypresence (optional).
- Thanks to the community for testing.

