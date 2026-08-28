"""Main desktop window matching the approved V1 layout baseline."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from staadprep.importers.contracts import ImportBatch
from staadprep.importers.dxf_reader import DxfReader
from staadprep.importers.raw_preview import raw_batch_to_preview_model
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import DeleteMember, DeleteNode, MergeNodes, RepairCommand
from staadprep.repair.history import RepairHistory
from staadprep.topology.connectivity import connected_components
from staadprep.ui.issue_console import IssueConsole
from staadprep.ui.panels import (
    ModelStatusBar,
    ProjectExplorerPanel,
    PropertiesPanel,
    QuickFixPanel,
    ValidationPanel,
)
from staadprep.validation.issues import Issue, IssueType
from staadprep.validation.validators import validate_model
from staadprep.viewer.widget import StructuralViewport

ConfirmDelete = Callable[[str], bool]


class MainWindow(QMainWindow):
    """Approved V1 engineering shell with issue inspection and repair orchestration."""

    def __init__(
        self,
        viewport_factory: Callable[[], QWidget] | None = None,
        *,
        confirm_delete: ConfirmDelete | None = None,
    ) -> None:
        super().__init__()
        self._viewport_factory = viewport_factory or StructuralViewport
        self._confirm_delete = confirm_delete or self._confirm_delete_dialog
        self.current_import_batch: ImportBatch | None = None
        self.current_model: ProjectModel | None = None
        self.current_issues: list[Issue] = []
        self.repair_history: RepairHistory | None = None
        self._selected_issue_id: str | None = None

        self.setWindowTitle("STAAD Model Preprocessor")
        self.resize(1480, 900)
        self.setMinimumSize(1080, 700)

        self._create_actions()
        self._create_toolbar()
        self._create_workspace()
        self.statusBar().showMessage("Ready — no model loaded")

    def _create_actions(self) -> None:
        self.import_action = QAction("Import Model", self)
        self.import_action.setToolTip("Import raw DXF geometry (SKP support arrives later)")
        self.import_action.triggered.connect(self._choose_dxf)

        self.unit_check_action = self._disabled_action("Unit Check", "UI wiring pending")
        self.repair_action = QAction("Repair", self)
        self.repair_action.setEnabled(False)
        self.repair_action.setToolTip("Apply the selected issue's predefined repair")
        self.repair_action.triggered.connect(self.apply_selected_quick_fix)
        self.normalize_axis_action = self._disabled_action(
            "Normalize Axis", "Available in Task 11"
        )
        self.renumber_action = self._disabled_action("Renumber", "Available in Task 12")
        self.validate_action = QAction("Validate", self)
        self.validate_action.setEnabled(False)
        self.validate_action.triggered.connect(self.refresh_validation)
        self.export_std_action = self._disabled_action("Export STD", "Available in Task 13")

        self.undo_action = QAction("Undo Repair", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self.undo_repair)
        self.addAction(self.undo_action)

        self.redo_action = QAction("Redo Repair", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self.redo_repair)
        self.addAction(self.redo_action)

    def _disabled_action(self, text: str, reason: str) -> QAction:
        action = QAction(text, self)
        action.setEnabled(False)
        action.setToolTip(reason)
        return action

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Model Tools", self)
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        for action in (
            self.import_action,
            self.unit_check_action,
            self.repair_action,
            self.normalize_axis_action,
            self.renumber_action,
            self.validate_action,
            self.export_std_action,
        ):
            toolbar.addAction(action)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

    def _create_workspace(self) -> None:
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 6)
        root_layout.setSpacing(8)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        self.project_explorer = ProjectExplorerPanel()
        self.project_explorer.setMinimumWidth(210)
        self.project_explorer.setMaximumWidth(330)
        main_splitter.addWidget(self.project_explorer)

        self.viewport_host = self._viewport_factory()
        main_splitter.addWidget(self.viewport_host)

        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        self.properties_panel = PropertiesPanel()
        self.validation_panel = ValidationPanel()
        self.quick_fix_panel = QuickFixPanel()
        self.quick_fix_panel.apply_button.clicked.connect(self.apply_selected_quick_fix)
        self.quick_fix_panel.undo_button.clicked.connect(self.undo_repair)
        self.quick_fix_panel.redo_button.clicked.connect(self.redo_repair)
        right_layout.addWidget(self.properties_panel, 3)
        right_layout.addWidget(self.validation_panel, 3)
        right_layout.addWidget(self.quick_fix_panel, 2)
        right_column.setMinimumWidth(250)
        right_column.setMaximumWidth(360)
        main_splitter.addWidget(right_column)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setStretchFactor(2, 0)
        main_splitter.setSizes([250, 900, 290])
        root_layout.addWidget(main_splitter, 1)

        self.issue_console = IssueConsole()
        self.issue_console.issue_selected.connect(self._on_issue_selected)
        self.issue_console.isolate_requested.connect(self._on_isolate_requested)
        self.issue_console.setMinimumHeight(150)
        self.issue_console.setMaximumHeight(240)
        root_layout.addWidget(self.issue_console)

        self.model_status_bar = ModelStatusBar()
        self.model_status = self.model_status_bar.status_label
        root_layout.addWidget(self.model_status_bar)
        self.setCentralWidget(central)

    def _choose_dxf(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import DXF",
            "",
            "DXF Files (*.dxf)",
        )
        if file_name:
            self.load_raw_dxf(Path(file_name))

    def load_raw_dxf(self, path: Path) -> ImportBatch:
        """Read and preview raw DXF geometry without cleanup or transformation."""
        batch = DxfReader().read(path)
        preview_model = raw_batch_to_preview_model(batch)
        self._set_viewport_model(preview_model)
        self.project_explorer.set_raw_preview_summary(
            node_count=len(preview_model.nodes),
            member_count=len(preview_model.members),
            unit=batch.declared_unit,
        )

        self.current_import_batch = batch
        self.current_model = None
        self.current_issues = []
        self.repair_history = None
        self._selected_issue_id = None
        self.issue_console.set_issues([])
        self.properties_panel.set_issue(None)
        self.quick_fix_panel.set_issue(None)
        self._update_history_actions()
        self.validate_action.setEnabled(False)
        self.repair_action.setEnabled(False)
        self.model_status.setText("RAW DXF PREVIEW — NOT VALIDATED")
        unit = batch.declared_unit or "unknown"
        self.statusBar().showMessage(
            "RAW DXF PREVIEW — NOT VALIDATED | "
            f"Segments: {len(batch.segments)} | Points: {len(batch.points)} | Unit: {unit}"
        )
        return batch

    def set_canonical_model(self, model: ProjectModel) -> None:
        """Attach a metre/Y-Up canonical model to validation and repair UI."""
        self.current_model = model
        self.current_import_batch = None
        self.repair_history = RepairHistory(model)
        self.validate_action.setEnabled(True)
        self._selected_issue_id = None
        self.refresh_validation()

    def refresh_validation(self) -> None:
        if self.current_model is None:
            return
        self.current_issues = validate_model(self.current_model)
        self._selected_issue_id = None
        self.issue_console.set_issues(self.current_issues)
        self.validation_panel.set_issues(self.current_issues)
        self.properties_panel.set_issue(None)
        self.quick_fix_panel.set_issue(None)
        self.repair_action.setEnabled(False)
        self._set_viewport_model(self.current_model)

        structures = connected_components(self.current_model)
        self.project_explorer.set_canonical_summary(
            node_count=len(self.current_model.nodes),
            member_count=len(self.current_model.members),
            structure_count=len(structures),
        )
        self.model_status_bar.set_canonical_summary(
            nodes=len(self.current_model.nodes),
            members=len(self.current_model.members),
            structures=len(structures),
        )
        if self.current_issues:
            self.model_status.setText(f"MODEL STATUS: {len(self.current_issues)} ISSUE(S)")
        else:
            self.model_status.setText("MODEL STATUS: CLEAN")
        self.statusBar().showMessage(
            f"Validation complete | Issues: {len(self.current_issues)} | "
            f"Revision: {self.current_model.revision}"
        )
        self._update_history_actions()

    def _on_issue_selected(self, issue_id: str) -> None:
        issue = self._issue_by_id(issue_id)
        if issue is None or self.current_model is None:
            return
        self._selected_issue_id = issue.id
        node_keys, member_keys = self._partition_entity_keys(issue.entity_keys)
        self._call_viewport("highlight_nodes", node_keys)
        self._call_viewport("highlight_members", member_keys)
        self._call_viewport("focus_entities", node_keys, member_keys, issue.location)
        self.properties_panel.set_issue(issue)
        self.quick_fix_panel.set_issue(issue)
        self.repair_action.setEnabled(issue.type in QuickFixPanel.SUPPORTED_TYPES)

    def _on_isolate_requested(self, issue_id: str) -> None:
        issue = self._issue_by_id(issue_id)
        if issue is None:
            return
        self._call_viewport("isolate_entities", issue.entity_keys)
        self.statusBar().showMessage("Detached structure isolated in viewport")

    def apply_selected_quick_fix(self) -> None:
        if self.current_model is None or self.repair_history is None:
            return
        issue = self._issue_by_id(self._selected_issue_id)
        if issue is None:
            return
        command = self._command_for_issue(issue)
        if command is None:
            self.statusBar().showMessage("No safe predefined quick fix for this issue")
            return
        if isinstance(command, (DeleteNode, DeleteMember)):
            if not self._confirm_delete(f"Apply destructive repair for {issue.type.value}?"):
                self.statusBar().showMessage("Repair cancelled")
                return
        self.repair_history.execute(command)
        self.refresh_validation()

    def undo_repair(self) -> None:
        if self.repair_history is None or not self.repair_history.undo_stack:
            return
        self.repair_history.undo()
        self.refresh_validation()

    def redo_repair(self) -> None:
        if self.repair_history is None or not self.repair_history.redo_stack:
            return
        self.repair_history.redo()
        self.refresh_validation()

    def _command_for_issue(self, issue: Issue) -> RepairCommand | None:
        if self.current_model is None:
            return None
        node_keys, member_keys = self._partition_entity_keys(issue.entity_keys)
        if issue.type in {
            IssueType.DUPLICATE_NODE,
            IssueType.NEAR_NODE,
            IssueType.UNCONNECTED_GAP,
        } and len(node_keys) >= 2:
            return MergeNodes(node_keys[0], node_keys[1])
        if issue.type is IssueType.ORPHAN_NODE and node_keys:
            return DeleteNode(node_keys[0])
        if issue.type in {IssueType.ZERO_LENGTH_MEMBER, IssueType.SHORT_MEMBER} and member_keys:
            return DeleteMember(member_keys[0])
        if issue.type is IssueType.DUPLICATE_MEMBER and len(member_keys) >= 2:
            return DeleteMember(member_keys[-1])
        return None

    def _partition_entity_keys(
        self,
        keys: tuple[UUID, ...],
    ) -> tuple[tuple[UUID, ...], tuple[UUID, ...]]:
        if self.current_model is None:
            return (), ()
        node_keys = tuple(key for key in keys if key in self.current_model.nodes)
        member_keys = tuple(key for key in keys if key in self.current_model.members)
        return node_keys, member_keys

    def _issue_by_id(self, issue_id: str | None) -> Issue | None:
        if issue_id is None:
            return None
        return next((issue for issue in self.current_issues if issue.id == issue_id), None)

    def _set_viewport_model(self, model: ProjectModel) -> None:
        set_model = getattr(self.viewport_host, "set_model", None)
        if set_model is None:
            raise TypeError("Configured viewport does not support set_model()")
        set_model(model)

    def _call_viewport(self, method_name: str, *args: object) -> None:
        method = getattr(self.viewport_host, method_name, None)
        if method is not None:
            method(*args)

    def _update_history_actions(self) -> None:
        can_undo = bool(self.repair_history and self.repair_history.undo_stack)
        can_redo = bool(self.repair_history and self.repair_history.redo_stack)
        self.undo_action.setEnabled(can_undo)
        self.redo_action.setEnabled(can_redo)
        self.quick_fix_panel.set_history_state(can_undo=can_undo, can_redo=can_redo)

    def _confirm_delete_dialog(self, message: str) -> bool:
        result = QMessageBox.question(
            self,
            "Confirm Repair",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result is QMessageBox.StandardButton.Yes
