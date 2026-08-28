"""Reusable panels for the approved desktop shell."""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class SectionPanel(QFrame):
    """Simple titled panel used throughout the shell."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("section_panel")
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(10, 8, 10, 10)
        self.body_layout.setSpacing(7)

        title_label = QLabel(title.upper())
        title_label.setObjectName("section_title")
        self.body_layout.addWidget(title_label)


class ViewportPlaceholder(QFrame):
    """Temporary structural-view placeholder until the real 3D viewer arrives in T04."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("viewport_host")
        self.setMinimumSize(480, 360)
        self.setToolTip("3D viewer integration is scheduled for Task 04")

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = self.rect().adjusted(18, 18, -18, -18)

        grid_pen = QPen(QColor("#202a34"), 1)
        painter.setPen(grid_pen)
        spacing = 42
        x = bounds.left()
        while x <= bounds.right():
            painter.drawLine(x, bounds.top(), x, bounds.bottom())
            x += spacing
        y = bounds.top()
        while y <= bounds.bottom():
            painter.drawLine(bounds.left(), y, bounds.right(), y)
            y += spacing

        frame_pen = QPen(QColor("#9aa9b8"), 2)
        painter.setPen(frame_pen)
        w = max(1, bounds.width())
        h = max(1, bounds.height())
        origin = QPointF(bounds.left() + w * 0.18, bounds.bottom() - h * 0.14)
        dx = w * 0.14
        dy = h * 0.14
        rise = h * 0.55

        base_points: list[QPointF] = []
        for bay in range(5):
            base = QPointF(origin.x() + bay * dx, origin.y() - bay * dy * 0.18)
            top = QPointF(base.x(), base.y() - rise)
            base_points.append(base)
            painter.drawLine(base, top)
            if bay:
                prev = base_points[bay - 1]
                prev_top = QPointF(prev.x(), prev.y() - rise)
                painter.drawLine(prev_top, top)
                painter.drawLine(prev, base)

        accent_pen = QPen(QColor("#4e89b8"), 2)
        painter.setPen(accent_pen)
        if len(base_points) >= 4:
            a = QPointF(base_points[1].x(), base_points[1].y() - rise)
            b = QPointF(base_points[3].x(), base_points[3].y() - rise)
            painter.drawLine(a, b)

        painter.setPen(QColor("#73808e"))
        painter.drawText(
            bounds.left() + 12,
            bounds.top() + 22,
            "3D VIEWPORT — available in Task 04",
        )
        painter.end()


class ProjectExplorerPanel(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Project Explorer", parent)
        self.setObjectName("project_explorer")
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAlternatingRowColors(True)
        model = QTreeWidgetItem(["Model"])
        self.node_item = QTreeWidgetItem(["Nodes (0)"])
        self.member_item = QTreeWidgetItem(["Members (0)"])
        self.support_item = QTreeWidgetItem(["Supports (0)"])
        model.addChildren([self.node_item, self.member_item, self.support_item])
        structures = QTreeWidgetItem(["Structures"])
        structures.addChild(QTreeWidgetItem(["No model loaded"]))
        self.tree.addTopLevelItems([QTreeWidgetItem(["Files"]), model, structures])
        self.tree.expandAll()
        self.body_layout.addWidget(self.tree, 1)

        summary_title = QLabel("MODEL SUMMARY")
        summary_title.setObjectName("section_title")
        self.body_layout.addWidget(summary_title)
        self.summary_label = QLabel(
            "Nodes      0\nMembers    0\nStructures 0\nUnit       —\nAxis       —"
        )
        self.summary_label.setObjectName("muted_label")
        self.body_layout.addWidget(self.summary_label)

    def set_raw_preview_summary(
        self,
        *,
        node_count: int,
        member_count: int,
        unit: str | None,
    ) -> None:
        self.node_item.setText(0, f"Nodes ({node_count})")
        self.member_item.setText(0, f"Members ({member_count})")
        unit_text = unit or "unknown"
        self.summary_label.setText(
            f"Nodes      {node_count}\n"
            f"Members    {member_count}\n"
            "Structures —\n"
            f"Unit       {unit_text}\n"
            "Axis       RAW / NOT TRANSFORMED"
        )


class PropertiesPanel(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Properties", parent)
        self.setObjectName("properties_panel")
        content = QLabel(
            "Selected entity\n\n"
            "Type       —\n"
            "ID         —\n"
            "Start Node —\n"
            "End Node   —\n"
            "Length     —\n"
            "Local Axis —"
        )
        content.setObjectName("muted_label")
        content.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.body_layout.addWidget(content, 1)


class ValidationPanel(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Validation", parent)
        self.setObjectName("validation_panel")
        rows = [
            "○ Units                 Not checked",
            "○ Reference Length      Not checked",
            "○ Orphan Nodes          Not checked",
            "○ Structures            Not checked",
            "○ Duplicate Members     Not checked",
            "○ Local X Direction     Not checked",
        ]
        for text in rows:
            label = QLabel(text)
            label.setObjectName("muted_label")
            self.body_layout.addWidget(label)


class QuickFixPanel(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Quick Fix", parent)
        self.setObjectName("quick_fix_panel")
        labels = (
            "Merge Nodes",
            "Split at Intersection",
            "Reverse Member",
            "Delete Orphan",
            "Auto Repair",
        )
        for label in labels:
            button = QPushButton(label)
            button.setEnabled(False)
            button.setToolTip("Repair functionality is added in later tasks")
            self.body_layout.addWidget(button)


class IssueConsole(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Issue Console", parent)
        self.setObjectName("issue_console")
        table = QTableWidget(1, 4)
        table.setHorizontalHeaderLabels(["Type", "ID", "Description", "Action"])
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        values = ["INFO", "—", "Import a model to begin validation", "—"]
        for column, value in enumerate(values):
            table.setItem(0, column, QTableWidgetItem(value))
        self.body_layout.addWidget(table)


class ModelStatusBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        summary = QLabel(
            "Unit: —   |   Axis: —   |   Nodes: 0   |   Members: 0   |   Structures: 0"
        )
        summary.setObjectName("muted_label")
        layout.addWidget(summary, 1)
        self.status_label = QLabel("MODEL STATUS: NO MODEL")
        self.status_label.setObjectName("model_status")
        layout.addWidget(self.status_label)
