
# === UWPLauncher_MONO.py (safe-embedded) ===
# Single-file bundle generated from your originals without changing flow.
# It registers each helper module in sys.modules under its original name,
# then executes the main script at top-level.
import sys, types

# Optional: faux "xbl" package so imports like "from xbl import ..." work
if "xbl" not in sys.modules:
    xbl_pkg = types.ModuleType("xbl")
    xbl_pkg.__path__ = []
    sys.modules["xbl"] = xbl_pkg

def _register_module(name: str, code: str, virtual_file: str):
    mod = types.ModuleType(name)
    mod.__file__ = virtual_file
    sys.modules[name] = mod
    exec(compile(code, virtual_file, "exec"), mod.__dict__)
    return mod

# PyQt5 -> PyQt6 shim if only PyQt6 is available
try:
    import PyQt6.QtWidgets as _Q6W
    import PyQt6.QtCore as _Q6C
    import PyQt6.QtGui as _Q6G
    _pyqt5 = types.ModuleType("PyQt5")
    _pyqt5.QtWidgets = _Q6W
    _pyqt5.QtCore = _Q6C
    _pyqt5.QtGui = _Q6G
    sys.modules.setdefault("PyQt5", _pyqt5)
    sys.modules.setdefault("PyQt5.QtWidgets", _Q6W)
    sys.modules.setdefault("PyQt5.QtCore", _Q6C)
    sys.modules.setdefault("PyQt5.QtGui", _Q6G)
except Exception:
    pass

# === Registered helper modules ===
_register_module("xbl_auth_device_any", "\nimport argparse, json, sys, time\n\nCANDIDATE_CLIENT_IDS = [\n    \"00000000402B5328\",  # Xbox app (commonly used for MSA device flow)\n    \"000000004C12AE6F\",  # Alternate public Xbox client id\n]\n\ndef run_device_flow(client_id: str, out_path: str) -> bool:\n    try:\n        import msal\n    except ImportError:\n        print(\"This script requires 'msal'. Install with:  py -m pip install msal\", flush=True)\n        return False\n    app = msal.PublicClientApplication(client_id, authority=\"https://login.microsoftonline.com/consumers\")\n    # IMPORTANT: Do NOT include reserved scopes (openid, profile, offline_access)\n    scopes = [\"XboxLive.signin\"]\n    flow = app.initiate_device_flow(scopes=scopes)\n    if \"user_code\" not in flow:\n        return False\n    print(\"\\n=== Microsoft Sign-in ===\")\n    print(\"Go to:\", flow[\"verification_uri\"])\n    print(\"Enter code:\", flow[\"user_code\"])\n    print(\"Then return here; this window will finish automatically.\\n\")\n    result = app.acquire_token_by_device_flow(flow)\n    if \"access_token\" not in result:\n        print(\"Sign-in failed:\", result, file=sys.stderr)\n        return False\n    data = {\n        \"access_token\": result[\"access_token\"],\n        \"refresh_token\": result.get(\"refresh_token\",\"\"),\n        \"expires_at\": int(time.time()) + int(result.get(\"expires_in\", 28800)),\n        \"obtained_at\": int(time.time()),\n        \"token_type\": result.get(\"token_type\",\"Bearer\"),\n        \"scope\": result.get(\"scope\",\"XboxLive.signin\"),\n        \"client_id\": client_id,\n    }\n    with open(out_path, \"w\", encoding=\"utf-8\") as f:\n        json.dump(data, f, indent=2)\n    print(f\"Wrote fresh tokens to: {out_path} (client_id={client_id})\")\n    return True\n\ndef main():\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--out\", default=\"tokens.json\", help=\"Where to write tokens.json\")\n    args = ap.parse_args()\n    for cid in CANDIDATE_CLIENT_IDS:\n        ok = run_device_flow(cid, args.out)\n        if ok:\n            return\n        else:\n            print(f\"Client {cid} failed, trying next\u2026\")\n    print(\"All client IDs failed. Ensure you are on a Microsoft Account (MSA) and try again.\", file=sys.stderr)\n    sys.exit(2)\n\nif __name__ == \"__main__\":\n    main()\n", "xbl_auth_device_any.py")
_register_module("xbl.xbl_auth_device_any", "\nimport argparse, json, sys, time\n\nCANDIDATE_CLIENT_IDS = [\n    \"00000000402B5328\",  # Xbox app (commonly used for MSA device flow)\n    \"000000004C12AE6F\",  # Alternate public Xbox client id\n]\n\ndef run_device_flow(client_id: str, out_path: str) -> bool:\n    try:\n        import msal\n    except ImportError:\n        print(\"This script requires 'msal'. Install with:  py -m pip install msal\", flush=True)\n        return False\n    app = msal.PublicClientApplication(client_id, authority=\"https://login.microsoftonline.com/consumers\")\n    # IMPORTANT: Do NOT include reserved scopes (openid, profile, offline_access)\n    scopes = [\"XboxLive.signin\"]\n    flow = app.initiate_device_flow(scopes=scopes)\n    if \"user_code\" not in flow:\n        return False\n    print(\"\\n=== Microsoft Sign-in ===\")\n    print(\"Go to:\", flow[\"verification_uri\"])\n    print(\"Enter code:\", flow[\"user_code\"])\n    print(\"Then return here; this window will finish automatically.\\n\")\n    result = app.acquire_token_by_device_flow(flow)\n    if \"access_token\" not in result:\n        print(\"Sign-in failed:\", result, file=sys.stderr)\n        return False\n    data = {\n        \"access_token\": result[\"access_token\"],\n        \"refresh_token\": result.get(\"refresh_token\",\"\"),\n        \"expires_at\": int(time.time()) + int(result.get(\"expires_in\", 28800)),\n        \"obtained_at\": int(time.time()),\n        \"token_type\": result.get(\"token_type\",\"Bearer\"),\n        \"scope\": result.get(\"scope\",\"XboxLive.signin\"),\n        \"client_id\": client_id,\n    }\n    with open(out_path, \"w\", encoding=\"utf-8\") as f:\n        json.dump(data, f, indent=2)\n    print(f\"Wrote fresh tokens to: {out_path} (client_id={client_id})\")\n    return True\n\ndef main():\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--out\", default=\"tokens.json\", help=\"Where to write tokens.json\")\n    args = ap.parse_args()\n    for cid in CANDIDATE_CLIENT_IDS:\n        ok = run_device_flow(cid, args.out)\n        if ok:\n            return\n        else:\n            print(f\"Client {cid} failed, trying next\u2026\")\n    print(\"All client IDs failed. Ensure you are on a Microsoft Account (MSA) and try again.\", file=sys.stderr)\n    sys.exit(2)\n\nif __name__ == \"__main__\":\n    main()\n", "xbl/xbl_auth_device_any.py")
_register_module("xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED", "\nfrom __future__ import annotations\n\n\n# === BEGIN XBL INLINE LOADER PATCH (no subprocess, works in one-file EXE) ===\nimport sys, os\nfrom pathlib import Path\nimport importlib.util\n\ndef _exe_dir() -> Path:\n    try:\n        return Path(sys.executable).parent\n    except Exception:\n        return Path.cwd()\n\ndef _ensure_exe_dir_on_syspath():\n    p = str(_exe_dir())\n    if p not in sys.path:\n        sys.path.insert(0, p)\n\ndef _load_helper_module_from_path(helper_path: Path):\n    \"\"\"Load a .py module from disk in-process (even when frozen).\"\"\"\n    try:\n        spec = importlib.util.spec_from_file_location(\"xbl_login_standalone_v3_dyn\", str(helper_path))\n        if not spec or not spec.loader:\n            return None\n        mod = importlib.util.module_from_spec(spec)\n        spec.loader.exec_module(mod)\n        return mod\n    except Exception:\n        return None\n\ndef _run_xbl_helper_inline(parent=None) -> bool:\n    \"\"\"\n    Order:\n      1) ENV XBL_HELPER_DIR\n      2) import from xbl package (with exe_dir on sys.path)\n      3) load from file: exe_dir/xbl, _MEIPASS/xbl, cwd/xbl\n    \"\"\"\n    helper_file = \"xbl_login_standalone_v3.py\"\n\n    # 0) ENV override\n    env_dir = os.environ.get(\"XBL_HELPER_DIR\")\n    if env_dir:\n        hp = Path(env_dir) / helper_file\n        if hp.exists():\n            mod = _load_helper_module_from_path(hp)\n            if mod and hasattr(mod, \"main\"):\n                try: mod.main()\n                except SystemExit: pass\n                return True\n\n    # 1) Import as package from sibling xbl/\n    try:\n        _ensure_exe_dir_on_syspath()\n        from xbl import xbl_login_standalone_v3 as _m\n        try: _m.main()\n        except SystemExit: pass\n        return True\n    except Exception:\n        pass\n\n    # 2) Load from common locations\n    candidates = [\n        _exe_dir() / \"xbl\" / helper_file,              # next to EXE\n        Path(getattr(sys, \"_MEIPASS\", _exe_dir())) / \"xbl\" / helper_file if getattr(sys, \"frozen\", False) else None,\n        Path.cwd() / \"xbl\" / helper_file,\n    ]\n    for hp in [c for c in candidates if c]:\n        if hp.exists():\n            mod = _load_helper_module_from_path(hp)\n            if mod and hasattr(mod, \"main\"):\n                try: mod.main()\n                except SystemExit: pass\n                return True\n\n    return False\n\n# Back-compat: if old code calls the legacy helper runner name, route it here\ntry:\n    _run_xbl_login_helper_from_xbl  # type: ignore[name-defined]\nexcept Exception:\n    def _run_xbl_login_helper_from_xbl(parent=None):  # legacy name\n        return _run_xbl_helper_inline(parent)\n# === END XBL INLINE LOADER PATCH ===\n\nimport os, sys, json, time, threading, datetime\nfrom typing import Dict, List, Optional\nfrom pathlib import Path\n\nimport requests\nimport subprocess\nfrom PyQt6 import QtWidgets, QtCore\n\nLOG_FILE = os.environ.get(\"XBL_LOG_FILE\")\n\ndef _log(*a):\n    s = \"[xbl_friends_dock] \" + \" \".join(str(x) for x in a)\n    print(s, flush=True)\n    if LOG_FILE:\n        try:\n            Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)\n            with open(LOG_FILE, \"a\", encoding=\"utf-8\") as f:\n                f.write(f\"{datetime.datetime.now().isoformat()} {s}\\n\")\n        except Exception:\n            pass\n\n# ---------- AUTH ----------\nXBL_USER_AUTH = \"https://user.auth.xboxlive.com/user/authenticate\"\nXBL_XSTS_AUTH = \"https://xsts.auth.xboxlive.com/xsts/authorize\"\n\ndef _strip_json_comments(s: str) -> str:\n    out = []; i=0; in_str=False; esc=False\n    while i < len(s):\n        ch = s[i]\n        if in_str:\n            out.append(ch)\n            if esc: esc=False\n            elif ch == '\\\\\\\\': esc=True\n            elif ch == '\"': in_str=False\n            i += 1; continue\n        if ch == '\"': in_str=True; out.append(ch); i += 1; continue\n        if ch == '/' and i+1 < len(s) and s[i+1] in ('/','*'):\n            if s[i+1] == '/':\n                j = s.find('\\\\n', i+2); \n                if j == -1: break\n                i = j + 1; continue\n            else:\n                j = s.find('*/', i+2)\n                if j == -1: break\n                i = j + 2; continue\n        out.append(ch); i += 1\n    return ''.join(out)\n\ndef _find_tokens_path() -> Optional[Path]:\n    env = os.environ.get(\"XBL_TOKENS_PATH\")\n    if env and Path(env).exists(): return Path(env)\n    here = Path(__file__).resolve().parent / \"tokens.json\"\n    if here.exists(): return here\n    cwd = Path(os.getcwd()) / \"tokens.json\"\n    if cwd.exists(): return cwd\n    local = Path(os.environ.get(\"LOCALAPPDATA\", Path.home())) / \"OpenXbox\" / \"xbox\" / \"tokens.json\"\n    if local.exists(): return local\n    return None\n\ndef _post_json(url: str, payload: dict) -> dict:\n    r = requests.post(url, headers={\"Content-Type\":\"application/json\",\"Accept\":\"application/json\",\"Accept-Language\":\"en-US\"}, json=payload, timeout=20)\n    _log(\"POST\", url, \"->\", r.status_code)\n    r.raise_for_status()\n    return r.json()\n\ndef _build_auth_from_tokens(tokens_path: Path) -> Dict[str,str]:\n    raw = tokens_path.read_text(encoding=\"utf-8\", errors=\"ignore\").strip()\n    try:\n        toks = json.loads(raw)\n    except Exception:\n        toks = json.loads(_strip_json_comments(raw))\n    at = toks.get(\"access_token\") or toks.get(\"AccessToken\") or toks.get(\"token\")\n    if not at:\n        raise RuntimeError(\"tokens.json missing access_token\")\n    # user token\n    user_req = {\n        \"RelyingParty\": \"http://auth.xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"AuthMethod\": \"RPS\",\n            \"SiteName\": \"user.auth.xboxlive.com\",\n            \"RpsTicket\": f\"d={at}\",\n        },\n    }\n    j = _post_json(XBL_USER_AUTH, user_req)\n    user_token = j[\"Token\"]\n    # xsts\n    xsts_req = {\n        \"RelyingParty\": \"http://xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"UserTokens\": [user_token],\n            \"SandboxId\": \"RETAIL\",\n        },\n    }\n    j2 = _post_json(XBL_XSTS_AUTH, xsts_req)\n    xsts = j2[\"Token\"]\n    uhs = j2[\"DisplayClaims\"][\"xui\"][0][\"uhs\"]\n    return {\n        \"Authorization\": f\"XBL3.0 x={uhs};{xsts}\",\n        \"Accept\": \"application/json\",\n        \"Accept-Language\": \"en-US\",\n    }\n\n# ---------- Service helpers ----------\ndef _request_json(url: str, headers: Dict, versions=(6,5,4,3,2,1), method=\"GET\", json=None, timeout=15):\n    last_exc = None\n    for ver in versions:\n        h = dict(headers); h[\"x-xbl-contract-version\"] = str(ver)\n        try:\n            if method == \"GET\":\n                r = requests.get(url, headers=h, timeout=timeout)\n            else:\n                r = requests.post(url, headers=h, json=json, timeout=timeout)\n            _log(f\"{method} {url} v{ver} ->\", r.status_code)\n            if r.status_code in (400,404):\n                continue\n            if r.status_code == 429:\n                time.sleep(0.5); continue\n            r.raise_for_status()\n            if r.content:\n                try: return r.json()\n                except Exception: return {}\n            return {}\n        except Exception as e:\n            last_exc = e\n    if last_exc: raise last_exc\n    return {}\n\ndef _me_xuid(headers: Dict) -> Optional[str]:\n    try:\n        data = _request_json(\"https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag\", headers, versions=(3,2,1))\n        pu = (data.get(\"profileUsers\") or [{}])[0]\n        return str(pu.get(\"id\") or \"\")\n    except Exception as e:\n        _log(\"xuid lookup failed:\", repr(e)); return None\n\ndef _fetch_friends(headers: Dict) -> List[Dict]:\n    urls = [\n        \"https://peoplehub.xboxlive.com/users/me/people/social\",\n        \"https://peoplehub.xboxlive.com/users/me/people\",\n        \"https://social.xboxlive.com/users/me/people\",\n    ]\n    me = _me_xuid(headers)\n    if me:\n        urls.insert(0, f\"https://peoplehub.xboxlive.com/users/xuid({me})/people/social\")\n        urls.insert(1, f\"https://peoplehub.xboxlive.com/users/xuid({me})/people/social/summary\")\n\n    for url in urls:\n        try:\n            data = _request_json(url, headers, versions=(6,5,4,3,2,1))\n            arr = data.get(\"people\") or data.get(\"peopleList\") or data.get(\"friends\") or data.get(\"summary\") or []\n            out = []\n            for p in arr or []:\n                x = str(p.get(\"xuid\") or p.get(\"xboxUserId\") or p.get(\"id\") or \"\")\n                g = p.get(\"gamertag\") or p.get(\"modernGamertag\") or p.get(\"preferredName\") or \"\"\n                out.append({\"xuid\": x, \"gamertag\": g})\n            if out:\n                _log(\"friends from\", url, \"->\", len(out))\n                return out\n        except Exception as e:\n            _log(\"friends error for\", url, \":\", repr(e))\n    return []\n\ndef _resolve_gamertags_batch(headers: Dict, xuids: List[str]) -> Dict[str,str]:\n    if not xuids: return {}\n    url = \"https://profile.xboxlive.com/users/batch/profile/settings\"\n    payload = {\"settings\": [\"Gamertag\"], \"userIds\": [f\"xuid({x})\" for x in xuids]}\n    try:\n        data = _request_json(url, headers, versions=(3,2,1), method=\"POST\", json=payload)\n        m = {}\n        for u in data.get(\"profileUsers\", []):\n            uid = str(u.get(\"id\") or \"\")\n            gt = \"\"\n            for s in u.get(\"settings\", []):\n                if s.get(\"id\") == \"Gamertag\":\n                    gt = s.get(\"value\") or \"\"\n            if uid and gt: m[uid] = gt\n        _log(\"resolved gamertags (batch):\", len(m))\n        return m\n    except Exception as e:\n        _log(\"resolve gt batch failed:\", repr(e)); return {}\n\ndef _resolve_gamertags_slow(headers: Dict, xuids: List[str]) -> Dict[str,str]:\n    out = {}\n    for x in xuids:\n        url = f\"https://profile.xboxlive.com/users/xuid({x})/profile/settings?settings=Gamertag\"\n        try:\n            data = _request_json(url, headers, versions=(3,2,1), method=\"GET\")\n            pu = (data.get(\"profileUsers\") or [{}])[0]\n            uid = str(pu.get(\"id\") or \"\")\n            gt = \"\"\n            for s in pu.get(\"settings\", []):\n                if s.get(\"id\") == \"Gamertag\": gt = s.get(\"value\") or \"\"\n            if uid and gt: out[uid] = gt\n        except Exception as e:\n            _log(\"resolve gt slow failed for\", x, \":\", repr(e))\n        time.sleep(0.05)\n    _log(\"resolved gamertags (slow):\", len(out))\n    return out\n\ndef _extract_title_from_presence(data: dict) -> str:\n    for d in data.get(\"devices\", []):\n        for t in d.get(\"titles\", []):\n            name = t.get(\"name\") or t.get(\"titleName\") or \"\"\n            act = t.get(\"activity\") or {}\n            if t.get(\"placement\") == \"Full\" or act.get(\"richPresence\") or act.get(\"broadcastTitle\"):\n                if name: return name\n    return \"\"\n\ndef _presence_batch(headers: Dict, xuids: List[str]) -> Dict[str, Dict]:\n    result = {}\n    try:\n        payload = {\"users\": [f\"xuid({x})\" for x in xuids], \"level\": \"all\"}\n        data = _request_json(\"https://presence.xboxlive.com/users/batch\", headers, versions=(3,2,1), method=\"POST\", json=payload)\n        users = data.get(\"responses\") or data.get(\"users\") or []\n        for u in users:\n            uid = u.get(\"id\") or u.get(\"xuid\") or \"\"\n            if isinstance(uid, str) and uid.startswith(\"xuid(\"): uid = uid[5:-1]\n            state = u.get(\"state\") or u.get(\"presenceState\") or \"\"\n            title = _extract_title_from_presence(u)\n            if uid: result[str(uid)] = {\"state\": state, \"title\": title}\n        if result:\n            _log(\"presence batch OK:\", len(result))\n            return result\n    except Exception as e:\n        _log(\"presence batch failed:\", repr(e))\n    return {}\n\ndef _presence_slow(headers: Dict, xuids: List[str], progress_cb=None) -> Dict[str, Dict]:\n    result = {}\n    for i, x in enumerate(xuids, 1):\n        url = f\"https://userpresence.xboxlive.com/users/xuid({x})?level=all\"\n        try:\n            data = _request_json(url, headers, versions=(3,2,1), method=\"GET\")\n            state = data.get(\"state\") or data.get(\"presenceState\") or \"\"\n            title = _extract_title_from_presence(data)\n            result[str(x)] = {\"state\": state, \"title\": title}\n            if progress_cb and (i % 10 == 0 or i == len(xuids)):\n                progress_cb(i, len(xuids))\n        except Exception as e:\n            _log(\"presence slow failed for\", x, \":\", repr(e))\n        time.sleep(0.045)\n    _log(\"presence slow collected:\", len(result))\n    return result\n\n# ---------- UI (filterable) ----------\n\nclass TransparencyDialog(QtWidgets.QDialog):\n    def __init__(self, dock: QtWidgets.QWidget):\n        super().__init__(dock)\n        self._dock = dock\n        self.setWindowTitle(\"Transparency\")\n        self.setModal(False)\n        self.resize(320, 100)\n\n        v = QtWidgets.QVBoxLayout(self)\n        self.label = QtWidgets.QLabel(self)\n        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)\n        self.slider.setMinimum(20)   # 20% minimum to avoid disappearing\n        self.slider.setMaximum(100)  # 100% = opaque\n        # initialize from current window opacity\n        current = int(round((dock.windowOpacity() or 1.0) * 100))\n        current = max(self.slider.minimum(), min(self.slider.maximum(), current))\n        self.slider.setValue(current)\n        self._update_label(current)\n\n        self.slider.valueChanged.connect(self._on_change)\n\n        btn_row = QtWidgets.QHBoxLayout()\n        self.btnReset = QtWidgets.QPushButton(\"Reset\")\n        self.btnClose = QtWidgets.QPushButton(\"Close\")\n        btn_row.addStretch(1)\n        btn_row.addWidget(self.btnReset)\n        btn_row.addWidget(self.btnClose)\n\n        v.addWidget(self.label)\n        v.addWidget(self.slider)\n        v.addLayout(btn_row)\n\n        self.btnReset.clicked.connect(self._reset)\n        self.btnClose.clicked.connect(self.close)\n\n    def _update_label(self, val: int):\n        self.label.setText(f\"Opacity: {val}%\")\n\n    def _on_change(self, val: int):\n        try:\n            self._dock.setWindowOpacity(val / 100.0)\n            self._update_label(val)\n            try:\n                self._dock._save_settings(opacity_percent=int(val))\n            except Exception as _e:\n                _log(\"settings write warn:\", repr(_e))\n        except Exception as e:\n            _log(\"opacity change error:\", repr(e))\n\n    def _reset(self):\n        self.slider.setValue(100)\n        try:\n            self._dock._save_settings(opacity_percent=100)\n        except Exception as _e:\n            _log(\"settings write warn:\", repr(_e))\n\nclass FriendsDock(QtWidgets.QDialog):\n\n    # --- Cache helpers (ADD-ONLY) ---\n    # --- Settings helpers (ADD-ONLY) ---\n    def _settings_path(self) -> Path:\n        try:\n            return Path(__file__).resolve().parent / \"friends_settings.json\"\n        except Exception:\n            return Path(\"friends_settings.json\")\n\n    def _load_settings(self) -> dict:\n        try:\n            p = self._settings_path()\n            if not p.exists():\n                return {}\n            raw = p.read_text(encoding=\"utf-8\", errors=\"ignore\")\n            return json.loads(raw) if raw.strip() else {}\n        except Exception as e:\n            _log(\"settings load error:\", repr(e))\n            return {}\n\n    def _save_settings(self, **updates):\n        try:\n            data = self._load_settings()\n            data.update(updates)\n            self._settings_path().write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding=\"utf-8\")\n            _log(\"settings saved:\", updates)\n        except Exception as e:\n            _log(\"settings save error:\", repr(e))\n    # --- end settings helpers ---\n\n    def _cache_path(self) -> Path:\n        try:\n            return Path(__file__).resolve().parent / \"friends_cache.json\"\n        except Exception:\n            return Path(\"friends_cache.json\")\n\n    def _save_cached_rows(self, rows):\n        try:\n            data = [{\"gamertag\": gt, \"status\": st, \"game\": gm} for (gt, st, gm) in (rows or [])]\n            self._cache_path().write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding=\"utf-8\")\n            _log(\"cache saved:\", str(self._cache_path()), len(data), \"rows\")\n        except Exception as e:\n            _log(\"cache save error:\", repr(e))\n\n    def _load_cached_rows(self):\n        try:\n            p = self._cache_path()\n            if not p.exists():\n                return False\n            raw = p.read_text(encoding=\"utf-8\", errors=\"ignore\")\n            arr = json.loads(raw) if raw.strip() else []\n            rows = [(d.get(\"gamertag\",\"\"), d.get(\"status\",\"\"), d.get(\"game\",\"\")) for d in arr]\n            if rows:\n                self.sig_set_rows.emit(rows)\n                self.sig_set_status.emit(f\"Restored {len(rows)} cached friends\")\n                _log(\"cache restored:\", len(rows), \"rows\")\n                return True\n            return False\n        except Exception as e:\n            _log(\"cache load error:\", repr(e))\n            return False\n    # --- end cache helpers ---\n\n    sig_set_status = QtCore.pyqtSignal(str)\n    sig_set_rows = QtCore.pyqtSignal(list)   # list of (gt, status, game)\n    sig_enable_btn = QtCore.pyqtSignal(bool)\n    sig_busy = QtCore.pyqtSignal(bool)\n\n    def __init__(self, parent=None):\n        super().__init__(parent)\n        self.setWindowTitle(\"Xbox Friends\")\n        self.resize(720, 740)\n        # Enable minimize button on title bar\n        try:\n            self.setWindowFlags(self.windowFlags() |\n                                QtCore.Qt.WindowType.WindowMinimizeButtonHint |\n                                QtCore.Qt.WindowType.WindowSystemMenuHint)\n        except Exception as _e:\n            _log(\"minimize flag warn:\", repr(_e))\n        self._full_rows: List[tuple] = []\n\n        v = QtWidgets.QVBoxLayout(self)\n        top = QtWidgets.QHBoxLayout()\n        self.lbl = QtWidgets.QLabel(\"Ready.\")\n        self.view = QtWidgets.QComboBox()\n        self.view.addItems([\"All (Online first)\", \"Online only\"])\n        self.btn = QtWidgets.QPushButton(\"Refresh\")\n        top.addWidget(self.lbl); top.addStretch(1); top.addWidget(QtWidgets.QLabel(\"View:\")); top.addWidget(self.view)\n        # \"Always on top\" toggle (ADD-ONLY)\n        self.chkAlwaysOnTop = QtWidgets.QCheckBox(\"Always on top\")\n        top.addWidget(self.chkAlwaysOnTop)\n        # Busy spinner (indeterminate) \u2014 hidden by default\n        self._busy = QtWidgets.QProgressBar(self)\n        self._busy.setRange(0, 0)\n        self._busy.setTextVisible(False)\n        self._busy.setFixedWidth(80)\n        self._busy.hide()\n        top.insertWidget(1, self._busy)\n        # Auto-refresh timer (1 minute; OFF by default)\n        self._autoRefreshTimer = QtCore.QTimer(self)\n        self._autoRefreshTimer.setInterval(60_000)\n        self._autoRefreshTimer.timeout.connect(self.refresh)\n        self.btnAuth = QtWidgets.QPushButton(\"Sign in / Choose tokens.json\")\n        self.btnRefreshTokenOnly = QtWidgets.QPushButton(\"Refresh token only\")\n        top.addWidget(self.btnAuth); top.addWidget(self.btnRefreshTokenOnly); top.addWidget(self.btn)\n\n        # ---- Settings dropdown (cosmetic only) ----\n        # ---- Settings dropdown (cosmetic only) ----\n        self.btnSettings = QtWidgets.QToolButton()\n        self.btnSettings.setText(\"Settings\")\n        self.btnSettings.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)\n        _menu = QtWidgets.QMenu(self.btnSettings)\n        _a_refresh = _menu.addAction(\"Refresh\"); _a_refresh.triggered.connect(self.refresh)\n        _a_signin  = _menu.addAction(\"Sign in / Choose tokens.json\"); _a_signin.triggered.connect(self._do_auth)\n        _a_rtonly  = _menu.addAction(\"Refresh token only\"); _a_rtonly.triggered.connect(self._refresh_token_only)\n        _a_transp  = _menu.addAction(\"Transparency\u2026\"); _a_transp.triggered.connect(self._open_transparency)\n        self._autoAction = _menu.addAction(\"Auto Refresh (1 minute)\")\n        self._autoAction.setCheckable(True)\n        self._autoAction.setChecked(False)\n        self._autoAction.triggered.connect(self._toggle_auto_refresh)\n        self.btnSettings.setMenu(_menu)\n        top.addWidget(self.btnSettings)\n        try:\n            self.btn.hide(); self.btnAuth.hide(); self.btnRefreshTokenOnly.hide()\n        except Exception:\n            pass\n        # ---- end Settings dropdown ----\n\n        # Hide original buttons (objects remain; signals intact)\n        try:\n            self.btn.hide()\n            self.btnAuth.hide()\n            self.btnRefreshTokenOnly.hide()\n        except Exception as _e:\n            _log(\"hide-buttons warning:\", repr(_e))\n        # ---- end Settings dropdown ----\n\n        v.addLayout(top)\n\n        self.table = QtWidgets.QTableWidget(0, 3)\n        self.table.setHorizontalHeaderLabels([\"Gamertag\", \"Status\", \"Game\"])\n        self.table.horizontalHeader().setStretchLastSection(True)\n        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)\n        v.addWidget(self.table, 1)\n\n        self.btn.clicked.connect(self.refresh)\n        self.btnAuth.clicked.connect(self._do_auth)\n        self.btnRefreshTokenOnly.clicked.connect(self._refresh_token_only)\n        self.view.currentIndexChanged.connect(self._reapply_filter)\n        self.view.currentIndexChanged.connect(lambda _i: self._save_settings(view_index=int(_i)))\n        self.chkAlwaysOnTop.toggled.connect(self._apply_always_on_top)\n\n        self.sig_set_status.connect(self._set_status)\n        self.sig_set_rows.connect(self._receive_full_rows)\n        self.sig_enable_btn.connect(self.btn.setEnabled)\n        self.sig_busy.connect(self._busy.setVisible)\n\n        # Load and apply persistent settings (opacity, auto-refresh)\n        try:\n            _s = self._load_settings()\n            # Apply opacity\n            _op = int(_s.get(\"opacity_percent\", 100))\n            _op = max(20, min(100, _op))\n            self.setWindowOpacity(_op / 100.0)\n            # Apply auto-refresh state\n            _auto = bool(_s.get(\"auto_refresh\", False))\n            if hasattr(self, \"_autoAction\"):\n                self._autoAction.setChecked(_auto)\n            if _auto:\n                self._autoRefreshTimer.start()\n            # Apply view filter index\n            try:\n                _vi = int(_s.get(\"view_index\", 0))\n                if 0 <= _vi < self.view.count():\n                    self.view.setCurrentIndex(_vi)\n            except Exception:\n                pass\n            # Apply 'Always on top'\n            _aot = bool(_s.get(\"always_on_top\", False))\n            if hasattr(self, 'chkAlwaysOnTop'):\n                self.chkAlwaysOnTop.setChecked(_aot)\n            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, _aot)\n            self.show()\n        except Exception as _e:\n            _log(\"apply settings warn:\", repr(_e))\n\n        # Show cached rows immediately (if available) before first refresh\n        try:\n            _had_cache = self._load_cached_rows()\n        except Exception as _e:\n            _had_cache = False\n            _log(\"warm restore warn:\", repr(_e))\n        if not _had_cache:\n            QtCore.QTimer.singleShot(150, self.refresh)\n\n    def _set_status(self, s: str):\n        self.lbl.setText(s); _log(\"status:\", s)\n\n    def _receive_full_rows(self, rows: List[tuple]):\n        # rows already have \"Online first\" order\n        self._full_rows = rows\n        self._reapply_filter()\n\n    def _reapply_filter(self):\n        rows = self._full_rows\n        if self.view.currentIndex() == 1:  # Online only\n            rows = [r for r in rows if r[1] == \"Online\"]\n        self._apply_rows(rows)\n\n\n    # --- Status LED helpers (ADD-ONLY) ---\n    def _build_led_icon(self, color: QtCore.Qt.GlobalColor) -> QtWidgets.QStyle.StandardPixmap | QtWidgets.QStyle:\n        # Create a small circular pixmap to act as an LED\n        pm = QtGui.QPixmap(14, 14)\n        pm.fill(QtCore.Qt.GlobalColor.transparent)\n        painter = QtGui.QPainter(pm)\n        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)\n        brush = QtGui.QBrush(color)\n        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black)\n        pen.setWidth(1)\n        painter.setPen(pen)\n        painter.setBrush(brush)\n        painter.drawEllipse(1, 1, 12, 12)\n        painter.end()\n        return QtGui.QIcon(pm)\n\n    def _icon_for_state(self, st: str) -> QtGui.QIcon:\n        try:\n            if not hasattr(self, \"_led_green\"):\n                self._led_green = self._build_led_icon(QtCore.Qt.GlobalColor.green)\n                self._led_red   = self._build_led_icon(QtCore.Qt.GlobalColor.red)\n                self._led_blank = self._build_led_icon(QtCore.Qt.GlobalColor.gray)\n        except Exception:\n            pass\n        s = (st or \"\").strip().lower()\n        if s == \"online\":\n            return getattr(self, \"_led_green\", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogApplyButton))\n        elif s == \"offline\":\n            return getattr(self, \"_led_red\", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogCancelButton))\n        return getattr(self, \"_led_blank\", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation))\n    # --- end Status LED helpers ---\n\n    def _apply_rows(self, rows: List[tuple]):\n        self.table.setSortingEnabled(False)\n        self.table.setRowCount(len(rows))\n        for i,(gt,st,gm) in enumerate(rows):\n            # Gamertag text\n            self.table.setItem(i,0, QtWidgets.QTableWidgetItem(gt))\n            # Status LED (icon only)\n            _status_item = QtWidgets.QTableWidgetItem(\"\")\n            try:\n                _status_item.setIcon(self._icon_for_state(st))\n                _status_item.setText(\"\")  # no text, icon only\n                _status_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)\n            except Exception:\n                _status_item.setText(st)\n            self.table.setItem(i,1, _status_item)\n            # Game text\n            self.table.setItem(i,2, QtWidgets.QTableWidgetItem(gm))\n        self.table.setSortingEnabled(True)\n        # Keep consistent order: Online first (already), within that alphabetically\n        self.table.sortItems(1, QtCore.Qt.SortOrder.AscendingOrder)\n\n\n    def _apply_always_on_top(self, checked: bool):\n        try:\n            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, bool(checked))\n            self.show()  # re-apply flags\n            try:\n                self._save_settings(always_on_top=bool(checked))\n            except Exception as _e:\n                _log(\"settings write warn:\", repr(_e))\n        except Exception as e:\n            _log(\"always on top apply error:\", repr(e))\n\n    def _open_transparency(self):\n        try:\n            if not hasattr(self, \"_transparencyDlg\") or self._transparencyDlg is None:\n                self._transparencyDlg = TransparencyDialog(self)\n            self._transparencyDlg.show()\n            self._transparencyDlg.raise_()\n            self._transparencyDlg.activateWindow()\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Error\", f\"Transparency error: {e}\")\n\n    def _refresh_token_only(self):\n        \"\"\"\n        Run xbl_login_standalone_v3.py to refresh tokens, then prompt where the new token was saved.\n        \"\"\"\n        try:\n            self.sig_enable_btn.emit(False)\n            self.sig_set_status.emit(\"Refreshing token via login helper...\")\n\n            base = Path(__file__).resolve().parent\n            helper = base / \"xbl_login_standalone_v3.py\"\n            if not helper.exists():\n                QtWidgets.QMessageBox.critical(self, \"Missing helper\", \"xbl_login_standalone_v3.py not found next to this script.\")\n                self.sig_enable_btn.emit(True)\n                return\n\n            proc = subprocess.run([sys.executable, str(helper)], cwd=str(base), capture_output=True, text=True)\n            out = (proc.stdout or \"\") + \"\\n\" + (proc.stderr or \"\")\n            if proc.returncode != 0:\n                QtWidgets.QMessageBox.critical(self, \"Refresh failed\", f\"Helper exited with {proc.returncode}.\\n\\nOutput (tail):\\n{out[-2000:]}\")\n                self.sig_enable_btn.emit(True)\n                return\n\n            # Parse output to find the saved tokens file\n            tokens_path = None\n            for line in out.splitlines():\n                s = line.strip()\n                if s.startswith(\"[Info] Tokens file:\"):\n                    tokens_path = s.split(\":\", 1)[1].strip()\n                    break\n            if not tokens_path:\n                # Fallback to typical default\n                tokens_path = str(Path(os.environ.get(\"LOCALAPPDATA\", Path.home())) / \"OpenXbox\" / \"xbox\" / \"tokens.json\")\n\n            # Prompt user where it was saved and offer to use it now\n            msg = QtWidgets.QMessageBox(self)\n            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)\n            msg.setWindowTitle(\"Token refreshed\")\n            msg.setText(f\"New tokens were saved here:\\n{tokens_path}\\n\\nUse this tokens.json now?\")\n            yes_btn = msg.addButton(\"Use now\", QtWidgets.QMessageBox.ButtonRole.AcceptRole)\n            no_btn = msg.addButton(\"Cancel\", QtWidgets.QMessageBox.ButtonRole.RejectRole)\n            msg.exec()\n            if msg.clickedButton() is yes_btn:\n                os.environ[\"XBL_TOKENS_PATH\"] = tokens_path\n                self.sig_set_status.emit(\"Using refreshed tokens. Reloading\u2026\")\n                QtCore.QTimer.singleShot(200, self.refresh)\n            else:\n                self.sig_enable_btn.emit(True)\n\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Error\", str(e))\n            self.sig_enable_btn.emit(True)\n\n    def _do_auth(self):\n        \"\"\"\n        Opens a small chooser:\n        - Use existing tokens.json (browse & load)\n        - Run device sign-in helper to create a new tokens.json\n        \"\"\"\n        try:\n            default_path = os.environ.get(\"XBL_TOKENS_PATH\") or str((Path.cwd() / \"tokens.json\"))\n            # Simple chooser via QMessageBox-style buttons\n            dlg = QtWidgets.QMessageBox(self)\n            dlg.setIcon(QtWidgets.QMessageBox.Icon.Question)\n            dlg.setWindowTitle(\"Xbox sign-in / tokens.json\")\n            dlg.setText(\"How would you like to provide tokens?\")\n            use_existing = dlg.addButton(\"Use existing tokens.json\u2026\", QtWidgets.QMessageBox.ButtonRole.AcceptRole)\n            run_helper  = dlg.addButton(\"Run device sign-in\u2026\", QtWidgets.QMessageBox.ButtonRole.ActionRole)\n            cancel_btn  = dlg.addButton(\"Cancel\", QtWidgets.QMessageBox.ButtonRole.RejectRole)\n            # PyQt6: exec()\n            dlg.exec()\n            clicked = dlg.clickedButton()\n            if clicked is cancel_btn:\n                return\n\n            if clicked is use_existing:\n                path, _ = QtWidgets.QFileDialog.getOpenFileName(\n                    self, \"Select tokens.json\", default_path, \"JSON Files (*.json);;All Files (*)\"\n                )\n                if not path:\n                    return\n                # point the app to this file and refresh\n                os.environ[\"XBL_TOKENS_PATH\"] = path\n                self.sig_set_status.emit(\"Using selected tokens.json. Reloading\u2026\")\n                QtCore.QTimer.singleShot(200, self.refresh)\n                return\n\n            # Otherwise run helper to produce a new tokens.json\n            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(\n                self, \"Save tokens.json\", default_path, \"JSON Files (*.json);;All Files (*)\"\n            )\n            if not save_path:\n                return\n\n            self.sig_enable_btn.emit(False)\n            self.sig_set_status.emit(\"Starting device sign-in\u2026 follow the console/device code flow\")\n\n            base = Path(__file__).resolve().parent\n            helper = None\n            for name in [\"xbl_auth_device_any.py\", \"xbl_login_standalone_v3.py\", \"xbl_signin_from_oauth_tokens.py\"]:\n                cand = base / name\n                if cand.exists():\n                    helper = str(cand)\n                    break\n            if helper is None:\n                QtWidgets.QMessageBox.critical(\n                    self, \"Missing helper\",\n                    \"Could not find a sign-in helper (xbl_auth_device_any.py or xbl_login_standalone_v3.py).\"\n                )\n                self.sig_enable_btn.emit(True)\n                return\n\n            import subprocess, sys\n            proc = subprocess.run([sys.executable, helper, \"--out\", save_path], cwd=str(base))\n            if proc.returncode != 0:\n                QtWidgets.QMessageBox.critical(self, \"Sign-in failed\", f\"Auth helper exited with code {proc.returncode}.\")\n                self.sig_enable_btn.emit(True)\n                return\n\n            os.environ[\"XBL_TOKENS_PATH\"] = save_path\n            self.sig_set_status.emit(\"Token saved. Reloading\u2026\")\n            QtCore.QTimer.singleShot(200, self.refresh)\n\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Error\", str(e))\n            self.sig_enable_btn.emit(True)\n\n\n    def _toggle_auto_refresh(self):\n        try:\n            if self._autoRefreshTimer.isActive():\n                self._autoRefreshTimer.stop()\n                if hasattr(self, '_autoAction') and self._autoAction:\n                    self._autoAction.setChecked(False)\n                self.sig_set_status.emit(\"Auto Refresh: OFF\")\n                try:\n                    self._save_settings(auto_refresh=False)\n                except Exception as _e:\n                    _log(\"settings write warn:\", repr(_e))\n            else:\n                self._autoRefreshTimer.start()\n                if hasattr(self, '_autoAction') and self._autoAction:\n                    self._autoAction.setChecked(True)\n                self.sig_set_status.emit(\"Auto Refresh: ON (every 1 min)\")\n                try:\n                    self._save_settings(auto_refresh=True)\n                except Exception as _e:\n                    _log(\"settings write warn:\", repr(_e))\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Auto Refresh Error\", str(e))\n\n    def refresh(self):\n        self.sig_enable_btn.emit(False); self.sig_set_status.emit(\"\"); self.sig_busy.emit(True); self.sig_set_rows.emit([])\n\n        def _run():\n            try:\n                # ----- auth\n                tpath = _find_tokens_path()\n                if not tpath:\n                    raise RuntimeError(\"tokens.json not found. Set XBL_TOKENS_PATH or place tokens.json next to the script.\")\n                _log(\"Using tokens.json at:\", str(tpath))\n                headers = _build_auth_from_tokens(tpath)\n\n                # ----- friends list\n                friends = _fetch_friends(headers)\n                if not friends:\n                    raise RuntimeError(\"No friends returned (service/permissions).\")\n\n                self.sig_set_status.emit(f\"{len(friends)} friends (resolving names...)\")\n\n                # ----- gamertags\n                missing = [f[\"xuid\"] for f in friends if f.get(\"xuid\") and not f.get(\"gamertag\")]\n                gmap = _resolve_gamertags_batch(headers, missing) if missing else {}\n                if missing and len(gmap) < len(missing):\n                    slow_needed = [x for x in missing if x not in gmap]\n                    if slow_needed:\n                        gmap.update(_resolve_gamertags_slow(headers, slow_needed))\n                for f in friends:\n                    if not f.get(\"gamertag\"):\n                        f[\"gamertag\"] = gmap.get(f.get(\"xuid\",\"\"), f.get(\"xuid\",\"\"))\n\n                self.sig_set_status.emit(f\"{len(friends)} friends (loading presence...)\")\n\n                # ----- presence\n                xuids = [f[\"xuid\"] for f in friends if f.get(\"xuid\")]\n                pres = _presence_batch(headers, xuids) if xuids else {}\n                if xuids and len(pres) < len(xuids):\n                    def _progress(i, n):\n                        self.sig_set_status.emit(f\"{len(friends)} friends (presence {i}/{n})\")\n                    pres.update(_presence_fast(headers, [x for x in xuids if x not in pres], _progress, workers=24))\n\n                rows = []\n                for f in friends:\n                    x = f.get(\"xuid\",\"\"); gt = f.get(\"gamertag\") or x\n                    p = pres.get(x, {})\n                    state = \"Online\" if str(p.get(\"state\",\"\")).lower()==\"online\" else (\"Offline\" if p else \"\")\n                    title = p.get(\"title\",\"\")\n                    rows.append((gt, state, title))\n                rows.sort(key=lambda r: (r[1]!=\"Online\", r[0].lower()))\n\n                self.sig_set_rows.emit(rows)\n                try:\n                    self._save_cached_rows(rows)\n                except Exception as _e:\n                    _log(\"cache post-refresh warn:\", repr(_e))\n                self.sig_set_status.emit(f\"{len(rows)} friends (presence applied)\")\n                self.sig_busy.emit(False)\n                self.sig_enable_btn.emit(True)\n\n            except Exception as e:\n                _log(\"Error:\", repr(e))\n                self.sig_set_status.emit(f\"Error: {e.__class__.__name__}: {e}\")\n                self.sig_busy.emit(False)\n                self.sig_enable_btn.emit(True)\n\n        threading.Thread(target=_run, daemon=True).start()\ndef _presence_fast(headers: Dict, xuids: List[str], progress_cb=None, workers: int = 24) -> Dict[str, Dict]:\n    \"\"\"Concurrent presence fetch using a shared Session. Keeps requests gentle but parallel.\"\"\"\n    import concurrent.futures, time, math\n    result = {}\n    if not xuids:\n        return result\n\n    # Shared session with connection pool\n    sess = requests.Session()\n    try:\n        from requests.adapters import HTTPAdapter\n        from urllib3.util.retry import Retry\n        adapter = HTTPAdapter(pool_connections=workers*2, pool_maxsize=workers*2, max_retries=0)\n        sess.mount(\"https://\", adapter); sess.mount(\"http://\", adapter)\n    except Exception:\n        pass\n\n    base_headers = dict(headers)\n    base_headers[\"x-xbl-contract-version\"] = \"3\"\n    url_tpl = \"https://userpresence.xboxlive.com/users/xuid({})?level=all\"\n\n    # Gentle concurrency: cap workers, backoff on 429, shorter timeout\n    def fetch_one(xuid: str):\n        url = url_tpl.format(xuid)\n        tries = 0\n        delay = 0.3\n        while True:\n            tries += 1\n            try:\n                r = sess.get(url, headers=base_headers, timeout=8)\n                status = r.status_code\n                if status == 429:\n                    # Too many requests; back off a bit and retry\n                    time.sleep(delay)\n                    delay = min(delay * 1.6, 3.0)\n                    if tries < 5:\n                        continue\n                if status in (400, 404):\n                    return xuid, {}\n                r.raise_for_status()\n                j = r.json() if r.content else {}\n                state = j.get(\"state\") or j.get(\"presenceState\") or \"\"\n                title = _extract_title_from_presence(j)\n                return xuid, {\"state\": state, \"title\": title}\n            except Exception:\n                if tries < 3:\n                    time.sleep(delay)\n                    delay = min(delay * 1.6, 3.0)\n                    continue\n                return xuid, {}\n\n    done = 0\n    report_every = max(10, len(xuids)//15)  # ~15 updates max\n    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 48))) as ex:\n        for xuid, info in ex.map(fetch_one, xuids):\n            done += 1\n            if info:\n                result[str(xuid)] = info\n            if progress_cb and (done % report_every == 0 or done == len(xuids)):\n                progress_cb(done, len(xuids))\n\n    _log(\"presence fast collected:\", len(result))\n    try:\n        sess.close()\n    except Exception:\n        pass\n    return result\n\n\ndef main():\n    _log(\"Starting Xbox Friends Dock (INLINE v5)\")\n    app = QtWidgets.QApplication(sys.argv)\n    w = FriendsDock(); w.show()\n    rc = app.exec()\n    _log(\"App exit code:\", rc); sys.exit(rc)\n\nif __name__ == \"__main__\":\n    main()", "xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED.py")
_register_module("xbl.xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED", "\nfrom __future__ import annotations\n\n\n# === BEGIN XBL INLINE LOADER PATCH (no subprocess, works in one-file EXE) ===\nimport sys, os\nfrom pathlib import Path\nimport importlib.util\n\ndef _exe_dir() -> Path:\n    try:\n        return Path(sys.executable).parent\n    except Exception:\n        return Path.cwd()\n\ndef _ensure_exe_dir_on_syspath():\n    p = str(_exe_dir())\n    if p not in sys.path:\n        sys.path.insert(0, p)\n\ndef _load_helper_module_from_path(helper_path: Path):\n    \"\"\"Load a .py module from disk in-process (even when frozen).\"\"\"\n    try:\n        spec = importlib.util.spec_from_file_location(\"xbl_login_standalone_v3_dyn\", str(helper_path))\n        if not spec or not spec.loader:\n            return None\n        mod = importlib.util.module_from_spec(spec)\n        spec.loader.exec_module(mod)\n        return mod\n    except Exception:\n        return None\n\ndef _run_xbl_helper_inline(parent=None) -> bool:\n    \"\"\"\n    Order:\n      1) ENV XBL_HELPER_DIR\n      2) import from xbl package (with exe_dir on sys.path)\n      3) load from file: exe_dir/xbl, _MEIPASS/xbl, cwd/xbl\n    \"\"\"\n    helper_file = \"xbl_login_standalone_v3.py\"\n\n    # 0) ENV override\n    env_dir = os.environ.get(\"XBL_HELPER_DIR\")\n    if env_dir:\n        hp = Path(env_dir) / helper_file\n        if hp.exists():\n            mod = _load_helper_module_from_path(hp)\n            if mod and hasattr(mod, \"main\"):\n                try: mod.main()\n                except SystemExit: pass\n                return True\n\n    # 1) Import as package from sibling xbl/\n    try:\n        _ensure_exe_dir_on_syspath()\n        from xbl import xbl_login_standalone_v3 as _m\n        try: _m.main()\n        except SystemExit: pass\n        return True\n    except Exception:\n        pass\n\n    # 2) Load from common locations\n    candidates = [\n        _exe_dir() / \"xbl\" / helper_file,              # next to EXE\n        Path(getattr(sys, \"_MEIPASS\", _exe_dir())) / \"xbl\" / helper_file if getattr(sys, \"frozen\", False) else None,\n        Path.cwd() / \"xbl\" / helper_file,\n    ]\n    for hp in [c for c in candidates if c]:\n        if hp.exists():\n            mod = _load_helper_module_from_path(hp)\n            if mod and hasattr(mod, \"main\"):\n                try: mod.main()\n                except SystemExit: pass\n                return True\n\n    return False\n\n# Back-compat: if old code calls the legacy helper runner name, route it here\ntry:\n    _run_xbl_login_helper_from_xbl  # type: ignore[name-defined]\nexcept Exception:\n    def _run_xbl_login_helper_from_xbl(parent=None):  # legacy name\n        return _run_xbl_helper_inline(parent)\n# === END XBL INLINE LOADER PATCH ===\n\nimport os, sys, json, time, threading, datetime\nfrom typing import Dict, List, Optional\nfrom pathlib import Path\n\nimport requests\nimport subprocess\nfrom PyQt6 import QtWidgets, QtCore\n\nLOG_FILE = os.environ.get(\"XBL_LOG_FILE\")\n\ndef _log(*a):\n    s = \"[xbl_friends_dock] \" + \" \".join(str(x) for x in a)\n    print(s, flush=True)\n    if LOG_FILE:\n        try:\n            Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)\n            with open(LOG_FILE, \"a\", encoding=\"utf-8\") as f:\n                f.write(f\"{datetime.datetime.now().isoformat()} {s}\\n\")\n        except Exception:\n            pass\n\n# ---------- AUTH ----------\nXBL_USER_AUTH = \"https://user.auth.xboxlive.com/user/authenticate\"\nXBL_XSTS_AUTH = \"https://xsts.auth.xboxlive.com/xsts/authorize\"\n\ndef _strip_json_comments(s: str) -> str:\n    out = []; i=0; in_str=False; esc=False\n    while i < len(s):\n        ch = s[i]\n        if in_str:\n            out.append(ch)\n            if esc: esc=False\n            elif ch == '\\\\\\\\': esc=True\n            elif ch == '\"': in_str=False\n            i += 1; continue\n        if ch == '\"': in_str=True; out.append(ch); i += 1; continue\n        if ch == '/' and i+1 < len(s) and s[i+1] in ('/','*'):\n            if s[i+1] == '/':\n                j = s.find('\\\\n', i+2); \n                if j == -1: break\n                i = j + 1; continue\n            else:\n                j = s.find('*/', i+2)\n                if j == -1: break\n                i = j + 2; continue\n        out.append(ch); i += 1\n    return ''.join(out)\n\ndef _find_tokens_path() -> Optional[Path]:\n    env = os.environ.get(\"XBL_TOKENS_PATH\")\n    if env and Path(env).exists(): return Path(env)\n    here = Path(__file__).resolve().parent / \"tokens.json\"\n    if here.exists(): return here\n    cwd = Path(os.getcwd()) / \"tokens.json\"\n    if cwd.exists(): return cwd\n    local = Path(os.environ.get(\"LOCALAPPDATA\", Path.home())) / \"OpenXbox\" / \"xbox\" / \"tokens.json\"\n    if local.exists(): return local\n    return None\n\ndef _post_json(url: str, payload: dict) -> dict:\n    r = requests.post(url, headers={\"Content-Type\":\"application/json\",\"Accept\":\"application/json\",\"Accept-Language\":\"en-US\"}, json=payload, timeout=20)\n    _log(\"POST\", url, \"->\", r.status_code)\n    r.raise_for_status()\n    return r.json()\n\ndef _build_auth_from_tokens(tokens_path: Path) -> Dict[str,str]:\n    raw = tokens_path.read_text(encoding=\"utf-8\", errors=\"ignore\").strip()\n    try:\n        toks = json.loads(raw)\n    except Exception:\n        toks = json.loads(_strip_json_comments(raw))\n    at = toks.get(\"access_token\") or toks.get(\"AccessToken\") or toks.get(\"token\")\n    if not at:\n        raise RuntimeError(\"tokens.json missing access_token\")\n    # user token\n    user_req = {\n        \"RelyingParty\": \"http://auth.xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"AuthMethod\": \"RPS\",\n            \"SiteName\": \"user.auth.xboxlive.com\",\n            \"RpsTicket\": f\"d={at}\",\n        },\n    }\n    j = _post_json(XBL_USER_AUTH, user_req)\n    user_token = j[\"Token\"]\n    # xsts\n    xsts_req = {\n        \"RelyingParty\": \"http://xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"UserTokens\": [user_token],\n            \"SandboxId\": \"RETAIL\",\n        },\n    }\n    j2 = _post_json(XBL_XSTS_AUTH, xsts_req)\n    xsts = j2[\"Token\"]\n    uhs = j2[\"DisplayClaims\"][\"xui\"][0][\"uhs\"]\n    return {\n        \"Authorization\": f\"XBL3.0 x={uhs};{xsts}\",\n        \"Accept\": \"application/json\",\n        \"Accept-Language\": \"en-US\",\n    }\n\n# ---------- Service helpers ----------\ndef _request_json(url: str, headers: Dict, versions=(6,5,4,3,2,1), method=\"GET\", json=None, timeout=15):\n    last_exc = None\n    for ver in versions:\n        h = dict(headers); h[\"x-xbl-contract-version\"] = str(ver)\n        try:\n            if method == \"GET\":\n                r = requests.get(url, headers=h, timeout=timeout)\n            else:\n                r = requests.post(url, headers=h, json=json, timeout=timeout)\n            _log(f\"{method} {url} v{ver} ->\", r.status_code)\n            if r.status_code in (400,404):\n                continue\n            if r.status_code == 429:\n                time.sleep(0.5); continue\n            r.raise_for_status()\n            if r.content:\n                try: return r.json()\n                except Exception: return {}\n            return {}\n        except Exception as e:\n            last_exc = e\n    if last_exc: raise last_exc\n    return {}\n\ndef _me_xuid(headers: Dict) -> Optional[str]:\n    try:\n        data = _request_json(\"https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag\", headers, versions=(3,2,1))\n        pu = (data.get(\"profileUsers\") or [{}])[0]\n        return str(pu.get(\"id\") or \"\")\n    except Exception as e:\n        _log(\"xuid lookup failed:\", repr(e)); return None\n\ndef _fetch_friends(headers: Dict) -> List[Dict]:\n    urls = [\n        \"https://peoplehub.xboxlive.com/users/me/people/social\",\n        \"https://peoplehub.xboxlive.com/users/me/people\",\n        \"https://social.xboxlive.com/users/me/people\",\n    ]\n    me = _me_xuid(headers)\n    if me:\n        urls.insert(0, f\"https://peoplehub.xboxlive.com/users/xuid({me})/people/social\")\n        urls.insert(1, f\"https://peoplehub.xboxlive.com/users/xuid({me})/people/social/summary\")\n\n    for url in urls:\n        try:\n            data = _request_json(url, headers, versions=(6,5,4,3,2,1))\n            arr = data.get(\"people\") or data.get(\"peopleList\") or data.get(\"friends\") or data.get(\"summary\") or []\n            out = []\n            for p in arr or []:\n                x = str(p.get(\"xuid\") or p.get(\"xboxUserId\") or p.get(\"id\") or \"\")\n                g = p.get(\"gamertag\") or p.get(\"modernGamertag\") or p.get(\"preferredName\") or \"\"\n                out.append({\"xuid\": x, \"gamertag\": g})\n            if out:\n                _log(\"friends from\", url, \"->\", len(out))\n                return out\n        except Exception as e:\n            _log(\"friends error for\", url, \":\", repr(e))\n    return []\n\ndef _resolve_gamertags_batch(headers: Dict, xuids: List[str]) -> Dict[str,str]:\n    if not xuids: return {}\n    url = \"https://profile.xboxlive.com/users/batch/profile/settings\"\n    payload = {\"settings\": [\"Gamertag\"], \"userIds\": [f\"xuid({x})\" for x in xuids]}\n    try:\n        data = _request_json(url, headers, versions=(3,2,1), method=\"POST\", json=payload)\n        m = {}\n        for u in data.get(\"profileUsers\", []):\n            uid = str(u.get(\"id\") or \"\")\n            gt = \"\"\n            for s in u.get(\"settings\", []):\n                if s.get(\"id\") == \"Gamertag\":\n                    gt = s.get(\"value\") or \"\"\n            if uid and gt: m[uid] = gt\n        _log(\"resolved gamertags (batch):\", len(m))\n        return m\n    except Exception as e:\n        _log(\"resolve gt batch failed:\", repr(e)); return {}\n\ndef _resolve_gamertags_slow(headers: Dict, xuids: List[str]) -> Dict[str,str]:\n    out = {}\n    for x in xuids:\n        url = f\"https://profile.xboxlive.com/users/xuid({x})/profile/settings?settings=Gamertag\"\n        try:\n            data = _request_json(url, headers, versions=(3,2,1), method=\"GET\")\n            pu = (data.get(\"profileUsers\") or [{}])[0]\n            uid = str(pu.get(\"id\") or \"\")\n            gt = \"\"\n            for s in pu.get(\"settings\", []):\n                if s.get(\"id\") == \"Gamertag\": gt = s.get(\"value\") or \"\"\n            if uid and gt: out[uid] = gt\n        except Exception as e:\n            _log(\"resolve gt slow failed for\", x, \":\", repr(e))\n        time.sleep(0.05)\n    _log(\"resolved gamertags (slow):\", len(out))\n    return out\n\ndef _extract_title_from_presence(data: dict) -> str:\n    for d in data.get(\"devices\", []):\n        for t in d.get(\"titles\", []):\n            name = t.get(\"name\") or t.get(\"titleName\") or \"\"\n            act = t.get(\"activity\") or {}\n            if t.get(\"placement\") == \"Full\" or act.get(\"richPresence\") or act.get(\"broadcastTitle\"):\n                if name: return name\n    return \"\"\n\ndef _presence_batch(headers: Dict, xuids: List[str]) -> Dict[str, Dict]:\n    result = {}\n    try:\n        payload = {\"users\": [f\"xuid({x})\" for x in xuids], \"level\": \"all\"}\n        data = _request_json(\"https://presence.xboxlive.com/users/batch\", headers, versions=(3,2,1), method=\"POST\", json=payload)\n        users = data.get(\"responses\") or data.get(\"users\") or []\n        for u in users:\n            uid = u.get(\"id\") or u.get(\"xuid\") or \"\"\n            if isinstance(uid, str) and uid.startswith(\"xuid(\"): uid = uid[5:-1]\n            state = u.get(\"state\") or u.get(\"presenceState\") or \"\"\n            title = _extract_title_from_presence(u)\n            if uid: result[str(uid)] = {\"state\": state, \"title\": title}\n        if result:\n            _log(\"presence batch OK:\", len(result))\n            return result\n    except Exception as e:\n        _log(\"presence batch failed:\", repr(e))\n    return {}\n\ndef _presence_slow(headers: Dict, xuids: List[str], progress_cb=None) -> Dict[str, Dict]:\n    result = {}\n    for i, x in enumerate(xuids, 1):\n        url = f\"https://userpresence.xboxlive.com/users/xuid({x})?level=all\"\n        try:\n            data = _request_json(url, headers, versions=(3,2,1), method=\"GET\")\n            state = data.get(\"state\") or data.get(\"presenceState\") or \"\"\n            title = _extract_title_from_presence(data)\n            result[str(x)] = {\"state\": state, \"title\": title}\n            if progress_cb and (i % 10 == 0 or i == len(xuids)):\n                progress_cb(i, len(xuids))\n        except Exception as e:\n            _log(\"presence slow failed for\", x, \":\", repr(e))\n        time.sleep(0.045)\n    _log(\"presence slow collected:\", len(result))\n    return result\n\n# ---------- UI (filterable) ----------\n\nclass TransparencyDialog(QtWidgets.QDialog):\n    def __init__(self, dock: QtWidgets.QWidget):\n        super().__init__(dock)\n        self._dock = dock\n        self.setWindowTitle(\"Transparency\")\n        self.setModal(False)\n        self.resize(320, 100)\n\n        v = QtWidgets.QVBoxLayout(self)\n        self.label = QtWidgets.QLabel(self)\n        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)\n        self.slider.setMinimum(20)   # 20% minimum to avoid disappearing\n        self.slider.setMaximum(100)  # 100% = opaque\n        # initialize from current window opacity\n        current = int(round((dock.windowOpacity() or 1.0) * 100))\n        current = max(self.slider.minimum(), min(self.slider.maximum(), current))\n        self.slider.setValue(current)\n        self._update_label(current)\n\n        self.slider.valueChanged.connect(self._on_change)\n\n        btn_row = QtWidgets.QHBoxLayout()\n        self.btnReset = QtWidgets.QPushButton(\"Reset\")\n        self.btnClose = QtWidgets.QPushButton(\"Close\")\n        btn_row.addStretch(1)\n        btn_row.addWidget(self.btnReset)\n        btn_row.addWidget(self.btnClose)\n\n        v.addWidget(self.label)\n        v.addWidget(self.slider)\n        v.addLayout(btn_row)\n\n        self.btnReset.clicked.connect(self._reset)\n        self.btnClose.clicked.connect(self.close)\n\n    def _update_label(self, val: int):\n        self.label.setText(f\"Opacity: {val}%\")\n\n    def _on_change(self, val: int):\n        try:\n            self._dock.setWindowOpacity(val / 100.0)\n            self._update_label(val)\n            try:\n                self._dock._save_settings(opacity_percent=int(val))\n            except Exception as _e:\n                _log(\"settings write warn:\", repr(_e))\n        except Exception as e:\n            _log(\"opacity change error:\", repr(e))\n\n    def _reset(self):\n        self.slider.setValue(100)\n        try:\n            self._dock._save_settings(opacity_percent=100)\n        except Exception as _e:\n            _log(\"settings write warn:\", repr(_e))\n\nclass FriendsDock(QtWidgets.QDialog):\n\n    # --- Cache helpers (ADD-ONLY) ---\n    # --- Settings helpers (ADD-ONLY) ---\n    def _settings_path(self) -> Path:\n        try:\n            return Path(__file__).resolve().parent / \"friends_settings.json\"\n        except Exception:\n            return Path(\"friends_settings.json\")\n\n    def _load_settings(self) -> dict:\n        try:\n            p = self._settings_path()\n            if not p.exists():\n                return {}\n            raw = p.read_text(encoding=\"utf-8\", errors=\"ignore\")\n            return json.loads(raw) if raw.strip() else {}\n        except Exception as e:\n            _log(\"settings load error:\", repr(e))\n            return {}\n\n    def _save_settings(self, **updates):\n        try:\n            data = self._load_settings()\n            data.update(updates)\n            self._settings_path().write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding=\"utf-8\")\n            _log(\"settings saved:\", updates)\n        except Exception as e:\n            _log(\"settings save error:\", repr(e))\n    # --- end settings helpers ---\n\n    def _cache_path(self) -> Path:\n        try:\n            return Path(__file__).resolve().parent / \"friends_cache.json\"\n        except Exception:\n            return Path(\"friends_cache.json\")\n\n    def _save_cached_rows(self, rows):\n        try:\n            data = [{\"gamertag\": gt, \"status\": st, \"game\": gm} for (gt, st, gm) in (rows or [])]\n            self._cache_path().write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding=\"utf-8\")\n            _log(\"cache saved:\", str(self._cache_path()), len(data), \"rows\")\n        except Exception as e:\n            _log(\"cache save error:\", repr(e))\n\n    def _load_cached_rows(self):\n        try:\n            p = self._cache_path()\n            if not p.exists():\n                return False\n            raw = p.read_text(encoding=\"utf-8\", errors=\"ignore\")\n            arr = json.loads(raw) if raw.strip() else []\n            rows = [(d.get(\"gamertag\",\"\"), d.get(\"status\",\"\"), d.get(\"game\",\"\")) for d in arr]\n            if rows:\n                self.sig_set_rows.emit(rows)\n                self.sig_set_status.emit(f\"Restored {len(rows)} cached friends\")\n                _log(\"cache restored:\", len(rows), \"rows\")\n                return True\n            return False\n        except Exception as e:\n            _log(\"cache load error:\", repr(e))\n            return False\n    # --- end cache helpers ---\n\n    sig_set_status = QtCore.pyqtSignal(str)\n    sig_set_rows = QtCore.pyqtSignal(list)   # list of (gt, status, game)\n    sig_enable_btn = QtCore.pyqtSignal(bool)\n    sig_busy = QtCore.pyqtSignal(bool)\n\n    def __init__(self, parent=None):\n        super().__init__(parent)\n        self.setWindowTitle(\"Xbox Friends\")\n        self.resize(720, 740)\n        # Enable minimize button on title bar\n        try:\n            self.setWindowFlags(self.windowFlags() |\n                                QtCore.Qt.WindowType.WindowMinimizeButtonHint |\n                                QtCore.Qt.WindowType.WindowSystemMenuHint)\n        except Exception as _e:\n            _log(\"minimize flag warn:\", repr(_e))\n        self._full_rows: List[tuple] = []\n\n        v = QtWidgets.QVBoxLayout(self)\n        top = QtWidgets.QHBoxLayout()\n        self.lbl = QtWidgets.QLabel(\"Ready.\")\n        self.view = QtWidgets.QComboBox()\n        self.view.addItems([\"All (Online first)\", \"Online only\"])\n        self.btn = QtWidgets.QPushButton(\"Refresh\")\n        top.addWidget(self.lbl); top.addStretch(1); top.addWidget(QtWidgets.QLabel(\"View:\")); top.addWidget(self.view)\n        # \"Always on top\" toggle (ADD-ONLY)\n        self.chkAlwaysOnTop = QtWidgets.QCheckBox(\"Always on top\")\n        top.addWidget(self.chkAlwaysOnTop)\n        # Busy spinner (indeterminate) \u2014 hidden by default\n        self._busy = QtWidgets.QProgressBar(self)\n        self._busy.setRange(0, 0)\n        self._busy.setTextVisible(False)\n        self._busy.setFixedWidth(80)\n        self._busy.hide()\n        top.insertWidget(1, self._busy)\n        # Auto-refresh timer (1 minute; OFF by default)\n        self._autoRefreshTimer = QtCore.QTimer(self)\n        self._autoRefreshTimer.setInterval(60_000)\n        self._autoRefreshTimer.timeout.connect(self.refresh)\n        self.btnAuth = QtWidgets.QPushButton(\"Sign in / Choose tokens.json\")\n        self.btnRefreshTokenOnly = QtWidgets.QPushButton(\"Refresh token only\")\n        top.addWidget(self.btnAuth); top.addWidget(self.btnRefreshTokenOnly); top.addWidget(self.btn)\n\n        # ---- Settings dropdown (cosmetic only) ----\n        # ---- Settings dropdown (cosmetic only) ----\n        self.btnSettings = QtWidgets.QToolButton()\n        self.btnSettings.setText(\"Settings\")\n        self.btnSettings.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)\n        _menu = QtWidgets.QMenu(self.btnSettings)\n        _a_refresh = _menu.addAction(\"Refresh\"); _a_refresh.triggered.connect(self.refresh)\n        _a_signin  = _menu.addAction(\"Sign in / Choose tokens.json\"); _a_signin.triggered.connect(self._do_auth)\n        _a_rtonly  = _menu.addAction(\"Refresh token only\"); _a_rtonly.triggered.connect(self._refresh_token_only)\n        _a_transp  = _menu.addAction(\"Transparency\u2026\"); _a_transp.triggered.connect(self._open_transparency)\n        self._autoAction = _menu.addAction(\"Auto Refresh (1 minute)\")\n        self._autoAction.setCheckable(True)\n        self._autoAction.setChecked(False)\n        self._autoAction.triggered.connect(self._toggle_auto_refresh)\n        self.btnSettings.setMenu(_menu)\n        top.addWidget(self.btnSettings)\n        try:\n            self.btn.hide(); self.btnAuth.hide(); self.btnRefreshTokenOnly.hide()\n        except Exception:\n            pass\n        # ---- end Settings dropdown ----\n\n        # Hide original buttons (objects remain; signals intact)\n        try:\n            self.btn.hide()\n            self.btnAuth.hide()\n            self.btnRefreshTokenOnly.hide()\n        except Exception as _e:\n            _log(\"hide-buttons warning:\", repr(_e))\n        # ---- end Settings dropdown ----\n\n        v.addLayout(top)\n\n        self.table = QtWidgets.QTableWidget(0, 3)\n        self.table.setHorizontalHeaderLabels([\"Gamertag\", \"Status\", \"Game\"])\n        self.table.horizontalHeader().setStretchLastSection(True)\n        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)\n        v.addWidget(self.table, 1)\n\n        self.btn.clicked.connect(self.refresh)\n        self.btnAuth.clicked.connect(self._do_auth)\n        self.btnRefreshTokenOnly.clicked.connect(self._refresh_token_only)\n        self.view.currentIndexChanged.connect(self._reapply_filter)\n        self.view.currentIndexChanged.connect(lambda _i: self._save_settings(view_index=int(_i)))\n        self.chkAlwaysOnTop.toggled.connect(self._apply_always_on_top)\n\n        self.sig_set_status.connect(self._set_status)\n        self.sig_set_rows.connect(self._receive_full_rows)\n        self.sig_enable_btn.connect(self.btn.setEnabled)\n        self.sig_busy.connect(self._busy.setVisible)\n\n        # Load and apply persistent settings (opacity, auto-refresh)\n        try:\n            _s = self._load_settings()\n            # Apply opacity\n            _op = int(_s.get(\"opacity_percent\", 100))\n            _op = max(20, min(100, _op))\n            self.setWindowOpacity(_op / 100.0)\n            # Apply auto-refresh state\n            _auto = bool(_s.get(\"auto_refresh\", False))\n            if hasattr(self, \"_autoAction\"):\n                self._autoAction.setChecked(_auto)\n            if _auto:\n                self._autoRefreshTimer.start()\n            # Apply view filter index\n            try:\n                _vi = int(_s.get(\"view_index\", 0))\n                if 0 <= _vi < self.view.count():\n                    self.view.setCurrentIndex(_vi)\n            except Exception:\n                pass\n            # Apply 'Always on top'\n            _aot = bool(_s.get(\"always_on_top\", False))\n            if hasattr(self, 'chkAlwaysOnTop'):\n                self.chkAlwaysOnTop.setChecked(_aot)\n            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, _aot)\n            self.show()\n        except Exception as _e:\n            _log(\"apply settings warn:\", repr(_e))\n\n        # Show cached rows immediately (if available) before first refresh\n        try:\n            _had_cache = self._load_cached_rows()\n        except Exception as _e:\n            _had_cache = False\n            _log(\"warm restore warn:\", repr(_e))\n        if not _had_cache:\n            QtCore.QTimer.singleShot(150, self.refresh)\n\n    def _set_status(self, s: str):\n        self.lbl.setText(s); _log(\"status:\", s)\n\n    def _receive_full_rows(self, rows: List[tuple]):\n        # rows already have \"Online first\" order\n        self._full_rows = rows\n        self._reapply_filter()\n\n    def _reapply_filter(self):\n        rows = self._full_rows\n        if self.view.currentIndex() == 1:  # Online only\n            rows = [r for r in rows if r[1] == \"Online\"]\n        self._apply_rows(rows)\n\n\n    # --- Status LED helpers (ADD-ONLY) ---\n    def _build_led_icon(self, color: QtCore.Qt.GlobalColor) -> QtWidgets.QStyle.StandardPixmap | QtWidgets.QStyle:\n        # Create a small circular pixmap to act as an LED\n        pm = QtGui.QPixmap(14, 14)\n        pm.fill(QtCore.Qt.GlobalColor.transparent)\n        painter = QtGui.QPainter(pm)\n        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)\n        brush = QtGui.QBrush(color)\n        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black)\n        pen.setWidth(1)\n        painter.setPen(pen)\n        painter.setBrush(brush)\n        painter.drawEllipse(1, 1, 12, 12)\n        painter.end()\n        return QtGui.QIcon(pm)\n\n    def _icon_for_state(self, st: str) -> QtGui.QIcon:\n        try:\n            if not hasattr(self, \"_led_green\"):\n                self._led_green = self._build_led_icon(QtCore.Qt.GlobalColor.green)\n                self._led_red   = self._build_led_icon(QtCore.Qt.GlobalColor.red)\n                self._led_blank = self._build_led_icon(QtCore.Qt.GlobalColor.gray)\n        except Exception:\n            pass\n        s = (st or \"\").strip().lower()\n        if s == \"online\":\n            return getattr(self, \"_led_green\", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogApplyButton))\n        elif s == \"offline\":\n            return getattr(self, \"_led_red\", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogCancelButton))\n        return getattr(self, \"_led_blank\", QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation))\n    # --- end Status LED helpers ---\n\n    def _apply_rows(self, rows: List[tuple]):\n        self.table.setSortingEnabled(False)\n        self.table.setRowCount(len(rows))\n        for i,(gt,st,gm) in enumerate(rows):\n            # Gamertag text\n            self.table.setItem(i,0, QtWidgets.QTableWidgetItem(gt))\n            # Status LED (icon only)\n            _status_item = QtWidgets.QTableWidgetItem(\"\")\n            try:\n                _status_item.setIcon(self._icon_for_state(st))\n                _status_item.setText(\"\")  # no text, icon only\n                _status_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)\n            except Exception:\n                _status_item.setText(st)\n            self.table.setItem(i,1, _status_item)\n            # Game text\n            self.table.setItem(i,2, QtWidgets.QTableWidgetItem(gm))\n        self.table.setSortingEnabled(True)\n        # Keep consistent order: Online first (already), within that alphabetically\n        self.table.sortItems(1, QtCore.Qt.SortOrder.AscendingOrder)\n\n\n    def _apply_always_on_top(self, checked: bool):\n        try:\n            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, bool(checked))\n            self.show()  # re-apply flags\n            try:\n                self._save_settings(always_on_top=bool(checked))\n            except Exception as _e:\n                _log(\"settings write warn:\", repr(_e))\n        except Exception as e:\n            _log(\"always on top apply error:\", repr(e))\n\n    def _open_transparency(self):\n        try:\n            if not hasattr(self, \"_transparencyDlg\") or self._transparencyDlg is None:\n                self._transparencyDlg = TransparencyDialog(self)\n            self._transparencyDlg.show()\n            self._transparencyDlg.raise_()\n            self._transparencyDlg.activateWindow()\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Error\", f\"Transparency error: {e}\")\n\n    def _refresh_token_only(self):\n        \"\"\"\n        Run xbl_login_standalone_v3.py to refresh tokens, then prompt where the new token was saved.\n        \"\"\"\n        try:\n            self.sig_enable_btn.emit(False)\n            self.sig_set_status.emit(\"Refreshing token via login helper...\")\n\n            base = Path(__file__).resolve().parent\n            helper = base / \"xbl_login_standalone_v3.py\"\n            if not helper.exists():\n                QtWidgets.QMessageBox.critical(self, \"Missing helper\", \"xbl_login_standalone_v3.py not found next to this script.\")\n                self.sig_enable_btn.emit(True)\n                return\n\n            proc = subprocess.run([sys.executable, str(helper)], cwd=str(base), capture_output=True, text=True)\n            out = (proc.stdout or \"\") + \"\\n\" + (proc.stderr or \"\")\n            if proc.returncode != 0:\n                QtWidgets.QMessageBox.critical(self, \"Refresh failed\", f\"Helper exited with {proc.returncode}.\\n\\nOutput (tail):\\n{out[-2000:]}\")\n                self.sig_enable_btn.emit(True)\n                return\n\n            # Parse output to find the saved tokens file\n            tokens_path = None\n            for line in out.splitlines():\n                s = line.strip()\n                if s.startswith(\"[Info] Tokens file:\"):\n                    tokens_path = s.split(\":\", 1)[1].strip()\n                    break\n            if not tokens_path:\n                # Fallback to typical default\n                tokens_path = str(Path(os.environ.get(\"LOCALAPPDATA\", Path.home())) / \"OpenXbox\" / \"xbox\" / \"tokens.json\")\n\n            # Prompt user where it was saved and offer to use it now\n            msg = QtWidgets.QMessageBox(self)\n            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)\n            msg.setWindowTitle(\"Token refreshed\")\n            msg.setText(f\"New tokens were saved here:\\n{tokens_path}\\n\\nUse this tokens.json now?\")\n            yes_btn = msg.addButton(\"Use now\", QtWidgets.QMessageBox.ButtonRole.AcceptRole)\n            no_btn = msg.addButton(\"Cancel\", QtWidgets.QMessageBox.ButtonRole.RejectRole)\n            msg.exec()\n            if msg.clickedButton() is yes_btn:\n                os.environ[\"XBL_TOKENS_PATH\"] = tokens_path\n                self.sig_set_status.emit(\"Using refreshed tokens. Reloading\u2026\")\n                QtCore.QTimer.singleShot(200, self.refresh)\n            else:\n                self.sig_enable_btn.emit(True)\n\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Error\", str(e))\n            self.sig_enable_btn.emit(True)\n\n    def _do_auth(self):\n        \"\"\"\n        Opens a small chooser:\n        - Use existing tokens.json (browse & load)\n        - Run device sign-in helper to create a new tokens.json\n        \"\"\"\n        try:\n            default_path = os.environ.get(\"XBL_TOKENS_PATH\") or str((Path.cwd() / \"tokens.json\"))\n            # Simple chooser via QMessageBox-style buttons\n            dlg = QtWidgets.QMessageBox(self)\n            dlg.setIcon(QtWidgets.QMessageBox.Icon.Question)\n            dlg.setWindowTitle(\"Xbox sign-in / tokens.json\")\n            dlg.setText(\"How would you like to provide tokens?\")\n            use_existing = dlg.addButton(\"Use existing tokens.json\u2026\", QtWidgets.QMessageBox.ButtonRole.AcceptRole)\n            run_helper  = dlg.addButton(\"Run device sign-in\u2026\", QtWidgets.QMessageBox.ButtonRole.ActionRole)\n            cancel_btn  = dlg.addButton(\"Cancel\", QtWidgets.QMessageBox.ButtonRole.RejectRole)\n            # PyQt6: exec()\n            dlg.exec()\n            clicked = dlg.clickedButton()\n            if clicked is cancel_btn:\n                return\n\n            if clicked is use_existing:\n                path, _ = QtWidgets.QFileDialog.getOpenFileName(\n                    self, \"Select tokens.json\", default_path, \"JSON Files (*.json);;All Files (*)\"\n                )\n                if not path:\n                    return\n                # point the app to this file and refresh\n                os.environ[\"XBL_TOKENS_PATH\"] = path\n                self.sig_set_status.emit(\"Using selected tokens.json. Reloading\u2026\")\n                QtCore.QTimer.singleShot(200, self.refresh)\n                return\n\n            # Otherwise run helper to produce a new tokens.json\n            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(\n                self, \"Save tokens.json\", default_path, \"JSON Files (*.json);;All Files (*)\"\n            )\n            if not save_path:\n                return\n\n            self.sig_enable_btn.emit(False)\n            self.sig_set_status.emit(\"Starting device sign-in\u2026 follow the console/device code flow\")\n\n            base = Path(__file__).resolve().parent\n            helper = None\n            for name in [\"xbl_auth_device_any.py\", \"xbl_login_standalone_v3.py\", \"xbl_signin_from_oauth_tokens.py\"]:\n                cand = base / name\n                if cand.exists():\n                    helper = str(cand)\n                    break\n            if helper is None:\n                QtWidgets.QMessageBox.critical(\n                    self, \"Missing helper\",\n                    \"Could not find a sign-in helper (xbl_auth_device_any.py or xbl_login_standalone_v3.py).\"\n                )\n                self.sig_enable_btn.emit(True)\n                return\n\n            import subprocess, sys\n            proc = subprocess.run([sys.executable, helper, \"--out\", save_path], cwd=str(base))\n            if proc.returncode != 0:\n                QtWidgets.QMessageBox.critical(self, \"Sign-in failed\", f\"Auth helper exited with code {proc.returncode}.\")\n                self.sig_enable_btn.emit(True)\n                return\n\n            os.environ[\"XBL_TOKENS_PATH\"] = save_path\n            self.sig_set_status.emit(\"Token saved. Reloading\u2026\")\n            QtCore.QTimer.singleShot(200, self.refresh)\n\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Error\", str(e))\n            self.sig_enable_btn.emit(True)\n\n\n    def _toggle_auto_refresh(self):\n        try:\n            if self._autoRefreshTimer.isActive():\n                self._autoRefreshTimer.stop()\n                if hasattr(self, '_autoAction') and self._autoAction:\n                    self._autoAction.setChecked(False)\n                self.sig_set_status.emit(\"Auto Refresh: OFF\")\n                try:\n                    self._save_settings(auto_refresh=False)\n                except Exception as _e:\n                    _log(\"settings write warn:\", repr(_e))\n            else:\n                self._autoRefreshTimer.start()\n                if hasattr(self, '_autoAction') and self._autoAction:\n                    self._autoAction.setChecked(True)\n                self.sig_set_status.emit(\"Auto Refresh: ON (every 1 min)\")\n                try:\n                    self._save_settings(auto_refresh=True)\n                except Exception as _e:\n                    _log(\"settings write warn:\", repr(_e))\n        except Exception as e:\n            QtWidgets.QMessageBox.critical(self, \"Auto Refresh Error\", str(e))\n\n    def refresh(self):\n        self.sig_enable_btn.emit(False); self.sig_set_status.emit(\"\"); self.sig_busy.emit(True); self.sig_set_rows.emit([])\n\n        def _run():\n            try:\n                # ----- auth\n                tpath = _find_tokens_path()\n                if not tpath:\n                    raise RuntimeError(\"tokens.json not found. Set XBL_TOKENS_PATH or place tokens.json next to the script.\")\n                _log(\"Using tokens.json at:\", str(tpath))\n                headers = _build_auth_from_tokens(tpath)\n\n                # ----- friends list\n                friends = _fetch_friends(headers)\n                if not friends:\n                    raise RuntimeError(\"No friends returned (service/permissions).\")\n\n                self.sig_set_status.emit(f\"{len(friends)} friends (resolving names...)\")\n\n                # ----- gamertags\n                missing = [f[\"xuid\"] for f in friends if f.get(\"xuid\") and not f.get(\"gamertag\")]\n                gmap = _resolve_gamertags_batch(headers, missing) if missing else {}\n                if missing and len(gmap) < len(missing):\n                    slow_needed = [x for x in missing if x not in gmap]\n                    if slow_needed:\n                        gmap.update(_resolve_gamertags_slow(headers, slow_needed))\n                for f in friends:\n                    if not f.get(\"gamertag\"):\n                        f[\"gamertag\"] = gmap.get(f.get(\"xuid\",\"\"), f.get(\"xuid\",\"\"))\n\n                self.sig_set_status.emit(f\"{len(friends)} friends (loading presence...)\")\n\n                # ----- presence\n                xuids = [f[\"xuid\"] for f in friends if f.get(\"xuid\")]\n                pres = _presence_batch(headers, xuids) if xuids else {}\n                if xuids and len(pres) < len(xuids):\n                    def _progress(i, n):\n                        self.sig_set_status.emit(f\"{len(friends)} friends (presence {i}/{n})\")\n                    pres.update(_presence_fast(headers, [x for x in xuids if x not in pres], _progress, workers=24))\n\n                rows = []\n                for f in friends:\n                    x = f.get(\"xuid\",\"\"); gt = f.get(\"gamertag\") or x\n                    p = pres.get(x, {})\n                    state = \"Online\" if str(p.get(\"state\",\"\")).lower()==\"online\" else (\"Offline\" if p else \"\")\n                    title = p.get(\"title\",\"\")\n                    rows.append((gt, state, title))\n                rows.sort(key=lambda r: (r[1]!=\"Online\", r[0].lower()))\n\n                self.sig_set_rows.emit(rows)\n                try:\n                    self._save_cached_rows(rows)\n                except Exception as _e:\n                    _log(\"cache post-refresh warn:\", repr(_e))\n                self.sig_set_status.emit(f\"{len(rows)} friends (presence applied)\")\n                self.sig_busy.emit(False)\n                self.sig_enable_btn.emit(True)\n\n            except Exception as e:\n                _log(\"Error:\", repr(e))\n                self.sig_set_status.emit(f\"Error: {e.__class__.__name__}: {e}\")\n                self.sig_busy.emit(False)\n                self.sig_enable_btn.emit(True)\n\n        threading.Thread(target=_run, daemon=True).start()\ndef _presence_fast(headers: Dict, xuids: List[str], progress_cb=None, workers: int = 24) -> Dict[str, Dict]:\n    \"\"\"Concurrent presence fetch using a shared Session. Keeps requests gentle but parallel.\"\"\"\n    import concurrent.futures, time, math\n    result = {}\n    if not xuids:\n        return result\n\n    # Shared session with connection pool\n    sess = requests.Session()\n    try:\n        from requests.adapters import HTTPAdapter\n        from urllib3.util.retry import Retry\n        adapter = HTTPAdapter(pool_connections=workers*2, pool_maxsize=workers*2, max_retries=0)\n        sess.mount(\"https://\", adapter); sess.mount(\"http://\", adapter)\n    except Exception:\n        pass\n\n    base_headers = dict(headers)\n    base_headers[\"x-xbl-contract-version\"] = \"3\"\n    url_tpl = \"https://userpresence.xboxlive.com/users/xuid({})?level=all\"\n\n    # Gentle concurrency: cap workers, backoff on 429, shorter timeout\n    def fetch_one(xuid: str):\n        url = url_tpl.format(xuid)\n        tries = 0\n        delay = 0.3\n        while True:\n            tries += 1\n            try:\n                r = sess.get(url, headers=base_headers, timeout=8)\n                status = r.status_code\n                if status == 429:\n                    # Too many requests; back off a bit and retry\n                    time.sleep(delay)\n                    delay = min(delay * 1.6, 3.0)\n                    if tries < 5:\n                        continue\n                if status in (400, 404):\n                    return xuid, {}\n                r.raise_for_status()\n                j = r.json() if r.content else {}\n                state = j.get(\"state\") or j.get(\"presenceState\") or \"\"\n                title = _extract_title_from_presence(j)\n                return xuid, {\"state\": state, \"title\": title}\n            except Exception:\n                if tries < 3:\n                    time.sleep(delay)\n                    delay = min(delay * 1.6, 3.0)\n                    continue\n                return xuid, {}\n\n    done = 0\n    report_every = max(10, len(xuids)//15)  # ~15 updates max\n    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 48))) as ex:\n        for xuid, info in ex.map(fetch_one, xuids):\n            done += 1\n            if info:\n                result[str(xuid)] = info\n            if progress_cb and (done % report_every == 0 or done == len(xuids)):\n                progress_cb(done, len(xuids))\n\n    _log(\"presence fast collected:\", len(result))\n    try:\n        sess.close()\n    except Exception:\n        pass\n    return result\n\n\ndef main():\n    _log(\"Starting Xbox Friends Dock (INLINE v5)\")\n    app = QtWidgets.QApplication(sys.argv)\n    w = FriendsDock(); w.show()\n    rc = app.exec()\n    _log(\"App exit code:\", rc); sys.exit(rc)\n\nif __name__ == \"__main__\":\n    main()", "xbl/xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED.py")
_register_module("xbl_login_standalone_v3", "\n# xbl_login_standalone_v3.py \u2014 Sign in to Xbox Live and save tokens\n# Usage: py xbl_login_standalone_v3.py\nimport os, sys, asyncio, urllib.parse as up\n\nfrom pythonxbox.authentication.manager import AuthenticationManager\nfrom pythonxbox.authentication.models import OAuth2TokenResponse\nfrom pythonxbox.common.signed_session import SignedSession\n\nDESKTOP_REDIRECT = \"https://login.live.com/oauth20_desktop.srf\"\n\ndef _tokens_path() -> str:\n    try:\n        from platformdirs import user_data_dir\n        base = user_data_dir(appname=\"xbox\", appauthor=\"OpenXbox\", roaming=False)\n    except Exception:\n        base = os.path.join(os.environ.get(\"LOCALAPPDATA\", os.path.expanduser(\"~\")), \"OpenXbox\", \"xbox\")\n    os.makedirs(base, exist_ok=True)\n    return os.path.join(base, \"tokens.json\")\n\ndef _client_constants():\n    try:\n        from pythonxbox.scripts import CLIENT_ID, CLIENT_SECRET\n        return CLIENT_ID, CLIENT_SECRET\n    except Exception:\n        return \"000000004C12AE6F\", \"\"  # public client ID, no secret\n\nTOKENS_FILE = _tokens_path()\nCLIENT_ID, CLIENT_SECRET = _client_constants()\n\ndef _extract_code(val: str) -> str:\n    s = val.strip()\n    if not s:\n        return \"\"\n    if s.lower().startswith(\"http\"):\n        q = up.urlparse(s).query\n        qs = up.parse_qs(q)\n        return (qs.get(\"code\") or [\"\"])[0]\n    # If they pasted a raw code with extra params like \"&lc=1033\", trim after first '&'\n    if \"&\" in s and not s.lower().startswith(\"microsoft\"):\n        s = s.split(\"&\", 1)[0]\n    return s\n\nasync def amain():\n    async with SignedSession() as session:\n        auth = AuthenticationManager(session, CLIENT_ID, CLIENT_SECRET, DESKTOP_REDIRECT)\n\n        # Try refresh existing tokens\n        try:\n            with open(TOKENS_FILE, \"r\", encoding=\"utf-8\") as f:\n                tokens_json = f.read()\n            auth.oauth = OAuth2TokenResponse.model_validate_json(tokens_json)\n            try:\n                await auth.refresh_tokens()\n                with open(TOKENS_FILE, \"w\", encoding=\"utf-8\") as f:\n                    f.write(auth.oauth.json())\n                print(\"[OK] Already signed in. Tokens refreshed.\")\n                print(f\"[Info] Tokens file: {TOKENS_FILE}\")\n                return\n            except Exception:\n                pass\n        except FileNotFoundError:\n            pass\n\n        # Start auth\n        url = auth.generate_authorization_url()\n        print(\"=== Xbox Sign\u2011In ===\")\n        print(\"1) Open this URL in a browser:\")\n        print(url)\n        print(\"2) Approve sign\u2011in; you will be redirected. If you see a code or a URL with '?code=', copy it.\")\n        val = input(\"3) Paste the code (or full URL) here, then press Enter: \").strip()\n        code = _extract_code(val)\n        if not code:\n            print(\"[CANCELLED] No code detected.\")\n            sys.exit(1)\n\n        try:\n            tokens = await auth.request_oauth_token(code)\n        except Exception as e:\n            print(\"[ERROR] Token exchange failed.\\n\"\n                  \"Tips:\\n\"\n                  \"  \u2022 Paste a **fresh** code (codes are single\u2011use).\\n\"\n                  \"  \u2022 If you pasted a code with '&lc=...', only paste up to the first '&'.\\n\"\n                  \"  \u2022 Or paste the **entire** redirected URL that contains '?code=...'\\n\"\n                  f\"Detail: {e}\", file=sys.stderr)\n            sys.exit(1)\n\n        auth.oauth = tokens\n        with open(TOKENS_FILE, \"w\", encoding=\"utf-8\") as f:\n            f.write(tokens.json())\n        print(\"[OK] Signed in and tokens saved.\")\n        print(f\"[Info] Tokens file: {TOKENS_FILE}\")\n\ndef main():\n    try:\n        asyncio.run(amain())\n    except KeyboardInterrupt:\n        print(\"\\n[Cancelled]\")\n    except Exception as e:\n        print(f\"[ERROR] {e}\", file=sys.stderr)\n        raise\n\nif __name__ == \"__main__\":\n    main()\n", "xbl_login_standalone_v3.py")
_register_module("xbl.xbl_login_standalone_v3", "\n# xbl_login_standalone_v3.py \u2014 Sign in to Xbox Live and save tokens\n# Usage: py xbl_login_standalone_v3.py\nimport os, sys, asyncio, urllib.parse as up\n\nfrom pythonxbox.authentication.manager import AuthenticationManager\nfrom pythonxbox.authentication.models import OAuth2TokenResponse\nfrom pythonxbox.common.signed_session import SignedSession\n\nDESKTOP_REDIRECT = \"https://login.live.com/oauth20_desktop.srf\"\n\ndef _tokens_path() -> str:\n    try:\n        from platformdirs import user_data_dir\n        base = user_data_dir(appname=\"xbox\", appauthor=\"OpenXbox\", roaming=False)\n    except Exception:\n        base = os.path.join(os.environ.get(\"LOCALAPPDATA\", os.path.expanduser(\"~\")), \"OpenXbox\", \"xbox\")\n    os.makedirs(base, exist_ok=True)\n    return os.path.join(base, \"tokens.json\")\n\ndef _client_constants():\n    try:\n        from pythonxbox.scripts import CLIENT_ID, CLIENT_SECRET\n        return CLIENT_ID, CLIENT_SECRET\n    except Exception:\n        return \"000000004C12AE6F\", \"\"  # public client ID, no secret\n\nTOKENS_FILE = _tokens_path()\nCLIENT_ID, CLIENT_SECRET = _client_constants()\n\ndef _extract_code(val: str) -> str:\n    s = val.strip()\n    if not s:\n        return \"\"\n    if s.lower().startswith(\"http\"):\n        q = up.urlparse(s).query\n        qs = up.parse_qs(q)\n        return (qs.get(\"code\") or [\"\"])[0]\n    # If they pasted a raw code with extra params like \"&lc=1033\", trim after first '&'\n    if \"&\" in s and not s.lower().startswith(\"microsoft\"):\n        s = s.split(\"&\", 1)[0]\n    return s\n\nasync def amain():\n    async with SignedSession() as session:\n        auth = AuthenticationManager(session, CLIENT_ID, CLIENT_SECRET, DESKTOP_REDIRECT)\n\n        # Try refresh existing tokens\n        try:\n            with open(TOKENS_FILE, \"r\", encoding=\"utf-8\") as f:\n                tokens_json = f.read()\n            auth.oauth = OAuth2TokenResponse.model_validate_json(tokens_json)\n            try:\n                await auth.refresh_tokens()\n                with open(TOKENS_FILE, \"w\", encoding=\"utf-8\") as f:\n                    f.write(auth.oauth.json())\n                print(\"[OK] Already signed in. Tokens refreshed.\")\n                print(f\"[Info] Tokens file: {TOKENS_FILE}\")\n                return\n            except Exception:\n                pass\n        except FileNotFoundError:\n            pass\n\n        # Start auth\n        url = auth.generate_authorization_url()\n        print(\"=== Xbox Sign\u2011In ===\")\n        print(\"1) Open this URL in a browser:\")\n        print(url)\n        print(\"2) Approve sign\u2011in; you will be redirected. If you see a code or a URL with '?code=', copy it.\")\n        val = input(\"3) Paste the code (or full URL) here, then press Enter: \").strip()\n        code = _extract_code(val)\n        if not code:\n            print(\"[CANCELLED] No code detected.\")\n            sys.exit(1)\n\n        try:\n            tokens = await auth.request_oauth_token(code)\n        except Exception as e:\n            print(\"[ERROR] Token exchange failed.\\n\"\n                  \"Tips:\\n\"\n                  \"  \u2022 Paste a **fresh** code (codes are single\u2011use).\\n\"\n                  \"  \u2022 If you pasted a code with '&lc=...', only paste up to the first '&'.\\n\"\n                  \"  \u2022 Or paste the **entire** redirected URL that contains '?code=...'\\n\"\n                  f\"Detail: {e}\", file=sys.stderr)\n            sys.exit(1)\n\n        auth.oauth = tokens\n        with open(TOKENS_FILE, \"w\", encoding=\"utf-8\") as f:\n            f.write(tokens.json())\n        print(\"[OK] Signed in and tokens saved.\")\n        print(f\"[Info] Tokens file: {TOKENS_FILE}\")\n\ndef main():\n    try:\n        asyncio.run(amain())\n    except KeyboardInterrupt:\n        print(\"\\n[Cancelled]\")\n    except Exception as e:\n        print(f\"[ERROR] {e}\", file=sys.stderr)\n        raise\n\nif __name__ == \"__main__\":\n    main()\n", "xbl/xbl_login_standalone_v3.py")
_register_module("xbl_profile_widget", "\nfrom __future__ import annotations\nimport sys, os, threading, time\nfrom pathlib import Path\nfrom urllib.parse import urlparse, urlunparse, urlencode, parse_qs, quote\nfrom PyQt6 import QtWidgets, QtCore\nfrom PyQt6.QtGui import QPixmap\nimport requests\n\n_HEADERS_INJECTED = None\n\ndef set_global_xbl_headers(h):\n    global _HEADERS_INJECTED\n    _HEADERS_INJECTED = h\n\ndef _possible_token_paths():\n    paths = []\n    env = os.environ.get(\"XBL_TOKENS_PATH\")\n    if env:\n        paths.append(Path(env))\n    paths.append(Path(os.getcwd()) / \"tokens.json\")\n    try:\n        here = Path(__file__).resolve().parent\n        paths.append(here / \"tokens.json\")\n    except Exception:\n        pass\n    local = Path(os.environ.get(\"LOCALAPPDATA\", Path.home())) / \"OpenXbox\" / \"xbox\" / \"tokens.json\"\n    paths.append(local)\n    return paths\n\ndef _read_headers_from_tokens():\n    from xbl_signin_from_oauth_tokens import get_xsts_from_tokens\n    last_err = None\n    for p in _possible_token_paths():\n        try:\n            if p.is_file():\n                print(f\"[xbl_profile_widget] using tokens.json at: {p}\")\n                info = get_xsts_from_tokens(str(p))\n                h = {\"Authorization\": info[\"Authorization\"], \"x-xbl-contract-version\": \"3\", \"Accept\": \"application/json\"}\n                return h\n        except Exception as e:\n            last_err = e\n            print(f\"[xbl_profile_widget] failed tokens at {p}: {e}\")\n    if last_err:\n        raise last_err\n    raise FileNotFoundError(\"tokens.json not found in any known location.\")\n\ndef _get_headers():\n    if _HEADERS_INJECTED:\n        h = dict(_HEADERS_INJECTED)\n        h.setdefault(\"Accept\", \"application/json\")\n        h.setdefault(\"x-xbl-contract-version\", \"3\")\n        return h\n    try:\n        return _read_headers_from_tokens()\n    except Exception as e:\n        print(\"[xbl_profile_widget] header load error:\", e)\n        return None\n\ndef _fetch_profile(headers):\n    url = \"https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag,GameDisplayPicRaw\"\n    print(\"[xbl_profile_widget] GET profile:\", url)\n    r = requests.get(url, headers=headers, timeout=8)\n    print(\"[xbl_profile_widget] profile status:\", r.status_code)\n    r.raise_for_status()\n    data = r.json()\n    user = (data.get(\"profileUsers\") or [None])[0] or {}\n    settings = {s.get(\"id\"): s.get(\"value\") for s in user.get(\"settings\", [])}\n    return settings.get(\"Gamertag\") or \"(unknown)\", settings.get(\"GameDisplayPicRaw\")\n\ndef _avatar_variants(u: str):\n    variants = []\n    try:\n        parsed = urlparse(u)\n        q = parse_qs(parsed.query)\n        inner = q.get(\"url\", [\"\"])[0]\n        if inner and (\"%2F\" not in inner and \"://\" in inner):\n            inner = quote(inner, safe=\"\")\n        base_q = {\"url\": inner} if inner else {}\n        size_opts = [\n            {\"w\": \"64\", \"h\": \"64\", \"format\": \"png\"},\n            {\"w\": \"128\", \"h\": \"128\", \"format\": \"png\"},\n            {\"w\": \"208\", \"h\": \"208\", \"format\": \"png\"},\n        ]\n        hosts = [\"images-eds-ssl.xboxlive.com\", \"images-eds.xboxlive.com\"]\n        for h in hosts:\n            for so in size_opts:\n                qd = dict(base_q); qd.update(so)\n                new = parsed._replace(scheme=\"https\", netloc=h, query=urlencode(qd, doseq=True), path=\"/image\")\n                variants.append(urlunparse(new))\n        variants.append(u)\n    except Exception:\n        variants.append(u)\n    seen = set(); out = []\n    for v in variants:\n        if v not in seen:\n            out.append(v); seen.add(v)\n    return out\n\ndef _download_avatar(url: str, timeout: int = 8) -> QPixmap | None:\n    ua = {\"User-Agent\": \"Mozilla/5.0\", \"Accept\": \"image/*\"}\n    variants = _avatar_variants(url)\n    last_err = None\n    for i, v in enumerate(variants, 1):\n        try:\n            print(f\"[xbl_profile_widget] avatar try {i}/{len(variants)}:\", v)\n            r = requests.get(v, headers=ua, timeout=8, allow_redirects=True)\n            print(\"[xbl_profile_widget] avatar status:\", r.status_code, \"len:\", len(r.content))\n            r.raise_for_status()\n            if not r.content:\n                raise RuntimeError(\"empty image\")\n            pm = QPixmap()\n            if pm.loadFromData(r.content):\n                return pm\n            last_err = RuntimeError(\"QPixmap load failed\")\n        except Exception as e:\n            last_err = e\n            print(f\"[xbl_profile_widget] avatar error:\", e)\n            time.sleep(0.1 if i < len(variants) else 0)\n    if last_err:\n        print(f\"[xbl_profile_widget] avatar failed: {last_err}\")\n    return None\n\nclass XboxProfileWidget(QtWidgets.QWidget):\n    profileReady = QtCore.pyqtSignal(str)     # gamertag\n    profileError = QtCore.pyqtSignal()\n    avatarReady  = QtCore.pyqtSignal(object)  # QPixmap\n\n    def __init__(self, parent=None):\n        super().__init__(parent)\n        row = QtWidgets.QHBoxLayout(self)\n        row.setContentsMargins(0,0,0,0)\n        self.lbl_avatar = QtWidgets.QLabel()\n        self.lbl_avatar.setFixedSize(48, 48)\n        self.lbl_avatar.setStyleSheet(\"border-radius:10px;background:#222;\")\n        self.lbl_name = QtWidgets.QLabel(\"<i>Not signed in</i>\")\n        self.lbl_name.setMinimumWidth(160)\n        self.btn_refresh = QtWidgets.QPushButton(\"Refresh\")\n        row.addWidget(self.lbl_avatar)\n        row.addSpacing(8)\n        row.addWidget(self.lbl_name)\n        row.addStretch(1)\n        row.addWidget(self.btn_refresh)\n\n        self._refreshing = False\n        self.btn_refresh.clicked.connect(self.refresh)\n\n        # Connect signals to UI slots (runs on main thread)\n        self.profileReady.connect(self._on_profile_ready)\n        self.profileError.connect(self._on_profile_error)\n        self.avatarReady.connect(self._on_avatar_ready)\n\n        QtCore.QTimer.singleShot(0, self.refresh)\n\n    def set_headers(self, headers: dict | None):\n        set_global_xbl_headers(headers)\n\n    @QtCore.pyqtSlot(str)\n    def _on_profile_ready(self, gamertag: str):\n        self.lbl_name.setText(gamertag)\n        self._refreshing = False\n\n    @QtCore.pyqtSlot()\n    def _on_profile_error(self):\n        self.lbl_name.setText(\"Profile error\")\n        self._refreshing = False\n\n    @QtCore.pyqtSlot(object)\n    def _on_avatar_ready(self, pm: QPixmap):\n        scaled = pm.scaled(48, 48, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation)\n        self.lbl_avatar.setPixmap(scaled)\n\n    def refresh(self):\n        if self._refreshing:\n            return\n        self._refreshing = True\n        self.lbl_name.setText(\"Fetching...\")\n\n        def run_profile():\n            headers = _get_headers()\n            if not headers:\n                self.profileError.emit()\n                return\n            try:\n                gt, pic = _fetch_profile(headers)\n                self.profileReady.emit(gt)  # emit immediately (no timer races)\n                if pic:\n                    def run_avatar():\n                        pm = _download_avatar(pic, timeout=8)\n                        if pm:\n                            self.avatarReady.emit(pm)\n                    threading.Thread(target=run_avatar, daemon=True).start()\n            except Exception as e:\n                print(\"[xbl_profile_widget] profile fetch error:\", e)\n                self.profileError.emit()\n        threading.Thread(target=run_profile, daemon=True).start()\n\nif __name__ == \"__main__\":\n    app = QtWidgets.QApplication(sys.argv)\n    w = QtWidgets.QWidget()\n    w.setWindowTitle(\"Xbox Profile\")\n    lay = QtWidgets.QVBoxLayout(w)\n    lay.setContentsMargins(12,12,12,12)\n    lay.addWidget(XboxProfileWidget())\n    w.resize(320, 80)\n    w.show()\n    sys.exit(app.exec())\n", "xbl_profile_widget.py")
_register_module("xbl.xbl_profile_widget", "\nfrom __future__ import annotations\nimport sys, os, threading, time\nfrom pathlib import Path\nfrom urllib.parse import urlparse, urlunparse, urlencode, parse_qs, quote\nfrom PyQt6 import QtWidgets, QtCore\nfrom PyQt6.QtGui import QPixmap\nimport requests\n\n_HEADERS_INJECTED = None\n\ndef set_global_xbl_headers(h):\n    global _HEADERS_INJECTED\n    _HEADERS_INJECTED = h\n\ndef _possible_token_paths():\n    paths = []\n    env = os.environ.get(\"XBL_TOKENS_PATH\")\n    if env:\n        paths.append(Path(env))\n    paths.append(Path(os.getcwd()) / \"tokens.json\")\n    try:\n        here = Path(__file__).resolve().parent\n        paths.append(here / \"tokens.json\")\n    except Exception:\n        pass\n    local = Path(os.environ.get(\"LOCALAPPDATA\", Path.home())) / \"OpenXbox\" / \"xbox\" / \"tokens.json\"\n    paths.append(local)\n    return paths\n\ndef _read_headers_from_tokens():\n    from xbl_signin_from_oauth_tokens import get_xsts_from_tokens\n    last_err = None\n    for p in _possible_token_paths():\n        try:\n            if p.is_file():\n                print(f\"[xbl_profile_widget] using tokens.json at: {p}\")\n                info = get_xsts_from_tokens(str(p))\n                h = {\"Authorization\": info[\"Authorization\"], \"x-xbl-contract-version\": \"3\", \"Accept\": \"application/json\"}\n                return h\n        except Exception as e:\n            last_err = e\n            print(f\"[xbl_profile_widget] failed tokens at {p}: {e}\")\n    if last_err:\n        raise last_err\n    raise FileNotFoundError(\"tokens.json not found in any known location.\")\n\ndef _get_headers():\n    if _HEADERS_INJECTED:\n        h = dict(_HEADERS_INJECTED)\n        h.setdefault(\"Accept\", \"application/json\")\n        h.setdefault(\"x-xbl-contract-version\", \"3\")\n        return h\n    try:\n        return _read_headers_from_tokens()\n    except Exception as e:\n        print(\"[xbl_profile_widget] header load error:\", e)\n        return None\n\ndef _fetch_profile(headers):\n    url = \"https://profile.xboxlive.com/users/me/profile/settings?settings=Gamertag,GameDisplayPicRaw\"\n    print(\"[xbl_profile_widget] GET profile:\", url)\n    r = requests.get(url, headers=headers, timeout=8)\n    print(\"[xbl_profile_widget] profile status:\", r.status_code)\n    r.raise_for_status()\n    data = r.json()\n    user = (data.get(\"profileUsers\") or [None])[0] or {}\n    settings = {s.get(\"id\"): s.get(\"value\") for s in user.get(\"settings\", [])}\n    return settings.get(\"Gamertag\") or \"(unknown)\", settings.get(\"GameDisplayPicRaw\")\n\ndef _avatar_variants(u: str):\n    variants = []\n    try:\n        parsed = urlparse(u)\n        q = parse_qs(parsed.query)\n        inner = q.get(\"url\", [\"\"])[0]\n        if inner and (\"%2F\" not in inner and \"://\" in inner):\n            inner = quote(inner, safe=\"\")\n        base_q = {\"url\": inner} if inner else {}\n        size_opts = [\n            {\"w\": \"64\", \"h\": \"64\", \"format\": \"png\"},\n            {\"w\": \"128\", \"h\": \"128\", \"format\": \"png\"},\n            {\"w\": \"208\", \"h\": \"208\", \"format\": \"png\"},\n        ]\n        hosts = [\"images-eds-ssl.xboxlive.com\", \"images-eds.xboxlive.com\"]\n        for h in hosts:\n            for so in size_opts:\n                qd = dict(base_q); qd.update(so)\n                new = parsed._replace(scheme=\"https\", netloc=h, query=urlencode(qd, doseq=True), path=\"/image\")\n                variants.append(urlunparse(new))\n        variants.append(u)\n    except Exception:\n        variants.append(u)\n    seen = set(); out = []\n    for v in variants:\n        if v not in seen:\n            out.append(v); seen.add(v)\n    return out\n\ndef _download_avatar(url: str, timeout: int = 8) -> QPixmap | None:\n    ua = {\"User-Agent\": \"Mozilla/5.0\", \"Accept\": \"image/*\"}\n    variants = _avatar_variants(url)\n    last_err = None\n    for i, v in enumerate(variants, 1):\n        try:\n            print(f\"[xbl_profile_widget] avatar try {i}/{len(variants)}:\", v)\n            r = requests.get(v, headers=ua, timeout=8, allow_redirects=True)\n            print(\"[xbl_profile_widget] avatar status:\", r.status_code, \"len:\", len(r.content))\n            r.raise_for_status()\n            if not r.content:\n                raise RuntimeError(\"empty image\")\n            pm = QPixmap()\n            if pm.loadFromData(r.content):\n                return pm\n            last_err = RuntimeError(\"QPixmap load failed\")\n        except Exception as e:\n            last_err = e\n            print(f\"[xbl_profile_widget] avatar error:\", e)\n            time.sleep(0.1 if i < len(variants) else 0)\n    if last_err:\n        print(f\"[xbl_profile_widget] avatar failed: {last_err}\")\n    return None\n\nclass XboxProfileWidget(QtWidgets.QWidget):\n    profileReady = QtCore.pyqtSignal(str)     # gamertag\n    profileError = QtCore.pyqtSignal()\n    avatarReady  = QtCore.pyqtSignal(object)  # QPixmap\n\n    def __init__(self, parent=None):\n        super().__init__(parent)\n        row = QtWidgets.QHBoxLayout(self)\n        row.setContentsMargins(0,0,0,0)\n        self.lbl_avatar = QtWidgets.QLabel()\n        self.lbl_avatar.setFixedSize(48, 48)\n        self.lbl_avatar.setStyleSheet(\"border-radius:10px;background:#222;\")\n        self.lbl_name = QtWidgets.QLabel(\"<i>Not signed in</i>\")\n        self.lbl_name.setMinimumWidth(160)\n        self.btn_refresh = QtWidgets.QPushButton(\"Refresh\")\n        row.addWidget(self.lbl_avatar)\n        row.addSpacing(8)\n        row.addWidget(self.lbl_name)\n        row.addStretch(1)\n        row.addWidget(self.btn_refresh)\n\n        self._refreshing = False\n        self.btn_refresh.clicked.connect(self.refresh)\n\n        # Connect signals to UI slots (runs on main thread)\n        self.profileReady.connect(self._on_profile_ready)\n        self.profileError.connect(self._on_profile_error)\n        self.avatarReady.connect(self._on_avatar_ready)\n\n        QtCore.QTimer.singleShot(0, self.refresh)\n\n    def set_headers(self, headers: dict | None):\n        set_global_xbl_headers(headers)\n\n    @QtCore.pyqtSlot(str)\n    def _on_profile_ready(self, gamertag: str):\n        self.lbl_name.setText(gamertag)\n        self._refreshing = False\n\n    @QtCore.pyqtSlot()\n    def _on_profile_error(self):\n        self.lbl_name.setText(\"Profile error\")\n        self._refreshing = False\n\n    @QtCore.pyqtSlot(object)\n    def _on_avatar_ready(self, pm: QPixmap):\n        scaled = pm.scaled(48, 48, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, QtCore.Qt.TransformationMode.SmoothTransformation)\n        self.lbl_avatar.setPixmap(scaled)\n\n    def refresh(self):\n        if self._refreshing:\n            return\n        self._refreshing = True\n        self.lbl_name.setText(\"Fetching...\")\n\n        def run_profile():\n            headers = _get_headers()\n            if not headers:\n                self.profileError.emit()\n                return\n            try:\n                gt, pic = _fetch_profile(headers)\n                self.profileReady.emit(gt)  # emit immediately (no timer races)\n                if pic:\n                    def run_avatar():\n                        pm = _download_avatar(pic, timeout=8)\n                        if pm:\n                            self.avatarReady.emit(pm)\n                    threading.Thread(target=run_avatar, daemon=True).start()\n            except Exception as e:\n                print(\"[xbl_profile_widget] profile fetch error:\", e)\n                self.profileError.emit()\n        threading.Thread(target=run_profile, daemon=True).start()\n\nif __name__ == \"__main__\":\n    app = QtWidgets.QApplication(sys.argv)\n    w = QtWidgets.QWidget()\n    w.setWindowTitle(\"Xbox Profile\")\n    lay = QtWidgets.QVBoxLayout(w)\n    lay.setContentsMargins(12,12,12,12)\n    lay.addWidget(XboxProfileWidget())\n    w.resize(320, 80)\n    w.show()\n    sys.exit(app.exec())\n", "xbl/xbl_profile_widget.py")
_register_module("xbl_signin_from_oauth_tokens", "\nimport json, requests, pathlib, os\n\nXBL_USER_AUTH = \"https://user.auth.xboxlive.com/user/authenticate\"\nXBL_XSTS_AUTH = \"https://xsts.auth.xboxlive.com/xsts/authorize\"\n\ndef get_xsts_from_tokens(tokens_path):\n    tokens_path = pathlib.Path(tokens_path)\n    data = json.loads(tokens_path.read_text())\n    access = data[\"access_token\"]\n    # user token\n    payload_user = {\n        \"RelyingParty\": \"http://auth.xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"AuthMethod\": \"RPS\",\n            \"SiteName\": \"user.auth.xboxlive.com\",\n            \"RpsTicket\": f\"d={access}\"\n        }\n    }\n    r = requests.post(XBL_USER_AUTH, json=payload_user, headers={\"Content-Type\":\"application/json\"})\n    r.raise_for_status()\n    j = r.json()\n    user_token = j[\"Token\"]\n    uhs = j[\"DisplayClaims\"][\"xui\"][0][\"uhs\"]\n\n    # xsts\n    payload_xsts = {\n        \"RelyingParty\": \"http://xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"UserTokens\": [user_token],\n            \"SandboxId\": \"RETAIL\"\n        }\n    }\n    r2 = requests.post(XBL_XSTS_AUTH, json=payload_xsts, headers={\"Content-Type\":\"application/json\"})\n    r2.raise_for_status()\n    j2 = r2.json()\n    xsts = j2[\"Token\"]\n    uhs2 = j2[\"DisplayClaims\"][\"xui\"][0][\"uhs\"]\n    return {\"Authorization\": f\"XBL3.0 x={uhs2};{xsts}\"}\n", "xbl_signin_from_oauth_tokens.py")
_register_module("xbl.xbl_signin_from_oauth_tokens", "\nimport json, requests, pathlib, os\n\nXBL_USER_AUTH = \"https://user.auth.xboxlive.com/user/authenticate\"\nXBL_XSTS_AUTH = \"https://xsts.auth.xboxlive.com/xsts/authorize\"\n\ndef get_xsts_from_tokens(tokens_path):\n    tokens_path = pathlib.Path(tokens_path)\n    data = json.loads(tokens_path.read_text())\n    access = data[\"access_token\"]\n    # user token\n    payload_user = {\n        \"RelyingParty\": \"http://auth.xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"AuthMethod\": \"RPS\",\n            \"SiteName\": \"user.auth.xboxlive.com\",\n            \"RpsTicket\": f\"d={access}\"\n        }\n    }\n    r = requests.post(XBL_USER_AUTH, json=payload_user, headers={\"Content-Type\":\"application/json\"})\n    r.raise_for_status()\n    j = r.json()\n    user_token = j[\"Token\"]\n    uhs = j[\"DisplayClaims\"][\"xui\"][0][\"uhs\"]\n\n    # xsts\n    payload_xsts = {\n        \"RelyingParty\": \"http://xboxlive.com\",\n        \"TokenType\": \"JWT\",\n        \"Properties\": {\n            \"UserTokens\": [user_token],\n            \"SandboxId\": \"RETAIL\"\n        }\n    }\n    r2 = requests.post(XBL_XSTS_AUTH, json=payload_xsts, headers={\"Content-Type\":\"application/json\"})\n    r2.raise_for_status()\n    j2 = r2.json()\n    xsts = j2[\"Token\"]\n    uhs2 = j2[\"DisplayClaims\"][\"xui\"][0][\"uhs\"]\n    return {\"Authorization\": f\"XBL3.0 x={uhs2};{xsts}\"}\n", "xbl/xbl_signin_from_oauth_tokens.py")


# === Embedded patches to avoid external helper files ===
try:
    import xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED as _fd
    # Resolve FriendsDock class
    FriendsDock = getattr(_fd, "FriendsDock", None)
    if FriendsDock is not None:
        def _embedded_refresh_token_only(self):
            # Mirror UI signals where possible
            try:
                self.sig_enable_btn.emit(False)
            except Exception:
                pass
            try:
                self.sig_set_status.emit("Refreshing token via embedded helper...")
            except Exception:
                pass
            # Prefer standalone login helper (embedded)
            _m = None
            try:
                import xbl_login_standalone_v3 as _m
            except Exception:
                try:
                    import xbl.xbl_login_standalone_v3 as _m
                except Exception:
                    _m = None
            ok = False
            if _m is not None and hasattr(_m, "main"):
                try:
                    _m.main()
                    ok = True
                except SystemExit:
                    ok = True
                except Exception as e:
                    ok = False
            # Notify
            msg = "Xbox token refresh complete." if ok else "Xbox token refresh failed."
            try:
                from PyQt6.QtWidgets import QMessageBox as _QMB6
                _QMB6.information(self, "Xbox token", msg)
            except Exception:
                try:
                    from PyQt5.QtWidgets import QMessageBox as _QMB5
                    _QMB5.information(self, "Xbox token", msg)
                except Exception:
                    print(msg)
            try:
                self.sig_enable_btn.emit(True)
            except Exception:
                pass

        def _embedded_do_auth(self):
            try:
                self.sig_enable_btn.emit(False)
            except Exception:
                pass
            try:
                self.sig_set_status.emit("Starting embedded sign-in...")
            except Exception:
                pass
            # Prefer device-code auth if present; otherwise fall back to login helper
            _m = None
            for name in ("xbl_auth_device_any", "xbl_login_standalone_v3"):
                try:
                    _m = __import__(name)
                    break
                except Exception:
                    try:
                        _m = __import__("xbl." + name, fromlist=["*"])
                        break
                    except Exception:
                        _m = None
            ok = False
            if _m is not None and hasattr(_m, "main"):
                try:
                    _m.main()
                    ok = True
                except SystemExit:
                    ok = True
                except Exception:
                    ok = False
            # Finalize
            try:
                self.sig_enable_btn.emit(True)
            except Exception:
                pass
            if not ok:
                try:
                    from PyQt6.QtWidgets import QMessageBox as _Q
                    _Q.critical(self, "Sign-in failed", "Embedded sign-in helper failed to run.")
                except Exception:
                    try:
                        from PyQt5.QtWidgets import QMessageBox as _Q
                        _Q.critical(self, "Sign-in failed", "Embedded sign-in helper failed to run.")
                    except Exception:
                        print("Embedded sign-in helper failed to run.")

        # Apply monkey patches
        FriendsDock._refresh_token_only = _embedded_refresh_token_only
        FriendsDock._do_auth = _embedded_do_auth
except Exception as _e:
    # Non-fatal; app will still run and can fall back to original behavior
    pass
# === End embedded patches ===

# === Begin main app (executed at top-level) ===

# === Add-only: PyQt5->PyQt6 runtime shim & exclude real PyQt5 at build time ===
# Purpose: some helpers still `import PyQt5.*`. We ship only PyQt6 and provide a shim.
try:
    import sys, types
    import PyQt6.QtWidgets as _Q6W
    import PyQt6.QtCore as _Q6C
    import PyQt6.QtGui as _Q6G
    _pyqt5 = types.ModuleType("PyQt5")
    _pyqt5.QtWidgets = _Q6W
    _pyqt5.QtCore = _Q6C
    _pyqt5.QtGui = _Q6G
    # expose into sys.modules so `from PyQt5 import QtWidgets` works
    sys.modules.setdefault("PyQt5", _pyqt5)
    sys.modules.setdefault("PyQt5.QtWidgets", _Q6W)
    sys.modules.setdefault("PyQt5.QtCore", _Q6C)
    sys.modules.setdefault("PyQt5.QtGui", _Q6G)
except Exception:
    pass
# === End shim ===


# === Add-only: XBL compat shims (package path, legacy import alias, token loader) ===

# === Add-only: SSL certs for frozen builds ===
try:
    import certifi, os as _os
    _ca = certifi.where()
    _os.environ.setdefault("SSL_CERT_FILE", _ca)
    _os.environ.setdefault("REQUESTS_CA_BUNDLE", _ca)
except Exception:
    pass
# === End SSL certs ===

import sys, os, json
from pathlib import Path

def _app_root():
    try:
        if getattr(sys, "frozen", False):
            return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return Path(__file__).parent
    except Exception:
        return Path.cwd()

# Make sure `xbl` package is importable
if str(_app_root()) not in sys.path:
    sys.path.insert(0, str(_app_root()))

# Back-compat alias: allow old code `import xbl_signin_from_oauth_tokens`
try:
    import importlib
    _alias = importlib.import_module("xbl.xbl_signin_from_oauth_tokens")
    import types as _types
    if "xbl_signin_from_oauth_tokens" not in sys.modules:
        sys.modules["xbl_signin_from_oauth_tokens"] = _alias
except Exception:
    pass

def _xbl_user_dir():
    base = os.environ.get("LOCALAPPDATA", str(Path.home()))
    p = Path(base) / "OpenXbox" / "xbox"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _xbl_tokens_get():
    candidates = [
        _app_root() / "tokens.json",
        Path.cwd() / "tokens.json",
        _xbl_user_dir() / "tokens.json",
    ]
    for c in candidates:
        try:
            if c.exists():
                return json.loads(c.read_text(encoding="utf-8")), c
        except Exception:
            continue
    return None, candidates[-1]
# === End compat shims ===

# === Add-only: more legacy import aliases for moved helpers ===
try:
    import importlib, sys as _sys
    def _alias_mod(old_name, new_qualname):
        try:
            mod = importlib.import_module(new_qualname)
            if old_name not in _sys.modules:
                _sys.modules[old_name] = mod
        except Exception:
            pass

    # legacy names -> new package paths
    _alias_mod("xbl_profile_widget", "xbl.xbl_profile_widget")
    _alias_mod("xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED", "xbl.xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED")
    _alias_mod("xbl_auth_device_any", "xbl.xbl_auth_device_any")
except Exception:
    pass
# === End aliases ===



# === Add-only: XBL token refresh that prefers helper inside an "xbl" folder ===
import sys, subprocess, os, json
from pathlib import Path

# === Add-only: helper loader (no subprocess) ===
def _exe_dir():
    import sys
    from pathlib import Path
    try:
        return Path(sys.executable).parent
    except Exception:
        return Path.cwd()

def _ensure_exe_dir_on_syspath():
    import sys
    p = str(_exe_dir())
    if p not in sys.path:
        sys.path.insert(0, p)

def _load_helper_module_from_path(helper_path):
    """Load a .py module from disk in-process (works in frozen EXE)."""
    try:
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location("xbl_login_standalone_v3_dyn", str(helper_path))
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

def _run_xbl_helper_inline(parent=None):
    """
    Order:
      1) ENV XBL_HELPER_DIR
      2) import from xbl package (with exe_dir on sys.path)
      3) load from file in exe_dir/xbl, _MEIPASS/xbl, cwd/xbl
    """
    import os, sys
    from pathlib import Path

    helper_file = "xbl_login_standalone_v3.py"

    # 0) ENV
    env_dir = os.environ.get("XBL_HELPER_DIR")
    if env_dir:
        hp = Path(env_dir) / helper_file
        if hp.exists():
            mod = _load_helper_module_from_path(hp)
            if mod and hasattr(mod, "main"):
                try:
                    mod.main()
                except SystemExit:
                    pass
                return True

    # 1) import package
    try:
        _ensure_exe_dir_on_syspath()  # allow import from sibling xbl next to EXE
        from xbl import xbl_login_standalone_v3 as _m
        try:
            _m.main()
        except SystemExit:
            pass
        return True
    except Exception:
        pass

    # 2) load from common locations
    candidates = []
    # exe_dir/xbl
    candidates.append(_exe_dir() / "xbl" / helper_file)
    # _MEIPASS/xbl
    try:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / "xbl" / helper_file)
    except Exception:
        pass
    # cwd/xbl
    candidates.append(Path.cwd() / "xbl" / helper_file)

    for hp in candidates:
        if hp.exists():
            mod = _load_helper_module_from_path(hp)
            if mod and hasattr(mod, "main"):
                try:
                    mod.main()
                except SystemExit:
                    pass
                return True

    return False
# === End helper loader ===


def _xbl_user_dir():
    base = os.environ.get("LOCALAPPDATA", str(Path.home()))
    p = Path(base) / "OpenXbox" / "xbox"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _is_frozen():
    return getattr(sys, "frozen", False)

def _app_root():
    if _is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    # Use this file's directory as root in dev
    try:
        return Path(__file__).parent
    except NameError:
        return Path.cwd()

def _try_import_run_helper_from_xbl():
    """
    Try importing xbl.xbl_login_standalone_v3 and calling main().
    Works if you package the helper as a module (preferred).
    """
    try:
        import importlib
        mod = importlib.import_module("xbl.xbl_login_standalone_v3")
        if hasattr(mod, "main"):
            try:
                mod.main()
            except SystemExit:
                pass
        return True
    except Exception:
        return False


def _helper_candidates():
    root = _app_root()
    cand = [
        root / "xbl" / "xbl_login_standalone_v3.py",
        Path.cwd() / "xbl" / "xbl_login_standalone_v3.py",
        root / "xbl_login_standalone_v3.py",  # last resort
    ]
    return [p for p in cand if p.exists()]


def _try_spawn_helper_from_xbl_folder():
    """
    Fallback: run a loose helper script placed in an 'xbl' subfolder.
    Works in dev and in PyInstaller if you add-data the folder.
    """
    root = _app_root()
    for hp in _helper_candidates():
        if hp.exists():
            try:
                subprocess.run([sys.executable, str(hp)], cwd=str(hp.parent), timeout=180)
                return True
            except Exception:
                pass
    return False

def refresh_xbl_token(parent=None):
    """
    1) Prefer importing xbl.xbl_login_standalone_v3 and running main()
    2) Else spawn xbl/xbl_login_standalone_v3.py if present
    3) Tokens live in %LOCALAPPDATA%/OpenXbox/xbox/tokens.json
    """
    ok = _try_import_run_helper_from_xbl()
    if not ok:
        ok = _try_spawn_helper_from_xbl_folder()

    tok = _xbl_user_dir() / "tokens.json"
    exists = tok.exists()

    lines = [
        "Token refresh " + ("succeeded." if (ok and exists) else "may have failed."),
        "Tokens path:",
        str(tok),
    ]
    msg = "\n".join(lines)

    # Try Qt info box, else print
    try:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(parent, "Xbox token", msg)
    except Exception:
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(parent, "Xbox token", msg)
        except Exception:
            print(msg)
# === End add-only block ===

import sys, os, time, json, ctypes, subprocess, threading
from datetime import datetime
from PyQt6 import QtWidgets, QtCore, QtGui

# === ADD-ONLY: Minimal ThemeManager (Xbox green/black) ===
from PyQt6 import QtWidgets as _QW6
class ThemeManager:
    def __init__(self, app):
        self.app = app
    def apply(self, name: str):
        if name == "xbox_original":
            qss = """
            QWidget { background-color: #0b0f0c; color: #e9f0e8; selection-background-color: #107C10; }
            QMenuBar, QMenu { background-color: #0e140f; color: #e9f0e8; }
            QMenuBar::item:selected, QMenu::item:selected { background-color: #107C10; }
            QPushButton, QToolButton, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #121712; color: #e9f0e8; border: 1px solid #1a8f13; border-radius: 6px; padding: 5px 8px;
            }
            QPushButton:hover, QToolButton:hover, QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {
                border: 1px solid #2fae27;
            }
            QHeaderView::section { background-color: #101510; color: #cfe5cf; border: 1px solid #1a8f13; padding: 4px; }
            QTableView, QTreeView, QTableWidget, QTreeWidget { gridline-color: #1a8f13; background-color: #0d120d; alternate-background-color: #111711; }
            QScrollBar::handle { background: #107C10; border-radius: 4px; min-height: 20px; min-width: 20px; }
            QProgressBar { background-color: #0e140f; border: 1px solid #1a8f13; border-radius: 6px; text-align: center; color: #e9f0e8; }
            QProgressBar::chunk { background-color: #107C10; margin: 1px; border-radius: 5px; }
            """
        else:
            qss = ""
        try:
            self.app.setStyleSheet(qss)
        except Exception:
            pass
# === END ADD-ONLY ThemeManager ===

import os
from pathlib import Path

# ---- XBL token helpers (shared) ----
def _discover_tokens_path():
    # 1) explicit env
    p = os.environ.get("XBL_TOKENS_PATH")
    if p and Path(p).is_file():
        return p
    # 2) working dir
    p2 = Path(os.getcwd()) / "tokens.json"
    if p2.is_file():
        return str(p2)
    # 3) next to this script
    p3 = Path(__file__).with_name("tokens.json")
    if p3.is_file():
        return str(p3)
    # 4) OpenXbox default
    p4 = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "OpenXbox" / "xbox" / "tokens.json"
    if p4.is_file():
        return str(p4)
    return None




# Xbox Friends dock (import with fallback launcher)
import subprocess, sys as _sys
from pathlib import Path as _Path
try:
    from xbl_friends_dock import FriendsDock as _FriendsDock
except Exception:
    _FriendsDock = None
def _launch_friends_popup_external():
    # Launch standalone dock as separate process so UI never blocks
    exe = _sys.executable
    here = _Path(__file__).parent
    candidates = [
        here / "xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED.py",
        here / "xbl_friends_dock_INLINE_v5_REFRESH_UI_v2.py",
        here / "xbl_friends_dock.py",
    ]
    for popup in candidates:
        if popup.exists():
            try:
                subprocess.Popen([exe, str(popup)], close_fds=True)
                return
            except Exception:
                continue
    # nothing worked
    return

# Optional Xbox Friends dock
try:
    # Try several module names for the friends dock
    FriendsDock = None
    try:
        from xbl_friends_dock import FriendsDock as _FD
        FriendsDock = _FD
    except Exception:
        try:
            from xbl_friends_dock_INLINE_v5_REFRESH_UI_v2_PATCHED import FriendsDock as _FD
            FriendsDock = _FD
        except Exception:
            try:
                from xbl_friends_dock_INLINE_v5_REFRESH_UI_v2 import FriendsDock as _FD
                FriendsDock = _FD
            except Exception:
                FriendsDock = None
except Exception:
    FriendsDock = None

# --- Optional Xbox profile widget ---
try:
    from xbl_profile_widget import XboxProfileWidget
except Exception:
    XboxProfileWidget = None


# ---- Xbox Live helpers (optional) ----
# Prefer existing tokens.json (OpenXbox) if present; fallback to device-code helper.
_XBL_IMPORT_ERR = ""
_XBL_IMPORT_OK = False
_XBL_TOKENS_OK = False
try:
    from xbl_signin_from_oauth_tokens import get_xsts_from_tokens as _xbl_tokens_get
    _XBL_TOKENS_OK = True
except Exception as _e:
    _XBL_IMPORT_ERR = str(_e)

try:
    from xbl_signin_standalone import get_xsts as _xbl_get_xsts
    _XBL_IMPORT_OK = True
except Exception as _e:
    if not _XBL_IMPORT_ERR:
        _XBL_IMPORT_ERR = str(_e)


# ================== Config ==================
UWPHOOK_EXE = ""  # no default path; will be resolved at runtime and saved in settings.json

# ---- UWPHook path resolver (first-run friendly) ----
def _resolve_uwphook_path(parent=None):
    """
    Return a valid path to UWPHook.exe.
    Order:
      1) settings.json → 'uwphook_path'
      2) same folder as this script
      3) prompt the user to locate it (then persist to settings.json)
    """
    try:
        settings = load_settings()
    except Exception:
        settings = {}

    # Candidates in priority order
    candidates = []
    p = (settings or {}).get("uwphook_path", "").strip()
    if p:
        candidates.append(p)
    try:
        here = str(Path(__file__).parent / "UWPHook.exe")
        candidates.append(here)
    except Exception:
        pass

    for c in candidates:
        try:
            if c and os.path.isfile(c):
                if (settings or {}).get("uwphook_path") != c:
                    try:
                        s = dict(settings or {})
                        s["uwphook_path"] = c
                        save_settings(s)
                    except Exception:
                        pass
                return c
        except Exception:
            pass

    # Not found → ask user
    try:
        from PyQt6 import QtWidgets
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent,
            "Locate UWPHook.exe",
            str(Path.home()),
            "UWPHook.exe (UWPHook.exe);;Executables (*.exe);;All Files (*)",
        )
        if fname and os.path.basename(fname).lower() == "uwphook.exe" and os.path.isfile(fname):
            try:
                s = dict(settings or {})
                s["uwphook_path"] = fname
                save_settings(s)
            except Exception:
                pass
            return fname
    except Exception:
        pass
    return ""


# Default flags used when "Use Flags" is checked (per-game flags live in games.json)
DEFAULT_FLAGS    = []



# -------- Discord RPC defaults (public; safe to ship) --------
DISCORD_CLIENT_ID_DEFAULT = "1434331516422455296"   # your Discord Application ID
DISCORD_ENABLED_DEFAULT   = True                    # auto-enable by default
# ============= Paths =============
BASE_DIR        = os.path.dirname(__file__)
GAMES_DB_PATH   = os.path.join(BASE_DIR, "games.json")
SETTINGS_PATH   = os.path.join(BASE_DIR, "settings.json")

# Kernel32 / Affinity / Priority
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
OpenProcess = kernel32.OpenProcess
SetPriorityClass = kernel32.SetPriorityClass
SetProcessAffinityMask = kernel32.SetProcessAffinityMask
CloseHandle = kernel32.CloseHandle

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_INFORMATION           = 0x0200

HIGH_PRIORITY_CLASS  = 0x00000080
NORMAL_PRIORITY_CLASS= 0x00000020

# ============= Games persistence =============
def _seed_defaults():
    # Two seed entries as examples
    return [
        {
            "name": "Gears of War Reloaded",
            "aumid": "Microsoft.Pender_8wekyb3d8bbwe!Launch.GOWDE",
            "exe_name": "Launch_GOWDE.exe",
            "flags": DEFAULT_FLAGS[:],
            "mask_hex": "",                # blank -> auto (all CPUs except CPU0)
            "use_flags": True,
            "high_priority": True,
            "apply_affinity": True,
        },
        {
            "name": "Gears 5",
            "aumid": "Microsoft.HalifaxBaseGame_8wekyb3d8bbwe!GearGameShippingInternal",
            "exe_name": "Gears5_EAC.exe",
            "flags": DEFAULT_FLAGS[:],
            "mask_hex": "",
            "use_flags": True,
            "high_priority": True,
            "apply_affinity": True,
        }
    ]

def load_games():
    try:
        with open(GAMES_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Normalize flags field into list
                try:
                    for __g in data:
                        __f = __g.get('flags', [])
                        if isinstance(__f, str):
                            __g['flags'] = [x for x in __f.strip().split() if x]
                except Exception:
                    pass
                return data
    except Exception:
        pass
    data = _seed_defaults()
    save_games(data)
    return data

def save_games(data):
    try:
        with open(GAMES_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed saving games.json:", e)

def get_game_by_name(name, games):
    for g in games:
        if g.get("name") == name:
            return g
    return None

# ============= Settings persistence (Discord RPC) =============
def _seed_settings():
    return {
        "discord_enabled": DISCORD_ENABLED_DEFAULT,
        "discord_client_id": DISCORD_CLIENT_ID_DEFAULT,
        "discord_details_tpl": "{name}",
        "discord_state_tpl": "HighPrio={high}  Affinity={aff}  Flags={flags}",
    }

def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                base = _seed_settings()
                base.update(data)
                # Fallback order: env var -> file -> hardcoded default
                cid_env = os.environ.get("DISCORD_CLIENT_ID", "").strip()
                if cid_env:
                    base["discord_client_id"] = cid_env
                if not base.get("discord_client_id"):
                    base["discord_client_id"] = DISCORD_CLIENT_ID_DEFAULT
                # If we have an ID, default to enabled
                if base.get("discord_client_id") and base.get("discord_enabled") is False:
                    base["discord_enabled"] = DISCORD_ENABLED_DEFAULT
                return base
    except Exception:
        pass
    data = _seed_settings()
    save_settings(data)
    return data

def save_settings(data):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed saving settings.json:", e)

# ============= Process helpers =============
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', ctypes.c_ulong),
        ('cntUsage', ctypes.c_ulong),
        ('th32ProcessID', ctypes.c_ulong),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', ctypes.c_ulong),
        ('cntThreads', ctypes.c_ulong),
        ('th32ParentProcessID', ctypes.c_ulong),
        ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', ctypes.c_ulong),
        ('szExeFile', ctypes.c_char * 260),
    ]

CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
Process32First           = ctypes.windll.kernel32.Process32First
Process32Next            = ctypes.windll.kernel32.Process32Next
_CloseHandle             = ctypes.windll.kernel32.CloseHandle
TH32CS_SNAPPROCESS       = 0x00000002

def iter_pids_by_name(exe_name: str):
    exe_name_low = exe_name.lower()
    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if hSnapshot == ctypes.c_void_p(-1).value:
        return
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if not Process32First(hSnapshot, ctypes.byref(entry)):
        _CloseHandle(hSnapshot); return
    while True:
        name = entry.szExeFile.decode(errors='ignore').lower()
        if name == exe_name_low:
            yield entry.th32ProcessID
        if not Process32Next(hSnapshot, ctypes.byref(entry)):
            break
    _CloseHandle(hSnapshot)

def compute_mask(mask_hex: str | None) -> int:
    if mask_hex:
        try:
            return int(mask_hex, 16)
        except Exception:
            pass
    # auto: use all CPUs except CPU0
    try:
        import multiprocessing
        n = multiprocessing.cpu_count()
    except Exception:
        n = 8
    if n <= 1:
        return 1
    return (1 << n) - 2  # drop CPU0

def apply_affinity_priority(exe_name: str, mask_hex: str, do_aff: bool, do_high: bool) -> tuple[int,int]:
    mask = compute_mask(mask_hex)
    changed = 0
    for pid in iter_pids_by_name(exe_name):
        access = PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_SET_INFORMATION
        h = OpenProcess(access, False, pid)
        if h:
            try:
                if do_aff:
                    SetProcessAffinityMask(h, ctypes.c_size_t(mask))
                if do_high:
                    SetPriorityClass(h, HIGH_PRIORITY_CLASS)
                changed += 1
            finally:
                CloseHandle(h)
    return changed, mask

# ============= Discord RPC =============
class DiscordManager:
    def __init__(self):
        self.enabled = False
        self.client_id = ""
        self.rpc = None
        self.connected = False
        self.start_time = None

        # Keyboard shortcut: Ctrl+F opens Friends pop-out
        try:
            sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+F'), self)
            sc.activated.connect(_friends_click)
            self._friends_shortcut = sc
        except Exception:
            pass

    def configure(self, enabled: bool, client_id: str):
        self.enabled = bool(enabled)
        self.client_id = (client_id or "").strip()

    def connect(self, log_cb=lambda s: None):
        if not self.enabled or not self.client_id:
            return False
        try:
            from pypresence import Presence  # requires pypresence installed
        except Exception as e:
            log_cb(f"Discord RPC unavailable (pypresence not installed): {e}")
            return False
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            self.start_time = int(time.time())
            log_cb("Discord RPC connected.")
            return True
        except Exception as e:
            log_cb(f"Discord RPC failed to connect: {e}")
            self.connected = False
            return False

    def set_presence(self, details: str, state: str, log_cb=lambda s: None):
        if not self.connected or not self.rpc:
            return
        try:
            self.rpc.update(details=details[:127], state=state[:127], start=self.start_time)
        except Exception as e:
            log_cb(f"Discord RPC update failed: {e}")

    def clear(self, log_cb=lambda s: None):
        if not self.connected or not self.rpc:
            return
        try:
            self.rpc.clear()
            log_cb("Discord RPC cleared.")
        except Exception as e:
            log_cb(f"Discord RPC clear failed: {e}")

    def close(self, log_cb=lambda s: None):
        if not self.connected or not self.rpc:
            return
        try:
            self.rpc.close()
            self.connected = False
            log_cb("Discord RPC closed.")
        except Exception as e:
            log_cb(f"Discord RPC close failed: {e}")

# ============= UWP Sync (Get-StartApps) =============
def get_start_apps_via_powershell():
    """
    Returns list of dicts: [{Name, AppID}, ...] gathered by Get-StartApps.
    Requires PowerShell (Windows 10/11). If not available, returns [].
    """
    try:
        # Ensure powershell is available
        ps = os.environ.get("SystemRoot", r"C:\Windows")
        ps_exe = os.path.join(ps, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
        if not os.path.isfile(ps_exe):
            ps_exe = "powershell"
        cmd = [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
               "Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Depth 3"]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, encoding="utf-8", creationflags=0x08000000 if os.name == "nt" else 0)
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        results = []
        for item in (data or []):
            name = item.get("Name", "")
            appid = item.get("AppID", "")
            if name and appid:
                results.append({"Name": name, "AppID": appid})
        return results
    except Exception:
        return []

class UWPSyncDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sync UWP Apps")
        self.resize(700, 500)
        v = QtWidgets.QVBoxLayout(self)

        self.info = QtWidgets.QLabel("Detected Start Apps (use search to filter). Select one to add as a game profile.")
        v.addWidget(self.info)

        search_row = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search apps...")
        search_row.addWidget(self.search)
        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        search_row.addWidget(self.btn_refresh)
        v.addLayout(search_row)

        self.list = QtWidgets.QListWidget()
        v.addWidget(self.list, 1)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("Add Selected")
        self.btn_close = QtWidgets.QPushButton("Close")
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_close)
        v.addLayout(btn_row)

        self.btn_close.clicked.connect(self.close)
        self.btn_refresh.clicked.connect(self.populate)
        self.search.textChanged.connect(self._apply_filter)
        self.populate()

    def populate(self):
        self.all_items = get_start_apps_via_powershell()
        self._refresh("")

    def _apply_filter(self, text):
        self._refresh(text or "")

    def _refresh(self, query: str):
        q = (query or "").lower()
        self.list.clear()
        for app in (self.all_items or []):
            line = f"{app['Name']}  —  {app['AppID']}"
            if not q or q in line.lower():
                it = QtWidgets.QListWidgetItem(line)
                it.setData(QtCore.Qt.ItemDataRole.UserRole, app)
                self.list.addItem(it)

    def selected_app(self):
        it = self.list.currentItem()
        if not it: return None
        return it.data(QtCore.Qt.ItemDataRole.UserRole)

# ============= UI Editors =============
class GameEditor(QtWidgets.QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Game Settings")
        self.setModal(True)
        self.data = data or {}
        form = QtWidgets.QFormLayout(self)

        self.name = QtWidgets.QLineEdit(self.data.get("name",""))
        self.aumid = QtWidgets.QLineEdit(self.data.get("aumid",""))
        self.exe = QtWidgets.QLineEdit(self.data.get("exe_name",""))
        self.flags = QtWidgets.QLineEdit(" ".join(self.data.get("flags", [])))
        self.mask = QtWidgets.QLineEdit(self.data.get("mask_hex",""))

        self.chk_use_flags = QtWidgets.QCheckBox()
        self.chk_use_flags.setChecked(bool(self.data.get("use_flags", True)))
        self.chk_high = QtWidgets.QCheckBox()
        self.chk_high.setChecked(bool(self.data.get("high_priority", True)))
        self.chk_aff = QtWidgets.QCheckBox()
        self.chk_aff.setChecked(bool(self.data.get("apply_affinity", True)))

        form.addRow("Name", self.name)
        form.addRow("AUMID / UWP ID", self.aumid)
        form.addRow("Game EXE (process)", self.exe)
        form.addRow("Flags (space-separated)", self.flags)
        form.addRow("Affinity Mask (HEX)", self.mask)
        form.addRow("Use Flags", self.chk_use_flags)
        form.addRow("High Priority", self.chk_high)
        form.addRow("Apply Affinity", self.chk_aff)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_data(self):
        return {
            "name": self.name.text().strip(),
            "aumid": self.aumid.text().strip(),
            "exe_name": self.exe.text().strip(),
            "flags": [f for f in self.flags.text().strip().split() if f],
            "mask_hex": self.mask.text().strip(),
            "use_flags": self.chk_use_flags.isChecked(),
            "high_priority": self.chk_high.isChecked(),
            "apply_affinity": self.chk_aff.isChecked(),
        }

class SettingsEditor(QtWidgets.QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings (Discord RPC)")
        self.setModal(True)
        self.settings = dict(settings or {})
        form = QtWidgets.QFormLayout(self)

        self.chk_discord = QtWidgets.QCheckBox()
        self.chk_discord.setChecked(bool(self.settings.get("discord_enabled", False)))
        self.client_id = QtWidgets.QLineEdit(self.settings.get("discord_client_id",""))
        self.details_tpl = QtWidgets.QLineEdit(self.settings.get("discord_details_tpl","{name}"))
        self.state_tpl = QtWidgets.QLineEdit(self.settings.get("discord_state_tpl","HighPrio={high}  Affinity={aff}  Flags={flags}"))

        form.addRow("Enable Discord RPC", self.chk_discord)
        form.addRow("Discord Client ID", self.client_id)
        form.addRow("Details Template", self.details_tpl)
        form.addRow("State Template", self.state_tpl)

        hint = QtWidgets.QLabel("Template vars: {name}, {high}, {aff}, {flags}")
        hint.setStyleSheet("color: gray;")
        form.addRow(hint)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_settings(self):
        return {
            "discord_enabled": self.chk_discord.isChecked(),
            "discord_client_id": self.client_id.text().strip(),
            "discord_details_tpl": self.details_tpl.text().strip() or "{name}",
            "discord_state_tpl": self.state_tpl.text().strip() or "HighPrio={high}  Affinity={aff}  Flags={flags}",
        }

# ============= Worker =============
class Worker(QtCore.QObject):
    progress = QtCore.pyqtSignal(str)
    done = QtCore.pyqtSignal(bool, str)
    presence = QtCore.pyqtSignal(dict)  # {details,str; state,str}

    def __init__(self, game, use_flags: bool, mask_hex: str, do_aff: bool, do_high: bool, extra_flags: list[str], discord_cfg: dict):
        super().__init__()
        self.game = game
        self.use_flags = use_flags
        self.mask_hex = mask_hex
        self.do_aff = do_aff
        self.do_high = do_high
        self.extra_flags = extra_flags or []
        self.discord_cfg = discord_cfg or {}

    def run(self):
        try:
            aumid = self.game.get("aumid","")
            exe = self.game.get("exe_name","")
            base_flags = self.game.get('flags', [])
            if isinstance(base_flags, str): base_flags = [x for x in base_flags.strip().split() if x]
            flags = (base_flags if self.use_flags else []) + self.extra_flags

            uwp_path = _resolve_uwphook_path(None)
            if not uwp_path:
                self.done.emit(False, "UWPHook.exe not found. Please locate it.")
                return
            argv = [uwp_path, aumid, exe] + flags
            self.progress.emit("Launching: " + " ".join(argv))
            subprocess.Popen(argv, close_fds=True)

            # Wait for actual game exe
            t0 = time.time()
            found_once = False
            while time.time() - t0 < 45:
                pids = list(iter_pids_by_name(exe))
                if pids:
                    found_once = True
                    break
                time.sleep(0.5)

            if not found_once:
                self.done.emit(False, f"Could not find process: {exe}")
                return

            changed, mask = apply_affinity_priority(exe, self.mask_hex, self.do_aff, self.do_high)
            self.progress.emit(f"Applied settings to {changed} process(es). Mask=0x{mask:X} High={self.do_high} Affinity={self.do_aff}")

            # Emit Discord presence payload
            try:
                details_tpl = self.discord_cfg.get("discord_details_tpl", "{name}")
                state_tpl   = self.discord_cfg.get("discord_state_tpl", "HighPrio={high}  Affinity={aff}  Flags={flags}")
                show_flags  = " ".join(flags) if flags else "(none)"
                payload = {
                    "details": details_tpl.format(name=self.game.get("name","")),
                    "state":   state_tpl.format(name=self.game.get("name",""), high=self.do_high, aff=self.do_aff, flags=show_flags),
                }
                self.presence.emit(payload)
            except Exception as e:
                self.progress.emit(f"Discord presence formatting failed: {e}")

            self.done.emit(True, "Done.")
        except Exception as e:
            self.done.emit(False, f"Error: {e}")

# ============= Main UI =============
class Main(QtWidgets.QWidget):
    def on_xbox_sign_in(self):
        try:
            self._append("Xbox Live: checking tokens.json...")
            tokens_path = _discover_tokens_path()
            if not tokens_path:
                self._append("Xbox sign-in failed: tokens.json not found. Set XBL_TOKENS_PATH or place tokens.json.")
                QtWidgets.QMessageBox.warning(self, "Xbox Sign-In", "tokens.json not found. Set XBL_TOKENS_PATH or place tokens.json next to the app.")
                return
            info = _xbl_tokens_get(tokens_path)
            auth = info.get("Authorization")
            if not auth:
                raise RuntimeError("helper returned no Authorization")
            self._xbl_headers = {
                "Authorization": auth,
                "Accept": "application/json",
                "x-xbl-contract-version": "3",
            }
            os.environ["XBL_TOKENS_PATH"] = tokens_path
            self._append("Xbox Live: signed in. (source: " + tokens_path + ")")
            try:
                if getattr(self, "xbox_profile", None):
                    self.xbox_profile.set_headers(self._xbl_headers)
                    self.xbox_profile.refresh()
            except Exception as e:
                self._append(f"[xbl_profile_widget] refresh failed: {e}")
            QtWidgets.QMessageBox.information(self, "Xbox Sign-In", "Signed in using:\n" + tokens_path)
        except Exception as e:
            self._append(f"Xbox sign-in failed: {e}")
            QtWidgets.QMessageBox.critical(self, "Xbox Sign-In", f"Failed: {e}")

    
    
    
    
            def _run():
                try:
                    # Prefer tokens.json path if available
                    if _XBL_TOKENS_OK:
                        self._append("Xbox Live: checking tokens.json...")
                        info = _xbl_tokens_get(tokens_path)
                    elif _XBL_IMPORT_OK:
                        self._append("Xbox Live: starting device-code sign-in...")
                        info = _xbl_get_xsts()
                    else:
                        self._append(f"Xbox Live helpers unavailable: {_XBL_IMPORT_ERR or 'no helper installed'}")
                        return
    
                    gt = info.get("gamertag") or "(unknown)"
                    xuid = info.get("xuid") or "(unknown)"
                    self._append(f"Signed in to Xbox Live as {gt}  (XUID: {xuid})")
                    # Save headers for later Xbox API calls
                    self._xbl_headers = {
                        "Authorization": info["Authorization"],
                        "x-xbl-contract-version": "3",
                    }
                    try:
                        if hasattr(self, '_friendsDock') and self._friendsDock:
                            self._friendsDock.set_headers(self._xbl_headers)
                    except Exception:
                        pass
                except Exception as e:
                    self._append(f"Xbox sign-in failed: {e}")
                finally:
                    try:
                        self.btn_xsignin.setDisabled(False)
                    except Exception:
                        pass
    
            import threading
            t = threading.Thread(target=_run, daemon=True)
            t.start()
    
    
        def closeEvent(self, e):
            try:
                self.discord.clear(self._append)
                self.discord.close(self._append)
            except Exception:
                pass
            super().closeEvent(e)
    
        

    def _open_friends(self):
        try:
            if 'FriendsDock' in globals() and FriendsDock:
                try:
                    dlg = FriendsDock(self)
                    dlg.setWindowModality(QtCore.Qt.WindowModality.NonModal)
                    dlg.show()
                    dlg.raise_()
                    dlg.activateWindow()
                    return
                except Exception as e:
                    self._append(f"[friends] inline launch failed: {e}")
            _launch_friends_popup_external()
        except Exception as e:
            self._append(f"[friends] failed to launch popup: {e}")
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReloadMe+ (Games Manager)")
        self.resize(920, 640)

        self.discord = DiscordManager()
        self.settings = load_settings()
        self.discord.configure(self.settings.get("discord_enabled", False), self.settings.get("discord_client_id",""))


        # Xbox headers will be populated after successful sign-in
        self._xbl_headers = None
        layout = QtWidgets.QVBoxLayout(self)
        # Add Xbox profile header (gamertag + avatar)
        if 'XboxProfileWidget' in globals() and XboxProfileWidget:
            try:
                self.xbox_profile = XboxProfileWidget(self)
                layout.addWidget(self.xbox_profile)
                try:
                    if getattr(self, '_xbl_headers', None):
                        self.xbox_profile.set_headers(self._xbl_headers)
                except Exception:
                    pass
                try:
                    self.xbox_profile.refresh()
                except Exception:
                    pass
            except Exception as _e:
                pass


        # Game selector + CRUD
        row = QtWidgets.QHBoxLayout()
        self.selector = QtWidgets.QComboBox()
        row.addWidget(QtWidgets.QLabel("Game:"))
        row.addWidget(self.selector, 1)
        self.btn_add = QtWidgets.QPushButton("Add")
        self.btn_edit = QtWidgets.QPushButton("Edit")
        self.btn_del = QtWidgets.QPushButton("Delete")
        self.btn_sync = QtWidgets.QPushButton("Sync UWP")
        row.addWidget(self.btn_add)
        row.addWidget(self.btn_edit)
        row.addWidget(self.btn_del)
        row.addWidget(self.btn_sync)

        # --- Settings menu to host Add/Edit/Delete/Sync ---
        self.btn_actions_settings = QtWidgets.QToolButton()
        self.btn_actions_settings.setText('Settings')
        self.btn_actions_settings.setToolTip('Add / Edit / Delete / Sync')
        self.btn_actions_settings.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu_actions = QtWidgets.QMenu(self)
        self.btn_actions_settings.setMenu(self.menu_actions)
        row.addWidget(self.btn_actions_settings)
        # Populate menu
        act_add = self.menu_actions.addAction('Add')
        act_edit = self.menu_actions.addAction('Edit')
        act_delete = self.menu_actions.addAction('Delete')
        self.menu_actions.addSeparator()
        act_sync = self.menu_actions.addAction('Sync UWP')
        # ---- Skins submenu (add-only) ----
        skins = self.menu_actions.addMenu('Skins')
        act_skin_default = skins.addAction('Default')
        act_skin_xbox = skins.addAction('Xbox Original (green/black)')
        def _apply_skin(name):
            try:
                tm = ThemeManager(QtWidgets.QApplication.instance())
                tm.apply(name)
            except Exception:
                pass
        act_skin_default.triggered.connect(lambda: _apply_skin('default'))
        act_skin_xbox.triggered.connect(lambda: _apply_skin('xbox_original'))
        # Wire actions to existing slots
        act_add.triggered.connect(self._on_add)
        act_edit.triggered.connect(self._on_edit)
        act_delete.triggered.connect(self._on_del)
        act_sync.triggered.connect(self._on_sync)
        # Hide the original row buttons so only the Settings menu shows
        self.btn_add.setVisible(False)
        self.btn_edit.setVisible(False)
        self.btn_del.setVisible(False)
        self.btn_sync.setVisible(False)

        self.btn_friends = QtWidgets.QPushButton('Friends')
        row.addWidget(self.btn_friends)
        self.btn_xsignin = QtWidgets.QPushButton("Xbox Sign-In")
        row.addWidget(self.btn_xsignin)
        layout.addLayout(row)

        # Toggles
        toggles = QtWidgets.QHBoxLayout()
        self.chk_priority = QtWidgets.QCheckBox("High priority")
        self.chk_affinity = QtWidgets.QCheckBox("Set CPU affinity")
        self.chk_flags = QtWidgets.QCheckBox("Use game flags")
        self.chk_priority.setChecked(True)
        self.chk_affinity.setChecked(True)
        self.chk_flags.setChecked(True)
        self.le_mask = QtWidgets.QLineEdit("")
        self.le_mask.setPlaceholderText("HEX mask (blank = auto, all CPUs except CPU0)")
        self.le_mask.setMaximumWidth(260)
        toggles.addWidget(self.chk_priority)
        toggles.addWidget(self.chk_affinity)
        toggles.addWidget(self.chk_flags)
        toggles.addWidget(QtWidgets.QLabel("Mask:"))
        toggles.addWidget(self.le_mask)
        toggles.addStretch(1)
        layout.addLayout(toggles)

        # Extra flags per‑launch
        self.extra_flags = QtWidgets.QLineEdit("")
        self.extra_flags.setPlaceholderText("Extra flags (space-separated, appended at launch)")
        layout.addWidget(self.extra_flags)

        # Discord RPC row
        disc_row = QtWidgets.QHBoxLayout()
        self.btn_settings = QtWidgets.QPushButton("Settings (Discord RPC)")
        self.lbl_discord = QtWidgets.QLabel(self._discord_status_text())
        self.lbl_discord.setStyleSheet("color: gray;")
        disc_row.addWidget(self.btn_settings)
        disc_row.addWidget(self.lbl_discord, 1)
        layout.addLayout(disc_row)

        # Launch button
        self.btn = QtWidgets.QPushButton("LAUNCH")
        self.btn.setMinimumHeight(72)
        layout.addWidget(self.btn)

        # Log
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)

        # Data
        self.games = load_games()
        self._refresh_selector()

        # Wire
        self.selector.currentIndexChanged.connect(self._on_sel_change)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_del.clicked.connect(self._on_del)
        self.btn_sync.clicked.connect(self._on_sync)
        self.btn.clicked.connect(self._on_launch)
        self.btn_settings.clicked.connect(self._on_settings)
        self.btn_friends.clicked.connect(self._open_friends)
        try:
            self.btn_xsignin.clicked.connect(self.on_xbox_sign_in)
        except Exception:
            pass

        # Show defaults of first game
        self._on_sel_change(self.selector.currentIndex())

        # Try to connect Discord if enabled
        self._connect_discord_if_needed()

                    # ---------- helpers ----------
    def _append(self, s:str):
        self.log.append(s)

    def _refresh_selector(self):
        self.selector.blockSignals(True)
        self.selector.clear()
        self.selector.addItems([g.get("name","") for g in self.games])
        self.selector.blockSignals(False)
        if self.selector.count() > 0:
            self.selector.setCurrentIndex(0)

    def _on_sel_change(self, idx:int):
        g = self._current_game()
        if not g: return
        self.chk_priority.setChecked(bool(g.get("high_priority", True)))
        self.chk_affinity.setChecked(bool(g.get("apply_affinity", True)))
        self.chk_flags.setChecked(bool(g.get("use_flags", True)))
        self.le_mask.setText(g.get("mask_hex",""))

    def _current_game(self):
        name = self.selector.currentText().strip()
        return get_game_by_name(name, self.games)

    # ---------- CRUD ----------
    def _on_add(self):
        dlg = GameEditor(self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            g = dlg.get_data()
            if g.get("name"):
                self.games.append(g)
                save_games(self.games)
                self._refresh_selector()
                self.selector.setCurrentIndex(self.selector.count()-1)

    def _on_edit(self):
        g = self._current_game()
        if not g: return
        dlg = GameEditor(self, g)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            newg = dlg.get_data()
            # replace the entry
            idx = 0
            for i, e in enumerate(self.games):
                if e.get("name") == g.get("name"):
                    self.games[i] = newg
                    idx = i
                    break
            save_games(self.games)
            self._refresh_selector()
            self.selector.setCurrentIndex(max(0, idx))

    def _on_del(self):
        idx = self.selector.currentIndex()
        if idx < 0: return
        name = self.selector.currentText()
        if QtWidgets.QMessageBox.question(self, "Delete", f"Remove '{name}' from launcher?") == QtWidgets.QMessageBox.StandardButton.Yes:
            self.games.pop(idx)
            save_games(self.games)
            self._refresh_selector()

    # ---------- UWP Sync ----------
    def _on_sync(self):
        dlg = UWPSyncDialog(self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            pass  # not used; we add via Add Selected button
        # Handle Add Selected here so main list updates immediately
        app = dlg.selected_app()
        if not app:
            return
        prefill = {
            "name": app.get("Name",""),
            "aumid": app.get("AppID",""),
            "exe_name": "",  # user must enter the running process name
            "flags": [],
            "mask_hex":"",
            "use_flags": True,
            "high_priority": True,
            "apply_affinity": True,
        }
        ge = GameEditor(self, prefill)
        if ge.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            g = ge.get_data()
            if g.get("name"):
                self.games.append(g)
                save_games(self.games)
                self._refresh_selector()
                self.selector.setCurrentIndex(self.selector.count()-1)

    # ---------- Settings / Discord ----------
    def _discord_status_text(self):
        if not self.settings.get("discord_enabled"):
            return "Discord RPC: disabled"
        cid = self.settings.get("discord_client_id","")
        return f"Discord RPC: enabled (Client ID: {cid or 'not set'})"

    def _on_settings(self):
        dlg = SettingsEditor(self, self.settings)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.settings = dlg.get_settings()
            save_settings(self.settings)
            self.lbl_discord.setText(self._discord_status_text())
            self.discord.configure(self.settings.get("discord_enabled", False), self.settings.get("discord_client_id",""))
            self._connect_discord_if_needed()

    def _connect_discord_if_needed(self):
        if self.settings.get("discord_enabled") and self.settings.get("discord_client_id",""):
            ok = self.discord.connect(self._append)
            if not ok:
                self._append("Discord not connected; continue without RPC.")
        else:
            self._append("Discord RPC disabled.")

    # ---------- Launch ----------
    def _on_launch(self):
        g = self._current_game()
        if not g:
            self._append("No game selected.")
            return

        # Apply current UI toggles to run (non-destructive to JSON unless you Edit/Save)
        use_flags = self.chk_flags.isChecked()
        mask_hex = self.le_mask.text().strip() or g.get("mask_hex","")
        do_aff = self.chk_affinity.isChecked()
        do_high = self.chk_priority.isChecked()
        extra = [x for x in self.extra_flags.text().strip().split() if x]

        # Log config
        self._append(f"UWPHook: {_resolve_uwphook_path(None) or '(not set)'}")
        self._append(f"AUMID:   {g.get('aumid','')}")
        self._append(f"EXE:     {g.get('exe_name','')}")
        base_flags = g.get('flags', [])
        if isinstance(base_flags, str): base_flags = [x for x in base_flags.strip().split() if x]
        show_flags = (base_flags if use_flags else []) + extra
        self._append(f"Flags:   {' '.join(show_flags) if show_flags else '(none)'}")
        self._append(f"Mask:    {mask_hex or '(auto: all CPUs except CPU0)'}")
        self._append(f"HighPrio:{do_high}  Affinity:{do_aff}")

        # Launch in thread
        self.btn.setDisabled(True)
        self.thread = QtCore.QThread(self)
        discord_cfg = {
            "discord_details_tpl": self.settings.get("discord_details_tpl","{name}"),
            "discord_state_tpl": self.settings.get("discord_state_tpl","HighPrio={high}  Affinity={aff}  Flags={flags}"),
        }
        self.worker = Worker(g, use_flags, mask_hex, do_aff, do_high, extra, discord_cfg)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._append)
        self.worker.done.connect(self._on_done)
        self.worker.presence.connect(self._on_presence)
        self.thread.start()

    def _on_presence(self, payload: dict):
        if not payload: return
        if self.settings.get("discord_enabled") and self.discord.connected:
            self.discord.set_presence(payload.get("details",""), payload.get("state",""), self._append)

    def _on_done(self, ok:bool, msg:str):
        self._append(msg)
        self.btn.setDisabled(False)
        if hasattr(self, "thread") and self.thread:
            self.thread.quit()
            self.thread.wait(2000)

    # ---------- close ----------

    # ---------- Xbox Live Sign-In ----------
    


# (moved into Main)

def _open_friends(self):
    try:
        if 'FriendsDock' in globals() and FriendsDock:
            try:
                dlg = FriendsDock(self)
                dlg.setWindowModality(QtCore.Qt.WindowModality.NonModal)
                dlg.show()
                dlg.raise_()
                dlg.activateWindow()
                return
            except Exception as e:
                self._append(f"[friends] inline launch failed: {e}")
        # Fallback: launch external helper script
        _launch_friends_popup_external()
    except Exception as e:
        self._append(f"[friends] failed to launch popup: {e}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()