from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.main_window import MainWindow
from staadprep.viewer.selection import SelectionState


def _key(value: int) -> UUID:
    return UUID(int=value)


class SelectionViewport(QWidget):
    selection_changed = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.selection = SelectionState()

    def set_model(self, model: ProjectModel) -> None:
        del model

    def set_edit_mode(self, mode: object) -> None:
        del mode

    def set_selection_filter(self, selection_filter: object) -> None:
        del selection_filter

    def set_label_visibility(self, visibility: object) -> None:
        del visibility


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(1.25, 2.5, 3.75), number=7),
            _key(2): Node(_key(2), Vec3(5.25, 2.5, 3.75), number=8),
        },
        members={
            _key(101): Member(
                _key(101),
                _key(1),
                _key(2),
                number=12,
                source_ref="Edge-4",
                group="Roof",
            )
        },
    )


def test_selected_node_and_member_populate_properties(qtbot) -> None:
    viewport = SelectionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(_model())

    viewport.selection_changed.emit((_key(1),), ())
    node_text = window.properties_panel.content.text()
    assert window.crop_selection_action.isEnabled()
    assert node_text == (
        "Selected entity\n\n"
        "Type Node\n"
        "Node No. 7\n"
        "X 1.25 m\n"
        "Y 2.5 m\n"
        "Z 3.75 m"
    )
    assert "UUID" not in node_text
    assert str(_key(1)) not in node_text
    assert "Source" not in node_text

    viewport.selection_changed.emit((), (_key(101),))
    member_text = window.properties_panel.content.text()
    assert member_text == (
        "Selected entity\n\n"
        "Type Member\n"
        "Member No. 12\n"
        "Start Node No. 7\n"
        "Start X 1.25 m\n"
        "Start Y 2.5 m\n"
        "Start Z 3.75 m\n"
        "End Node No. 8\n"
        "End X 5.25 m\n"
        "End Y 2.5 m\n"
        "End Z 3.75 m\n"
        "Length 4 m\n"
        "Group / Layer Roof"
    )
    assert "UUID" not in member_text
    assert str(_key(101)) not in member_text
    assert str(_key(1)) not in member_text
    assert str(_key(2)) not in member_text
    assert "Source" not in member_text
    assert "Edge-4" not in member_text


def test_cleared_and_mixed_selection_have_explicit_properties_state(qtbot) -> None:
    viewport = SelectionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(_model())

    viewport.selection_changed.emit((_key(1),), (_key(101),))
    assert "Mixed selection" in window.properties_panel.content.text()
    assert "Nodes 1" in window.properties_panel.content.text()
    assert "Members 1" in window.properties_panel.content.text()

    viewport.selection_changed.emit((), ())
    assert "Type —" in window.properties_panel.content.text()
    assert not window.crop_selection_action.isEnabled()
