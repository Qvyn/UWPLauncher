"""
Starter plugin template for UWPLauncher.

Instructions:
- Save this file in the 'scripts' folder (e.g. scripts/my_plugin.py).
- Enable it in the Plugin Manager.
- Restart UWPLauncher.
"""

from __future__ import annotations

PLUGIN_NAME = "MyPluginTemplate"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Starter template for UWPLauncher plugins."

try:
    from PyQt6 import QtWidgets
except Exception:
    QtWidgets = None


def register_plugin(window):
    if QtWidgets is None:
        return {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "error": "PyQt6 not available in this build.",
        }

    # Find the main Actions menu
    menu = getattr(window, "menu_actions", None)
    if menu is None or not isinstance(menu, QtWidgets.QMenu):
        return {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "error": "menu_actions QMenu not found on window.",
        }

    # Add your action(s) here
    act = menu.addAction("Template plugin: test action")

    def on_trigger():
        # Example toast
        try:
            if hasattr(window, "_show_toast"):
                window._show_toast("Template plugin triggered!", "info")
        except Exception:
            pass

        # Example message box
        QtWidgets.QMessageBox.information(
            window, "Template plugin", "Template plugin triggered!"
        )

    act.triggered.connect(on_trigger)

    # Return metadata
    return {
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
    }


def register(window):      # pragma: no cover
    return register_plugin(window)


def init_plugin(window):   # pragma: no cover
    return register_plugin(window)
