"""Interactive validation issue table for the desktop workflow."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from staadprep.validation.issues import Issue, IssueSeverity, IssueType


class IssueConsole(QFrame):
    issue_selected = Signal(str)
    issues_selected = Signal(object)
    isolate_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("issue_console")
        self._issues: tuple[Issue, ...] = ()
        self._by_id: dict[str, Issue] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(7)

        header = QHBoxLayout()
        title = QLabel("ISSUE CONSOLE")
        title.setObjectName("section_title")
        header.addWidget(title)
        header.addStretch(1)
        self.counts_label = QLabel("Errors 0  |  Warnings 0  |  Info 0")
        self.counts_label.setObjectName("muted_label")
        header.addWidget(self.counts_label)
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(("ALL", "ERROR", "WARNING", "INFO"))
        self.severity_filter.currentTextChanged.connect(self._rebuild_table)
        header.addWidget(self.severity_filter)
        self.isolate_button = QPushButton("Isolate Structure")
        self.isolate_button.setEnabled(False)
        self.isolate_button.clicked.connect(self.request_isolate_selected)
        header.addWidget(self.isolate_button)
        layout.addLayout(header)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(("Severity", "Type", "Description", "Action"))
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            2, self.table.horizontalHeader().ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table, 1)

    @property
    def selected_issues(self) -> tuple[Issue, ...]:
        issues: list[Issue] = []
        rows = sorted(index.row() for index in self.table.selectionModel().selectedRows())
        for row in rows:
            item = self.table.item(row, 0)
            if item is None:
                continue
            issue = self._by_id.get(str(item.data(Qt.ItemDataRole.UserRole)))
            if issue is not None:
                issues.append(issue)
        return tuple(issues)

    @property
    def selected_issue(self) -> Issue | None:
        selected = self.selected_issues
        return selected[0] if len(selected) == 1 else None

    def set_issues(self, issues: list[Issue] | tuple[Issue, ...]) -> None:
        signals_were_blocked = self.table.blockSignals(True)
        try:
            self.table.clearSelection()
            self.table.setCurrentCell(-1, -1)
            self._issues = tuple(issues)
            self._by_id = {issue.id: issue for issue in self._issues}
            counts = {severity: 0 for severity in IssueSeverity}
            for issue in self._issues:
                counts[issue.severity] += 1
            self.counts_label.setText(
                f"Errors {counts[IssueSeverity.ERROR]}  |  "
                f"Warnings {counts[IssueSeverity.WARNING]}  |  "
                f"Info {counts[IssueSeverity.INFO]}"
            )
            self._rebuild_table()
        finally:
            self.table.blockSignals(signals_were_blocked)
        self._update_isolate_button()

    def select_issue(self, issue_id: str) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == issue_id:
                signals_were_blocked = self.table.blockSignals(True)
                self.table.clearSelection()
                self.table.selectRow(row)
                self.table.setCurrentCell(row, 0)
                self.table.blockSignals(signals_were_blocked)
                if not signals_were_blocked:
                    self._on_selection_changed()
                return
        raise KeyError(f"Issue {issue_id} is not visible in the current filter")

    def request_isolate_selected(self) -> None:
        issue = self.selected_issue
        if issue is not None and issue.type is IssueType.DISCONNECTED_STRUCTURE:
            self.isolate_requested.emit(issue.id)

    def _rebuild_table(self, *_args: object) -> None:
        selected_ids = {issue.id for issue in self.selected_issues}
        filter_value = self.severity_filter.currentText()
        visible = [
            issue
            for issue in self._issues
            if filter_value == "ALL" or issue.severity.value == filter_value
        ]
        signals_were_blocked = self.table.blockSignals(True)
        try:
            self.table.clearSelection()
            self.table.setCurrentCell(-1, -1)
            self.table.setRowCount(len(visible))
            for row, issue in enumerate(visible):
                values = (
                    issue.severity.value,
                    issue.type.value,
                    issue.description,
                    issue.suggested_actions[0] if issue.suggested_actions else "Inspect",
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, issue.id)
                    self.table.setItem(row, column, item)
                if issue.id in selected_ids:
                    self.table.selectRow(row)
        finally:
            self.table.blockSignals(signals_were_blocked)
        self._update_isolate_button()
        if not signals_were_blocked:
            self._on_selection_changed()

    def _on_selection_changed(self) -> None:
        issues = self.selected_issues
        self._update_isolate_button()
        self.issues_selected.emit(issues)
        if len(issues) == 1:
            self.issue_selected.emit(issues[0].id)

    def _update_isolate_button(self) -> None:
        issue = self.selected_issue
        self.isolate_button.setEnabled(
            issue is not None and issue.type is IssueType.DISCONNECTED_STRUCTURE
        )
