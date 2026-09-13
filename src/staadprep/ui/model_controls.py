"""Focused preview UI for STAAD numbering and member-direction controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from staadprep.model.project import ProjectModel
from staadprep.numbering.renumber import NumberingMap


class NumberingPreviewCommand(Protocol):
    def preview(self, model: ProjectModel) -> NumberingMap: ...


@dataclass(frozen=True, slots=True)
class NumberingPreviewRow:
    entity_type: str
    key: UUID
    old_number: int | None
    new_number: int


def numbering_preview_rows(
    model: ProjectModel,
    preview: NumberingMap,
) -> tuple[NumberingPreviewRow, ...]:
    rows: list[NumberingPreviewRow] = []
    for key, number in sorted(preview.node_numbers.items(), key=lambda item: item[0].int):
        node = model.nodes[key]
        rows.append(NumberingPreviewRow("Node", key, node.number, number))
    for key, number in sorted(preview.member_numbers.items(), key=lambda item: item[0].int):
        member = model.members[key]
        rows.append(NumberingPreviewRow("Member", key, member.number, number))
    return tuple(rows)


class NumberingPreviewDialog(QDialog):
    """Read-only Old -> New numbering preview; mutation happens outside this dialog."""

    def __init__(
        self,
        model: ProjectModel,
        command: NumberingPreviewCommand,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("STAAD Numbering Preview")
        self.resize(720, 420)
        self.preview = command.preview(model)
        self.rows = numbering_preview_rows(model, self.preview)

        root = QVBoxLayout(self)
        root.addWidget(
            QLabel("Preview only — Apply changes STAAD-facing numbers, not UUID geometry.")
        )

        self.table = QTableWidget(len(self.rows), 4, self)
        self.table.setHorizontalHeaderLabels(("Entity", "UUID", "Old", "New"))
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        for row_index, row in enumerate(self.rows):
            old = "—" if row.old_number is None else str(row.old_number)
            values = (row.entity_type, str(row.key), old, str(row.new_number))
            for column, value in enumerate(values):
                self.table.setItem(row_index, column, QTableWidgetItem(value))
        root.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.apply_button = QPushButton("Apply", self)
        self.cancel_button = QPushButton("Cancel", self)
        buttons.addWidget(self.apply_button)
        buttons.addWidget(self.cancel_button)
        root.addLayout(buttons)
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
