from __future__ import annotations

from uuid import UUID

from staadprep.editing.create_node import ExistingNodeResolution, RepeatConnectionMode
from staadprep.model.entities import Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.create_node_dialog import (
    CreateNodeDialog,
    PrecisionNodePreviewRequest,
    RepeatPreviewRequest,
    TranslationalRepeatDialog,
)


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_create_node_preview_signal_contains_position_reference_and_member_flag(qtbot) -> None:
    model = ProjectModel(nodes={_key(1): Node(_key(1), Vec3(10.0, 4.0, 3.0))})
    dialog = CreateNodeDialog(model, reference_node=_key(1))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentWidget(dialog.relative_tab)
    dialog.relative_dx.setValue(1.0)
    dialog.create_member_checkbox.setChecked(True)
    emitted: list[object] = []
    dialog.preview_requested.connect(emitted.append)

    dialog.preview_current()

    request = emitted[-1]
    assert isinstance(request, PrecisionNodePreviewRequest)
    assert request.position == Vec3(11.0, 4.0, 3.0)
    assert request.reference_node == _key(1)
    assert request.create_member is True


def test_repeat_preview_signal_contains_spec_preview_and_resolutions(qtbot) -> None:
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        }
    )
    dialog = TranslationalRepeatDialog(model, reference_node=_key(1), tolerance_m=1e-6)
    qtbot.addWidget(dialog)
    dialog.dx.setValue(1.0)
    dialog.repeats.setValue(3)
    emitted: list[object] = []
    dialog.preview_requested.connect(emitted.append)

    dialog.preview_current()
    combo = dialog.collision_table.cellWidget(0, 2)
    assert combo is not None
    index = combo.findData(ExistingNodeResolution.USE_EXISTING)
    combo.setCurrentIndex(index)
    dialog.preview_current()

    request = emitted[-1]
    assert isinstance(request, RepeatPreviewRequest)
    assert request.spec.connection_mode is RepeatConnectionMode.CONSECUTIVE
    assert request.preview.reused_node_count == 1
    assert request.resolutions == {2: ExistingNodeResolution.USE_EXISTING}


def test_repeat_apply_does_not_accept_unresolved_collision(qtbot) -> None:
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        }
    )
    dialog = TranslationalRepeatDialog(model, reference_node=_key(1), tolerance_m=1e-6)
    qtbot.addWidget(dialog)
    dialog.dx.setValue(1.0)
    dialog.repeats.setValue(3)
    dialog.preview_current()

    dialog.apply_button.click()

    assert dialog.result() == 0
    assert "Choose resolution" in dialog.preview_summary.text()
