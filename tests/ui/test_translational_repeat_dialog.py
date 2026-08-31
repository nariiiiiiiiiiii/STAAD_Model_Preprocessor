from __future__ import annotations

from uuid import UUID

from staadprep.editing.create_node import ExistingNodeResolution, RepeatConnectionMode
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.create_node_dialog import (
    MemberTranslationalRepeatDialog,
    TranslationalRepeatDialog,
)


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model(*, collision: bool = False) -> ProjectModel:
    nodes = {_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))}
    if collision:
        nodes[_key(2)] = Node(_key(2), Vec3(2.0, 0.0, 0.0))
    return ProjectModel(nodes=nodes)


def test_repeat_dialog_labels_delta_axes_and_count_excludes_reference(qtbot) -> None:
    dialog = TranslationalRepeatDialog(_model(), reference_node=_key(1), tolerance_m=1e-6)
    qtbot.addWidget(dialog)

    assert dialog.dx_label.text() == "ΔX"
    assert dialog.dy_label.text() == "ΔY (Vertical)"
    assert dialog.dz_label.text() == "ΔZ"
    assert "excluding reference" in dialog.repeat_label.text().lower()
    assert dialog.connection_combo.currentData() == RepeatConnectionMode.CONSECUTIVE


def test_repeat_preview_reports_counts_and_final_coordinate_without_mutation(qtbot) -> None:
    model = _model()
    dialog = TranslationalRepeatDialog(model, reference_node=_key(1), tolerance_m=1e-6)
    qtbot.addWidget(dialog)
    dialog.dx.setValue(1.0)
    dialog.repeats.setValue(5)
    revision = model.revision

    preview = dialog.preview_current()

    assert preview.new_node_count == 5
    assert preview.new_member_count == 5
    assert preview.final_coordinate == Vec3(5.0, 0.0, 0.0)
    assert "New Nodes: 5" in dialog.preview_summary.text()
    assert "New Members: 5" in dialog.preview_summary.text()
    assert "Final: X=5.000" in dialog.preview_summary.text()
    assert model.revision == revision


def test_collision_preview_requires_explicit_resolution_and_exposes_choices(qtbot) -> None:
    model = _model(collision=True)
    dialog = TranslationalRepeatDialog(model, reference_node=_key(1), tolerance_m=1e-6)
    qtbot.addWidget(dialog)
    dialog.dx.setValue(1.0)
    dialog.repeats.setValue(3)

    preview = dialog.preview_current()

    assert preview.collisions == {2: _key(2)}
    assert dialog.collision_table.rowCount() == 1
    resolution_combo = dialog.collision_table.cellWidget(0, 2)
    assert resolution_combo is not None
    values = [resolution_combo.itemData(index) for index in range(resolution_combo.count())]
    assert ExistingNodeResolution.USE_EXISTING in values
    assert ExistingNodeResolution.SKIP_STEP in values
    assert ExistingNodeResolution.CANCEL in values
    assert dialog.current_resolutions() == {}

    resolution_combo.setCurrentIndex(values.index(ExistingNodeResolution.USE_EXISTING))
    assert dialog.current_resolutions() == {2: ExistingNodeResolution.USE_EXISTING}


def test_member_repeat_dialog_reports_selected_members_and_counts(qtbot) -> None:
    model = ProjectModel(
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
    dialog = MemberTranslationalRepeatDialog(
        model,
        member_keys=(_key(101), _key(102)),
        tolerance_m=1e-6,
    )
    qtbot.addWidget(dialog)
    dialog.dy.setValue(3.0)
    dialog.repeats.setValue(2)

    preview = dialog.preview_current()

    assert "2 selected Members" in dialog.selection_label.text()
    assert preview.source_node_count == 3
    assert preview.new_node_count == 6
    assert preview.new_member_count == 4
    assert "New Members: 4" in dialog.preview_summary.text()
    assert dialog.current_spec().member_keys == (_key(101), _key(102))


def test_member_repeat_dialog_emits_viewport_preview_request(qtbot) -> None:
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    dialog = MemberTranslationalRepeatDialog(
        model,
        member_keys=(_key(101),),
        tolerance_m=1e-6,
    )
    qtbot.addWidget(dialog)
    dialog.dy.setValue(3.0)
    requests: list[object] = []
    dialog.preview_requested.connect(requests.append)

    preview = dialog.preview_current()

    assert len(requests) == 1
    request = requests[0]
    assert request.preview == preview
    assert request.spec == dialog.current_spec()
    assert request.resolutions == {}
