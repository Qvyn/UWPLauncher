
from __future__ import annotations
import sys, os, threading, time
from pathlib import Path
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs, quote
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QPixmap
import requests

_HEADERS_INJECTED = None

def set_global_xbl_headers(h):
    global _HEADERS_INJECTED
    _HEADERS_INJECTED = h

def _possible_token_paths():
    paths = []
    env = os.environ.get("XBL_TOKENS_PATH")
    if env:
        paths.append(Path(env))
    paths.append(Path(os.getcwd()) / "tokens.json")
    try:
        here = Path(__file__).resolve().parent
        paths.append(here / "tokens.json")
    except Exception as e:
        # tokens.json next to this module is optional; log and continue.
        print(f"[xbl_profile_widget] optional tokens.json near module not usable: {e}")
    local = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "OpenXbox" / "xbox" / "tokens.json"
    paths.append(local)
    return paths

def _read_headers_from_tokens():
    from xbl_signin_from_oauth_tokens import get_xsts_from_tokens
    last_err = None
    for p in _possible_token_paths():
        try:
            if p.is_file():
                print(f"[xbl_profile_widget] using tokens.json at: {p}")
                info = get_xsts_from_tokens(str(p))
                h = {"Authorization": info["Authorization"], "x-xbl-contract-version": "3", "Accept": "application/json"}
                return h
        except Exception as e:
            last_err = e
            print(f"[xbl_profile_widget] failed tokens at {p}: {e}")
    if last_err:
        raise last_err
    raise FileNotFoundError("tokens.json not found in any known location.")

def _get_headers():
    if _HEADERS_INJECTED:
        h = dict(_HEADERS_INJECTED)
        h.setdefault("Accept", "application/json")
        h.setdefault("x-xbl-contract-version", "3")
        return h
    try:
        return _read_headers_from_tokens()
    except Exception as e:
        print("[xbl_profile_widget] header load error:", e)
        return None

def _fetch_profile(headers):
    url = "https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag,GameDisplayPicRaw"
    print("[xbl_profile_widget] GET profile:", url)
    r = requests.get(url, headers=headers, timeout=8)
    print("[xbl_profile_widget] profile status:", r.status_code)
    r.raise_for_status()
    data = r.json()
    user = (data.get("profileUsers") or [None])[0] or {}
    settings = {s.get("id"): s.get("value") for s in user.get("settings", [])}
    return settings.get("Gamertag") or "(unknown)", settings.get("GameDisplayPicRaw")

def _avatar_variants(u: str):
    variants = []
    try:
        parsed = urlparse(u)
        q = parse_qs(parsed.query)
        inner = q.get("url", [""])[0]
        if inner and ("%2F" not in inner and "://" in inner):
            inner = quote(inner, safe="")
        base_q = {"url": inner} if inner else {}
        size_opts = [
            {"w": "64", "h": "64", "format": "png"},
            {"w": "128", "h": "128", "format": "png"},
            {"w": "208", "h": "208", "format": "png"},
        ]
        hosts = ["images-eds-ssl.xboxlive.com", "images-eds.xboxlive.com"]
        for h in hosts:
            for so in size_opts:
                qd = dict(base_q); qd.update(so)
                new = parsed._replace(scheme="https", netloc=h, query=urlencode(qd, doseq=True), path="/image")
                variants.append(urlunparse(new))
        variants.append(u)
    except Exception:
        variants.append(u)
    seen = set(); out = []
    for v in variants:
        if v not in seen:
            out.append(v); seen.add(v)
    return out

def _download_avatar(url: str, timeout: int = 8) -> QPixmap | None:
    ua = {"User-Agent": "Mozilla/5.0", "Accept": "image/*"}
    variants = _avatar_variants(url)
    last_err = None
    for i, v in enumerate(variants, 1):
        try:
            print(f"[xbl_profile_widget] avatar try {i}/{len(variants)}:", v)
            r = requests.get(v, headers=ua, timeout=8, allow_redirects=True)
            print("[xbl_profile_widget] avatar status:", r.status_code, "len:", len(r.content))
            r.raise_for_status()
            if not r.content:
                raise RuntimeError("empty image")
            pm = QPixmap()
            if pm.loadFromData(r.content):
                return pm
            last_err = RuntimeError("QPixmap load failed")
        except Exception as e:
            last_err = e
            print(f"[xbl_profile_widget] avatar error:", e)
            time.sleep(0.1 if i < len(variants) else 0)
    if last_err:
        print(f"[xbl_profile_widget] avatar failed: {last_err}")
    return None

class XboxProfileWidget(QtWidgets.QWidget):
    profileReady = QtCore.pyqtSignal(str)     # gamertag
    profileError = QtCore.pyqtSignal()
    avatarReady  = QtCore.pyqtSignal(object)  # QPixmap

    def __init__(self, parent=None):
        super().__init__(parent)
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0,0,0,0)
        self.lbl_avatar = QtWidgets.QLabel()
        self.lbl_avatar.setFixedSize(48, 48)
        self.lbl_avatar.setStyleSheet("border-radius:10px;background:#222;")
        self.lbl_name = QtWidgets.QLabel("<i>Not signed in</i>")
        self.lbl_name.setMinimumWidth(160)
        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        row.addWidget(self.lbl_avatar)
        row.addSpacing(8)
        row.addWidget(self.lbl_name)
        row.addStretch(1)
        row.addWidget(self.btn_refresh)

        self._refreshing = False
        self.btn_refresh.clicked.connect(self.refresh)

        # Connect signals to UI slots (runs on main thread)
        self.profileReady.connect(self._on_profile_ready)
        self.profileError.connect(self._on_profile_error)
        self.avatarReady.connect(self._on_avatar_ready)

        QtCore.QTimer.singleShot(0, self.refresh)

    def set_headers(self, headers: dict | None):
        set_global_xbl_headers(headers)

    @QtCore.pyqtSlot(str)
    def _on_profile_ready(self, gamertag: str):
        self.lbl_name.setText(gamertag)
        self._refreshing = False

    @QtCore.pyqtSlot()
    def _on_profile_error(self):
        self.lbl_name.setText("Profile error")
        self._refreshing = False

    @QtCore.pyqtSlot(object)
    def _on_avatar_ready(self, pm: QPixmap):
        scaled = pm.scaled(48, 48, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.lbl_avatar.setPixmap(scaled)

    def refresh(self):
        if self._refreshing:
            return
        self._refreshing = True
        self.lbl_name.setText("Fetching...")

        def run_profile():
            headers = _get_headers()
            if not headers:
                self.profileError.emit()
                return
            try:
                gt, pic = _fetch_profile(headers)
                self.profileReady.emit(gt)  # emit immediately (no timer races)
                if pic:
                    def run_avatar():
                        pm = _download_avatar(pic, timeout=8)
                        if pm:
                            self.avatarReady.emit(pm)
                    threading.Thread(target=run_avatar, daemon=True).start()
            except Exception as e:
                print("[xbl_profile_widget] profile fetch error:", e)
                self.profileError.emit()
        threading.Thread(target=run_profile, daemon=True).start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Xbox Profile")
    lay = QtWidgets.QVBoxLayout(w)
    lay.setContentsMargins(12,12,12,12)
    lay.addWidget(XboxProfileWidget())
    w.resize(320, 80)
    w.show()
    sys.exit(app.exec())
