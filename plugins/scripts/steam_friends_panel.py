"""
Steam Friends plugin for UWPLauncher

- Uses the same encrypted Steam API key stored in config/steam.json
  (fields: "steamid", "api_key_enc").
- Adds "Steam → Steam Friends…" to the existing Actions/menu_actions menu.
- Shows a table of your Steam friends with:
    * Name
    * Status (Online / Away / etc.)
    * Current game (if any)
    * "Playing current game" flag if they are in the selected game's appid.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

try:
    import requests
except Exception:
    requests = None  # handled gracefully

try:
    from PyQt6 import QtWidgets, QtCore
except Exception:  # pragma: no cover
    QtWidgets = None
    QtCore = None


PLUGIN_NAME = "SteamFriends"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Shows your Steam friends and who is playing the selected game."


# ---- encryption helpers (match UWPLauncher) ----

_STEAM_SECRET = b"UWPLauncherSteamKey"


def _steam_decrypt(ciphertext: str) -> str:
    """Decrypt api_key_enc from steam.json using the same scheme as UWPLauncher."""
    if not ciphertext:
        return ""
    import base64

    try:
        raw = base64.b64decode(ciphertext.encode("ascii", errors="ignore"))
    except Exception:
        return ""
    key = _STEAM_SECRET
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    try:
        return out.decode("utf-8")
    except Exception:
        return ""


def _load_steam_credentials():
    """
    Load steamid + decrypted API key from config/steam.json.

    Returns (steamid, api_key) – either may be "" if missing/invalid.
    """
    try:
        cfg_dir = Path("config")
        cfg_file = cfg_dir / "steam.json"
        if not cfg_file.is_file():
            return "", ""
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
    except Exception:
        return "", ""

    steamid = str(data.get("steamid", "")).strip()
    api_key_enc = str(data.get("api_key_enc", "")).strip()
    if not steamid or not api_key_enc:
        return "", ""

    api_key = _steam_decrypt(api_key_enc)
    if not api_key:
        return steamid, ""
    return steamid, api_key


# ---- Steam Web API helpers ----


def _fetch_friend_ids(steamid: str, api_key: str) -> List[str]:
    """
    Call ISteamUser/GetFriendList to get list of friend SteamIDs.
    """
    if not requests:
        return []
    url = "https://api.steampowered.com/ISteamUser/GetFriendList/v1/"
    params = {
        "key": api_key,
        "steamid": steamid,
        "relationship": "friend",
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
    except Exception:
        return []
    if resp.status_code != 200:
        return []
    try:
        obj = resp.json()
        friends = (obj.get("friendslist") or {}).get("friends") or []
        return [str(f.get("steamid", "")).strip() for f in friends if f.get("steamid")]
    except Exception:
        return []


def _fetch_player_summaries(steamids: List[str], api_key: str) -> List[Dict]:
    """
    Call ISteamUser/GetPlayerSummaries for the given list of SteamIDs.
    """
    if not requests or not steamids:
        return []
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        "key": api_key,
        "steamids": ",".join(steamids),
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
    except Exception:
        return []
    if resp.status_code != 200:
        return []
    try:
        obj = resp.json()
        players = (obj.get("response") or {}).get("players") or []
        return players
    except Exception:
        return []


def _persona_state_text(state: int) -> str:
    mapping = {
        0: "Offline",
        1: "Online",
        2: "Busy",
        3: "Away",
        4: "Snooze",
        5: "Looking to trade",
        6: "Looking to play",
    }
    return mapping.get(int(state), "Unknown")


def _current_game_appid(window) -> str:
    """
    Try to resolve the appid of the currently selected game in the launcher.
    """
    # Preferred: internal helper if present
    try:
        if hasattr(window, "_current_game") and callable(window._current_game):
            g = window._current_game()
        else:
            g = None
    except Exception:
        g = None

    if g is None:
        # Fallback via selector + games list
        try:
            games = getattr(window, "games", None)
            selector = getattr(window, "selector", None)
            if games and selector is not None:
                idx = selector.currentIndex()
                if 0 <= idx < len(games):
                    g = games[idx]
        except Exception:
            g = None

    if not g:
        return ""
    try:
        return str(g.get("appid", "")).strip()
    except Exception:
        return ""


# ---- UI ----


def _show_friends_dialog(window, steamid: str, api_key: str):
    """
    Fetch friends + player summaries and render them in a Qt dialog.
    """
    friends_ids = _fetch_friend_ids(steamid, api_key)
    if not friends_ids:
        QtWidgets.QMessageBox.information(
            window,
            "Steam Friends",
            "No friends were returned by the Steam Web API.\n\n"
            "This could be due to privacy settings or a network error.",
        )
        return

    players = _fetch_player_summaries(friends_ids, api_key)
    if not players:
        QtWidgets.QMessageBox.warning(
            window,
            "Steam Friends",
            "Failed to fetch player summaries from Steam.",
        )
        return

    current_appid = _current_game_appid(window)

    # Build dialog
    dlg = QtWidgets.QDialog(window)
    dlg.setWindowTitle("Steam Friends")
    dlg.resize(700, 400)
    layout = QtWidgets.QVBoxLayout(dlg)

    table = QtWidgets.QTableWidget()
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(["Name", "Status", "Current game", "Playing current game"])
    table.setRowCount(len(players))
    table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)

    playing_current = []

    for row, p in enumerate(players):
        name = str(p.get("personaname", "") or "")
        state = _persona_state_text(p.get("personastate", 0))
        game = str(p.get("gameextrainfo", "") or "")
        gameid = str(p.get("gameid", "") or "")

        # Determine if this friend is playing the currently selected game
        is_playing_current = bool(current_appid and gameid and gameid == str(current_appid))

        if is_playing_current:
            playing_current.append(name)

        items = [
            QtWidgets.QTableWidgetItem(name or "(unknown)"),
            QtWidgets.QTableWidgetItem(state),
            QtWidgets.QTableWidgetItem(game or ""),
            QtWidgets.QTableWidgetItem("Yes" if is_playing_current else ""),
        ]
        for col, item in enumerate(items):
            if is_playing_current:
                # Slight highlight if they are on the current game
                item.setBackground(QtCore.Qt.GlobalColor.darkGreen)
                item.setForeground(QtCore.Qt.GlobalColor.white)
            table.setItem(row, col, item)

    layout.addWidget(table)

    # Close button
    btn_box = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Close
    )
    btn_box.rejected.connect(dlg.reject)
    layout.addWidget(btn_box)

    dlg.exec()

    # Toast: who is playing the current game, if anyone
    try:
        if playing_current and hasattr(window, "_show_toast") and callable(window._show_toast):
            if len(playing_current) == 1:
                msg = f"{playing_current[0]} is playing this on Steam."
            else:
                msg = f"{len(playing_current)} friends are playing this on Steam."
            try:
                window._show_toast(msg, "info")
            except Exception:
                pass
    except Exception:
        pass


# ---- plugin hook ----


def register_plugin(window):
    """
    Main plugin registration hook. Called once at startup with the main window.
    """
    if QtWidgets is None:
        return {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "error": "PyQt6 not available",
        }

    # Find the main Actions/menu_actions menu
    menu = getattr(window, "menu_actions", None)
    if menu is None or not isinstance(menu, QtWidgets.QMenu):
        return {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "error": "menu_actions QMenu not found on window",
        }

    # Try to reuse an existing "Steam" submenu if one exists (from DeepSteamIntegration).
    steam_menu = None
    try:
        for act in menu.actions():
            sub = act.menu()
            if sub is not None and sub.title().strip().lower() == "steam":
                steam_menu = sub
                break
    except Exception:
        steam_menu = None

    if steam_menu is None:
        steam_menu = menu.addMenu("Steam")

    act_friends = steam_menu.addAction("Steam Friends…")

    def on_open_friends():
        if requests is None:
            QtWidgets.QMessageBox.warning(
                window,
                "Steam Friends",
                "The 'requests' module is not available in this build.\n\n"
                "Rebuild the launcher with 'requests' included to use this plugin.",
            )
            return

        steamid, api_key = _load_steam_credentials()
        if not steamid or not api_key:
            QtWidgets.QMessageBox.warning(
                window,
                "Steam Friends",
                "Steam API key or SteamID is not configured.\n\n"
                "Open the Steam sync dialog once and save your credentials.",
            )
            return

        _show_friends_dialog(window, steamid, api_key)

    act_friends.triggered.connect(on_open_friends)

    # Metadata for Plugin Manager
    return {
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
    }


# compatibility aliases
def register(window):  # pragma: no cover
    return register_plugin(window)


def init_plugin(window):  # pragma: no cover
    return register_plugin(window)
