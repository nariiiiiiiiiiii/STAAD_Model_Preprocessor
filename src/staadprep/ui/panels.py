"""Reusable panels for the approved desktop shell."""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from staadprep.validation.issues import Issue, IssueSeverity, IssueType


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
    """Lightweight viewport stand-in used by non-VTK UI tests."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("viewport_host")
        self.setMinimumSize(480, 360)
        self.setToolTip("Lightweight viewport placeholder")

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = self.rect().adjusted(18, 18, -18, -18)

        painter.setPen(QPen(QColor("#202a34"), 1))
        spacing = 42
        x = bounds.left()
        while x <= bounds.right():
            painter.drawLine(x, bounds.top(), x, bounds.bottom())
            x += spacing
        y = bounds.top()
        while y <= bounds.bottom():
            painter.drawLine(bounds.left(), y, bounds.right(), y)
            y += spacing

        painter.setPen(QPen(QColor("#9aa9b8"), 2))
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

        painter.setPen(QPen(QColor("#4e89b8"), 2))
        if len(base_points) >= 4:
            a = QPointF(base_points[1].x(), base_points[1].y() - rise)
            b = QPointF(base_points[3].x(), base_points[3].y() - rise)
            painter.drawLine(a, b)

        painter.setPen(QColor("#73808e"))
        painter.drawText(bounds.left() + 12, bounds.top() + 22, "3D VIEWPORT")
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
        self.structures_item = QTreeWidgetItem(["Structures"])
        self.structures_item.addChild(QTreeWidgetItem(["No model loaded"]))
        self.tree.addTopLevelItems([QTreeWidgetItem(["Files"]), model, self.structures_item])
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

    def set_canonical_summary(
        self,
        *,
        node_count: int,
        member_count: int,
        structure_count: int,
    ) -> None:
        self.node_item.setText(0, f"Nodes ({node_count})")
        self.member_item.setText(0, f"Members ({member_count})")
        self.structures_item.takeChildren()
        for index in range(structure_count):
            self.structures_item.addChild(QTreeWidgetItem([f"Structure {index + 1}"]))
        self.summary_label.setText(
            f"Nodes      {node_count}\n"
            f"Members    {member_count}\n"
            f"Structures {structure_count}\n"
            "Unit       m\n"
            "Axis       Y-UP"
        )


class PropertiesPanel(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Properties", parent)
        self.setObjectName("properties_panel")
        self.content = QLabel("Selected entity\n\nType —\nID —\nLocation —")
        self.content.setObjectName("muted_label")
        self.content.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.body_layout.addWidget(self.content, 1)

    def set_issue(self, issue: Issue | None) -> None:
        if issue is None:
            self.content.setText("Selected entity\n\nType —\nID —\nLocation —")
            return
        location = issue.location.as_tuple() if issue.location is not None else "—"
        self.content.setText(
            f"Selected issue\n\nType {issue.type.value}\n"
            f"ID {issue.id}\nLocation {location}\n"
            f"Entities {len(issue.entity_keys)}"
        )


class ValidationPanel(SectionPanel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Validation", parent)
        self.setObjectName("validation_panel")
        self.summary_label = QLabel("No canonical model validated")
        self.summary_label.setObjectName("muted_label")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.body_layout.addWidget(self.summary_label, 1)

    def set_issues(self, issues: list[Issue]) -> None:
        errors = sum(issue.severity is IssueSeverity.ERROR for issue in issues)
        warnings = sum(issue.severity is IssueSeverity.WARNING for issue in issues)
        infos = sum(issue.severity is IssueSeverity.INFO for issue in issues)
        self.summary_label.setText(
            f"Errors      {errors}\n"
            f"Warnings    {warnings}\n"
            f"Info        {infos}\n"
            f"Total       {len(issues)}"
        )


class QuickFixPanel(SectionPanel):
    SUPPORTED_TYPES = {
        IssueType.DUPLICATE_NODE,
        IssueType.NEAR_NODE,
        IssueType.UNCONNECTED_GAP,
        IssueType.ORPHAN_NODE,
        IssueType.ZERO_LENGTH_MEMBER,
        IssueType.SHORT_MEMBER,
        IssueType.DUPLICATE_MEMBER,
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Quick Fix", parent)
        self.setObjectName("quick_fix_panel")
        self.selected_label = QLabel("Select an issue to inspect available actions")
        self.selected_label.setObjectName("muted_label")
        self.body_layout.addWidget(self.selected_label)

        self.apply_button = QPushButton("Apply Selected Fix")
        self.apply_button.setEnabled(False)
        self.body_layout.addWidget(self.apply_button)

        history_row = QHBoxLayout()
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")
        self.undo_button.setEnabled(False)
        self.redo_button.setEnabled(False)
        history_row.addWidget(self.undo_button)
        history_row.addWidget(self.redo_button)
        self.body_layout.addLayout(history_row)

    def set_issue(self, issue: Issue | None) -> None:
        if issue is None:
            self.selected_label.setText("Select an issue to inspect available actions")
            self.apply_button.setEnabled(False)
            return
        action_text = issue.suggested_actions[-1] if issue.suggested_actions else "Inspect"
        self.selected_label.setText(action_text)
        self.apply_button.setEnabled(issue.type in self.SUPPORTED_TYPES)

    def set_history_state(self, *, can_undo: bool, can_redo: bool) -> None:
        self.undo_button.setEnabled(can_undo)
        self.redo_button.setEnabled(can_redo)


class ModelStatusBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.summary_label = QLabel(
            "Unit: —   |   Axis: —   |   Nodes: 0   |   Members: 0   |   Structures: 0"
        )
        self.summary_label.setObjectName("muted_label")
        layout.addWidget(self.summary_label, 1)
        self.status_label = QLabel("MODEL STATUS: NO MODEL")
        self.status_label.setObjectName("model_status")
        layout.addWidget(self.status_label)

    def set_canonical_summary(
        self,
        *,
        nodes: int,
        members: int,
        structures: int,
    ) -> None:
        self.summary_label.setText(
            f"Unit: m   |   Axis: Y-UP   |   Nodes: {nodes}   |   "
            f"Members: {members}   |   Structures: {structures}"
        )
