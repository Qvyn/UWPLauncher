"""
Deep Steam Integration plugin for UWPLauncher (v3).

What it does now:
- Adds "Steam → Show game info…" to the Actions / menu_actions menu.
- For the *currently selected game* (must have an "appid" in games.json),
  it calls public Steam endpoints and shows:
    * Name + type
    * Release date
    * Price + discount
    * Live user review summary (Steam reviews)
    * Live current player count (Steam concurrent players)
    * Genres / categories
    * Short description
    * (If available) Xbox friends currently playing this title, from FriendsDock cache

No Steam API key required (uses Store + keyless Web API).
"""
from __future__ import annotations

import json
import textwrap
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # we'll handle this gracefully

try:
    from PyQt6 import QtWidgets, QtCore  # type: ignore
except Exception:  # pragma: no cover
    QtWidgets = None
    QtCore = None


PLUGIN_NAME = "DeepSteamIntegration"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = (
    "Shows live Steam Store + review + player-count info for the selected game."
)


# ---------- helpers: current game / appid ----------


def _get_current_game(window):
    """
    Resolve the currently selected game dict from the main window.
    """
    # Preferred: internal helper
    try:
        if hasattr(window, "_current_game") and callable(window._current_game):
            g = window._current_game()
            if g:
                return g
    except Exception:
        pass

    # Fallback: selector + games list
    try:
        games = getattr(window, "games", None)
        selector = getattr(window, "selector", None)
        if games and selector is not None:
            idx = selector.currentIndex()
            if 0 <= idx < len(games):
                return games[idx]
    except Exception:
        pass

    return None


def _require_appid(window, game):
    """
    Ensure the game has a valid Steam appid. If not, show an info box.
    Returns the string appid on success, or None on failure.
    """
    if game is None:
        QtWidgets.QMessageBox.information(
            window,
            "Deep Steam Integration",
            "Select a game first.",
        )
        return None

    appid = ""
    try:
        appid = str(game.get("appid", "")).strip()
    except Exception:
        appid = ""

    if not appid:
        QtWidgets.QMessageBox.information(
            window,
            "Deep Steam Integration",
            "This game does not have a Steam appid set.\n\n"
            "Edit the game entry and add an 'appid' to use Steam integration.",
        )
        return None

    return appid


# ---------- helpers: Steam HTTP ----------


def _fetch_steam_store_data(appid: str) -> Optional[Dict[str, Any]]:
    """
    Call Steam's public Store API for the given appid.

    Example:
      https://store.steampowered.com/api/appdetails?appids=570&cc=us&l=en

    Returns the 'data' object for that appid, or None on failure.
    """
    if requests is None:
        return None

    try:
        url = "https://store.steampowered.com/api/appdetails"
        params = {
            "appids": str(appid),
            "cc": "us",
            "l": "en",
        }
        resp = requests.get(url, params=params, timeout=5)
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    try:
        obj = resp.json()
    except Exception:
        try:
            obj = json.loads(resp.text)
        except Exception:
            return None

    try:
        entry = obj.get(str(appid), {})
        if not entry.get("success"):
            return None
        data = entry.get("data") or {}
        if not data:
            return None
        return data
    except Exception:
        return None


def _fetch_live_player_count(appid: str) -> Optional[int]:
    """
    Call Steam's keyless Web API to get current player count.

    https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=APPID
    """
    if requests is None:
        return None

    try:
        url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        params = {"appid": str(appid)}
        resp = requests.get(url, params=params, timeout=5)
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    try:
        obj = resp.json()
        return int(((obj or {}).get("response") or {}).get("player_count") or 0) or None
    except Exception:
        return None


def _fetch_review_summary(appid: str) -> Optional[Dict[str, Any]]:
    """
    Use the public appreviews endpoint to get a compact review summary.

    Example:
      https://store.steampowered.com/appreviews/570?json=1&filter=summary&language=all
    """
    if requests is None:
        return None

    try:
        url = f"https://store.steampowered.com/appreviews/{appid}"
        params = {
            "json": 1,
            "filter": "summary",
            "language": "all",
            "purchase_type": "all",
        }
        resp = requests.get(url, params=params, timeout=5)
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    try:
        obj = resp.json()
    except Exception:
        try:
            obj = json.loads(resp.text)
        except Exception:
            return None

    q = (obj or {}).get("query_summary") or {}
    try:
        total = int(q.get("total_reviews") or 0)
        pos = int(q.get("total_positive") or 0)
        desc = (q.get("review_score_desc") or "").strip()
    except Exception:
        return None

    if total <= 0:
        return None

    pct = 0.0
    try:
        pct = (pos / float(total)) * 100.0 if total else 0.0
    except Exception:
        pct = 0.0

    return {
        "total": total,
        "positive": pos,
        "pct_positive": pct,
        "desc": desc,
    }


# ---------- helpers: Xbox friends (FriendsDock cache) ----------


def _guess_game_title(game: dict) -> str:
    for key in ("title", "name", "display_name", "game_name"):
        try:
            v = str(game.get(key, "")).strip()
        except Exception:
            v = ""
        if v:
            return v
    # Fallback: nothing
    return ""


def _friends_cache_path() -> Path:
    """
    FriendsDock writes its cache into ./config/friends_cache.json via the
    monkey-patched helpers in UWPLauncher. We mirror that logic here.
    """
    try:
        root = Path(__file__).resolve().parent / "config"
    except Exception:
        root = Path.cwd() / "config"
    return root / "friends_cache.json"


def _load_friends_rows() -> List[Tuple[str, str, str]]:
    """
    Return cached rows from FriendsDock, if any:
      [(gamertag, status, game_title), ...]
    """
    rows: List[Tuple[str, str, str]] = []
    try:
        p = _friends_cache_path()
        if not p.exists():
            return rows
        raw = p.read_text(encoding="utf-8", errors="ignore")
        if not raw.strip():
            return rows
        arr = json.loads(raw)
    except Exception:
        return rows

    try:
        for d in arr or []:
            try:
                gt = str(d.get("gamertag", "")).strip()
                st = str(d.get("status", "")).strip()
                gm = str(d.get("game", "")).strip()
            except Exception:
                continue
            rows.append((gt, st, gm))
    except Exception:
        pass
    return rows


def _friends_playing_title(game_title: str) -> List[str]:
    """
    Return a list of Xbox gamertags currently playing *approximately* this game,
    based on FriendsDock's cached rows (if available).
    """
    if not game_title:
        return []

    title_norm = game_title.lower()
    rows = _load_friends_rows()
    friends: List[str] = []

    for (gt, status, gtitle) in rows:
        try:
            s = (status or "").lower()
            t = (gtitle or "").lower()
        except Exception:
            continue
        if not gt or not t:
            continue
        # Require them to be online / in-game.
        if "online" not in s and "playing" not in s and "in-game" not in s:
            continue
        # Very loose title match – this is just for flavor, not strict linking.
        if title_norm in t or t in title_norm:
            friends.append(gt)

    # Deduplicate while preserving order
    seen = set()
    out: List[str] = []
    for name in friends:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


# ---------- summary text ----------


def _build_summary_text(
    data: Dict[str, Any],
    review_info: Optional[Dict[str, Any]] = None,
    player_count: Optional[int] = None,
    friends_playing: Optional[List[str]] = None,
) -> str:
    """
    Turn the Steam 'data' JSON (plus optional live info) into a human-readable block.
    """
    name = data.get("name", "Unknown")
    gtype = data.get("type", "")
    release = (data.get("release_date") or {}).get("date", "Unknown")

    price = ""
    discount = ""
    try:
        p = data.get("price_overview") or {}
        if p:
            price = p.get("final_formatted") or ""
            discount_percent = int(p.get("discount_percent") or 0)
            if discount_percent > 0:
                discount = f"-{discount_percent}%"
    except Exception:
        pass

    # Metacritic (if present)
    metacritic_line = ""
    try:
        mc = (data.get("metacritic") or {}).get("score", "")
        if mc:
            metacritic_line = f"Metacritic: {mc}"
    except Exception:
        metacritic_line = ""

    # Steam review summary info
    review_line = ""
    if review_info:
        try:
            desc = (review_info.get("desc") or "").strip()
            pct = review_info.get("pct_positive")
            total = int(review_info.get("total") or 0)
            if pct is not None and total:
                review_line = (
                    f"User reviews: {desc or 'Mixed'} – "
                    f"{pct:.0f}% positive ({total:,d} reviews)"
                )
            elif desc or total:
                review_line = (
                    f"User reviews: {desc or 'Mixed'} "
                    f"({total:,d} reviews)"
                )
        except Exception:
            review_line = ""

    # Genres / categories
    genres: List[str] = []
    try:
        for g in data.get("genres") or []:
            d = (g.get("description") or "").strip()
            if d:
                genres.append(d)
    except Exception:
        pass

    cats: List[str] = []
    try:
        for c in data.get("categories") or []:
            d = (c.get("description") or "").strip()
            if d:
                cats.append(d)
    except Exception:
        pass

    short_desc = (data.get("short_description") or "").strip()

    lines: List[str] = []
    lines.append(f"{name}")
    if gtype:
        lines.append(f"Type: {gtype}")
    lines.append(f"Release: {release}")

    # Live player count, if available
    if player_count is not None:
        lines.append(f"Players online right now (Steam): {player_count:,d}")

    # Pricing
    if price or discount:
        if discount:
            lines.append(f"Price: {price} ({discount})")
        else:
            lines.append(f"Price: {price or 'N/A'}")

    # Reviews
    if review_line:
        lines.append(review_line)
    if metacritic_line:
        lines.append(metacritic_line)

    # Xbox friends playing (best-effort flavor)
    if friends_playing:
        if len(friends_playing) == 1:
            lines.append(f"Friends playing now (Xbox): {friends_playing[0]}")
        else:
            lines.append(
                "Friends playing now (Xbox): "
                + ", ".join(friends_playing[:5])
            )

    if genres:
        lines.append("Genres: " + ", ".join(genres))
    if cats:
        lines.append("Categories: " + ", ".join(cats))

    if short_desc:
        lines.append("")
        wrapped = textwrap.wrap(short_desc, width=90)
        lines.extend(wrapped)

    return "\n".join(lines)


# ---------- dialog ----------


def _show_game_info_dialog(
    window,
    appid: str,
    data: Dict[str, Any],
    review_info: Optional[Dict[str, Any]] = None,
    player_count: Optional[int] = None,
    friends_playing: Optional[List[str]] = None,
):
    """
    Render the Steam data in a simple, readable Qt dialog.
    """
    dlg = QtWidgets.QDialog(window)
    dlg.setWindowTitle(f"Steam Info – {appid}")
    dlg.resize(720, 420)

    layout = QtWidgets.QVBoxLayout(dlg)

    # Multi-line read-only text view
    text = _build_summary_text(
        data,
        review_info=review_info,
        player_count=player_count,
        friends_playing=friends_playing,
    )
    edit = QtWidgets.QPlainTextEdit()
    edit.setReadOnly(True)
    edit.setPlainText(text)
    layout.addWidget(edit)

    # Button row
    btns_row = QtWidgets.QHBoxLayout()
    btn_open_store = QtWidgets.QPushButton("Open Store Page")
    btn_open_hub = QtWidgets.QPushButton("Open Community Hub")
    btns_row.addWidget(btn_open_store)
    btns_row.addWidget(btn_open_hub)
    btns_row.addStretch(1)
    layout.addLayout(btns_row)

    # Close button
    box = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Close
    )
    box.rejected.connect(dlg.reject)
    layout.addWidget(box)

    # Handlers for buttons → open in browser
    def _open_store():
        url = f"https://store.steampowered.com/app/{appid}/"
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def _open_hub():
        url = f"https://steamcommunity.com/app/{appid}/"
        try:
            webbrowser.open(url)
        except Exception:
            pass

    btn_open_store.clicked.connect(_open_store)
    btn_open_hub.clicked.connect(_open_hub)

    dlg.exec()


# ---------- plugin hook ----------


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

    # Use the same QMenu the launcher already uses for Actions/settings.
    menu = getattr(window, "menu_actions", None)
    if menu is None or not isinstance(menu, QtWidgets.QMenu):
        return {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "error": "menu_actions QMenu not found on window",
        }

    steam_menu = menu.addMenu("Steam")

    act_info = steam_menu.addAction("Show game info…")

    def on_show_info():
        if requests is None:
            QtWidgets.QMessageBox.warning(
                window,
                "Deep Steam Integration",
                "The 'requests' module is not available in this build.\n\n"
                "Rebuild the launcher with 'requests' included to use this plugin.",
            )
            return

        game = _get_current_game(window)
        appid = _require_appid(window, game)
        if not appid:
            return

        # Network calls (best-effort; none of these are fatal)
        store_data = _fetch_steam_store_data(appid)
        if not store_data:
            QtWidgets.QMessageBox.warning(
                window,
                "Deep Steam Integration",
                "Failed to fetch Steam Store data for this game.\n\n"
                "It may not exist on Steam, or there may be a network error.",
            )
            return

        review_info = _fetch_review_summary(appid)
        player_count = _fetch_live_player_count(appid)

        # Xbox friends flavor, if FriendsDock has a cache
        friends_playing: Optional[List[str]] = None
        try:
            title = _guess_game_title(game or {})
            if title:
                friends_playing = _friends_playing_title(title)
        except Exception:
            friends_playing = None

        # Optional toast if we detect friends playing this now
        try:
            if friends_playing:
                # Show at most first three names in the toast to avoid giant strings
                names_preview = ", ".join(friends_playing[:3])
                if hasattr(window, "_show_toast"):
                    window._show_toast(
                        f"{names_preview} playing this now (Xbox friends cache).",
                        "info",
                    )
        except Exception:
            pass

        _show_game_info_dialog(
            window,
            appid,
            store_data,
            review_info=review_info,
            player_count=player_count,
            friends_playing=friends_playing,
        )

    act_info.triggered.connect(on_show_info)

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
