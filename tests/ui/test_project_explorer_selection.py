from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.main_window import MainWindow
from staadprep.ui.panels import ProjectExplorerPanel
from staadprep.viewer.selection import SelectionState


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), number=20),
            _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0), number=10),
            _key(3): Node(_key(3), Vec3(2.0, 0.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2), number=8),
            _key(102): Member(_key(102), _key(2), _key(3), number=4),
        },
    )


class ExplorerViewport(QWidget):
    selection_changed = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.selection = SelectionState()
        self.selection_filter = None

    def set_model(self, model: ProjectModel) -> None:
        del model

    def set_edit_mode(self, mode: object) -> None:
        del mode

    def set_selection_filter(self, selection_filter: object) -> None:
        self.selection_filter = selection_filter

    def set_label_visibility(self, visibility: object) -> None:
        del visibility

    def clear_selection(self) -> None:
        self.selection.clear()
        self.selection_changed.emit((), ())

    def highlight_nodes(self, keys: tuple[UUID, ...]) -> None:
        self.selection.set_nodes(tuple(keys))
        self.selection_changed.emit(
            self.selection.selected_nodes,
            self.selection.selected_members,
        )

    def highlight_members(self, keys: tuple[UUID, ...]) -> None:
        self.selection.set_members(tuple(keys))
        self.selection_changed.emit(
            self.selection.selected_nodes,
            self.selection.selected_members,
        )


def test_entity_rows_are_number_sorted_and_rebuild_without_duplicates(qtbot) -> None:
    panel = ProjectExplorerPanel()
    qtbot.addWidget(panel)

    panel.set_canonical_entities(_model())

    assert [
        panel.node_item.child(index).text(0)
        for index in range(panel.node_item.childCount())
    ] == ["Node No. 10", "Node No. 20", "Node No. —"]
    assert [
        panel.member_item.child(index).text(0)
        for index in range(panel.member_item.childCount())
    ] == ["Member No. 4", "Member No. 8"]

    panel.set_canonical_entities(_model())

    assert panel.node_item.childCount() == 3
    assert panel.member_item.childCount() == 2


def test_individual_and_group_rows_emit_exact_entity_keys(qtbot) -> None:
    panel = ProjectExplorerPanel()
    qtbot.addWidget(panel)
    panel.set_canonical_entities(_model())

    with qtbot.waitSignal(panel.node_selection_requested) as node_selected:
        panel.tree.itemClicked.emit(panel.node_item.child(0), 0)
    assert node_selected.args == [(_key(2),)]

    with qtbot.waitSignal(panel.member_selection_requested) as members_selected:
        panel.tree.itemClicked.emit(panel.member_item, 0)
    assert members_selected.args == [(_key(102), _key(101))]
    assert panel.member_item.isExpanded()


def test_explorer_selection_highlights_viewport_and_updates_properties(qtbot) -> None:
    viewport = ExplorerViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(_model())

    window.project_explorer.tree.itemClicked.emit(
        window.project_explorer.node_item.child(0),
        0,
    )

    assert viewport.selection.selected_nodes == (_key(2),)
    assert viewport.selection.selected_members == ()
    assert viewport.selection_filter.nodes
    assert not viewport.selection_filter.members
    assert "Type Node" in window.properties_panel.content.text()
    assert "Node No. 10" in window.properties_panel.content.text()

    window.project_explorer.tree.itemClicked.emit(
        window.project_explorer.member_item,
        0,
    )

    assert viewport.selection.selected_nodes == ()
    assert viewport.selection.selected_members == (_key(102), _key(101))
    assert not viewport.selection_filter.nodes
    assert viewport.selection_filter.members
    assert "Mixed selection" in window.properties_panel.content.text()
    assert "Members 2" in window.properties_panel.content.text()
