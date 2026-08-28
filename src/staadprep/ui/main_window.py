"""Main desktop window matching the approved V1 layout baseline."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from staadprep.importers.contracts import ImportBatch
from staadprep.importers.dxf_reader import DxfReader
from staadprep.importers.raw_preview import raw_batch_to_preview_model
from staadprep.ui.panels import (
    IssueConsole,
    ModelStatusBar,
    ProjectExplorerPanel,
    PropertiesPanel,
    QuickFixPanel,
    ValidationPanel,
)
from staadprep.viewer.widget import StructuralViewport


class MainWindow(QMainWindow):
    """Approved V1 engineering shell; feature actions are enabled by later tasks."""

    def __init__(
        self,
        viewport_factory: Callable[[], QWidget] | None = None,
    ) -> None:
        super().__init__()
        self._viewport_factory = viewport_factory or StructuralViewport
        self.current_import_batch: ImportBatch | None = None
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

        self.unit_check_action = self._disabled_action("Unit Check", "Available in Task 06")
        self.repair_action = self._disabled_action("Repair", "Available in Task 09")
        self.normalize_axis_action = self._disabled_action(
            "Normalize Axis", "Available in Task 11"
        )
        self.renumber_action = self._disabled_action("Renumber", "Available in Task 12")
        self.validate_action = self._disabled_action("Validate", "Available in validation tasks")
        self.export_std_action = self._disabled_action("Export STD", "Available in Task 13")

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
        self.issue_console.setMinimumHeight(150)
        self.issue_console.setMaximumHeight(230)
        root_layout.addWidget(self.issue_console)

        model_status_bar = ModelStatusBar()
        self.model_status = model_status_bar.status_label
        root_layout.addWidget(model_status_bar)

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
        set_model = getattr(self.viewport_host, "set_model", None)
        if set_model is None:
            raise TypeError("Configured viewport does not support set_model()")
        set_model(preview_model)
        self.project_explorer.set_raw_preview_summary(
            node_count=len(preview_model.nodes),
            member_count=len(preview_model.members),
            unit=batch.declared_unit,
        )

        self.current_import_batch = batch
        self.model_status.setText("RAW DXF PREVIEW — NOT VALIDATED")
        unit = batch.declared_unit or "unknown"
        self.statusBar().showMessage(
            "RAW DXF PREVIEW — NOT VALIDATED | "
            f"Segments: {len(batch.segments)} | Points: {len(batch.points)} | Unit: {unit}"
        )
        return batch
