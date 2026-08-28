"""Desktop application entry point."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from staadprep.ui.main_window import MainWindow
from staadprep.ui.theme import APP_STYLESHEET
from staadprep.viewer.demo import build_demo_frame


def create_application() -> QApplication:
    """Return the process QApplication, creating and styling it when needed."""
    existing = QApplication.instance()
    if existing is not None:
        return existing

    app = QApplication(sys.argv)
    app.setApplicationName("STAAD Model Preprocessor")
    app.setOrganizationName("STAAD Model Preprocessor")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    return app


def main() -> int:
    app = create_application()
    window = MainWindow()

    if os.environ.get("STAADPREP_DEMO") == "1":
        window.viewport_host.set_model(build_demo_frame())
        window.statusBar().showMessage("Development demo model — not validated")

    window.show()

    smoke_ms = os.environ.get("STAADPREP_SMOKE_MS")
    if smoke_ms:
        QTimer.singleShot(max(0, int(smoke_ms)), app.quit)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
