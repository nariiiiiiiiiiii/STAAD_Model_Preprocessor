"""Desktop application entry point."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import cast

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from staadprep.packaged_smoke import run_packaged_workflow_smoke
from staadprep.paths import ProjectPaths
from staadprep.portable_paths import PortablePaths
from staadprep.ui.main_window import MainWindow
from staadprep.ui.theme import APP_STYLESHEET
from staadprep.version import __version__
from staadprep.viewer.demo import build_demo_frame
from staadprep.viewer.widget import StructuralViewport


def resolve_application_icon() -> Path | None:
    """Find the executable-adjacent packaged logo or the source-tree branding asset."""
    icon_relative_path = Path("branding") / "staad-model-preprocessor.png"
    executable_icon = Path(sys.executable).resolve().parent / icon_relative_path
    source_icon = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "branding"
        / "staad-model-preprocessor.png"
    )

    for candidate in (executable_icon, source_icon):
        if candidate.is_file():
            return candidate
    return None


def create_application() -> QApplication:
    """Return the process QApplication, creating and styling it when needed."""
    existing = QApplication.instance()
    app = QApplication(sys.argv) if existing is None else cast(QApplication, existing)

    app.setApplicationName("STAAD Model Preprocessor")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("STAAD Model Preprocessor")
    icon_path = resolve_application_icon()
    if icon_path is not None:
        app.setWindowIcon(QIcon(str(icon_path)))
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


def run_optional_packaged_workflow_smoke(window: MainWindow) -> None:
    """Run the non-interactive packaged workflow only when explicitly requested."""
    if os.environ.get("STAADPREP_PACKAGED_WORKFLOW_SMOKE") == "1":
        run_packaged_workflow_smoke(window)


def main() -> int:
    app = create_application()
    try:
        project_paths, sketchup_inbox = resolve_runtime_paths()
    except PermissionError as exc:
        QMessageBox.critical(None, "Portable folder is not writable", str(exc))
        return 2

    smoke_ms = os.environ.get("STAADPREP_SMOKE_MS")
    window = MainWindow(
        project_paths=project_paths,
        sketchup_inbox=sketchup_inbox,
        confirm_exit=(lambda _dirty: True) if smoke_ms else None,
    )

    if os.environ.get("STAADPREP_DEMO") == "1":
        cast(StructuralViewport, window.viewport_host).set_model(build_demo_frame())
        window.statusBar().showMessage("Development demo model — not validated")

    window.show()
    run_optional_packaged_workflow_smoke(window)

    if smoke_ms:
        QTimer.singleShot(max(0, int(smoke_ms)), app.quit)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
