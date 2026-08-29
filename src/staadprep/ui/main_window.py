"""Main desktop window matching the approved V1 layout baseline."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from staadprep.editing.create_node import (
    ExactNodeSpec,
    ExistingNodeCollision,
    ExistingNodeResolution,
    RelativeNodeSpec,
    RepeatResolutionRequired,
    TranslationalRepeatSpec,
    build_exact_create,
    build_relative_create,
    build_translational_repeat,
)
from staadprep.editing.manual_ops import (
    build_split_member_distance,
    build_split_member_midpoint,
    build_split_member_percentage,
    build_split_selected_intersection,
)
from staadprep.exporters.staad_std import ExportReport, StaadExportError, export_staad_std
from staadprep.importers.contracts import ImportBatch
from staadprep.importers.dxf_reader import DxfReader
from staadprep.importers.neutral_reader import NeutralReader, NeutralReaderError
from staadprep.importers.pipeline import ImportPipelineError, canonicalize_import_batch
from staadprep.importers.raw_preview import raw_batch_to_preview_model
from staadprep.model.project import ProjectModel
from staadprep.numbering.commands import (
    RenumberAllCommand,
    RenumberMembersCommand,
    RenumberNodesCommand,
)
from staadprep.numbering.renumber import NumberingPolicy
from staadprep.orientation.commands import (
    SetMemberStart,
    build_auto_fix_all,
    build_auto_fix_selected,
    build_flip_selected,
)
from staadprep.orientation.normalize import normalization_commands
from staadprep.paths import ProjectPaths
from staadprep.repair.audit import write_validation_report
from staadprep.repair.commands import (
    ConnectNodes,
    DeleteMember,
    DeleteNode,
    MergeNodes,
    RepairCommand,
)
from staadprep.repair.history import RepairHistory
from staadprep.topology.connectivity import connected_components
from staadprep.ui.create_node_dialog import (
    CreateNodeDialog,
    PrecisionNodePreviewRequest,
    RepeatPreviewRequest,
    TranslationalRepeatDialog,
)
from staadprep.ui.issue_console import IssueConsole
from staadprep.ui.model_controls import NumberingPreviewDialog
from staadprep.ui.panels import (
    ModelStatusBar,
    ProjectExplorerPanel,
    PropertiesPanel,
    QuickFixPanel,
    ValidationPanel,
)
from staadprep.validation.issues import Issue, IssueType
from staadprep.validation.ready_gate import ReadyGate, ReadyStatus
from staadprep.validation.validators import validate_model
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter
from staadprep.viewer.widget import StructuralViewport

ConfirmDelete = Callable[[str], bool]
ConfirmUseExisting = Callable[[str], bool]
RunNumberingPreview = Callable[[NumberingPreviewDialog], bool]


class MainWindow(QMainWindow):
    """Approved V1 engineering shell with issue inspection and repair orchestration."""

    def __init__(
        self,
        viewport_factory: Callable[[], QWidget] | None = None,
        *,
        confirm_delete: ConfirmDelete | None = None,
        confirm_use_existing: ConfirmUseExisting | None = None,
        numbering_preview_runner: RunNumberingPreview | None = None,
        ready_gate: ReadyGate | None = None,
        project_root: Path | None = None,
    ) -> None:
        super().__init__()
        configured_root = project_root or Path(os.environ.get("STAADPREP_PROJECT_ROOT", Path.cwd()))
        self._project_paths = ProjectPaths.from_root(configured_root)
        self._project_paths.ensure_layout()
        self.neutral_reader = NeutralReader(self._project_paths.root)
        self.neutral_reader.inbox.mkdir(parents=True, exist_ok=True)
        self._viewport_factory = viewport_factory or StructuralViewport
        self._confirm_delete = confirm_delete or self._confirm_delete_dialog
        self._confirm_use_existing = confirm_use_existing or self._confirm_use_existing_dialog
        self._run_numbering_preview = (
            numbering_preview_runner or self._default_numbering_preview_runner
        )
        self.ready_gate = ready_gate or ReadyGate()
        self.current_ready_status: ReadyStatus | None = None
        self._direction_member_key: UUID | None = None
        self.current_import_batch: ImportBatch | None = None
        self.current_model: ProjectModel | None = None
        self.current_issues: list[Issue] = []
        self.repair_history: RepairHistory | None = None
        self._selected_issue_id: str | None = None
        self.orientation_reverse_count = 0

        self.setWindowTitle("STAAD Model Preprocessor")
        self.resize(1480, 900)
        self.setMinimumSize(1080, 700)

        self._create_actions()
        self._create_toolbar()
        self._create_workspace()
        self.statusBar().showMessage(
            "Ready — no model loaded | SketchUp Bridge + Direct DXF available"
        )

    def _create_actions(self) -> None:
        self.import_action = QAction("Import Model", self)
        self.import_menu = QMenu(self)
        self.import_sketchup_action = QAction("Import SketchUp Bridge JSON", self)
        self.import_sketchup_action.setToolTip(
            f"Import Neutral JSON v1 from {self.neutral_reader.inbox}"
        )
        self.import_sketchup_action.triggered.connect(self._choose_sketchup_neutral)
        self.import_dxf_action = QAction("Import DXF", self)
        self.import_dxf_action.setToolTip(
            "Import DXF directly through the shared canonical pipeline"
        )
        self.import_dxf_action.triggered.connect(self._choose_dxf)
        self.import_menu.addAction(self.import_sketchup_action)
        self.import_menu.addAction(self.import_dxf_action)
        self.import_action.setMenu(self.import_menu)
        self.import_action.setToolTip("Import from SketchUp Bridge inbox or import DXF directly")

        self.unit_check_action = self._disabled_action("Unit Check", "UI wiring pending")
        self.repair_action = QAction("Repair", self)
        self.repair_action.setEnabled(False)
        self.repair_action.setToolTip("Apply the selected issue's predefined repair")
        self.repair_action.triggered.connect(self.apply_selected_quick_fix)
        self.auto_fix_axis_action = QAction("Auto Fix Axis", self)
        self.auto_fix_axis_action.setEnabled(False)
        self.auto_fix_axis_action.setToolTip("Load a canonical model to preview member local-X")
        self.auto_fix_axis_action.triggered.connect(self._auto_fix_all_directions)
        # Compatibility alias retained for T11/T16 tests and existing callers.
        self.normalize_axis_action = self.auto_fix_axis_action

        self.renumber_action = QAction("Numbering", self)
        self.renumber_action.setEnabled(False)
        self.numbering_menu = QMenu(self)
        self.auto_node_number_action = QAction("Auto Node Number", self)
        self.auto_member_number_action = QAction("Auto Member Number", self)
        self.auto_number_all_action = QAction("Auto Number All", self)
        for action in (
            self.auto_node_number_action,
            self.auto_member_number_action,
            self.auto_number_all_action,
        ):
            action.setEnabled(False)
            self.numbering_menu.addAction(action)
        self.renumber_action.setMenu(self.numbering_menu)
        self.auto_node_number_action.triggered.connect(self._auto_number_nodes)
        self.auto_member_number_action.triggered.connect(self._auto_number_members)
        self.auto_number_all_action.triggered.connect(self._auto_number_all)
        self.validate_action = QAction("Validate", self)
        self.validate_action.setEnabled(False)
        self.validate_action.triggered.connect(self.refresh_validation)
        self.export_std_action = QAction("Export STD", self)
        self.export_std_action.setEnabled(False)
        self.export_std_action.setToolTip(
            "Requires validated canonical model with complete STAAD numbering"
        )
        self.export_std_action.triggered.connect(self._choose_export_std)

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

        self.select_mode_action = QAction("Select", self)
        self.select_mode_action.setCheckable(True)
        self.select_mode_action.setChecked(True)
        self.select_mode_action.setToolTip("Safe selection mode; dragging does not edit geometry")
        self.select_mode_action.triggered.connect(self._activate_select_mode)

        self.create_node_mode_action = QAction("Create Node", self)
        self.create_node_mode_action.setCheckable(True)
        self.create_node_mode_action.setToolTip(
            "Create analytical Node by resolved click/snap inference"
        )
        self.create_node_mode_action.triggered.connect(
            lambda: self._activate_edit_mode(EditMode.CREATE_NODE)
        )

        self.create_node_dialog_action = QAction("Create Node…", self)
        self.create_node_dialog_action.setEnabled(False)
        self.create_node_dialog_action.setToolTip(
            "Create Node by exact STAAD XYZ or relative to a selected Node"
        )
        self.create_node_dialog_action.triggered.connect(self._open_create_node_dialog)

        self.translational_repeat_action = QAction("Translational Repeat…", self)
        self.translational_repeat_action.setEnabled(False)
        self.translational_repeat_action.setToolTip(
            "Repeat Node/member creation by canonical ΔX / ΔY / ΔZ"
        )
        self.translational_repeat_action.triggered.connect(self._open_translational_repeat_dialog)

        self.draw_member_action = QAction("Draw Member", self)
        self.draw_member_action.setCheckable(True)
        self.draw_member_action.setToolTip("Draw analytical member using Node/snap inference")
        self.draw_member_action.triggered.connect(
            lambda: self._activate_edit_mode(EditMode.DRAW_MEMBER)
        )

        self.move_snap_action = QAction("Move/Snap", self)
        self.move_snap_action.setCheckable(True)
        self.move_snap_action.setToolTip("Move or snap one analytical Node")
        self.move_snap_action.triggered.connect(
            lambda: self._activate_edit_mode(EditMode.MOVE_SNAP_NODE)
        )

        self.delete_mode_action = QAction("Delete", self)
        self.delete_mode_action.setCheckable(True)
        self.delete_mode_action.setToolTip("Delete the exact selected analytical entity")
        self.delete_mode_action.triggered.connect(lambda: self._activate_edit_mode(EditMode.DELETE))

        self.split_action = QAction("Split", self)
        self.split_action.setEnabled(False)
        self.split_action.setToolTip("Split selected analytical Member")
        self.split_menu = QMenu(self)
        self.split_midpoint_action = QAction("At Midpoint", self)
        self.split_percentage_action = QAction("At Percentage…", self)
        self.split_distance_action = QAction("At Distance from Start…", self)
        self.split_intersection_action = QAction("At Intersection", self)
        self.split_midpoint_action.triggered.connect(self._split_selected_midpoint)
        self.split_percentage_action.triggered.connect(self._split_selected_percentage)
        self.split_distance_action.triggered.connect(self._split_selected_distance)
        self.split_intersection_action.triggered.connect(self._split_selected_intersection)
        for split_action in (
            self.split_midpoint_action,
            self.split_percentage_action,
            self.split_distance_action,
            self.split_intersection_action,
        ):
            self.split_menu.addAction(split_action)
        self.split_action.setMenu(self.split_menu)

        self.auto_fix_selected_action = QAction("Auto Fix Selected", self)
        self.auto_fix_selected_action.setEnabled(False)
        self.auto_fix_selected_action.triggered.connect(self._auto_fix_selected_directions)
        self.flip_selected_action = QAction("Flip Selected", self)
        self.flip_selected_action.setEnabled(False)
        self.flip_selected_action.triggered.connect(self._flip_selected_directions)
        self.set_direction_action = QAction("Set Direction", self)
        self.set_direction_action.setCheckable(True)
        self.set_direction_action.setEnabled(False)
        self.set_direction_action.triggered.connect(self._start_set_direction)

        self.edit_mode_group = QActionGroup(self)
        self.edit_mode_group.setExclusive(True)
        for action in (
            self.select_mode_action,
            self.create_node_mode_action,
            self.draw_member_action,
            self.move_snap_action,
            self.delete_mode_action,
            self.set_direction_action,
        ):
            self.edit_mode_group.addAction(action)

        self.select_nodes_action = QAction("Nodes", self)
        self.select_nodes_action.setCheckable(True)
        self.select_nodes_action.setChecked(True)
        self.select_nodes_action.toggled.connect(self._sync_selection_filter)

        self.select_members_action = QAction("Members", self)
        self.select_members_action.setCheckable(True)
        self.select_members_action.setChecked(True)
        self.select_members_action.toggled.connect(self._sync_selection_filter)

        self.node_numbers_action = QAction("Node No.", self)
        self.node_numbers_action.setCheckable(True)
        self.node_numbers_action.toggled.connect(self._sync_label_visibility)

        self.member_numbers_action = QAction("Member No.", self)
        self.member_numbers_action.setCheckable(True)
        self.member_numbers_action.toggled.connect(self._sync_label_visibility)

        self.local_x_view_action = QAction("Local-X", self)
        self.local_x_view_action.setCheckable(True)
        self.local_x_view_action.toggled.connect(self._sync_label_visibility)

        self.coordinates_action = QAction("Coordinates", self)
        self.coordinates_action.setCheckable(True)
        self.coordinates_action.toggled.connect(self._sync_label_visibility)

        self.fit_model_action = QAction("Fit", self)
        self.fit_model_action.setShortcut(QKeySequence("Shift+Z"))
        self.fit_model_action.setToolTip("Fit the whole model in the viewport (Shift+Z)")
        self.fit_model_action.triggered.connect(lambda: self._call_viewport("fit_model"))
        self.addAction(self.fit_model_action)

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
            self.create_node_dialog_action,
            self.translational_repeat_action,
            self.validate_action,
            self.export_std_action,
        ):
            toolbar.addAction(action)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        view_toolbar = QToolBar("View & Selection", self)
        view_toolbar.setObjectName("view_selection_toolbar")
        view_toolbar.setMovable(False)
        view_toolbar.setFloatable(False)
        view_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        for action in (
            self.select_mode_action,
            self.create_node_mode_action,
            self.draw_member_action,
            self.move_snap_action,
            self.delete_mode_action,
            self.split_action,
            self.auto_fix_selected_action,
            self.flip_selected_action,
            self.set_direction_action,
        ):
            view_toolbar.addAction(action)
        view_toolbar.addSeparator()
        for action in (
            self.select_nodes_action,
            self.select_members_action,
        ):
            view_toolbar.addAction(action)
        view_toolbar.addSeparator()
        for action in (
            self.node_numbers_action,
            self.member_numbers_action,
            self.local_x_view_action,
            self.coordinates_action,
        ):
            view_toolbar.addAction(action)
        view_toolbar.addSeparator()
        view_toolbar.addAction(self.fit_model_action)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, view_toolbar)

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
        manual_signal = getattr(self.viewport_host, "manual_command_requested", None)
        if manual_signal is not None:
            manual_signal.connect(self._execute_manual_command)
        direction_signal = getattr(self.viewport_host, "direction_endpoint_selected", None)
        if direction_signal is not None:
            direction_signal.connect(self._apply_direction_endpoint)
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
        self._activate_select_mode()
        self._sync_selection_filter()
        self._sync_label_visibility()

    def _activate_select_mode(self) -> None:
        self.select_mode_action.setChecked(True)
        self._activate_edit_mode(EditMode.SELECT)

    def _activate_edit_mode(self, mode: EditMode) -> None:
        action_by_mode = {
            EditMode.SELECT: self.select_mode_action,
            EditMode.CREATE_NODE: self.create_node_mode_action,
            EditMode.DRAW_MEMBER: self.draw_member_action,
            EditMode.MOVE_SNAP_NODE: self.move_snap_action,
            EditMode.DELETE: self.delete_mode_action,
            EditMode.SET_DIRECTION: self.set_direction_action,
        }
        action = action_by_mode.get(mode)
        if action is not None:
            action.setChecked(True)
        self._call_viewport("set_edit_mode", mode)

    @staticmethod
    def _default_numbering_preview_runner(dialog: NumberingPreviewDialog) -> bool:
        return dialog.exec() == dialog.DialogCode.Accepted

    def _run_numbering_command(
        self,
        command: RenumberNodesCommand | RenumberMembersCommand | RenumberAllCommand,
    ) -> None:
        model = self.current_model
        if model is None or self.repair_history is None:
            return
        dialog = NumberingPreviewDialog(model, command, parent=self)
        if not self._run_numbering_preview(dialog):
            self.statusBar().showMessage("STAAD numbering cancelled")
            return
        self._execute_manual_command(command)

    def _auto_number_nodes(self) -> None:
        self._run_numbering_command(RenumberNodesCommand(NumberingPolicy()))

    def _auto_number_members(self) -> None:
        self._run_numbering_command(RenumberMembersCommand(NumberingPolicy()))

    def _auto_number_all(self) -> None:
        self._run_numbering_command(RenumberAllCommand(NumberingPolicy()))

    def _auto_fix_all_directions(self) -> None:
        model = self.current_model
        if model is None:
            return
        command = build_auto_fix_all(model)
        if command is None:
            self._refresh_orientation_preview()
            self.statusBar().showMessage("Member incidence/local-X already normalized")
            return
        self._execute_manual_command(command)

    def _auto_fix_selected_directions(self) -> None:
        model = self.current_model
        if model is None:
            return
        selected = self._selected_member_keys()
        if not selected:
            self.statusBar().showMessage("Auto Fix Selected requires selected Member(s)")
            return
        try:
            command = build_auto_fix_selected(model, selected)
        except ValueError as exc:
            self.statusBar().showMessage(f"Direction control rejected: {exc}")
            return
        if command is None:
            self.statusBar().showMessage("Selected member incidence/local-X already normalized")
            return
        self._execute_manual_command(command)

    def _flip_selected_directions(self) -> None:
        model = self.current_model
        if model is None:
            return
        selected = self._selected_member_keys()
        if not selected:
            self.statusBar().showMessage("Flip Selected requires selected Member(s)")
            return
        try:
            command = build_flip_selected(model, selected)
        except ValueError as exc:
            self.statusBar().showMessage(f"Direction control rejected: {exc}")
            return
        if command is not None:
            self._execute_manual_command(command)

    def _start_set_direction(self) -> None:
        model = self.current_model
        if model is None:
            return
        selected = self._selected_member_keys()
        if len(selected) != 1:
            self.statusBar().showMessage("Set Direction requires exactly one selected Member")
            self.set_direction_action.setChecked(False)
            return
        member_key = selected[0]
        self._direction_member_key = member_key
        self.local_x_view_action.setChecked(True)
        self._activate_edit_mode(EditMode.SET_DIRECTION)
        self._call_viewport("begin_set_direction", member_key)
        self.statusBar().showMessage("Set Direction: click the endpoint that must become Start (i)")

    def _apply_direction_endpoint(self, node_key: UUID) -> None:
        model = self.current_model
        member_key = self._direction_member_key
        if model is None or member_key is None:
            return
        try:
            command = SetMemberStart(member_key, node_key).build(model)
        except ValueError as exc:
            self.statusBar().showMessage(f"Set Direction rejected: {exc}")
            return
        if command is None:
            self.statusBar().showMessage("Selected endpoint is already Start (i)")
        else:
            self._execute_manual_command(command)
        self._direction_member_key = None
        self._activate_select_mode()

    def _execute_manual_command(self, command: RepairCommand) -> None:
        if self.current_model is None or self.repair_history is None:
            return
        if isinstance(command, (DeleteNode, DeleteMember)):
            if not self._confirm_delete(
                f"Delete selected {type(command).__name__.removeprefix('Delete')}?"
            ):
                self.statusBar().showMessage("Manual edit cancelled")
                return
        try:
            self.repair_history.execute(command)
        except (ValueError, RuntimeError) as exc:
            self.statusBar().showMessage(f"Manual edit rejected: {exc}")
            return
        self.refresh_validation()

    def _selected_node_keys(self) -> tuple[UUID, ...]:
        selection = getattr(self.viewport_host, "selection", None)
        selected = getattr(selection, "selected_nodes", ())
        return tuple(selected)

    def _apply_existing_node_collision(
        self,
        collision: ExistingNodeCollision,
        *,
        reference_node: UUID | None = None,
        create_member: bool = False,
    ) -> None:
        message = f"Target matches existing Node {collision.node_key}. Use Existing Node?"
        if not self._confirm_use_existing(message):
            self.statusBar().showMessage("Create Node cancelled")
            return
        self._call_viewport("highlight_nodes", (collision.node_key,))
        if create_member and reference_node is not None and reference_node != collision.node_key:
            self._execute_manual_command(ConnectNodes(reference_node, collision.node_key))
            return
        self.statusBar().showMessage(f"Using existing Node {collision.node_key}")

    def _apply_exact_node_spec(
        self,
        spec: ExactNodeSpec,
        *,
        tolerance_m: float,
    ) -> None:
        model = self.current_model
        if model is None:
            return
        try:
            result = build_exact_create(model, spec, tolerance_m)
        except ValueError as exc:
            self.statusBar().showMessage(f"Create Node rejected: {exc}")
            return
        if isinstance(result, ExistingNodeCollision):
            self._apply_existing_node_collision(result)
            return
        self._execute_manual_command(result)

    def _apply_relative_node_spec(
        self,
        spec: RelativeNodeSpec,
        *,
        tolerance_m: float,
    ) -> None:
        model = self.current_model
        if model is None:
            return
        try:
            result = build_relative_create(model, spec, tolerance_m)
        except ValueError as exc:
            self.statusBar().showMessage(f"Create Node rejected: {exc}")
            return
        if isinstance(result, ExistingNodeCollision):
            self._apply_existing_node_collision(
                result,
                reference_node=spec.reference_node,
                create_member=spec.create_member,
            )
            return
        self._execute_manual_command(result)

    def _apply_translational_repeat(
        self,
        spec: TranslationalRepeatSpec,
        *,
        resolutions: dict[int, ExistingNodeResolution],
        tolerance_m: float,
    ) -> None:
        model = self.current_model
        if model is None:
            return
        try:
            result = build_translational_repeat(
                model,
                spec,
                resolutions=resolutions,
                tolerance_m=tolerance_m,
            )
        except ValueError as exc:
            self.statusBar().showMessage(f"Repeat rejected: {exc}")
            return
        if isinstance(result, RepeatResolutionRequired):
            steps = ", ".join(str(step) for step in sorted(result.collisions))
            self.statusBar().showMessage(
                f"Repeat requires collision resolution for step(s): {steps}"
            )
            return
        if result is None:
            self.statusBar().showMessage("Translational Repeat cancelled or produced no changes")
            return
        self._execute_manual_command(result)

    def _show_precision_preview_request(self, request: PrecisionNodePreviewRequest) -> None:
        method = getattr(self.viewport_host, "show_precise_node_preview", None)
        if method is None:
            return
        method(
            request.position,
            reference_node=request.reference_node,
            create_member=request.create_member,
        )

    def _show_repeat_preview_request(self, request: RepeatPreviewRequest) -> None:
        method = getattr(self.viewport_host, "show_translational_repeat_preview", None)
        if method is None:
            return
        method(request.preview, request.spec, request.resolutions)

    def _open_create_node_dialog(self) -> None:
        model = self.current_model
        if model is None:
            return
        selected = self._selected_node_keys()
        reference = selected[0] if len(selected) == 1 else None
        dialog = CreateNodeDialog(model, reference_node=reference, parent=self)
        dialog.preview_requested.connect(self._show_precision_preview_request)
        if dialog.exec() != dialog.DialogCode.Accepted:
            self._call_viewport("clear_precision_preview")
            return
        if dialog.tabs.currentWidget() is dialog.relative_tab:
            self._apply_relative_node_spec(
                dialog.current_relative_spec(),
                tolerance_m=1e-6,
            )
        else:
            self._apply_exact_node_spec(dialog.current_exact_spec(), tolerance_m=1e-6)
        self._call_viewport("clear_precision_preview")

    def _open_translational_repeat_dialog(self) -> None:
        model = self.current_model
        if model is None:
            return
        selected = self._selected_node_keys()
        if len(selected) != 1:
            self.statusBar().showMessage(
                "Translational Repeat requires exactly one selected reference Node"
            )
            return
        dialog = TranslationalRepeatDialog(
            model,
            reference_node=selected[0],
            tolerance_m=1e-6,
            parent=self,
        )
        dialog.preview_requested.connect(self._show_repeat_preview_request)
        if dialog.exec() != dialog.DialogCode.Accepted:
            self._call_viewport("clear_precision_preview")
            return
        self._apply_translational_repeat(
            dialog.current_spec(),
            resolutions=dialog.current_resolutions(),
            tolerance_m=1e-6,
        )
        self._call_viewport("clear_precision_preview")

    def _selected_member_keys(self) -> tuple[UUID, ...]:
        selection = getattr(self.viewport_host, "selection", None)
        selected = getattr(selection, "selected_members", ())
        return tuple(selected)

    def _single_selected_member(self) -> UUID | None:
        selected = self._selected_member_keys()
        if len(selected) != 1:
            self.statusBar().showMessage("Split requires exactly one selected Member")
            return None
        return selected[0]

    def _execute_split_factory(self, factory: Callable[[], RepairCommand]) -> None:
        try:
            command = factory()
        except ValueError as exc:
            self.statusBar().showMessage(f"Split rejected: {exc}")
            return
        self._execute_manual_command(command)

    def _split_selected_midpoint(self) -> None:
        model = self.current_model
        if model is None:
            return
        member_key = self._single_selected_member()
        if member_key is None:
            return
        self._execute_split_factory(lambda: build_split_member_midpoint(model, member_key))

    def _split_selected_percentage(self) -> None:
        model = self.current_model
        if model is None:
            return
        member_key = self._single_selected_member()
        if member_key is None:
            return
        value, accepted = QInputDialog.getDouble(
            self,
            "Split Member",
            "Percentage from start (%)",
            50.0,
            0.001,
            99.999,
            3,
        )
        if not accepted:
            return
        self._execute_split_factory(lambda: build_split_member_percentage(model, member_key, value))

    def _split_selected_distance(self) -> None:
        model = self.current_model
        if model is None:
            return
        member_key = self._single_selected_member()
        if member_key is None:
            return
        value, accepted = QInputDialog.getDouble(
            self,
            "Split Member",
            "Distance from start (m)",
            1.0,
            0.000001,
            1_000_000_000.0,
            6,
        )
        if not accepted:
            return
        self._execute_split_factory(lambda: build_split_member_distance(model, member_key, value))

    def _split_selected_intersection(self) -> None:
        model = self.current_model
        if model is None:
            return
        selected = self._selected_member_keys()
        if len(selected) != 2:
            self.statusBar().showMessage("Intersection split requires exactly two selected Members")
            return
        self._execute_split_factory(
            lambda: build_split_selected_intersection(model, selected[0], selected[1])
        )

    def _sync_selection_filter(self) -> None:
        selection_filter = SelectionFilter(
            nodes=self.select_nodes_action.isChecked(),
            members=self.select_members_action.isChecked(),
        )
        self._call_viewport("set_selection_filter", selection_filter)

    def _current_label_visibility(self) -> LabelVisibility:
        return LabelVisibility(
            node_numbers=self.node_numbers_action.isChecked(),
            member_numbers=self.member_numbers_action.isChecked(),
            local_x=self.local_x_view_action.isChecked(),
            coordinates=self.coordinates_action.isChecked(),
        )

    def _sync_label_visibility(self) -> None:
        visibility = self._current_label_visibility()
        method = getattr(self.viewport_host, "set_label_visibility", None)
        if method is not None:
            method(visibility)
            return
        self._call_viewport("show_local_x_arrows", visibility.local_x)

    def _choose_sketchup_neutral(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import SketchUp Bridge JSON",
            str(self.neutral_reader.inbox),
            "Neutral JSON (*.json)",
        )
        if not file_name:
            return
        try:
            self.load_sketchup_neutral(Path(file_name))
        except (NeutralReaderError, ImportPipelineError, ValueError) as exc:
            self.statusBar().showMessage(f"SketchUp Bridge import blocked: {exc}")
            QMessageBox.warning(self, "Import Blocked", str(exc))

    def _choose_dxf(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import DXF",
            "",
            "DXF Files (*.dxf)",
        )
        if not file_name:
            return
        try:
            self.load_dxf_canonical(Path(file_name))
        except (ImportPipelineError, OSError, ValueError) as exc:
            self.statusBar().showMessage(f"Direct DXF import blocked: {exc}")
            QMessageBox.warning(self, "Import Blocked", str(exc))

    def load_sketchup_neutral(self, path: Path) -> ProjectModel:
        """Import SketchUp Neutral JSON through the shared T06/T07 canonical path."""
        batch = self.neutral_reader.read(path)
        model = canonicalize_import_batch(batch)
        self.set_canonical_model(model)
        self.statusBar().showMessage(
            f"SKETCHUP BRIDGE IMPORTED | Nodes: {len(model.nodes)} | Members: {len(model.members)}"
        )
        return model

    def load_dxf_canonical(self, path: Path) -> ProjectModel:
        """Import DXF directly through the shared T06/T07 canonical path."""
        batch = DxfReader().read(path)
        model = canonicalize_import_batch(batch)
        self.set_canonical_model(model)
        self.statusBar().showMessage(
            f"DIRECT DXF IMPORTED | Nodes: {len(model.nodes)} | Members: {len(model.members)}"
        )
        return model

    def _choose_export_std(self) -> None:
        initial_path = self._project_paths.artifacts / "model.std"
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export STAAD STD",
            str(initial_path),
            "STAAD Model (*.std)",
        )
        if not file_name:
            return
        try:
            self.export_current_std(Path(file_name))
        except (StaadExportError, ValueError) as exc:
            self.statusBar().showMessage(f"Export blocked: {exc}")
            QMessageBox.warning(self, "Export Blocked", str(exc))

    def export_current_std(self, path: Path) -> ExportReport:
        """Export only a model currently accepted by the authoritative ReadyGate."""
        if self.current_model is None:
            raise StaadExportError("canonical model is required before STAAD export")
        issues = validate_model(self.current_model)
        status = self.ready_gate.evaluate(self.current_model, issues)
        self.current_issues = issues
        self.current_ready_status = status
        if not status.ready:
            blockers = ", ".join(status.blockers)
            raise StaadExportError(f"model is not READY FOR STAAD: {blockers}")
        safe_path = self._project_paths.assert_inside_project(path)
        report = export_staad_std(self.current_model, safe_path)
        audit_entries = () if self.repair_history is None else self.repair_history.audit.entries
        write_validation_report(
            report.path.with_suffix(".validation.json"),
            model=self.current_model,
            issues=issues,
            ready_status=status,
            audit_entries=audit_entries,
            export_report=report,
        )
        self.statusBar().showMessage(
            "Exported STAAD STD | "
            f"Nodes: {report.node_count} | Members: {report.member_count} | "
            f"Warnings: {len(report.warning_issue_ids)} | {report.path}"
        )
        return report

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
        self.current_ready_status = None
        self.repair_history = None
        self._selected_issue_id = None
        self.issue_console.set_issues([])
        self.properties_panel.set_issue(None)
        self.quick_fix_panel.set_issue(None)
        self._update_history_actions()
        self.validate_action.setEnabled(False)
        self.repair_action.setEnabled(False)
        self.export_std_action.setEnabled(False)
        self.export_std_action.setToolTip("Canonical validated and numbered model required")
        self.split_action.setEnabled(False)
        self.renumber_action.setEnabled(False)
        for action in (
            self.auto_node_number_action,
            self.auto_member_number_action,
            self.auto_number_all_action,
            self.auto_fix_selected_action,
            self.flip_selected_action,
            self.set_direction_action,
        ):
            action.setEnabled(False)
        self._direction_member_key = None
        self.orientation_reverse_count = 0
        self.normalize_axis_action.setEnabled(False)
        self.normalize_axis_action.setToolTip("Canonical metre/Y-Up model required")
        self.validation_panel.set_local_x_preview(reverse_count=0, total=0)
        self._call_viewport("show_local_x_arrows", False)
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
        self.create_node_dialog_action.setEnabled(True)
        self.translational_repeat_action.setEnabled(True)
        self.split_action.setEnabled(True)
        self.renumber_action.setEnabled(True)
        for action in (
            self.auto_node_number_action,
            self.auto_member_number_action,
            self.auto_number_all_action,
        ):
            action.setEnabled(True)
        has_members = bool(model.members)
        self.auto_fix_selected_action.setEnabled(has_members)
        self.flip_selected_action.setEnabled(has_members)
        self.set_direction_action.setEnabled(has_members)
        self._direction_member_key = None
        self._selected_issue_id = None
        self.refresh_validation()

    def refresh_validation(self) -> None:
        if self.current_model is None:
            return
        self.current_issues = validate_model(self.current_model)
        self.current_ready_status = self.ready_gate.evaluate(
            self.current_model,
            self.current_issues,
        )
        self._selected_issue_id = None
        self.issue_console.set_issues(self.current_issues)
        self.validation_panel.set_issues(self.current_issues)
        self.properties_panel.set_issue(None)
        self.quick_fix_panel.set_issue(None)
        self.repair_action.setEnabled(False)
        self._set_viewport_model(self.current_model)
        self._refresh_orientation_preview()

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
        if self.current_ready_status.ready:
            self.model_status.setText("MODEL STATUS: READY FOR STAAD")
        else:
            blockers = ", ".join(self.current_ready_status.blockers)
            self.model_status.setText(f"MODEL STATUS: NOT READY | {blockers}")
        self.statusBar().showMessage(
            f"Validation complete | Issues: {len(self.current_issues)} | "
            f"Ready: {self.current_ready_status.ready} | "
            f"Revision: {self.current_model.revision}"
        )
        self._update_history_actions()
        self._refresh_export_gate()

    def _refresh_export_gate(self) -> None:
        model = self.current_model
        status = self.current_ready_status
        if model is None or status is None:
            self.export_std_action.setEnabled(False)
            self.export_std_action.setToolTip(
                "Load and validate a canonical model before STAAD export"
            )
            return
        if not status.ready:
            self.export_std_action.setEnabled(False)
            blockers = ", ".join(status.blockers)
            self.export_std_action.setToolTip(f"Model is not READY FOR STAAD: {blockers}")
            return
        self.export_std_action.setEnabled(True)
        self.export_std_action.setToolTip("Export READY FOR STAAD geometry (.std)")

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

    def normalize_member_directions(self) -> None:
        """Normalize all member incidence/local-X through reversible repair history."""
        if self.current_model is None or self.repair_history is None:
            return
        commands = normalization_commands(self.current_model)
        if not commands:
            self._refresh_orientation_preview()
            self.statusBar().showMessage("Member incidence/local-X already normalized")
            return
        for command in commands:
            self.repair_history.execute(command)
        count = len(commands)
        self.refresh_validation()
        self.statusBar().showMessage(f"Normalized local-X incidence for {count} member(s)")

    def _refresh_orientation_preview(self) -> None:
        if self.current_model is None:
            self.orientation_reverse_count = 0
            self.normalize_axis_action.setEnabled(False)
            self.validation_panel.set_local_x_preview(reverse_count=0, total=0)
            self._sync_label_visibility()
            return
        commands = normalization_commands(self.current_model)
        self.orientation_reverse_count = len(commands)
        total = len(self.current_model.members)
        self.validation_panel.set_local_x_preview(
            reverse_count=self.orientation_reverse_count,
            total=total,
        )
        self._sync_label_visibility()
        if self.orientation_reverse_count:
            self.normalize_axis_action.setEnabled(True)
            self.normalize_axis_action.setToolTip(
                f"{self.orientation_reverse_count} member(s) need reversal; "
                "normalizes incidence/local-X only"
            )
        else:
            self.normalize_axis_action.setEnabled(False)
            self.normalize_axis_action.setToolTip("Member incidence/local-X already normalized")

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
        if (
            issue.type
            in {
                IssueType.DUPLICATE_NODE,
                IssueType.NEAR_NODE,
                IssueType.UNCONNECTED_GAP,
            }
            and len(node_keys) >= 2
        ):
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

    def _confirm_use_existing_dialog(self, message: str) -> bool:
        result = QMessageBox.question(
            self,
            "Existing Node",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result is QMessageBox.StandardButton.Yes

    def _confirm_delete_dialog(self, message: str) -> bool:
        result = QMessageBox.question(
            self,
            "Confirm Repair",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result is QMessageBox.StandardButton.Yes
