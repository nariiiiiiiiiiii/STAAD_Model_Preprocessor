from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from staadprep.editing.create_node import (
    ExactNodeSpec,
    MemberTranslationalRepeatSpec,
    RelativeNodeSpec,
    RepeatConnectionMode,
    TranslationalRepeatSpec,
    analyze_member_translational_repeat,
    analyze_translational_repeat,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.create_node_dialog import (
    PrecisionNodePreviewRequest,
    RepeatPreviewRequest,
)
from staadprep.ui.main_window import MainWindow
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter
from staadprep.viewer.selection import SelectionState


def _key(value: int) -> UUID:
    return UUID(int=value)


class PrecisionViewport(QWidget):
    manual_command_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.model: ProjectModel | None = None
        self.mode = EditMode.SELECT
        self.selection = SelectionState()
        self.highlighted_nodes: tuple[UUID, ...] = ()
        self.precision_previews: list[object] = []
        self.repeat_previews: list[object] = []
        self.member_repeat_previews: list[object] = []
        self.clear_preview_calls = 0

    def set_model(self, model: ProjectModel) -> None:
        self.model = model

    def set_edit_mode(self, mode: EditMode) -> None:
        self.mode = mode

    def set_selection_filter(self, selection_filter: SelectionFilter) -> None:
        del selection_filter

    def set_label_visibility(self, visibility: LabelVisibility) -> None:
        del visibility

    def highlight_nodes(self, keys: tuple[UUID, ...]) -> None:
        self.highlighted_nodes = tuple(keys)

    def show_precise_node_preview(
        self,
        position: Vec3,
        *,
        reference_node: UUID | None = None,
        create_member: bool = False,
    ) -> None:
        self.precision_previews.append((position, reference_node, create_member))

    def show_translational_repeat_preview(
        self,
        preview: object,
        spec: object,
        resolutions: object,
    ) -> None:
        self.repeat_previews.append((preview, spec, resolutions))

    def show_member_translational_repeat_preview(
        self,
        preview: object,
        spec: object,
        resolutions: object,
    ) -> None:
        self.member_repeat_previews.append((preview, spec, resolutions))

    def clear_precision_preview(self) -> None:
        self.clear_preview_calls += 1


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(3.0, 0.0, 0.0)),
        }
    )


def test_create_node_mode_action_switches_viewport_mode(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.create_node_mode_action.trigger()

    assert viewport.mode is EditMode.CREATE_NODE
    assert window.create_node_mode_action.isChecked()


def test_exact_create_executes_reversible_command_through_history(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)

    window._apply_exact_node_spec(ExactNodeSpec(1.0, 2.0, 3.0), tolerance_m=1e-6)

    assert any(node.position == Vec3(1.0, 2.0, 3.0) for node in model.nodes.values())
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    window.undo_repair()
    assert len(model.nodes) == 2


def test_relative_create_member_is_atomic_and_one_undo(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)

    window._apply_relative_node_spec(
        RelativeNodeSpec(_key(1), 0.0, 2.0, 0.0, create_member=True),
        tolerance_m=1e-6,
    )

    assert len(model.nodes) == 3
    assert len(model.members) == 1
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    window.undo_repair()
    assert len(model.nodes) == 2
    assert not model.members


def test_collision_use_existing_does_not_create_duplicate_node(qtbot) -> None:
    viewport = PrecisionViewport()
    prompts: list[str] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_use_existing=lambda message: prompts.append(message) or True,
    )
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)

    window._apply_exact_node_spec(ExactNodeSpec(3.0, 0.0, 0.0), tolerance_m=1e-6)

    assert prompts
    assert len(model.nodes) == 2
    assert viewport.highlighted_nodes == (_key(2),)
    assert model.revision == 0


def test_relative_collision_use_existing_with_create_member_connects_reference(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_use_existing=lambda _message: True,
    )
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)

    window._apply_relative_node_spec(
        RelativeNodeSpec(_key(1), 3.0, 0.0, 0.0, create_member=True),
        tolerance_m=1e-6,
    )

    assert len(model.nodes) == 2
    assert len(model.members) == 1
    member = next(iter(model.members.values()))
    assert {member.start, member.end} == {_key(1), _key(2)}
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_repeat_apply_is_one_atomic_history_item(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = ProjectModel(nodes={_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))})
    window.set_canonical_model(model)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.CONSECUTIVE)

    window._apply_translational_repeat(spec, resolutions={}, tolerance_m=1e-6)

    assert len(model.nodes) == 4
    assert len(model.members) == 3
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    window.undo_repair()
    assert len(model.nodes) == 1
    assert not model.members


def test_selected_member_repeat_apply_is_one_atomic_history_item(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2), group="Roof")},
    )
    window.set_canonical_model(model)
    spec = MemberTranslationalRepeatSpec((_key(101),), 0.0, 3.0, 0.0, 2)

    window._apply_member_translational_repeat(spec, resolutions={}, tolerance_m=1e-6)

    assert len(model.nodes) == 6
    assert len(model.members) == 3
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    window.undo_repair()
    assert len(model.nodes) == 2
    assert len(model.members) == 1


def test_precision_preview_request_is_forwarded_to_viewport(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    request = PrecisionNodePreviewRequest(
        position=Vec3(1.0, 2.0, 3.0),
        reference_node=_key(1),
        create_member=True,
    )

    window._show_precision_preview_request(request)

    assert viewport.precision_previews == [(Vec3(1.0, 2.0, 3.0), _key(1), True)]


def test_repeat_preview_request_is_forwarded_to_viewport(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = ProjectModel(nodes={_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))})
    window.set_canonical_model(model)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 2, RepeatConnectionMode.CONSECUTIVE)
    preview = analyze_translational_repeat(model, spec, tolerance_m=1e-6)
    request = RepeatPreviewRequest(preview, spec, {})

    window._show_repeat_preview_request(request)

    assert viewport.repeat_previews == [(preview, spec, {})]


def test_member_repeat_preview_request_is_forwarded_to_viewport(qtbot) -> None:
    viewport = PrecisionViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    window.set_canonical_model(model)
    spec = MemberTranslationalRepeatSpec((_key(101),), 0.0, 3.0, 0.0, 1)
    preview = analyze_member_translational_repeat(model, spec, tolerance_m=1e-6)
    request = SimpleNamespace(preview=preview, spec=spec, resolutions={})

    window._show_member_repeat_preview_request(request)

    assert viewport.member_repeat_previews == [(preview, spec, {})]
