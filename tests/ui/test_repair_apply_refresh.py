from __future__ import annotations

from dataclasses import asdict
from uuid import UUID

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import needs_reverse
from staadprep.ui.main_window import MainWindow
from staadprep.ui.repair_apply_dialog import RepairApplyDialog
from staadprep.validation.issues import IssueType
from staadprep.viewer.selection import SelectionState


def _key(value: int) -> UUID:
    return UUID(int=value)


def _graph(model: ProjectModel) -> tuple[object, ...]:
    return (
        tuple(
            sorted(
                (key.int, asdict(node))
                for key, node in model.nodes.items()
            )
        ),
        tuple(
            sorted(
                (key.int, asdict(member))
                for key, member in model.members.items()
            )
        ),
        model.revision,
    )


class RefreshViewport(QWidget):
    selection_changed = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.selection = SelectionState()
        self.model: ProjectModel | None = None
        self.set_model_calls = 0
        self.clear_selection_calls = 0

    def set_model(self, model: ProjectModel) -> None:
        self.model = model
        self.set_model_calls += 1
        self.selection.clear()

    def clear_selection(self) -> None:
        self.selection.clear()
        self.clear_selection_calls += 1
        self.selection_changed.emit((), ())


class RejectingCommand:
    def apply(self, _model: ProjectModel):
        raise ValueError("independent rejection evidence")

    def revert(self, _model: ProjectModel):
        raise RuntimeError("RejectingCommand was never applied")

    def audit_parameters(self) -> dict[str, object]:
        return {}


def _orphan_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0), number=2),
            _key(50): Node(_key(50), Vec3(20.0, 0.0, 0.0), number=50),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2), number=1)},
    )


def _split_model() -> ProjectModel:
    return ProjectModel(
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


def _near_gap_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(1.0005, 0.0, 0.0)),
            _key(4): Node(_key(4), Vec3(2.0, 0.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(3), _key(4)),
        },
    )


def _direction_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(4.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(0.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, 4.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(2), _key(3)),
        },
        revision=7,
    )


def _apply_then_ok_runner(
    qtbot,
    model: ProjectModel,
    observed: list[tuple[int, int, int]],
):
    def run(dialog: RepairApplyDialog) -> None:
        assert dialog.ok_button.isEnabled() is False
        qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        history = dialog.parent().repair_history
        assert history is not None
        observed.append((model.revision, len(history.audit.entries), len(history.undo_stack)))
        qtbot.mouseClick(dialog.ok_button, Qt.MouseButton.LeftButton)
        observed.append((model.revision, len(history.audit.entries), len(history.undo_stack)))

    return run


def test_delete_apply_then_ok_refreshes_once_and_undo_restores_exact_graph(qtbot) -> None:
    viewport = RefreshViewport()
    model = _orphan_model()
    observed: list[tuple[int, int, int]] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        repair_dialog_runner=_apply_then_ok_runner(qtbot, model, observed),
    )
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    before = _graph(model)
    viewport.selection.set_nodes((_key(50),))
    viewport.selection_changed.emit((_key(50),), ())
    renders_before = viewport.set_model_calls

    window.delete_selection_action.trigger()

    assert observed[0] == observed[1]
    assert observed[0] == (before[2] + 1, 1, 1)
    assert _key(50) not in model.nodes
    assert viewport.set_model_calls >= renders_before + 2
    assert viewport.clear_selection_calls >= 2
    assert viewport.selection.selected_nodes == ()
    assert window.project_explorer.node_item.text(0) == "Nodes (2)"
    assert window.undo_action.isEnabled() is True
    assert "Type —" in window.properties_panel.content.text()

    window.undo_repair()
    assert _graph(model) == before


def test_merge_apply_then_ok_executes_once_and_undo_restores_exact_graph(qtbot) -> None:
    viewport = RefreshViewport()
    model = _split_model()
    observed: list[tuple[int, int, int]] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        repair_dialog_runner=_apply_then_ok_runner(qtbot, model, observed),
    )
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    before = _graph(model)
    viewport.selection.set_members((_key(101), _key(102)))
    viewport.selection_changed.emit((), (_key(101), _key(102)))

    window.merge_members_action.trigger()

    assert observed[0] == observed[1] == (before[2] + 1, 1, 1)
    assert set(model.nodes) == {_key(1), _key(3)}
    assert set(model.members) == {_key(101)}
    assert window.project_explorer.member_item.text(0) == "Members (1)"
    window.undo_repair()
    assert _graph(model) == before


def test_quick_fix_apply_then_ok_revalidates_without_undo_and_is_reversible(qtbot) -> None:
    viewport = RefreshViewport()
    model = _near_gap_model()
    observed: list[tuple[int, int, int]] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        repair_dialog_runner=_apply_then_ok_runner(qtbot, model, observed),
    )
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    before = _graph(model)
    gap = next(issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP)
    window.issue_console.select_issue(gap.id)

    window.apply_selected_quick_fix()

    assert observed[0] == observed[1] == (before[2] + 1, 1, 1)
    assert not any(issue.type is IssueType.UNCONNECTED_GAP for issue in window.current_issues)
    window.undo_repair()
    assert _graph(model) == before


def test_auto_fix_all_and_selected_apply_exactly_once_and_undo(qtbot) -> None:
    for selected_only in (False, True):
        viewport = RefreshViewport()
        model = _direction_model()
        observed: list[tuple[int, int, int]] = []
        window = MainWindow(
            viewport_factory=lambda viewport=viewport: viewport,
            repair_dialog_runner=_apply_then_ok_runner(qtbot, model, observed),
        )
        qtbot.addWidget(window)
        window.set_canonical_model(model)
        before = _graph(model)
        assert needs_reverse(model, model.members[_key(101)])

        if selected_only:
            viewport.selection.set_members((_key(101),))
            viewport.selection_changed.emit((), (_key(101),))
            window.auto_fix_selected_action.trigger()
        else:
            window.auto_fix_axis_action.trigger()

        assert observed[0] == observed[1]
        assert observed[0][1:] == (1, 1)
        assert not needs_reverse(model, model.members[_key(101)])
        window.undo_repair()
        assert _graph(model) == before


def test_cancel_before_apply_preserves_graph_revision_audit_and_history(qtbot) -> None:
    viewport = RefreshViewport()
    model = _orphan_model()

    def cancel(dialog: RepairApplyDialog) -> None:
        qtbot.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)

    window = MainWindow(
        viewport_factory=lambda: viewport,
        repair_dialog_runner=cancel,
    )
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    before = _graph(model)
    viewport.selection.set_nodes((_key(50),))

    window.delete_selected_entities()

    assert _graph(model) == before
    assert window.repair_history is not None
    assert window.repair_history.audit.entries == ()
    assert window.repair_history.undo_stack == ()


def test_rejected_apply_shows_exact_error_and_preserves_graph_and_history(qtbot) -> None:
    viewport = RefreshViewport()
    model = _orphan_model()
    messages: list[str] = []

    def reject_after_attempt(dialog: RepairApplyDialog) -> None:
        qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        messages.append(dialog.error_label.text())
        assert dialog.ok_button.isEnabled() is False
        assert dialog.apply_button.isEnabled() is True
        qtbot.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)

    window = MainWindow(
        viewport_factory=lambda: viewport,
        repair_dialog_runner=reject_after_attempt,
    )
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    before = _graph(model)

    applied = window._run_repair_apply_dialog(
        RejectingCommand(),
        title="Rejected Repair",
        summary="This command must be rejected",
    )

    assert applied is False
    assert messages == ["Repair rejected: independent rejection evidence"]
    assert _graph(model) == before
    assert window.repair_history is not None
    assert window.repair_history.audit.entries == ()
    assert window.repair_history.undo_stack == ()


def test_multiple_orphan_quick_fixes_clear_stale_row_and_can_repeat(qtbot) -> None:
    viewport = RefreshViewport()
    model = _orphan_model()
    model.nodes[_key(51)] = Node(_key(51), Vec3(24.0, 0.0, 0.0), number=51)
    before = _graph(model)
    observed: list[tuple[int, int, int]] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        repair_dialog_runner=_apply_then_ok_runner(qtbot, model, observed),
    )
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    first = next(issue for issue in window.current_issues if issue.type is IssueType.ORPHAN_NODE)
    window.issue_console.select_issue(first.id)

    window.apply_selected_quick_fix()

    remaining = [
        issue for issue in window.current_issues if issue.type is IssueType.ORPHAN_NODE
    ]
    assert len(remaining) == 1
    assert window.issue_console.selected_issue is None
    assert window.repair_action.isEnabled() is False

    window.issue_console.select_issue(remaining[0].id)
    assert window._selected_issue_id == remaining[0].id
    assert window.repair_action.isEnabled() is True
    window.apply_selected_quick_fix()

    assert not any(issue.type is IssueType.ORPHAN_NODE for issue in window.current_issues)
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 2
    window.undo_repair()
    assert sum(
        issue.type is IssueType.ORPHAN_NODE for issue in window.current_issues
    ) == 1
    window.undo_repair()
    assert _graph(model) == before
