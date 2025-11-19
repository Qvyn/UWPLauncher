
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
UWPHOOK_EXE      = r"E:\misc\UWPHook\UWPHook.exe"   # adjust if needed

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

            if not os.path.isfile(UWPHOOK_EXE):
                self.done.emit(False, f"UWPHook.exe not found: {UWPHOOK_EXE}")
                return

            argv = [UWPHOOK_EXE, aumid, exe] + flags
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
        self._append(f"UWPHook: {UWPHOOK_EXE}")
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