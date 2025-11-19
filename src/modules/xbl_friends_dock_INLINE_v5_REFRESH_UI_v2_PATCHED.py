
from __future__ import annotations


# === BEGIN XBL INLINE LOADER PATCH (no subprocess, works in one-file EXE) ===
import sys, os
from pathlib import Path
import importlib.util

def _exe_dir() -> Path:
    try:
        return Path(sys.executable).parent
    except Exception:
        return Path.cwd()

def _ensure_exe_dir_on_syspath():
    p = str(_exe_dir())
    if p not in sys.path:
        sys.path.insert(0, p)

def _load_helper_module_from_path(helper_path: Path):
    """Load a .py module from disk in-process (even when frozen)."""
    try:
        spec = importlib.util.spec_from_file_location("xbl_login_standalone_v3_dyn", str(helper_path))
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

def _run_xbl_helper_inline(parent=None) -> bool:
    """
    Order:
      1) ENV XBL_HELPER_DIR
      2) import from xbl package (with exe_dir on sys.path)
      3) load from file: exe_dir/xbl, _MEIPASS/xbl, cwd/xbl
    """
    helper_file = "xbl_login_standalone_v3.py"

    # 0) ENV override
    env_dir = os.environ.get("XBL_HELPER_DIR")
    if env_dir:
        hp = Path(env_dir) / helper_file
        if hp.exists():
            mod = _load_helper_module_from_path(hp)
            if mod and hasattr(mod, "main"):
                try: mod.main()
                except SystemExit: pass
                return True

    # 1) Import as package from sibling xbl/
    try:
        _ensure_exe_dir_on_syspath()
        from xbl import xbl_login_standalone_v3 as _m
        try: _m.main()
        except SystemExit: pass
        return True
    except Exception:
        pass

    # 2) Load from common locations
    candidates = [
        _exe_dir() / "xbl" / helper_file,              # next to EXE
        Path(getattr(sys, "_MEIPASS", _exe_dir())) / "xbl" / helper_file if getattr(sys, "frozen", False) else None,
        Path.cwd() / "xbl" / helper_file,
    ]
    for hp in [c for c in candidates if c]:
        if hp.exists():
            mod = _load_helper_module_from_path(hp)
            if mod and hasattr(mod, "main"):
                try: mod.main()
                except SystemExit: pass
                return True

    return False

# Back-compat: if old code calls the legacy helper runner name, route it here
try:
    _run_xbl_login_helper_from_xbl  # type: ignore[name-defined]
except Exception:
    def _run_xbl_login_helper_from_xbl(parent=None):  # legacy name
        return _run_xbl_helper_inline(parent)
# === END XBL INLINE LOADER PATCH ===

import os, sys, json, time, threading, datetime
from typing import Dict, List, Optional
from pathlib import Path

import requests
import subprocess
from PyQt6 import QtWidgets, QtCore

LOG_FILE = os.environ.get("XBL_LOG_FILE")

def _log(*a):
    s = "[xbl_friends_dock] " + " ".join(str(x) for x in a)
    print(s, flush=True)
    if LOG_FILE:
        try:
            Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now().isoformat()} {s}\n")
        except Exception:
            pass

# ---------- AUTH ----------
XBL_USER_AUTH = "https://user.auth.xboxlive.com/user/authenticate"
XBL_XSTS_AUTH = "https://xsts.auth.xboxlive.com/xsts/authorize"

def _strip_json_comments(s: str) -> str:
    out = []; i=0; in_str=False; esc=False
    while i < len(s):
        ch = s[i]
        if in_str:
            out.append(ch)
            if esc: esc=False
            elif ch == '\\\\': esc=True
            elif ch == '"': in_str=False
            i += 1; continue
        if ch == '"': in_str=True; out.append(ch); i += 1; continue
        if ch == '/' and i+1 < len(s) and s[i+1] in ('/','*'):
            if s[i+1] == '/':
                j = s.find('\\n', i+2); 
                if j == -1: break
                i = j + 1; continue
            else:
                j = s.find('*/', i+2)
                if j == -1: break
                i = j + 2; continue
        out.append(ch); i += 1
    return ''.join(out)

def _find_tokens_path() -> Optional[Path]:
    env = os.environ.get("XBL_TOKENS_PATH")
    if env and Path(env).exists(): return Path(env)
    here = Path(__file__).resolve().parent / "tokens.json"
    if here.exists(): return here
    cwd = Path(os.getcwd()) / "tokens.json"
    if cwd.exists(): return cwd
    local = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "OpenXbox" / "xbox" / "tokens.json"
    if local.exists(): return local
    return None

def _post_json(url: str, payload: dict) -> dict:
    r = requests.post(url, headers={"Content-Type":"application/json","Accept":"application/json","Accept-Language":"en-US"}, json=payload, timeout=20)
    _log("POST", url, "->", r.status_code)
    r.raise_for_status()
    return r.json()

def _build_auth_from_tokens(tokens_path: Path) -> Dict[str,str]:
    raw = tokens_path.read_text(encoding="utf-8", errors="ignore").strip()
    try:
        toks = json.loads(raw)
    except Exception:
        toks = json.loads(_strip_json_comments(raw))
    at = toks.get("access_token") or toks.get("AccessToken") or toks.get("token")
    if not at:
        raise RuntimeError("tokens.json missing access_token")
    # user token
    user_req = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={at}",
        },
    }
    j = _post_json(XBL_USER_AUTH, user_req)
    user_token = j["Token"]
    # xsts
    xsts_req = {
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL",
        },
    }
    j2 = _post_json(XBL_XSTS_AUTH, xsts_req)
    xsts = j2["Token"]
    uhs = j2["DisplayClaims"]["xui"][0]["uhs"]
    return {
        "Authorization": f"XBL3.0 x={uhs};{xsts}",
        "Accept": "application/json",
        "Accept-Language": "en-US",
    }

# ---------- Service helpers ----------
def _request_json(url: str, headers: Dict, versions=(6,5,4,3,2,1), method="GET", json=None, timeout=15):
    last_exc = None
    for ver in versions:
        h = dict(headers); h["x-xbl-contract-version"] = str(ver)
        try:
            if method == "GET":
                r = requests.get(url, headers=h, timeout=timeout)
            else:
                r = requests.post(url, headers=h, json=json, timeout=timeout)
            _log(f"{method} {url} v{ver} ->", r.status_code)
            if r.status_code in (400,404):
                continue
            if r.status_code == 429:
                time.sleep(0.5); continue
            r.raise_for_status()
            if r.content:
                try: return r.json()
                except Exception: return {}
            return {}
        except Exception as e:
            last_exc = e
    if last_exc: raise last_exc
    return {}

def _me_xuid(headers: Dict) -> Optional[str]:
    try:
        data = _request_json("https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag", headers, versions=(3,2,1))
        pu = (data.get("profileUsers") or [{}])[0]
        return str(pu.get("id") or "")
    except Exception as e:
        _log("xuid lookup failed:", repr(e)); return None

def _fetch_friends(headers: Dict) -> List[Dict]:
    urls = [
        "https://peoplehub.xboxlive.com/users/me/people/social",
        "https://peoplehub.xboxlive.com/users/me/people",
        "https://social.xboxlive.com/users/me/people",
    ]
    me = _me_xuid(headers)
    if me:
        urls.insert(0, f"https://peoplehub.xboxlive.com/users/xuid({me})/people/social")
        urls.insert(1, f"https://peoplehub.xboxlive.com/users/xuid({me})/people/social/summary")

    for url in urls:
        try:
            data = _request_json(url, headers, versions=(6,5,4,3,2,1))
            arr = data.get("people") or data.get("peopleList") or data.get("friends") or data.get("summary") or []
            out = []
            for p in arr or []:
                x = str(p.get("xuid") or p.get("xboxUserId") or p.get("id") or "")
                g = p.get("gamertag") or p.get("modernGamertag") or p.get("preferredName") or ""
                out.append({"xuid": x, "gamertag": g})
            if out:
                _log("friends from", url, "->", len(out))
                return out
        except Exception as e:
            _log("friends error for", url, ":", repr(e))
    return []

def _resolve_gamertags_batch(headers: Dict, xuids: List[str]) -> Dict[str,str]:
    if not xuids: return {}
    url = "https://profile.xboxlive.com/users/batch/profile/settings"
    payload = {"settings": ["Gamertag"], "userIds": [f"xuid({x})" for x in xuids]}
    try:
        data = _request_json(url, headers, versions=(3,2,1), method="POST", json=payload)
        m = {}
        for u in data.get("profileUsers", []):
            uid = str(u.get("id") or "")
            gt = ""
            for s in u.get("settings", []):
                if s.get("id") == "Gamertag":
                    gt = s.get("value") or ""
            if uid and gt: m[uid] = gt
        _log("resolved gamertags (batch):", len(m))
        return m
    except Exception as e:
        _log("resolve gt batch failed:", repr(e)); return {}

def _resolve_gamertags_slow(headers: Dict, xuids: List[str]) -> Dict[str,str]:
    out = {}
    for x in xuids:
        url = f"https://profile.xboxlive.com/users/xuid({x})/profile/settings?settings=Gamertag"
        try:
            data = _request_json(url, headers, versions=(3,2,1), method="GET")
            pu = (data.get("profileUsers") or [{}])[0]
            uid = str(pu.get("id") or "")
            gt = ""
            for s in pu.get("settings", []):
                if s.get("id") == "Gamertag": gt = s.get("value") or ""
            if uid and gt: out[uid] = gt
        except Exception as e:
            _log("resolve gt slow failed for", x, ":", repr(e))
        time.sleep(0.05)
    _log("resolved gamertags (slow):", len(out))
    return out

def _extract_title_from_presence(data: dict) -> str:
    for d in data.get("devices", []):
        for t in d.get("titles", []):
            name = t.get("name") or t.get("titleName") or ""
            act = t.get("activity") or {}
            if t.get("placement") == "Full" or act.get("richPresence") or act.get("broadcastTitle"):
                if name: return name
    return ""

def _presence_batch(headers: Dict, xuids: List[str]) -> Dict[str, Dict]:
    result = {}
    try:
        payload = {"users": [f"xuid({x})" for x in xuids], "level": "all"}
        data = _request_json("https://presence.xboxlive.com/users/batch", headers, versions=(3,2,1), method="POST", json=payload)
        users = data.get("responses") or data.get("users") or []
        for u in users:
            uid = u.get("id") or u.get("xuid") or ""
            if isinstance(uid, str) and uid.startswith("xuid("): uid = uid[5:-1]
            state = u.get("state") or u.get("presenceState") or ""
            title = _extract_title_from_presence(u)
            if uid: result[str(uid)] = {"state": state, "title": title}
        if result:
            _log("presence batch OK:", len(result))
            return result
    except Exception as e:
        _log("presence batch failed:", repr(e))
    return {}

def _presence_slow(headers: Dict, xuids: List[str], progress_cb=None) -> Dict[str, Dict]:
    result = {}
    for i, x in enumerate(xuids, 1):
        url = f"https://userpresence.xboxlive.com/users/xuid({x})?level=all"
        try:
            data = _request_json(url, headers, versions=(3,2,1), method="GET")
            state = data.get("state") or data.get("presenceState") or ""
            title = _extract_title_from_presence(data)
            result[str(x)] = {"state": state, "title": title}
            if progress_cb and (i % 10 == 0 or i == len(xuids)):
                progress_cb(i, len(xuids))
        except Exception as e:
            _log("presence slow failed for", x, ":", repr(e))
        time.sleep(0.045)
    _log("presence slow collected:", len(result))
    return result

# ---------- UI (filterable) ----------

class TransparencyDialog(QtWidgets.QDialog):
    def __init__(self, dock: QtWidgets.QWidget):
        super().__init__(dock)
        self._dock = dock
        self.setWindowTitle("Transparency")
        self.setModal(False)
        self.resize(320, 100)

        v = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.slider.setMinimum(20)   # 20% minimum to avoid disappearing
        self.slider.setMaximum(100)  # 100% = opaque
        # initialize from current window opacity
        current = int(round((dock.windowOpacity() or 1.0) * 100))
        current = max(self.slider.minimum(), min(self.slider.maximum(), current))
        self.slider.setValue(current)
        self._update_label(current)

        self.slider.valueChanged.connect(self._on_change)

        btn_row = QtWidgets.QHBoxLayout()
        self.btnReset = QtWidgets.QPushButton("Reset")
        self.btnClose = QtWidgets.QPushButton("Close")
        btn_row.addStretch(1)
        btn_row.addWidget(self.btnReset)
        btn_row.addWidget(self.btnClose)

        v.addWidget(self.label)
        v.addWidget(self.slider)
        v.addLayout(btn_row)

        self.btnReset.clicked.connect(self._reset)
        self.btnClose.clicked.connect(self.close)

    def _update_label(self, val: int):
        self.label.setText(f"Opacity: {val}%")

    def _on_change(self, val: int):
        try:
            self._dock.setWindowOpacity(val / 100.0)
            self._update_label(val)
            try:
                self._dock._save_settings(opacity_percent=int(val))
            except Exception as _e:
                _log("settings write warn:", repr(_e))
        except Exception as e:
            _log("opacity change error:", repr(e))

    def _reset(self):
        self.slider.setValue(100)
        try:
            self._dock._save_settings(opacity_percent=100)
        except Exception as _e:
            _log("settings write warn:", repr(_e))

class FriendsDock(QtWidgets.QDialog):

    # --- Cache helpers (ADD-ONLY) ---
    # --- Settings helpers (ADD-ONLY) ---
    def _settings_path(self) -> Path:
        try:
            return Path(__file__).resolve().parent / "friends_settings.json"
        except Exception:
            return Path("friends_settings.json")

    def _load_settings(self) -> dict:
        try:
            p = self._settings_path()
            if not p.exists():
                return {}
            raw = p.read_text(encoding="utf-8", errors="ignore")
            return json.loads(raw) if raw.strip() else {}
        except Exception as e:
            _log("settings load error:", repr(e))
            return {}

    def _save_settings(self, **updates):
        try:
            data = self._load_settings()
            data.update(updates)
            self._settings_path().write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
            _log("settings saved:", updates)
        except Exception as e:
            _log("settings save error:", repr(e))
    # --- end settings helpers ---

    def _cache_path(self) -> Path:
        try:
            return Path(__file__).resolve().parent / "friends_cache.json"
        except Exception:
            return Path("friends_cache.json")

    def _save_cached_rows(self, rows):
        try:
            data = [{"gamertag": gt, "status": st, "game": gm} for (gt, st, gm) in (rows or [])]
            self._cache_path().write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
            _log("cache saved:", str(self._cache_path()), len(data), "rows")
        except Exception as e:
            _log("cache save error:", repr(e))

    def _load_cached_rows(self):
        try:
            p = self._cache_path()
            if not p.exists():
                return False
            raw = p.read_text(encoding="utf-8", errors="ignore")
            arr = json.loads(raw) if raw.strip() else []
            rows = [(d.get("gamertag",""), d.get("status",""), d.get("game","")) for d in arr]
            if rows:
                self.sig_set_rows.emit(rows)
                self.sig_set_status.emit(f"Restored {len(rows)} cached friends")
                _log("cache restored:", len(rows), "rows")
                return True
            return False
        except Exception as e:
            _log("cache load error:", repr(e))
            return False
    # --- end cache helpers ---

    sig_set_status = QtCore.pyqtSignal(str)
    sig_set_rows = QtCore.pyqtSignal(list)   # list of (gt, status, game)
    sig_enable_btn = QtCore.pyqtSignal(bool)
    sig_busy = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xbox Friends")
        self.resize(720, 740)
        # Enable minimize button on title bar
        try:
            self.setWindowFlags(self.windowFlags() |
                                QtCore.Qt.WindowType.WindowMinimizeButtonHint |
                                QtCore.Qt.WindowType.WindowSystemMenuHint)
        except Exception as _e:
            _log("minimize flag warn:", repr(_e))
        self._full_rows: List[tuple] = []

        v = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.lbl = QtWidgets.QLabel("Ready.")
        self.view = QtWidgets.QComboBox()
        self.view.addItems(["All (Online first)", "Online only"])
        self.btn = QtWidgets.QPushButton("Refresh")
        top.addWidget(self.lbl); top.addStretch(1); top.addWidget(QtWidgets.QLabel("View:")); top.addWidget(self.view)
        # "Always on top" toggle (ADD-ONLY)
        self.chkAlwaysOnTop = QtWidgets.QCheckBox("Always on top")
        top.addWidget(self.chkAlwaysOnTop)
        # Busy spinner (indeterminate) — hidden by default
        self._busy = QtWidgets.QProgressBar(self)
        self._busy.setRange(0, 0)
        self._busy.setTextVisible(False)
        self._busy.setFixedWidth(80)
        self._busy.hide()
        top.insertWidget(1, self._busy)
        # Auto-refresh timer (1 minute; OFF by default)
        self._autoRefreshTimer = QtCore.QTimer(self)
        self._autoRefreshTimer.setInterval(60_000)
        self._autoRefreshTimer.timeout.connect(self.refresh)
        self.btnAuth = QtWidgets.QPushButton("Sign in / Choose tokens.json")
        self.btnRefreshTokenOnly = QtWidgets.QPushButton("Refresh token only")
        top.addWidget(self.btnAuth); top.addWidget(self.btnRefreshTokenOnly); top.addWidget(self.btn)

        # ---- Settings dropdown (cosmetic only) ----
        # ---- Settings dropdown (cosmetic only) ----
        self.btnSettings = QtWidgets.QToolButton()
        self.btnSettings.setText("Settings")
        self.btnSettings.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        _menu = QtWidgets.QMenu(self.btnSettings)
        _a_refresh = _menu.addAction("Refresh"); _a_refresh.triggered.connect(self.refresh)
        _a_signin  = _menu.addAction("Sign in / Choose tokens.json"); _a_signin.triggered.connect(self._do_auth)
        _a_rtonly  = _menu.addAction("Refresh token only"); _a_rtonly.triggered.connect(self._refresh_token_only)
        _a_transp  = _menu.addAction("Transparency…"); _a_transp.triggered.connect(self._open_transparency)
        self._autoAction = _menu.addAction("Auto Refresh (1 minute)")
        self._autoAction.setCheckable(True)
        self._autoAction.setChecked(False)
        self._autoAction.triggered.connect(self._toggle_auto_refresh)
        self.btnSettings.setMenu(_menu)
        top.addWidget(self.btnSettings)
        try:
            self.btn.hide(); self.btnAuth.hide(); self.btnRefreshTokenOnly.hide()
        except Exception:
            pass
        # ---- end Settings dropdown ----

        # Hide original buttons (objects remain; signals intact)
        try:
            self.btn.hide()
            self.btnAuth.hide()
            self.btnRefreshTokenOnly.hide()
        except Exception as _e:
            _log("hide-buttons warning:", repr(_e))
        # ---- end Settings dropdown ----

        v.addLayout(top)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Gamertag", "Status", "Game"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        v.addWidget(self.table, 1)

        self.btn.clicked.connect(self.refresh)
        self.btnAuth.clicked.connect(self._do_auth)
        self.btnRefreshTokenOnly.clicked.connect(self._refresh_token_only)
        self.view.currentIndexChanged.connect(self._reapply_filter)
        self.view.currentIndexChanged.connect(lambda _i: self._save_settings(view_index=int(_i)))
        self.chkAlwaysOnTop.toggled.connect(self._apply_always_on_top)

        self.sig_set_status.connect(self._set_status)
        self.sig_set_rows.connect(self._receive_full_rows)
        self.sig_enable_btn.connect(self.btn.setEnabled)
        self.sig_busy.connect(self._busy.setVisible)

        # Load and apply persistent settings (opacity, auto-refresh)
        try:
            _s = self._load_settings()
            # Apply opacity
            _op = int(_s.get("opacity_percent", 100))
            _op = max(20, min(100, _op))
            self.setWindowOpacity(_op / 100.0)
            # Apply auto-refresh state
            _auto = bool(_s.get("auto_refresh", False))
            if hasattr(self, "_autoAction"):
                self._autoAction.setChecked(_auto)
            if _auto:
                self._autoRefreshTimer.start()
            # Apply view filter index
            try:
                _vi = int(_s.get("view_index", 0))
                if 0 <= _vi < self.view.count():
                    self.view.setCurrentIndex(_vi)
            except Exception:
                pass
            # Apply 'Always on top'
            _aot = bool(_s.get("always_on_top", False))
            if hasattr(self, 'chkAlwaysOnTop'):
                self.chkAlwaysOnTop.setChecked(_aot)
            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, _aot)
            self.show()
        except Exception as _e:
            _log("apply settings warn:", repr(_e))

        # Show cached rows immediately (if available) before first refresh
        try:
            _had_cache = self._load_cached_rows()
        except Exception as _e:
            _had_cache = False
            _log("warm restore warn:", repr(_e))
        if not _had_cache:
            QtCore.QTimer.singleShot(150, self.refresh)

    def _set_status(self, s: str):
        self.lbl.setText(s); _log("status:", s)

    def _receive_full_rows(self, rows: List[tuple]):
        # rows already have "Online first" order
        self._full_rows = rows
        self._reapply_filter()

    def _reapply_filter(self):
        rows = self._full_rows
        if self.view.currentIndex() == 1:  # Online only
            rows = [r for r in rows if r[1] == "Online"]
        self._apply_rows(rows)


    # --- Status LED helpers (ADD-ONLY) ---
    def _build_led_icon(self, color: QtCore.Qt.GlobalColor) -> QtWidgets.QStyle.StandardPixmap | QtWidgets.QStyle:
        # Create a small circular pixmap to act as an LED
        pm = QtGui.QPixmap(14, 14)
        pm.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pm)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        brush = QtGui.QBrush(color)
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, 12, 12)
        painter.end()
        return QtGui.QIcon(pm)

    def _icon_for_state(self, st: str) -> QtGui.QIcon:
        try:
            if not hasattr(self, "_led_green"):
                self._led_green = self._build_led_icon(QtCore.Qt.GlobalColor.green)
                self._led_red   = self._build_led_icon(QtCore.Qt.GlobalColor.red)
                self._led_blank = self._build_led_icon(QtCore.Qt.GlobalColor.gray)
        except Exception:
            pass
        s = (st or "").strip().lower()
        if s == "online":
            return getattr(self, "_led_green", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogApplyButton))
        elif s == "offline":
            return getattr(self, "_led_red", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogCancelButton))
        return getattr(self, "_led_blank", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation))
    # --- end Status LED helpers ---

    def _apply_rows(self, rows: List[tuple]):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for i,(gt,st,gm) in enumerate(rows):
            # Gamertag text
            self.table.setItem(i,0, QtWidgets.QTableWidgetItem(gt))
            # Status LED (icon only)
            _status_item = QtWidgets.QTableWidgetItem("")
            try:
                _status_item.setIcon(self._icon_for_state(st))
                _status_item.setText("")  # no text, icon only
                _status_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            except Exception:
                _status_item.setText(st)
            self.table.setItem(i,1, _status_item)
            # Game text
            self.table.setItem(i,2, QtWidgets.QTableWidgetItem(gm))
        self.table.setSortingEnabled(True)
        # Keep consistent order: Online first (already), within that alphabetically
        self.table.sortItems(1, QtCore.Qt.SortOrder.AscendingOrder)


    def _apply_always_on_top(self, checked: bool):
        try:
            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, bool(checked))
            self.show()  # re-apply flags
            try:
                self._save_settings(always_on_top=bool(checked))
            except Exception as _e:
                _log("settings write warn:", repr(_e))
        except Exception as e:
            _log("always on top apply error:", repr(e))

    def _open_transparency(self):
        try:
            if not hasattr(self, "_transparencyDlg") or self._transparencyDlg is None:
                self._transparencyDlg = TransparencyDialog(self)
            self._transparencyDlg.show()
            self._transparencyDlg.raise_()
            self._transparencyDlg.activateWindow()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Transparency error: {e}")

    def _refresh_token_only(self):
        """
        Run xbl_login_standalone_v3.py to refresh tokens, then prompt where the new token was saved.
        """
        try:
            self.sig_enable_btn.emit(False)
            self.sig_set_status.emit("Refreshing token via login helper...")

            base = Path(__file__).resolve().parent
            helper = base / "xbl_login_standalone_v3.py"
            if not helper.exists():
                QtWidgets.QMessageBox.critical(self, "Missing helper", "xbl_login_standalone_v3.py not found next to this script.")
                self.sig_enable_btn.emit(True)
                return

            proc = subprocess.run([sys.executable, str(helper)], cwd=str(base), capture_output=True, text=True)
            out = (proc.stdout or "") + "\n" + (proc.stderr or "")
            if proc.returncode != 0:
                QtWidgets.QMessageBox.critical(self, "Refresh failed", f"Helper exited with {proc.returncode}.\n\nOutput (tail):\n{out[-2000:]}")
                self.sig_enable_btn.emit(True)
                return

            # Parse output to find the saved tokens file
            tokens_path = None
            for line in out.splitlines():
                s = line.strip()
                if s.startswith("[Info] Tokens file:"):
                    tokens_path = s.split(":", 1)[1].strip()
                    break
            if not tokens_path:
                # Fallback to typical default
                tokens_path = str(Path(os.environ.get("LOCALAPPDATA", Path.home())) / "OpenXbox" / "xbox" / "tokens.json")

            # Prompt user where it was saved and offer to use it now
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setWindowTitle("Token refreshed")
            msg.setText(f"New tokens were saved here:\n{tokens_path}\n\nUse this tokens.json now?")
            yes_btn = msg.addButton("Use now", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
            no_btn = msg.addButton("Cancel", QtWidgets.QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            if msg.clickedButton() is yes_btn:
                os.environ["XBL_TOKENS_PATH"] = tokens_path
                self.sig_set_status.emit("Using refreshed tokens. Reloading…")
                QtCore.QTimer.singleShot(200, self.refresh)
            else:
                self.sig_enable_btn.emit(True)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            self.sig_enable_btn.emit(True)

    def _do_auth(self):
        """
        Opens a small chooser:
        - Use existing tokens.json (browse & load)
        - Run device sign-in helper to create a new tokens.json
        """
        try:
            default_path = os.environ.get("XBL_TOKENS_PATH") or str((Path.cwd() / "tokens.json"))
            # Simple chooser via QMessageBox-style buttons
            dlg = QtWidgets.QMessageBox(self)
            dlg.setIcon(QtWidgets.QMessageBox.Icon.Question)
            dlg.setWindowTitle("Xbox sign-in / tokens.json")
            dlg.setText("How would you like to provide tokens?")
            use_existing = dlg.addButton("Use existing tokens.json…", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
            run_helper  = dlg.addButton("Run device sign-in…", QtWidgets.QMessageBox.ButtonRole.ActionRole)
            cancel_btn  = dlg.addButton("Cancel", QtWidgets.QMessageBox.ButtonRole.RejectRole)
            # PyQt6: exec()
            dlg.exec()
            clicked = dlg.clickedButton()
            if clicked is cancel_btn:
                return

            if clicked is use_existing:
                path, _ = QtWidgets.QFileDialog.getOpenFileName(
                    self, "Select tokens.json", default_path, "JSON Files (*.json);;All Files (*)"
                )
                if not path:
                    return
                # point the app to this file and refresh
                os.environ["XBL_TOKENS_PATH"] = path
                self.sig_set_status.emit("Using selected tokens.json. Reloading…")
                QtCore.QTimer.singleShot(200, self.refresh)
                return

            # Otherwise run helper to produce a new tokens.json
            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save tokens.json", default_path, "JSON Files (*.json);;All Files (*)"
            )
            if not save_path:
                return

            self.sig_enable_btn.emit(False)
            self.sig_set_status.emit("Starting device sign-in… follow the console/device code flow")

            base = Path(__file__).resolve().parent
            helper = None
            for name in ["xbl_auth_device_any.py", "xbl_login_standalone_v3.py", "xbl_signin_from_oauth_tokens.py"]:
                cand = base / name
                if cand.exists():
                    helper = str(cand)
                    break
            if helper is None:
                QtWidgets.QMessageBox.critical(
                    self, "Missing helper",
                    "Could not find a sign-in helper (xbl_auth_device_any.py or xbl_login_standalone_v3.py)."
                )
                self.sig_enable_btn.emit(True)
                return

            import subprocess, sys
            proc = subprocess.run([sys.executable, helper, "--out", save_path], cwd=str(base))
            if proc.returncode != 0:
                QtWidgets.QMessageBox.critical(self, "Sign-in failed", f"Auth helper exited with code {proc.returncode}.")
                self.sig_enable_btn.emit(True)
                return

            os.environ["XBL_TOKENS_PATH"] = save_path
            self.sig_set_status.emit("Token saved. Reloading…")
            QtCore.QTimer.singleShot(200, self.refresh)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            self.sig_enable_btn.emit(True)


    def _toggle_auto_refresh(self):
        try:
            if self._autoRefreshTimer.isActive():
                self._autoRefreshTimer.stop()
                if hasattr(self, '_autoAction') and self._autoAction:
                    self._autoAction.setChecked(False)
                self.sig_set_status.emit("Auto Refresh: OFF")
                try:
                    self._save_settings(auto_refresh=False)
                except Exception as _e:
                    _log("settings write warn:", repr(_e))
            else:
                self._autoRefreshTimer.start()
                if hasattr(self, '_autoAction') and self._autoAction:
                    self._autoAction.setChecked(True)
                self.sig_set_status.emit("Auto Refresh: ON (every 1 min)")
                try:
                    self._save_settings(auto_refresh=True)
                except Exception as _e:
                    _log("settings write warn:", repr(_e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Auto Refresh Error", str(e))

    def refresh(self):
        self.sig_enable_btn.emit(False); self.sig_set_status.emit(""); self.sig_busy.emit(True); self.sig_set_rows.emit([])

        def _run():
            try:
                # ----- auth
                tpath = _find_tokens_path()
                if not tpath:
                    raise RuntimeError("tokens.json not found. Set XBL_TOKENS_PATH or place tokens.json next to the script.")
                _log("Using tokens.json at:", str(tpath))
                headers = _build_auth_from_tokens(tpath)

                # ----- friends list
                friends = _fetch_friends(headers)
                if not friends:
                    raise RuntimeError("No friends returned (service/permissions).")

                self.sig_set_status.emit(f"{len(friends)} friends (resolving names...)")

                # ----- gamertags
                missing = [f["xuid"] for f in friends if f.get("xuid") and not f.get("gamertag")]
                gmap = _resolve_gamertags_batch(headers, missing) if missing else {}
                if missing and len(gmap) < len(missing):
                    slow_needed = [x for x in missing if x not in gmap]
                    if slow_needed:
                        gmap.update(_resolve_gamertags_slow(headers, slow_needed))
                for f in friends:
                    if not f.get("gamertag"):
                        f["gamertag"] = gmap.get(f.get("xuid",""), f.get("xuid",""))

                self.sig_set_status.emit(f"{len(friends)} friends (loading presence...)")

                # ----- presence
                xuids = [f["xuid"] for f in friends if f.get("xuid")]
                pres = _presence_batch(headers, xuids) if xuids else {}
                if xuids and len(pres) < len(xuids):
                    def _progress(i, n):
                        self.sig_set_status.emit(f"{len(friends)} friends (presence {i}/{n})")
                    pres.update(_presence_fast(headers, [x for x in xuids if x not in pres], _progress, workers=24))

                rows = []
                for f in friends:
                    x = f.get("xuid",""); gt = f.get("gamertag") or x
                    p = pres.get(x, {})
                    state = "Online" if str(p.get("state","")).lower()=="online" else ("Offline" if p else "")
                    title = p.get("title","")
                    rows.append((gt, state, title))
                rows.sort(key=lambda r: (r[1]!="Online", r[0].lower()))

                self.sig_set_rows.emit(rows)
                try:
                    self._save_cached_rows(rows)
                except Exception as _e:
                    _log("cache post-refresh warn:", repr(_e))
                self.sig_set_status.emit(f"{len(rows)} friends (presence applied)")
                self.sig_busy.emit(False)
                self.sig_enable_btn.emit(True)

            except Exception as e:
                _log("Error:", repr(e))
                self.sig_set_status.emit(f"Error: {e.__class__.__name__}: {e}")
                self.sig_busy.emit(False)
                self.sig_enable_btn.emit(True)

        threading.Thread(target=_run, daemon=True).start()
def _presence_fast(headers: Dict, xuids: List[str], progress_cb=None, workers: int = 24) -> Dict[str, Dict]:
    """Concurrent presence fetch using a shared Session. Keeps requests gentle but parallel."""
    import concurrent.futures, time, math
    result = {}
    if not xuids:
        return result

    # Shared session with connection pool
    sess = requests.Session()
    try:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        adapter = HTTPAdapter(pool_connections=workers*2, pool_maxsize=workers*2, max_retries=0)
        sess.mount("https://", adapter); sess.mount("http://", adapter)
    except Exception:
        pass

    base_headers = dict(headers)
    base_headers["x-xbl-contract-version"] = "3"
    url_tpl = "https://userpresence.xboxlive.com/users/xuid({})?level=all"

    # Gentle concurrency: cap workers, backoff on 429, shorter timeout
    def fetch_one(xuid: str):
        url = url_tpl.format(xuid)
        tries = 0
        delay = 0.3
        while True:
            tries += 1
            try:
                r = sess.get(url, headers=base_headers, timeout=8)
                status = r.status_code
                if status == 429:
                    # Too many requests; back off a bit and retry
                    time.sleep(delay)
                    delay = min(delay * 1.6, 3.0)
                    if tries < 5:
                        continue
                if status in (400, 404):
                    return xuid, {}
                r.raise_for_status()
                j = r.json() if r.content else {}
                state = j.get("state") or j.get("presenceState") or ""
                title = _extract_title_from_presence(j)
                return xuid, {"state": state, "title": title}
            except Exception:
                if tries < 3:
                    time.sleep(delay)
                    delay = min(delay * 1.6, 3.0)
                    continue
                return xuid, {}

    done = 0
    report_every = max(10, len(xuids)//15)  # ~15 updates max
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 48))) as ex:
        for xuid, info in ex.map(fetch_one, xuids):
            done += 1
            if info:
                result[str(xuid)] = info
            if progress_cb and (done % report_every == 0 or done == len(xuids)):
                progress_cb(done, len(xuids))

    _log("presence fast collected:", len(result))
    try:
        sess.close()
    except Exception:
        pass
    return result


def main():
    _log("Starting Xbox Friends Dock (INLINE v5)")
    app = QtWidgets.QApplication(sys.argv)
    w = FriendsDock(); w.show()
    rc = app.exec()
    _log("App exit code:", rc); sys.exit(rc)

if __name__ == "__main__":
    main()