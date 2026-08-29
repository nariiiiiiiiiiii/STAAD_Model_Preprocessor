from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.numbering.commands import RenumberAllCommand
from staadprep.numbering.renumber import NumberingPolicy
from staadprep.orientation.normalize import needs_reverse
from staadprep.ui.main_window import MainWindow
from staadprep.ui.model_controls import NumberingPreviewDialog
from staadprep.viewer.interaction import EditMode, LabelVisibility


def _key(value: int) -> UUID:
    return UUID(int=value)


class ModelControlsViewport(QWidget):
    manual_command_requested = Signal(object)
    direction_endpoint_selected = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.selection = SimpleNamespace(selected_nodes=(), selected_members=())
        self.model: ProjectModel | None = None
        self.last_mode = EditMode.SELECT
        self.label_history: list[LabelVisibility] = []
        self.highlighted_nodes: tuple[UUID, ...] = ()
        self.highlighted_members: tuple[UUID, ...] = ()

    def set_model(self, model: ProjectModel) -> None:
        self.model = model

    def set_edit_mode(self, mode: EditMode) -> None:
        self.last_mode = mode

    def set_selection_filter(self, _selection_filter: object) -> None:
        pass

    def set_label_visibility(self, visibility: LabelVisibility) -> None:
        self.label_history.append(visibility)

    def highlight_nodes(self, keys: tuple[UUID, ...]) -> None:
        self.highlighted_nodes = tuple(keys)

    def highlight_members(self, keys: tuple[UUID, ...]) -> None:
        self.highlighted_members = tuple(keys)

    def begin_set_direction(self, member_key: UUID) -> None:
        assert self.model is not None
        member = self.model.members[member_key]
        self.highlight_members((member_key,))
        self.highlight_nodes((member.start, member.end))

    def show_local_x_arrows(self, _visible: bool) -> None:
        pass


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), number=50),
            _key(2): Node(_key(2), Vec3(-4.0, 0.0, 0.0), number=10),
            _key(3): Node(_key(3), Vec3(0.0, 3.0, 0.0), number=80),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2), number=900),
            _key(102): Member(_key(102), _key(1), _key(3), number=300),
        },
        revision=4,
    )


def test_numbering_preview_dialog_shows_old_to_new_rows_without_mutation(qtbot) -> None:
    model = _model()
    before_revision = model.revision
    before_numbers = (
        {key: node.number for key, node in model.nodes.items()},
        {key: member.number for key, member in model.members.items()},
    )
    command = RenumberAllCommand(NumberingPolicy())

    dialog = NumberingPreviewDialog(model, command)
    qtbot.addWidget(dialog)

    assert dialog.table.horizontalHeaderItem(2).text() == "Old"
    assert dialog.table.horizontalHeaderItem(3).text() == "New"
    assert dialog.table.rowCount() == len(model.nodes) + len(model.members)
    assert any(row.old_number == 50 and row.new_number != 50 for row in dialog.rows)
    assert model.revision == before_revision
    assert {key: node.number for key, node in model.nodes.items()} == before_numbers[0]
    assert {key: member.number for key, member in model.members.items()} == before_numbers[1]


def test_toolbar_exposes_all_t20_numbering_and_direction_actions(qtbot) -> None:
    viewport = ModelControlsViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    assert window.auto_node_number_action.text() == "Auto Node Number"
    assert window.auto_member_number_action.text() == "Auto Member Number"
    assert window.auto_number_all_action.text() == "Auto Number All"
    assert window.auto_fix_axis_action.text() == "Auto Fix Axis"
    assert window.auto_fix_selected_action.text() == "Auto Fix Selected"
    assert window.flip_selected_action.text() == "Flip Selected"
    assert window.set_direction_action.text() == "Set Direction"


def test_auto_number_all_previews_then_applies_as_one_history_item(qtbot) -> None:
    viewport = ModelControlsViewport()
    dialogs: list[NumberingPreviewDialog] = []

    def run_preview(dialog: NumberingPreviewDialog) -> bool:
        dialogs.append(dialog)
        return True

    window = MainWindow(
        viewport_factory=lambda: viewport,
        numbering_preview_runner=run_preview,
    )
    qtbot.addWidget(window)
    model = _model()
    geometry = {key: node.position for key, node in model.nodes.items()}
    incidence = {key: (member.start, member.end) for key, member in model.members.items()}
    window.set_canonical_model(model)

    window.auto_number_all_action.trigger()

    assert len(dialogs) == 1
    assert dialogs[0].rows
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    assert sorted(node.number for node in model.nodes.values()) == [1, 2, 3]
    assert sorted(member.number for member in model.members.values()) == [1, 2]
    assert {key: node.position for key, node in model.nodes.items()} == geometry
    assert {key: (member.start, member.end) for key, member in model.members.items()} == incidence


def test_set_direction_requires_one_member_and_endpoint_click_sets_start_with_local_x_preview(
    qtbot,
) -> None:
    viewport = ModelControlsViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    viewport.selection.selected_members = (_key(101),)
    before_positions = {key: node.position for key, node in model.nodes.items()}

    window.set_direction_action.trigger()

    assert viewport.last_mode is EditMode.SET_DIRECTION
    assert viewport.highlighted_members == (_key(101),)
    assert set(viewport.highlighted_nodes) == {_key(1), _key(2)}
    assert viewport.label_history[-1].local_x is True
    revision = model.revision

    viewport.direction_endpoint_selected.emit(_key(2))

    assert model.members[_key(101)].start == _key(2)
    assert model.members[_key(101)].end == _key(1)
    assert model.revision == revision + 1
    assert {key: node.position for key, node in model.nodes.items()} == before_positions
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    assert viewport.last_mode is EditMode.SELECT


def test_auto_fix_selected_is_atomic_and_only_changes_selected_incidence(qtbot) -> None:
    viewport = ModelControlsViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    viewport.selection.selected_members = (_key(101),)
    unselected = (model.members[_key(102)].start, model.members[_key(102)].end)

    assert needs_reverse(model, model.members[_key(101)])
    window.auto_fix_selected_action.trigger()

    assert not needs_reverse(model, model.members[_key(101)])
    assert (model.members[_key(102)].start, model.members[_key(102)].end) == unselected
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_flip_selected_is_atomic_and_reversible_from_history(qtbot) -> None:
    viewport = ModelControlsViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    viewport.selection.selected_members = (_key(101), _key(102))
    before = {key: (member.start, member.end) for key, member in model.members.items()}

    window.flip_selected_action.trigger()

    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    for key in (_key(101), _key(102)):
        assert (model.members[key].start, model.members[key].end) == (
            before[key][1],
            before[key][0],
        )

    window.undo_repair()
    assert {key: (member.start, member.end) for key, member in model.members.items()} == before
