"""Real Qt/VTK smoke check for member local-X preview and normalization."""

from __future__ import annotations

import os
from uuid import UUID

os.environ.setdefault("QT_API", "pyside6")

from PySide6.QtWidgets import QApplication

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import needs_reverse
from staadprep.ui.main_window import MainWindow
from staadprep.ui.repair_apply_dialog import RepairApplyDialog
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(4.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(0.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, 5.0, 0.0)),
        _key(4): Node(_key(4), Vec3(0.0, 5.0, 8.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(2), _key(3)),
        _key(103): Member(_key(103), _key(4), _key(3)),
    }
    return ProjectModel(nodes=nodes, members=members)


def _apply_repair(dialog: RepairApplyDialog) -> None:
    dialog.apply_button.click()
    dialog.ok_button.click()


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(
        repair_dialog_runner=_apply_repair,
        confirm_exit=lambda _dirty: True,
    )
    model = _model()
    window.set_canonical_model(model)
    app.processEvents()

    viewport = window.viewport_host
    if not isinstance(viewport, StructuralViewport):
        raise RuntimeError("MainWindow did not create the real StructuralViewport")
    preview = window.orientation_reverse_count
    if preview != 2:
        raise RuntimeError(f"Expected 2 reversals before normalization, got {preview}")
    if viewport._local_x_actor is not None:
        raise RuntimeError("Local-X arrows should be hidden by default in T16")
    revision_before_view_toggle = model.revision
    viewport.highlight_members((_key(101),))
    window.local_x_view_action.setChecked(True)
    app.processEvents()
    if viewport._local_x_actor is None:
        raise RuntimeError("Local-X arrow actor was not rendered after view toggle")
    if model.revision != revision_before_view_toggle:
        raise RuntimeError("Local-X view toggle mutated the canonical model")

    window.normalize_member_directions()
    app.processEvents()

    normalized = window.orientation_reverse_count
    if normalized != 0:
        raise RuntimeError(f"Expected 0 reversals after normalization, got {normalized}")
    if model.revision != 2:
        raise RuntimeError(f"Expected revision 2, got {model.revision}")
    if any(needs_reverse(model, member) for member in model.members.values()):
        raise RuntimeError("A member still violates the deterministic incidence rule")
    if not window.local_x_view_action.isChecked():
        raise RuntimeError("Local-X view mode did not survive model refresh")
    viewport.highlight_members((_key(101),))
    app.processEvents()
    if viewport._local_x_actor is None:
        raise RuntimeError("Local-X arrows did not return after reselection")

    window.close()
    app.processEvents()
    print(
        "ORIENTATION_SMOKE_PASS",
        f"preview={preview}",
        f"normalized={normalized}",
        "arrows=pass",
        f"revision={model.revision}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
