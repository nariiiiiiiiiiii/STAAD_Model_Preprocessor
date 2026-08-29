from __future__ import annotations

from uuid import UUID

from staadprep.model.entities import Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.create_node_dialog import CreateNodeDialog


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(nodes={_key(21): Node(_key(21), Vec3(10.0, 4.0, 3.0))})


def test_dialog_labels_canonical_staadd_axes_and_reference_coordinates(qtbot) -> None:
    model = _model()
    dialog = CreateNodeDialog(model, reference_node=_key(21))
    qtbot.addWidget(dialog)

    assert dialog.exact_x_label.text() == "STAAD X"
    assert dialog.exact_y_label.text() == "STAAD Y (Vertical)"
    assert dialog.exact_z_label.text() == "STAAD Z"
    assert dialog.reference_label.text() == "Reference: X=10.000, Y=4.000, Z=3.000 m"
    assert dialog.create_member_checkbox.text().startswith("Create Member")


def test_relative_preview_uses_reference_plus_offsets_without_model_mutation(qtbot) -> None:
    model = _model()
    dialog = CreateNodeDialog(model, reference_node=_key(21))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentWidget(dialog.relative_tab)
    dialog.relative_dx.setValue(1.0)
    dialog.relative_dy.setValue(-0.0)
    dialog.relative_dz.setValue(0.0)
    revision = model.revision

    position = dialog.preview_current()

    assert position == Vec3(11.0, 4.0, 3.0)
    assert dialog.result_label.text() == "Result: X=11.000, Y=4.000, Z=3.000 m"
    assert model.revision == revision


def test_exact_preview_and_spec_are_explicit_staadd_coordinates(qtbot) -> None:
    model = _model()
    dialog = CreateNodeDialog(model, reference_node=_key(21))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentWidget(dialog.exact_tab)
    dialog.exact_x.setValue(12.5)
    dialog.exact_y.setValue(7.25)
    dialog.exact_z.setValue(-1.0)

    assert dialog.preview_current() == Vec3(12.5, 7.25, -1.0)
    spec = dialog.current_exact_spec()
    assert (spec.x, spec.y, spec.z) == (12.5, 7.25, -1.0)


def test_relative_spec_includes_create_member_checkbox(qtbot) -> None:
    dialog = CreateNodeDialog(_model(), reference_node=_key(21))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentWidget(dialog.relative_tab)
    dialog.relative_dx.setValue(1.0)
    dialog.create_member_checkbox.setChecked(True)

    spec = dialog.current_relative_spec()

    assert spec.reference_node == _key(21)
    assert spec.dx == 1.0
    assert spec.create_member is True
