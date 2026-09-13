from __future__ import annotations

import sys
from copy import deepcopy
from uuid import UUID

from PySide6.QtWidgets import QApplication

from staadprep.editing.create_node import (
    ExactNodeSpec,
    RelativeNodeSpec,
    RepeatConnectionMode,
    TranslationalRepeatSpec,
    analyze_translational_repeat,
)
from staadprep.model.entities import Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.create_node_dialog import RepeatPreviewRequest
from staadprep.ui.main_window import MainWindow
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _graph_signature(
    model: ProjectModel,
) -> tuple[tuple[tuple[int, tuple[float, float, float]], ...], tuple[tuple[int, int], ...], int]:
    nodes = tuple(sorted((key.int, node.position.as_tuple()) for key, node in model.nodes.items()))
    incidences = tuple(
        sorted(
            tuple(sorted((member.start.int, member.end.int))) for member in model.members.values()
        )
    )
    return nodes, incidences, model.revision


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    viewport = StructuralViewport()
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_exit=lambda _dirty: True,
    )
    model = ProjectModel(nodes={_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))})
    before = deepcopy(model)
    window.set_canonical_model(model)
    window.show()
    app.processEvents()

    window._apply_exact_node_spec(ExactNodeSpec(10.0, 4.0, 3.0), tolerance_m=1e-9)
    app.processEvents()
    if not any(node.position == Vec3(10.0, 4.0, 3.0) for node in model.nodes.values()):
        raise RuntimeError("Exact XYZ creation failed")
    window.undo_repair()
    app.processEvents()
    if _graph_signature(model) != _graph_signature(before):
        raise RuntimeError("Exact XYZ Undo did not restore graph")

    window._apply_relative_node_spec(
        RelativeNodeSpec(_key(1), 1.0, 2.0, 3.0, create_member=True),
        tolerance_m=1e-9,
    )
    app.processEvents()
    if len(model.nodes) != 2 or len(model.members) != 1:
        raise RuntimeError("Relative node + member creation failed")
    if not any(node.position == Vec3(1.0, 2.0, 3.0) for node in model.nodes.values()):
        raise RuntimeError("Relative coordinate result is incorrect")
    window.undo_repair()
    app.processEvents()
    if _graph_signature(model) != _graph_signature(before):
        raise RuntimeError("Relative create Undo did not restore graph")

    spec = TranslationalRepeatSpec(
        reference_node=_key(1),
        dx=1.0,
        dy=0.5,
        dz=0.0,
        repeats=3,
        connection_mode=RepeatConnectionMode.CONSECUTIVE,
    )
    preview = analyze_translational_repeat(model, spec, tolerance_m=1e-9)
    revision = model.revision
    window._show_repeat_preview_request(RepeatPreviewRequest(preview, spec, {}))
    app.processEvents()
    if viewport._precision_ghost_node_count != 3:
        raise RuntimeError("Repeat preview did not render all ghost nodes")
    if viewport._precision_ghost_member_count != 3:
        raise RuntimeError("Repeat preview did not render all ghost members")
    if model.revision != revision:
        raise RuntimeError("Repeat preview mutated canonical model")

    window._apply_translational_repeat(spec, resolutions={}, tolerance_m=1e-9)
    app.processEvents()
    expected_positions = {
        (0.0, 0.0, 0.0),
        (1.0, 0.5, 0.0),
        (2.0, 1.0, 0.0),
        (3.0, 1.5, 0.0),
    }
    if {node.position.as_tuple() for node in model.nodes.values()} != expected_positions:
        raise RuntimeError("Translational Repeat coordinates are incorrect")
    if len(model.members) != 3:
        raise RuntimeError("Translational Repeat incidences are incorrect")
    if window.repair_history is None or len(window.repair_history.undo_stack) != 1:
        raise RuntimeError("Translational Repeat was not one atomic history item")

    window.undo_repair()
    app.processEvents()
    if _graph_signature(model) != _graph_signature(before):
        raise RuntimeError("Repeat Undo did not restore exact graph")

    nav_revision = model.revision
    viewport.begin_navigation(shift=False)
    viewport.navigate_drag(12.0, -7.0)
    viewport.end_navigation()
    app.processEvents()
    if model.revision != nav_revision:
        raise RuntimeError("Navigation mutated canonical model")

    window.close()
    app.processEvents()
    print(
        "PRECISION_CREATE_SMOKE_PASS",
        "exact=pass",
        "relative=pass",
        "repeat=pass",
        "preview=pass",
        "undo=pass",
        "navigation=pass",
        "graph=restored",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
