"""Desktop application entry point."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from staadprep.paths import ProjectPaths
from staadprep.portable_paths import PortablePaths
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


def resolve_runtime_paths() -> tuple[ProjectPaths | None, Path | None]:
    """Prepare portable runtime paths when running from a compiled standalone build."""
    portable = PortablePaths.detect()
    if portable is None:
        return None, None

    portable.ensure_layout()
    portable.assert_writable()
    portable.apply_environment()
    return ProjectPaths.from_runtime_root(portable.data), portable.sketchup_inbox


def main() -> int:
    app = create_application()
    project_paths, sketchup_inbox = resolve_runtime_paths()
    window = MainWindow(
        project_paths=project_paths,
        sketchup_inbox=sketchup_inbox,
    )

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
