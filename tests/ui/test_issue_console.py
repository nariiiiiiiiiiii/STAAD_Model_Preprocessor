from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QTableWidget, QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.issue_console import IssueConsole
from staadprep.ui.main_window import MainWindow
from staadprep.validation.issues import Issue, IssueSeverity, IssueType


def _key(value: int) -> UUID:
    return UUID(int=value)


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("viewport_host")
        self.model: ProjectModel | None = None
        self.highlighted_nodes: tuple[UUID, ...] = ()
        self.highlighted_members: tuple[UUID, ...] = ()
        self.focused: tuple[tuple[UUID, ...], tuple[UUID, ...], Vec3 | None] | None = None
        self.isolated: tuple[UUID, ...] = ()

    def set_model(self, model: ProjectModel) -> None:
        self.model = model

    def highlight_nodes(self, keys) -> None:
        self.highlighted_nodes = tuple(keys)

    def highlight_members(self, keys) -> None:
        self.highlighted_members = tuple(keys)

    def focus_entities(self, node_keys, member_keys, location=None) -> None:
        self.focused = (tuple(node_keys), tuple(member_keys), location)

    def isolate_entities(self, keys) -> None:
        self.isolated = tuple(keys)


def _near_gap_model() -> ProjectModel:
    nodes = [
        Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        Node(_key(2), Vec3(1.0, 0.0, 0.0)),
        Node(_key(3), Vec3(1.0005, 0.0, 0.0)),
        Node(_key(4), Vec3(2.0, 0.0, 0.0)),
    ]
    members = [
        Member(_key(101), _key(1), _key(2)),
        Member(_key(102), _key(3), _key(4)),
    ]
    return ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )


def _orphan_model() -> ProjectModel:
    nodes = [
        Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        Node(_key(2), Vec3(1.0, 0.0, 0.0)),
        Node(_key(3), Vec3(5.0, 0.0, 0.0)),
    ]
    member = Member(_key(101), _key(1), _key(2))
    return ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member},
    )


def _two_structure_model() -> ProjectModel:
    nodes = [
        Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        Node(_key(2), Vec3(1.0, 0.0, 0.0)),
        Node(_key(3), Vec3(10.0, 0.0, 0.0)),
        Node(_key(4), Vec3(11.0, 0.0, 0.0)),
    ]
    members = [
        Member(_key(101), _key(1), _key(2)),
        Member(_key(102), _key(3), _key(4)),
    ]
    return ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )


def test_issue_console_binds_rows_to_exact_issue_ids_and_filters(qtbot) -> None:
    console = IssueConsole()
    qtbot.addWidget(console)
    issues = [
        Issue(
            id="issue-error",
            severity=IssueSeverity.ERROR,
            type=IssueType.ORPHAN_NODE,
            entity_keys=(_key(1),),
            location=None,
            description="orphan",
        ),
        Issue(
            id="issue-warning",
            severity=IssueSeverity.WARNING,
            type=IssueType.SHORT_MEMBER,
            entity_keys=(_key(101),),
            location=None,
            description="short",
        ),
    ]

    console.set_issues(issues)

    assert console.table.rowCount() == 2
    assert console.table.item(0, 0).data(Qt.ItemDataRole.UserRole) == "issue-error"
    assert console.table.item(1, 0).data(Qt.ItemDataRole.UserRole) == "issue-warning"
    assert console.counts_label.text() == "Errors 1  |  Warnings 1  |  Info 0"

    console.severity_filter.setCurrentText("ERROR")
    assert console.table.rowCount() == 1
    assert console.table.item(0, 0).data(Qt.ItemDataRole.UserRole) == "issue-error"


def test_issue_console_supports_extended_multi_issue_selection(qtbot) -> None:
    console = IssueConsole()
    qtbot.addWidget(console)
    issues = (
        Issue(
            id="issue-orphan-a",
            severity=IssueSeverity.ERROR,
            type=IssueType.ORPHAN_NODE,
            entity_keys=(_key(50),),
            location=None,
            description="first orphan",
        ),
        Issue(
            id="issue-orphan-b",
            severity=IssueSeverity.ERROR,
            type=IssueType.ORPHAN_NODE,
            entity_keys=(_key(51),),
            location=None,
            description="second orphan",
        ),
        Issue(
            id="issue-short-member",
            severity=IssueSeverity.ERROR,
            type=IssueType.SHORT_MEMBER,
            entity_keys=(_key(101),),
            location=None,
            description="short member",
        ),
    )
    observed: list[tuple[str, ...]] = []
    console.issues_selected.connect(
        lambda selected: observed.append(tuple(issue.id for issue in selected))
    )
    console.set_issues(issues)

    assert (
        console.table.selectionMode()
        is QTableWidget.SelectionMode.ExtendedSelection
    )
    console.table.selectRow(0)
    console.table.selectionModel().select(
        console.table.model().index(1, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )

    assert console.selected_issues == issues[:2]
    assert console.selected_issue is None
    assert observed[-1] == ("issue-orphan-a", "issue-orphan-b")

    console.select_issue("issue-short-member")
    assert console.selected_issues == (issues[2],)
    assert console.selected_issue == issues[2]
    assert observed[-1] == ("issue-short-member",)


def test_selecting_issue_highlights_and_focuses_exact_entities(qtbot) -> None:
    viewport = RecordingViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(_near_gap_model())

    gap = next(issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP)
    window.issue_console.select_issue(gap.id)

    assert set(viewport.highlighted_nodes) == {_key(2), _key(3)}
    assert viewport.highlighted_members == ()
    assert viewport.focused is not None
    assert set(viewport.focused[0]) == {_key(2), _key(3)}


def test_multi_issue_selection_highlights_union_and_preflights_batch(qtbot) -> None:
    viewport = RecordingViewport()
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(1.0005, 0.0, 0.0)),
            _key(4): Node(_key(4), Vec3(2.0, 0.0, 0.0)),
            _key(50): Node(_key(50), Vec3(10.0, 10.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(3), _key(4)),
        },
    )
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    gap = next(issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP)
    orphan = next(issue for issue in window.current_issues if issue.type is IssueType.ORPHAN_NODE)

    window.issue_console.select_issue(gap.id)
    orphan_row = next(
        row
        for row in range(window.issue_console.table.rowCount())
        if window.issue_console.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == orphan.id
    )
    window.issue_console.table.selectionModel().select(
        window.issue_console.table.model().index(orphan_row, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )

    assert window.issue_console.selected_issue is None
    assert {issue.id for issue in window.issue_console.selected_issues} == {gap.id, orphan.id}
    assert set(viewport.highlighted_nodes) == {_key(2), _key(3), _key(50)}
    assert "2 issues" in window.properties_panel.content.text()
    assert "2 issues" in window.quick_fix_panel.selected_label.text()
    assert window.quick_fix_panel.apply_button.isEnabled()
    assert window.repair_action.isEnabled()


def test_conflicting_multi_issue_selection_disables_quick_fix(qtbot) -> None:
    viewport = RecordingViewport()
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0)),
            _key(50): Node(_key(50), Vec3(10.0, 0.0, 0.0)),
            _key(51): Node(_key(51), Vec3(10.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    duplicate = next(
        issue for issue in window.current_issues if issue.type is IssueType.DUPLICATE_NODE
    )
    orphan = next(
        issue
        for issue in window.current_issues
        if issue.type is IssueType.ORPHAN_NODE and _key(50) in issue.entity_keys
    )

    window.issue_console.select_issue(duplicate.id)
    orphan_row = next(
        row
        for row in range(window.issue_console.table.rowCount())
        if window.issue_console.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == orphan.id
    )
    window.issue_console.table.selectionModel().select(
        window.issue_console.table.model().index(orphan_row, 0),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )

    assert len(window.issue_console.selected_issues) == 2
    assert "overlap" in window.quick_fix_panel.selected_label.text().lower()
    assert not window.quick_fix_panel.apply_button.isEnabled()
    assert not window.repair_action.isEnabled()


def test_crossing_issue_offers_split_at_intersection_quick_fix(qtbot) -> None:
    viewport = RecordingViewport()
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, -2.0, 0.0)),
            _key(4): Node(_key(4), Vec3(0.0, 2.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(3), _key(4)),
        },
    )
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(model)
    crossing = next(
        issue
        for issue in window.current_issues
        if issue.type is IssueType.CROSSING_WITHOUT_NODE
    )

    window.issue_console.select_issue(crossing.id)

    assert window.quick_fix_panel.apply_button.isEnabled()
    assert "Split at Intersection" in window.quick_fix_panel.selected_label.text()


def test_merge_quick_fix_revalidates_and_undo_redo_round_trip(qtbot) -> None:
    viewport = RecordingViewport()
    window = MainWindow(viewport_factory=lambda: viewport, confirm_delete=lambda _message: True)
    qtbot.addWidget(window)
    window.set_canonical_model(_near_gap_model())

    gap = next(issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP)
    window.issue_console.select_issue(gap.id)
    window.apply_selected_quick_fix()

    assert len(window.current_model.nodes) == 3
    assert not [issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP]
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1

    window.undo_repair()
    assert len(window.current_model.nodes) == 4
    assert [issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP]

    window.redo_repair()
    assert len(window.current_model.nodes) == 3
    assert not [issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP]


def test_destructive_orphan_delete_requires_confirmation(qtbot) -> None:
    confirmations: list[str] = []

    def deny(message: str) -> bool:
        confirmations.append(message)
        return False

    window = MainWindow(viewport_factory=RecordingViewport, confirm_delete=deny)
    qtbot.addWidget(window)
    window.set_canonical_model(_orphan_model())
    orphan = next(issue for issue in window.current_issues if issue.type is IssueType.ORPHAN_NODE)
    window.issue_console.select_issue(orphan.id)

    window.apply_selected_quick_fix()

    assert confirmations
    assert _key(3) in window.current_model.nodes
    assert window.repair_history is not None
    assert window.repair_history.undo_stack == ()


def test_disconnected_structure_issue_can_isolate_its_entities(qtbot) -> None:
    viewport = RecordingViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.set_canonical_model(_two_structure_model())
    detached = next(
        issue for issue in window.current_issues if issue.type is IssueType.DISCONNECTED_STRUCTURE
    )

    window.issue_console.select_issue(detached.id)
    window.issue_console.request_isolate_selected()

    assert set(viewport.isolated) == set(detached.entity_keys)
