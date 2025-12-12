"""
YouTube search + audio/video player plugin for UWPLauncher.

- Adds a "YouTube Player..." entry under the existing Settings gear menu.
- Lets you search YouTube (or paste a URL), play audio-only in the background,
  and optionally open a resizable popup window to view the video.
- Uses the external "yt-dlp" CLI instead of importing yt_dlp, so it works
  inside the PyInstaller EXE as long as yt-dlp.exe is on PATH.

Requires on the SYSTEM (not in the EXE):
    pip install yt-dlp
    (and for video popup)
    pip install PyQt6-WebEngine

Optionally supports offline audio downloads:
    - Audio files are saved under ~/Music/UWPLauncher_YT (created if needed).
"""

from __future__ import annotations

import json
import os
import sys
import re
import shutil
import subprocess
import traceback
from typing import List, Dict, Any, Optional

from PyQt6 import QtWidgets, QtCore, QtGui

import tempfile
import datetime

import time
_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_player.log")

def _log_file(msg: str):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}\n"
        # Write to file
        with open(_LOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
            f.write(line)
        # Also print so it shows in your console/log if you run with console
        print(line, end="")
    except Exception:
        pass


# --- Lazy-import targets (avoid doing heavy QtMultimedia/WebEngine work at import time) ---
QMediaPlayer = None
QAudioOutput = None
QWebEngineView = None

# --- WebEngine helper process (plugin-safe) -----------------------------------
def _choose_python_runner():
    """Return a program + args prefix to run a new python process.
    Tries pythonw/python, then Windows 'py' launcher.
    """
    import shutil
    candidates = ["pythonw", "python"]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p, []
    py = shutil.which("py")
    if py:
        return py, ["-3"]
    return None, []


def _spawn_webengine_helper(url: str, parent: Optional[QtCore.QObject] = None):
    """Launch this plugin file in a separate process to host QtWebEngine.

    Logging is written to:
        %TEMP%\youtube_player_webengine_helper.log
    """
    try:
        program, prefix = _choose_python_runner()
        if not program:
            _log("WebEngine helper: no python runner found on PATH (python/pythonw/py).")
            return False, "No python runner found on PATH (python/pythonw/py)."

        script = os.path.abspath(__file__)
        args = prefix + [script, "--webengine-helper", url]

        _log("WebEngine helper spawn requested")
        _log(f"  log_path={_LOG_PATH}")
        _log(f"  program={program}")
        _log(f"  args={args}")
        _log(f"  script={script}")
        _log(f"  cwd={os.getcwd()}")

        # If we have a parent QObject (e.g., the dialog), use a managed QProcess so we can
        # capture stdout/stderr and lifecycle events without blocking the launcher.
        if parent is not None:
            try:
                proc = QtCore.QProcess(parent)
                # Store reference on the parent to avoid GC
                setattr(parent, "_yt_webengine_proc", proc)

                proc.setProgram(program)
                proc.setArguments(args)

                # Merge channels so we can read everything from standard output
                proc.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)

                def _on_started():
                    try:
                        _log("WebEngine helper: process started")
                        _log(f"  pid={proc.processId()}")
                    except Exception:
                        pass

                def _on_error(err):
                    try:
                        _log(f"WebEngine helper: QProcess error={err} ({proc.errorString()})")
                    except Exception:
                        pass

                def _on_finished(code, status):
                    try:
                        _log(f"WebEngine helper: finished code={code} status={status}")
                        data = bytes(proc.readAllStandardOutput()).decode("utf-8", errors="ignore")
                        if data.strip():
                            _log("WebEngine helper output (merged):")
                            for ln in data.splitlines():
                                _log("  " + ln)
                    except Exception:
                        pass

                def _on_ready():
                    try:
                        data = bytes(proc.readAllStandardOutput()).decode("utf-8", errors="ignore")
                        if data.strip():
                            for ln in data.splitlines():
                                _log("WebEngine helper: " + ln)
                    except Exception:
                        pass

                proc.started.connect(_on_started)
                proc.errorOccurred.connect(_on_error)
                proc.finished.connect(_on_finished)
                proc.readyReadStandardOutput.connect(_on_ready)

                proc.start()
                if not proc.waitForStarted(1500):
                    _log(f"WebEngine helper: failed to start ({proc.errorString()})")
                    return False, f"WebEngine helper failed to start: {proc.errorString()}"
                return True, ""
            except Exception as e:
                _log("WebEngine helper: managed QProcess path failed")
                _log(traceback.format_exc())
                # fall back to detached below

        # Detached fallback so the launcher never hangs or depends on the helper lifecycle.
        try:
            res = QtCore.QProcess.startDetached(program, args)
            # Qt6 can return bool or (bool, pid)
            if isinstance(res, tuple):
                ok, pid = res[0], (res[1] if len(res) > 1 else 0)
            else:
                ok, pid = bool(res), 0
            _log(f"WebEngine helper: startDetached ok={ok} pid={pid}")
            if not ok:
                return False, f"QProcess.startDetached failed (program={program})."
            return True, ""
        except Exception:
            _log("WebEngine helper: startDetached exception")
            _log(traceback.format_exc())
            return False, "QProcess.startDetached threw an exception."
    except Exception as e:
        _log("WebEngine helper: unexpected exception")
        _log(traceback.format_exc())
        return False, str(e)



def _lazy_import_multimedia():
    """
    Import QtMultimedia only when needed.
    """
    global QMediaPlayer, QAudioOutput
    if QMediaPlayer is not None and QAudioOutput is not None:
        return

    try:
        from PyQt6.QtMultimedia import QMediaPlayer as _QMediaPlayer, QAudioOutput as _QAudioOutput
        QMediaPlayer = _QMediaPlayer
        QAudioOutput = _QAudioOutput
    except Exception:
        QMediaPlayer = None
        QAudioOutput = None


def _lazy_import_webengine():
    """
    Import QtWebEngine only when needed.

    NOTE:
    QtWebEngine requires Qt.AA_ShareOpenGLContexts to be set *before* the first
    Q(Core)Application is created, OR the WebEngine modules must be imported
    before the application is constructed. In the launcher, the QApplication
    may already exist by the time this plugin tries to import WebEngine.
    We attempt to set the attribute anyway (harmless if already set), then
    import. If it still fails, we log the real reason to webengine_error.log
    and fall back to opening the video in the system browser.
    """
    global QWebEngineView
    if QWebEngineView is not None:
        return

    # Best-effort: set required attribute before importing WebEngine.
    try:
        QtCore.QCoreApplication.setAttribute(
            QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts,
            True,
        )
    except Exception:
        pass

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView as _QWebEngineView
        QWebEngineView = _QWebEngineView
    except Exception:
        QWebEngineView = None
        # NOTE: In frozen (PyInstaller) builds, WebEngine may be installed but fail to load
        # due to missing bundled resources/DLLs OR due to late-import ordering requirements.
        # Log the real exception to avoid guessing.
        try:
            with open("webengine_error.log", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
                # Add a short hint for the common late-import error.
                if QtCore.QCoreApplication.instance() is not None:
                    f.write(
                        "\n\n[hint] A Q(Core)Application instance already exists. "
                        "QtWebEngine may require AA_ShareOpenGLContexts to be set "
                        "before the QApplication is created.\n"
                    )
        except Exception:
            pass


PLUGIN_META = {
    "name": "YouTube Player",
    "description": "Search YouTube and play audio/video inside the launcher.",
    "version": "1.3.0",
}

YOUTUBE_URL_RE = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/", re.IGNORECASE)


def _log(window_or_msg, msg: str = None):
    """Use launcher's log area if available, otherwise print."""
    # Supports both _log("message") and _log(window, "message")
    if msg is None:
        window = None
        msg = str(window_or_msg)
    else:
        window = window_or_msg
        msg = str(msg)

    # Always write to temp log file for debugging helper launches
    try:
        _log_file(msg)
    except Exception:
        pass
    try:
        if hasattr(window, "_append") and callable(window._append):
            window._append(f"[YouTubePlugin] {msg}")
            return
    except Exception:
        pass
    print(f"[YouTubePlugin] {msg}")




# ----------------------------
# WebEngine helper entrypoint
# ----------------------------
def _webengine_helper_main(url: str) -> int:
    """
    Run a standalone QtWebEngine window in *this* process.

    IMPORTANT: Keep all QtWebEngine imports inside this function so importing the plugin
    inside the launcher never imports QtWebEngine in-process.
    """
    try:
        _log("[helper] starting")
        _log(f"[helper] url={url}")

        # A few conservative Chromium flags to avoid GPU-related crashes on some systems.
        # Respect existing user-defined flags if already present.
        try:
            existing = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "").strip()
            if not existing:
                os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-gpu-compositing --disable-features=VizDisplayCompositor"
                _log(f"[helper] set QTWEBENGINE_CHROMIUM_FLAGS={os.environ['QTWEBENGINE_CHROMIUM_FLAGS']}")
            else:
                _log(f"[helper] using existing QTWEBENGINE_CHROMIUM_FLAGS={existing}")
        except Exception as e:
            _log(f"[helper] could not set chromium flags: {e}")

        # Create the app and window.
        from PyQt6 import QtCore, QtWidgets  # safe
        # Only import WebEngine widgets here (helper process only)
        from PyQt6.QtWebEngineWidgets import QWebEngineView

        # (Optional) set attributes in the helper process only.
        try:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)
            _log("[helper] set AA_UseSoftwareOpenGL")
        except Exception as e:
            _log(f"[helper] could not set AA_UseSoftwareOpenGL: {e}")

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

        win = QtWidgets.QMainWindow()
        win.setWindowTitle("YouTube (Helper)")
        win.resize(1100, 700)

        view = QWebEngineView(win)
        view.setUrl(QtCore.QUrl(url))
        win.setCentralWidget(view)

        win.show()
        _log("[helper] window shown; entering event loop")
        rc = app.exec()
        _log(f"[helper] event loop exited rc={rc}")
        return int(rc)
    except Exception as e:
        try:
            _log(f"[helper] fatal exception: {e}")
            import traceback
            _log(traceback.format_exc())
        except Exception:
            pass
        return 1


# If launched as a helper process, run the WebEngine window and exit immediately.
# This runs *before* the plugin registers itself in the launcher.
if "--webengine-helper" in sys.argv:
    try:
        idx = sys.argv.index("--webengine-helper")
        url = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
    except Exception:
        url = ""
    if not url:
        try:
            _log("[helper] missing url argument; exiting")
        except Exception:
            pass
        raise SystemExit(2)
    raise SystemExit(_webengine_helper_main(url))
def _yt_dlp_available() -> bool:
    """Return True if yt-dlp CLI is available on PATH."""
    return shutil.which("yt-dlp") is not None


def _run_yt_dlp(args: List[str]) -> str:
    """
    Run yt-dlp with given args, return stdout text or raise RuntimeError.
    """
    exe = shutil.which("yt-dlp")
    if not exe:
        raise RuntimeError(
            "yt-dlp.exe not found on PATH.\n\n"
            "Make sure you installed it with:\n"
            "  pip install yt-dlp\n"
            "and that the Python Scripts folder is on PATH."
        )

    proc = subprocess.run(
        [exe] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or "yt-dlp failed."
        raise RuntimeError(err)
    return proc.stdout


def _yt_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Use yt-dlp CLI to search YouTube or fetch info for a URL.
    Returns a list of entries similar to yt_dlp's JSON.
    """
    # If it's a URL, ask yt-dlp for info about that URL
    if YOUTUBE_URL_RE.search(query):
        out = _run_yt_dlp(["--dump-json", "--skip-download", query])
        try:
            info = json.loads(out)
            return [info]
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse yt-dlp JSON: {e}")

    # Otherwise, treat as search
    search_spec = f"ytsearch{max_results}:{query}"
    out = _run_yt_dlp(["--dump-json", "--skip-download", search_spec])

    entries: List[Dict[str, Any]] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            info = json.loads(line)
        except json.JSONDecodeError:
            continue
        entries.append(info)
    return entries


def _yt_get_audio_stream(url: str) -> str:
    """
    Use yt-dlp CLI to get the best audio stream URL.
    """
    out = _run_yt_dlp(["-g", "-f", "bestaudio/best", url])
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("yt-dlp did not return any stream URLs.")
    # Usually first line is what we want
    return lines[0]


def _yt_get_video_stream(url: str) -> str:
    """
    Use yt-dlp CLI to get a *muxed* (audio+video) stream URL suitable for QtMultimedia.
    We prefer a progressive MP4 with both audio+video and avoid HLS/DASH manifests.
    """
    # Prefer a single progressive https URL that already includes audio+video.
    # Avoid HLS (m3u8) because Qt/FFmpeg will fetch segments that often 403 without browser headers/cookies.
    fmt = (
        "best[ext=mp4][protocol^=https][protocol!=m3u8][protocol!=m3u8_native][vcodec!=none][acodec!=none]"
        "/best[protocol^=https][protocol!=m3u8][protocol!=m3u8_native][vcodec!=none][acodec!=none]"
        "/best[protocol^=https][protocol!=m3u8][protocol!=m3u8_native]"
        "/best"
    )
    out = _run_yt_dlp([
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android",
        "-g", "-f", fmt, url
    ])
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("yt-dlp did not return any stream URLs.")
    return lines[0]

def _default_download_dir() -> str:
    """
    Return a default directory for offline audio downloads.
    We use ~/Music/UWPLauncher_YT by default.
    """
    home = os.path.expanduser("~")
    base = os.path.join(home, "Music", "UWPLauncher_YT")
    os.makedirs(base, exist_ok=True)
    return base


def _yt_download_audio_file(url: str, out_dir: str) -> str:
    """
    Use yt-dlp CLI to download the best audio stream to out_dir.
    Returns the local file path.
    """
    os.makedirs(out_dir, exist_ok=True)

    # Robust detection: record a timestamp and pick the newest file created after the download starts.
    t0 = time.time()

    outtmpl = os.path.join(out_dir, "%(title).200s.%(ext)s")
    # Download bestaudio (no conversion here; conversion is optional and depends on FFmpeg availability).
    _run_yt_dlp([
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android",
        "-f", "bestaudio/best",
        "-o", outtmpl,
        url
    ])

    # Find newest file created/modified after t0
    candidates = []
    for name in os.listdir(out_dir):
        p = os.path.join(out_dir, name)
        if not os.path.isfile(p):
            continue
        # ignore partials
        if name.endswith(".part") or name.endswith(".ytdl") or name.endswith(".temp"):
            continue
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if mt >= t0 - 1.0:
            candidates.append((mt, p))

    if not candidates:
        # Fall back: pick newest media-like file in folder
        media_exts = (".mp3", ".m4a", ".opus", ".webm", ".aac", ".wav", ".flac")
        for name in os.listdir(out_dir):
            if not name.lower().endswith(media_exts):
                continue
            p = os.path.join(out_dir, name)
            if os.path.isfile(p):
                try:
                    candidates.append((os.path.getmtime(p), p))
                except OSError:
                    pass

    if not candidates:
        raise RuntimeError("yt-dlp did not produce an audio file.")

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


class YouTubeVideoWindow(QtWidgets.QDialog):
    """
    Simple, resizable popup that embeds the YouTube video via QWebEngineView.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube Video")
        self.resize(960, 540)
        layout = QtWidgets.QVBoxLayout(self)

        _lazy_import_webengine()

        if QWebEngineView is None:
            label = QtWidgets.QLabel(
                "PyQt6-WebEngine is not installed or unavailable.\n\n"
                "Install with:\n    pip install PyQt6-WebEngine"
            )
            label.setWordWrap(True)
            layout.addWidget(label)
            self._view = None
            return

        self._view = QWebEngineView(self)
        layout.addWidget(self._view)

    def load_video(self, url: str):
        if self._view is None:
            return
        from PyQt6 import QtCore as _QtCore
        self._view.setUrl(_QtCore.QUrl(url))


class YouTubeMediaVideoWindow(QtWidgets.QDialog):
    """
    Resizable popup that renders video via QtMultimedia (QMediaPlayer + QVideoWidget),
    avoiding QtWebEngine entirely.
    """

    def __init__(self, player: "QMediaPlayer", parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube Video")
        self.resize(960, 540)
        self._player = player

        layout = QtWidgets.QVBoxLayout(self)

        # Lazy import to avoid hard dependency if QtMultimediaWidgets isn't present.
        try:
            from PyQt6.QtMultimediaWidgets import QVideoWidget
            self._video = QVideoWidget(self)
            layout.addWidget(self._video)
            try:
                # Attach video output immediately (safe even before source is set)
                self._player.setVideoOutput(self._video)
            except Exception:
                pass
        except Exception as e:
            self._video = None
            label = QtWidgets.QLabel(
                "Video playback is unavailable (PyQt6.QtMultimediaWidgets missing).\n\n"                f"Error: {e}",
                self,
            )
            label.setWordWrap(True)
            layout.addWidget(label)

    def closeEvent(self, event):
        # Detach the video output so audio-only mode can continue safely.
        try:
            if self._player is not None:
                self._player.setVideoOutput(None)
        except Exception:
            pass
        super().closeEvent(event)


class YouTubePlayerDialog(QtWidgets.QDialog):
    """
    Main YouTube search + audio player UI.

    - Search field / URL field
    - Results list
    - Play audio-only using QMediaPlayer
    - Optional video popup using QWebEngineView
    - Optional "Download audio" for offline playback
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YouTube Player")
        self.resize(800, 500)

        self._results: List[Dict[str, Any]] = []
        self._video_window: Optional[YouTubeVideoWindow] = None

        # ==== UI ====
        main_layout = QtWidgets.QVBoxLayout(self)

        # Search row
        search_row = QtWidgets.QHBoxLayout()
        self.edit_search = QtWidgets.QLineEdit(self)
        self.edit_search.setPlaceholderText("Search YouTube or paste a YouTube URL…")
        self.btn_search = QtWidgets.QPushButton("Search", self)
        search_row.addWidget(self.edit_search)
        search_row.addWidget(self.btn_search)
        main_layout.addLayout(search_row)

        # Results list
        self.list_results = QtWidgets.QListWidget(self)
        self.list_results.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        main_layout.addWidget(self.list_results, 1)

        # Controls row
        controls_row = QtWidgets.QHBoxLayout()
        self.btn_play_audio = QtWidgets.QPushButton("Play audio only", self)
        self.btn_download_audio = QtWidgets.QPushButton("Download audio", self)
        self.btn_play_video = QtWidgets.QPushButton("Play with video", self)
        self.btn_stop = QtWidgets.QPushButton("Stop", self)
        self.btn_pause = QtWidgets.QPushButton("Pause/Resume", self)
        controls_row.addWidget(self.btn_play_audio)
        controls_row.addWidget(self.btn_download_audio)
        controls_row.addWidget(self.btn_play_video)
        controls_row.addWidget(self.btn_pause)
        controls_row.addWidget(self.btn_stop)

        # Volume
        controls_row.addStretch(1)
        controls_row.addWidget(QtWidgets.QLabel("Volume"))
        self.slider_volume = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(60)
        controls_row.addWidget(self.slider_volume)
        main_layout.addLayout(controls_row)

        # Status label
        self.lbl_status = QtWidgets.QLabel("", self)
        self.lbl_status.setWordWrap(True)
        main_layout.addWidget(self.lbl_status)

        # ==== Audio player ====
        self.player: Optional[QMediaPlayer] = None
        self.audio_output: Optional[QAudioOutput] = None

        _lazy_import_multimedia()

        if QMediaPlayer is not None and QAudioOutput is not None:
            self.player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(self.slider_volume.value() / 100.0)

            # If backend isn't actually available, disable the controls gracefully
            try:
                if not self.player.isAvailable():
                    self._disable_audio_ui(
                        "QtMultimedia backend is not available. Audio playback disabled."
                    )
                else:
                    # Hook error signal for safety
                    try:
                        if hasattr(self.player, "errorChanged"):
                            self.player.errorChanged.connect(self._on_player_error)
                        elif hasattr(self.player, "errorOccurred"):
                            self.player.errorOccurred.connect(self._on_player_error)
                    except Exception:
                        pass
            except Exception:
                # If isAvailable() explodes for some reason, disable audio UI
                self._disable_audio_ui(
                    "QtMultimedia reported an error. Audio playback disabled."
                )
        else:
            # No QtMultimedia, disable audio UI
            self._disable_audio_ui(
                "QtMultimedia is not available. Audio playback is disabled.\n"
                "Install it with PyQt6 if needed."
            )

        # ==== Signals ====
        self.btn_search.clicked.connect(self._on_search)
        self.list_results.itemDoubleClicked.connect(
            lambda _: self._play_selected(audio_only=True)
        )
        self.btn_play_audio.clicked.connect(lambda: self._play_selected(audio_only=True))
        self.btn_download_audio.clicked.connect(self._on_download_audio)
        self.btn_play_video.clicked.connect(lambda: self._play_selected(audio_only=False))
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_pause.clicked.connect(self._on_pause)
        self.slider_volume.valueChanged.connect(self._on_volume_changed)

    # ---------- Helpers ----------

    def _disable_audio_ui(self, message: str):
        """Disable audio-related controls and show a status message."""
        self.btn_play_audio.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.slider_volume.setEnabled(False)
        self._set_status(message)

    def _set_status(self, text: str):
        self.lbl_status.setText(text)

    def _ensure_video_window(self) -> Optional[YouTubeVideoWindow]:
        _lazy_import_webengine()
        if QWebEngineView is None:
            QtWidgets.QMessageBox.warning(
                self,
                "YouTube Video",
                "PyQt6-WebEngine is not installed or unavailable.\n\n"
                "Install with:\n    pip install PyQt6-WebEngine",
            )
            return None
        if self._video_window is None:
            self._video_window = YouTubeVideoWindow(self)
        return self._video_window

    def _current_result(self) -> Optional[Dict[str, Any]]:
        idx = self.list_results.currentRow()
        if idx < 0 or idx >= len(self._results):
            return None
        return self._results[idx]

    # ---------- Slots ----------

    def _on_search(self):
        query = self.edit_search.text().strip()
        if not query:
            self._set_status("Enter a search term or paste a YouTube URL.")
            return

        if not _yt_dlp_available():
            QtWidgets.QMessageBox.warning(
                self,
                "YouTube search",
                "yt-dlp.exe is not available on PATH.\n\n"
                "Install with:\n    pip install yt-dlp\n"
                "and make sure your Python Scripts directory is in PATH.",
            )
            return

        self._set_status("Searching YouTube…")
        self.list_results.clear()
        self._results = []
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.BusyCursor)
        try:
            infos = _yt_search(query, max_results=10) or []

            for entry in infos:
                if not entry:
                    continue
                vid_id = entry.get("id")
                title = entry.get("title") or "(no title)"
                channel = entry.get("channel") or entry.get("uploader") or ""
                duration = entry.get("duration")  # seconds
                display = title
                if channel:
                    display += f" — {channel}"
                if duration is not None:
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    display += f" [{mins}:{secs:02d}]"

                item = QtWidgets.QListWidgetItem(display)
                self.list_results.addItem(item)
                self._results.append(
                    {
                        "id": vid_id,
                        "title": title,
                        "channel": channel,
                        "duration": duration,
                        "webpage_url": entry.get("webpage_url"),
                    }
                )

            if not self._results:
                self._set_status("No results.")
            else:
                self._set_status(f"Found {len(self._results)} result(s).")
                self.list_results.setCurrentRow(0)
        except Exception as e:
            self._set_status(f"Search failed: {e}")
            traceback.print_exc()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def _play_selected(self, audio_only: bool):
        res = self._current_result()
        if not res:
            self._set_status("Select a result first.")
            return

        url = res.get("webpage_url")
        if not url and res.get("id"):
            url = f"https://www.youtube.com/watch?v={res['id']}"

        if not url:
            self._set_status("Invalid result – no URL.")
            return

        if audio_only:
            self._play_audio_from_url(url)
        else:
            self._play_video_in_popup(url)

    def _on_download_audio(self):
        res = self._current_result()
        if not res:
            self._set_status("Select a result first.")
            return

        url = res.get("webpage_url")
        if not url and res.get("id"):
            url = f"https://www.youtube.com/watch?v={res['id']}"

        if not url:
            self._set_status("Invalid result – no URL.")
            return

        if not _yt_dlp_available():
            QtWidgets.QMessageBox.warning(
                self,
                "Download audio",
                "yt-dlp.exe is not available on PATH.\n\n"
                "Install with:\n    pip install yt-dlp\n"
                "and make sure your Python Scripts directory is in PATH.",
            )
            return

        out_dir = _default_download_dir()
        self._set_status(f"Downloading audio to {out_dir}…")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.BusyCursor)
        try:
            path = _yt_download_audio_file(url, out_dir)
            self._set_status(f"Downloaded audio to:\n{path}")
            # Optional: ask to open the folder
            try:
                ans = QtWidgets.QMessageBox.question(
                    self,
                    "Download complete",
                    f"Audio was downloaded to:\n{path}\n\nOpen the folder?",
                    QtWidgets.QMessageBox.StandardButton.Yes
                    | QtWidgets.QMessageBox.StandardButton.No,
                )
                if ans == QtWidgets.QMessageBox.StandardButton.Yes:
                    folder_url = QtCore.QUrl.fromLocalFile(os.path.dirname(path))
                    QtGui.QDesktopServices.openUrl(folder_url)
            except Exception:
                pass
        except Exception as e:
            self._set_status(f"Download failed: {e}")
            traceback.print_exc()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def _play_audio_from_url(self, url: str):
        if self.player is None or self.audio_output is None:
            self._set_status("Audio playback is not available (QtMultimedia missing).")
            return

        if not _yt_dlp_available():
            QtWidgets.QMessageBox.warning(
                self,
                "YouTube audio",
                "yt-dlp.exe is not available on PATH.\n\n"
                "Install with:\n    pip install yt-dlp\n"
                "and make sure your Python Scripts directory is in PATH.",
            )
            return

        self._set_status("Resolving audio stream…")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.BusyCursor)
        try:
            stream_url = _yt_get_audio_stream(url)
            from PyQt6 import QtCore as _QtCore

            self.audio_output.setVolume(self.slider_volume.value() / 100.0)
            self.player.setSource(_QtCore.QUrl(stream_url))
            self.player.play()
            self._set_status("Playing audio…")
        except Exception as e:
            self._set_status(f"Audio playback failed: {e}")
            traceback.print_exc()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    
    def _play_video_in_popup(self, url: str):
            # Video playback via QtMultimedia (no browser, no WebEngine).
            if self.player is None or self.audio_output is None:
                self._set_status("Video playback is not available (QtMultimedia missing).")
                return

            if not _yt_dlp_available():
                QtWidgets.QMessageBox.warning(
                    self,
                    "YouTube video",
                    "yt-dlp.exe is not available on PATH.\n\n"                    "Install with:\n    pip install yt-dlp\n"                    "and make sure your Python Scripts directory is in PATH.",
                )
                return

            self._set_status("Resolving video stream…")
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
            try:
                stream_url = _yt_get_video_stream(url)
                from PyQt6 import QtCore as _QtCore

                # Create/show the video window (reused across plays)
                try:
                    if not hasattr(self, "video_window") or self.video_window is None:
                        self.video_window = YouTubeMediaVideoWindow(self.player, parent=self)
                    # If window exists but video widget missing, keep going (it will show error label)
                    self.video_window.show()
                    self.video_window.raise_()
                    self.video_window.activateWindow()
                except Exception:
                    pass

                self.audio_output.setVolume(self.slider_volume.value() / 100.0)
                self.player.setSource(_QtCore.QUrl(stream_url))
                self.player.play()
                self._set_status("Playing video…")
            except Exception as e:
                self._set_status(f"Video playback failed: {e}")
                traceback.print_exc()
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()

    def _on_stop(self):
        if self.player is not None:
            try:
                self.player.stop()
            except Exception:
                pass
        self._set_status("Stopped.")

    def _on_pause(self):
        if self.player is None:
            return
        try:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.pause()
                self._set_status("Paused.")
            else:
                self.player.play()
                self._set_status("Playing.")
        except Exception:
            pass

    def _on_volume_changed(self, value: int):
        if self.audio_output is not None:
            try:
                self.audio_output.setVolume(max(0.0, min(1.0, value / 100.0)))
            except Exception:
                pass

    def _on_player_error(self, err):
        """Handle QMediaPlayer backend errors gracefully."""
        # Convert enum/int to a simple code
        try:
            code = int(err)
        except Exception:
            code = -1
        if code == 0:
            return

        msg = ""
        try:
            if hasattr(self.player, "errorString") and callable(self.player.errorString):
                msg = self.player.errorString() or ""
        except Exception:
            msg = ""

        self._disable_audio_ui(
            msg or "QtMultimedia backend reported an error. Audio playback disabled."
        )

    def closeEvent(self, event):
        try:
            proc = getattr(self, '_yt_webengine_proc', None)
            if proc is not None:
                _log('WebEngine helper: terminating on dialog close')
                proc.terminate()
                proc.waitForFinished(1000)
        except Exception:
            pass

        # Clean up audio when closing dialog
        try:
            if self.player is not None:
                self.player.stop()
        except Exception:
            pass
        super().closeEvent(event)


# ------------ Plugin entry point ------------

def register_plugin(window):
    """
    Entry point used by the UWPLauncher plugin system.

    We:
    - Attach a single YouTubePlayerDialog to the main window
    - Add a "YouTube Player..." menu item under the existing Settings gear
    """

    _log(window, "Registering YouTube Player plugin…")

    # Store dialog on the window so it’s reused
    if not hasattr(window, "_youtube_player_dialog"):
        window._youtube_player_dialog = None

    def _ensure_dialog():
        if window._youtube_player_dialog is None:
            dlg = YouTubePlayerDialog(window)
            window._youtube_player_dialog = dlg
        return window._youtube_player_dialog

    # Attach to existing settings menu if available
    actions_menu = getattr(window, "menu_actions", None)
    if isinstance(actions_menu, QtWidgets.QMenu):
        yt_menu = actions_menu.addMenu("YouTube")
        act_open = yt_menu.addAction("YouTube Player…")

        act_open.triggered.connect(
            lambda: (
                _ensure_dialog().show(),
                _ensure_dialog().raise_(),
                _ensure_dialog().activateWindow(),
            )
        )
        _log(window, "Added YouTube Player entry to Settings menu.")
    else:
        # No menu – don't auto-open anything on startup (avoids freezes)
        _log(
            window,
            "Settings menu not found; YouTube Player not attached (no auto dialog).",
        )

    # Optionally keep metadata on the window (used by Plugin Manager UI)
    try:
        meta_list = getattr(window, "_plugin_meta", []) or []
        meta_list.append(
            {
                "name": PLUGIN_META.get("name", "YouTubePlayer"),
                "description": PLUGIN_META.get("description", ""),
                "path": __file__,
            }
        )
        window._plugin_meta = meta_list
    except Exception:
        pass