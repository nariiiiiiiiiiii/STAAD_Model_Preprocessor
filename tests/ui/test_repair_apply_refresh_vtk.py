from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Qt

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.main_window import MainWindow
from staadprep.ui.repair_apply_dialog import RepairApplyDialog
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _apply_then_ok(qtbot):
    def run(dialog: RepairApplyDialog) -> None:
        qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        qtbot.mouseClick(dialog.ok_button, Qt.MouseButton.LeftButton)

    return run


def test_real_vtk_scene_matches_delete_and_merge_without_undo(qtbot) -> None:
    delete_model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
            _key(50): Node(_key(50), Vec3(20.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    delete_viewport = StructuralViewport()
    delete_window = MainWindow(
        viewport_factory=lambda: delete_viewport,
        repair_dialog_runner=_apply_then_ok(qtbot),
    )
    qtbot.addWidget(delete_window)
    delete_window.set_canonical_model(delete_model)
    delete_viewport.selection.set_nodes((_key(50),))

    delete_window.delete_selected_entities()

    assert len(delete_model.nodes) == 2
    assert delete_viewport.scene is not None
    assert len(delete_viewport.scene.point_keys) == len(delete_model.nodes)
    assert len(delete_viewport.scene.member_keys) == len(delete_model.members)
    assert delete_viewport.plotter.render_window is not None

    merge_model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(8.0, 0.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(2), _key(3)),
        },
    )
    merge_viewport = StructuralViewport()
    merge_window = MainWindow(
        viewport_factory=lambda: merge_viewport,
        repair_dialog_runner=_apply_then_ok(qtbot),
    )
    qtbot.addWidget(merge_window)
    merge_window.set_canonical_model(merge_model)
    merge_viewport.selection.set_members((_key(101), _key(102)))
    merge_viewport.selection_changed.emit((), (_key(101), _key(102)))

    merge_window.merge_members_action.trigger()

    assert len(merge_model.nodes) == 2
    assert len(merge_model.members) == 1
    assert merge_viewport.scene is not None
    assert len(merge_viewport.scene.point_keys) == len(merge_model.nodes)
    assert len(merge_viewport.scene.member_keys) == len(merge_model.members)
    assert merge_viewport.plotter.render_window is not None
