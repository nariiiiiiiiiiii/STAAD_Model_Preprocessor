"""Focused dialogs for precise Node creation and translational repeat."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from staadprep.editing.create_node import (
    ExactNodeSpec,
    ExistingNodeResolution,
    MemberTranslationalRepeatPreview,
    MemberTranslationalRepeatSpec,
    RelativeNodeSpec,
    RepeatConnectionMode,
    TranslationalRepeatPreview,
    TranslationalRepeatSpec,
    analyze_member_translational_repeat,
    analyze_translational_repeat,
    exact_position,
    relative_position,
)
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


@dataclass(frozen=True, slots=True)
class PrecisionNodePreviewRequest:
    position: Vec3
    reference_node: UUID | None
    create_member: bool


@dataclass(frozen=True, slots=True)
class RepeatPreviewRequest:
    preview: TranslationalRepeatPreview
    spec: TranslationalRepeatSpec
    resolutions: dict[int, ExistingNodeResolution]


@dataclass(frozen=True, slots=True)
class MemberRepeatPreviewRequest:
    preview: MemberTranslationalRepeatPreview
    spec: MemberTranslationalRepeatSpec
    resolutions: dict[tuple[int, UUID], ExistingNodeResolution]


class CreateNodeDialog(QDialog):
    preview_requested = Signal(object)

    def __init__(
        self,
        model: ProjectModel,
        *,
        reference_node: UUID | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.model = model
        self.reference_node = reference_node
        self.setWindowTitle("Create Node")
        self.setModal(True)

        root = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.exact_tab = QWidget(self.tabs)
        self.relative_tab = QWidget(self.tabs)
        self.tabs.addTab(self.exact_tab, "Exact XYZ")
        self.tabs.addTab(self.relative_tab, "Relative to Node")
        root.addWidget(self.tabs)

        self.exact_x_label = QLabel("STAAD X")
        self.exact_y_label = QLabel("STAAD Y (Vertical)")
        self.exact_z_label = QLabel("STAAD Z")
        self.exact_x = self._coordinate_spin()
        self.exact_y = self._coordinate_spin()
        self.exact_z = self._coordinate_spin()
        exact_form = QFormLayout(self.exact_tab)
        exact_form.addRow(self.exact_x_label, self.exact_x)
        exact_form.addRow(self.exact_y_label, self.exact_y)
        exact_form.addRow(self.exact_z_label, self.exact_z)

        self.reference_label = QLabel()
        self.relative_dx = self._coordinate_spin()
        self.relative_dy = self._coordinate_spin()
        self.relative_dz = self._coordinate_spin()
        self.create_member_checkbox = QCheckBox(
            "Create Member — Reference Node → New Node",
            self.relative_tab,
        )
        relative_form = QFormLayout(self.relative_tab)
        relative_form.addRow(self.reference_label)
        relative_form.addRow("ΔX", self.relative_dx)
        relative_form.addRow("ΔY (Vertical)", self.relative_dy)
        relative_form.addRow("ΔZ", self.relative_dz)
        relative_form.addRow(self.create_member_checkbox)

        self.result_label = QLabel("Result: —")
        root.addWidget(self.result_label)

        buttons = QHBoxLayout()
        self.preview_button = QPushButton("Preview", self)
        self.create_button = QPushButton("Create", self)
        self.cancel_button = QPushButton("Cancel", self)
        buttons.addWidget(self.preview_button)
        buttons.addWidget(self.create_button)
        buttons.addWidget(self.cancel_button)
        root.addLayout(buttons)

        self.preview_button.clicked.connect(self.preview_current)
        self.create_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self._sync_reference_ui()

    @staticmethod
    def _coordinate_spin() -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setDecimals(6)
        spin.setRange(-1_000_000_000.0, 1_000_000_000.0)
        spin.setSingleStep(0.1)
        spin.setSuffix(" m")
        return spin

    def _sync_reference_ui(self) -> None:
        if self.reference_node is None or self.reference_node not in self.model.nodes:
            self.reference_label.setText("Reference: none selected")
            self.tabs.setTabEnabled(self.tabs.indexOf(self.relative_tab), False)
            self.create_member_checkbox.setEnabled(False)
            return
        point = self.model.nodes[self.reference_node].position
        self.reference_label.setText(
            f"Reference: X={point.x:.3f}, Y={point.y:.3f}, Z={point.z:.3f} m"
        )

    def current_exact_spec(self) -> ExactNodeSpec:
        return ExactNodeSpec(
            x=self.exact_x.value(),
            y=self.exact_y.value(),
            z=self.exact_z.value(),
        )

    def current_relative_spec(self) -> RelativeNodeSpec:
        if self.reference_node is None:
            raise ValueError("Relative Node creation requires a reference node")
        return RelativeNodeSpec(
            reference_node=self.reference_node,
            dx=self.relative_dx.value(),
            dy=self.relative_dy.value(),
            dz=self.relative_dz.value(),
            create_member=self.create_member_checkbox.isChecked(),
        )

    def preview_current(self) -> Vec3:
        is_relative = self.tabs.currentWidget() is self.relative_tab
        if is_relative:
            spec = self.current_relative_spec()
            position = relative_position(self.model, spec)
            reference_node = spec.reference_node
            create_member = spec.create_member
        else:
            position = exact_position(self.current_exact_spec())
            reference_node = None
            create_member = False
        self.result_label.setText(
            f"Result: X={position.x:.3f}, Y={position.y:.3f}, Z={position.z:.3f} m"
        )
        self.preview_requested.emit(
            PrecisionNodePreviewRequest(position, reference_node, create_member)
        )
        return position


class TranslationalRepeatDialog(QDialog):
    preview_requested = Signal(object)

    def __init__(
        self,
        model: ProjectModel,
        *,
        reference_node: UUID,
        tolerance_m: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.model = model
        self.reference_node = reference_node
        self.tolerance_m = tolerance_m
        if reference_node not in model.nodes:
            raise ValueError(f"Reference node {reference_node} does not exist")

        self.setWindowTitle("Translational Repeat")
        self.setModal(True)
        root = QVBoxLayout(self)

        reference = model.nodes[reference_node].position
        self.reference_label = QLabel(
            f"Reference: X={reference.x:.3f}, Y={reference.y:.3f}, Z={reference.z:.3f} m"
        )
        root.addWidget(self.reference_label)

        form = QFormLayout()
        self.dx_label = QLabel("ΔX")
        self.dy_label = QLabel("ΔY (Vertical)")
        self.dz_label = QLabel("ΔZ")
        self.dx = CreateNodeDialog._coordinate_spin()
        self.dy = CreateNodeDialog._coordinate_spin()
        self.dz = CreateNodeDialog._coordinate_spin()
        self.repeat_label = QLabel("Repeat count (new positions, excluding reference)")
        self.repeats = QSpinBox(self)
        self.repeats.setRange(1, 100_000)
        self.repeats.setValue(1)
        self.connection_combo = QComboBox(self)
        self.connection_combo.addItem("Connect Consecutive Nodes", RepeatConnectionMode.CONSECUTIVE)
        self.connection_combo.addItem(
            "Connect From Reference Node", RepeatConnectionMode.FROM_REFERENCE
        )
        self.connection_combo.addItem("No Members", RepeatConnectionMode.NONE)
        form.addRow(self.dx_label, self.dx)
        form.addRow(self.dy_label, self.dy)
        form.addRow(self.dz_label, self.dz)
        form.addRow(self.repeat_label, self.repeats)
        form.addRow("Connection", self.connection_combo)
        root.addLayout(form)

        self.preview_summary = QLabel("Preview: —", self)
        root.addWidget(self.preview_summary)

        self.collision_table = QTableWidget(0, 3, self)
        self.collision_table.setHorizontalHeaderLabels(("Step", "Existing Node", "Resolution"))
        self.collision_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.collision_table.setVisible(False)
        root.addWidget(self.collision_table)

        buttons = QHBoxLayout()
        self.preview_button = QPushButton("Preview", self)
        self.apply_button = QPushButton("Apply", self)
        self.cancel_button = QPushButton("Cancel", self)
        buttons.addWidget(self.preview_button)
        buttons.addWidget(self.apply_button)
        buttons.addWidget(self.cancel_button)
        root.addLayout(buttons)
        self.preview_button.clicked.connect(self.preview_current)
        self.apply_button.clicked.connect(self._accept_if_resolved)
        self.cancel_button.clicked.connect(self.reject)

    def current_spec(self) -> TranslationalRepeatSpec:
        raw_mode = self.connection_combo.currentData()
        try:
            mode = RepeatConnectionMode(raw_mode)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid Translational Repeat connection mode") from exc
        return TranslationalRepeatSpec(
            reference_node=self.reference_node,
            dx=self.dx.value(),
            dy=self.dy.value(),
            dz=self.dz.value(),
            repeats=self.repeats.value(),
            connection_mode=mode,
        )

    def current_resolutions(self) -> dict[int, ExistingNodeResolution]:
        result: dict[int, ExistingNodeResolution] = {}
        for row in range(self.collision_table.rowCount()):
            step_item = self.collision_table.item(row, 0)
            combo = self.collision_table.cellWidget(row, 2)
            if step_item is None or not isinstance(combo, QComboBox):
                continue
            raw_resolution = combo.currentData()
            if raw_resolution is None:
                continue
            try:
                resolution = ExistingNodeResolution(raw_resolution)
            except (TypeError, ValueError):
                continue
            result[int(step_item.text())] = resolution
        return result

    def _populate_collisions(
        self,
        collisions: dict[int, UUID],
        previous: dict[int, ExistingNodeResolution],
    ) -> None:
        self.collision_table.setRowCount(0)
        for row, (step, node_key) in enumerate(sorted(collisions.items())):
            self.collision_table.insertRow(row)
            self.collision_table.setItem(row, 0, QTableWidgetItem(str(step)))
            self.collision_table.setItem(row, 1, QTableWidgetItem(str(node_key)))
            combo = QComboBox(self.collision_table)
            combo.addItem("Choose resolution…", None)
            combo.addItem("Use Existing Node", ExistingNodeResolution.USE_EXISTING)
            combo.addItem("Skip Step", ExistingNodeResolution.SKIP_STEP)
            combo.addItem("Cancel Repeat", ExistingNodeResolution.CANCEL)
            selected = previous.get(step)
            if selected is not None:
                index = combo.findData(selected)
                if index >= 0:
                    combo.setCurrentIndex(index)
            self.collision_table.setCellWidget(row, 2, combo)
        self.collision_table.setVisible(bool(collisions))

    def preview_current(self) -> TranslationalRepeatPreview:
        previous = self.current_resolutions()
        spec = self.current_spec()
        preview = analyze_translational_repeat(
            self.model,
            spec,
            tolerance_m=self.tolerance_m,
            resolutions=previous,
        )
        self._populate_collisions(preview.collisions, previous)
        final = preview.final_coordinate
        self.preview_summary.setText(
            "Preview | "
            f"New Nodes: {preview.new_node_count} | "
            f"New Members: {preview.new_member_count} | "
            f"Reused: {preview.reused_node_count} | "
            f"Skipped: {preview.skipped_count} | "
            f"Final: X={final.x:.3f}, Y={final.y:.3f}, Z={final.z:.3f} m"
        )
        request = RepeatPreviewRequest(
            preview=preview,
            spec=spec,
            resolutions=self.current_resolutions(),
        )
        self.preview_requested.emit(request)
        return preview

    def _accept_if_resolved(self) -> None:
        preview = self.preview_current()
        resolutions = self.current_resolutions()
        unresolved = sorted(set(preview.collisions) - set(resolutions))
        if unresolved:
            steps = ", ".join(str(step) for step in unresolved)
            self.preview_summary.setText(
                self.preview_summary.text() + f" | Choose resolution for step(s): {steps}"
            )
            return
        self.accept()


class MemberTranslationalRepeatDialog(QDialog):
    """Translate selected Members while preserving their shared-node topology."""

    preview_requested = Signal(object)

    def __init__(
        self,
        model: ProjectModel,
        *,
        member_keys: tuple[UUID, ...],
        tolerance_m: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.model = model
        self.member_keys = tuple(sorted(set(member_keys), key=lambda key: key.int))
        self.tolerance_m = tolerance_m
        if not self.member_keys:
            raise ValueError("Member Translational Repeat requires selected Members")

        self.setWindowTitle("Translational Repeat — Members")
        self.setModal(True)
        root = QVBoxLayout(self)
        self.selection_label = QLabel(
            f"Selection: {len(self.member_keys)} selected Members",
            self,
        )
        root.addWidget(self.selection_label)

        form = QFormLayout()
        self.dx = CreateNodeDialog._coordinate_spin()
        self.dy = CreateNodeDialog._coordinate_spin()
        self.dz = CreateNodeDialog._coordinate_spin()
        self.repeats = QSpinBox(self)
        self.repeats.setRange(1, 100_000)
        self.repeats.setValue(1)
        form.addRow("ΔX", self.dx)
        form.addRow("ΔY (Vertical)", self.dy)
        form.addRow("ΔZ", self.dz)
        form.addRow("Repeat count (copies)", self.repeats)
        root.addLayout(form)

        self.preview_summary = QLabel("Preview: —", self)
        root.addWidget(self.preview_summary)
        self.collision_table = QTableWidget(0, 4, self)
        self.collision_table.setHorizontalHeaderLabels(
            ("Step", "Source Node", "Existing Node", "Resolution")
        )
        self.collision_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.collision_table.setVisible(False)
        root.addWidget(self.collision_table)

        buttons = QHBoxLayout()
        self.preview_button = QPushButton("Preview", self)
        self.apply_button = QPushButton("Apply", self)
        self.cancel_button = QPushButton("Cancel", self)
        buttons.addWidget(self.preview_button)
        buttons.addWidget(self.apply_button)
        buttons.addWidget(self.cancel_button)
        root.addLayout(buttons)
        self.preview_button.clicked.connect(self.preview_current)
        self.apply_button.clicked.connect(self._accept_if_resolved)
        self.cancel_button.clicked.connect(self.reject)

    def current_spec(self) -> MemberTranslationalRepeatSpec:
        return MemberTranslationalRepeatSpec(
            member_keys=self.member_keys,
            dx=self.dx.value(),
            dy=self.dy.value(),
            dz=self.dz.value(),
            repeats=self.repeats.value(),
        )

    def current_resolutions(
        self,
    ) -> dict[tuple[int, UUID], ExistingNodeResolution]:
        result: dict[tuple[int, UUID], ExistingNodeResolution] = {}
        for row in range(self.collision_table.rowCount()):
            step_item = self.collision_table.item(row, 0)
            source_item = self.collision_table.item(row, 1)
            combo = self.collision_table.cellWidget(row, 3)
            if (
                step_item is None
                or source_item is None
                or not isinstance(combo, QComboBox)
            ):
                continue
            raw_resolution = combo.currentData()
            if raw_resolution is None:
                continue
            try:
                result[(int(step_item.text()), UUID(source_item.text()))] = (
                    ExistingNodeResolution(raw_resolution)
                )
            except (TypeError, ValueError):
                continue
        return result

    def _populate_collisions(
        self,
        collisions: dict[tuple[int, UUID], UUID],
        previous: dict[tuple[int, UUID], ExistingNodeResolution],
    ) -> None:
        self.collision_table.setRowCount(0)
        for row, (collision_key, existing_key) in enumerate(
            sorted(collisions.items(), key=lambda item: (item[0][0], item[0][1].int))
        ):
            step, source_key = collision_key
            self.collision_table.insertRow(row)
            self.collision_table.setItem(row, 0, QTableWidgetItem(str(step)))
            self.collision_table.setItem(row, 1, QTableWidgetItem(str(source_key)))
            self.collision_table.setItem(row, 2, QTableWidgetItem(str(existing_key)))
            combo = QComboBox(self.collision_table)
            combo.addItem("Choose resolution…", None)
            combo.addItem("Use Existing Node", ExistingNodeResolution.USE_EXISTING)
            combo.addItem("Cancel Repeat", ExistingNodeResolution.CANCEL)
            selected = previous.get(collision_key)
            if selected is not None:
                index = combo.findData(selected)
                if index >= 0:
                    combo.setCurrentIndex(index)
            self.collision_table.setCellWidget(row, 3, combo)
        self.collision_table.setVisible(bool(collisions))

    def preview_current(self) -> MemberTranslationalRepeatPreview:
        previous = self.current_resolutions()
        preview = analyze_member_translational_repeat(
            self.model,
            self.current_spec(),
            tolerance_m=self.tolerance_m,
            resolutions=previous,
        )
        self._populate_collisions(preview.collisions, previous)
        self.preview_summary.setText(
            "Preview | "
            f"Source Nodes: {preview.source_node_count} | "
            f"New Nodes: {preview.new_node_count} | "
            f"New Members: {preview.new_member_count} | "
            f"Reused: {preview.reused_node_count}"
        )
        self.preview_requested.emit(
            MemberRepeatPreviewRequest(
                preview=preview,
                spec=self.current_spec(),
                resolutions=self.current_resolutions(),
            )
        )
        return preview

    def _accept_if_resolved(self) -> None:
        preview = self.preview_current()
        resolutions = self.current_resolutions()
        unresolved = sorted(
            set(preview.collisions) - set(resolutions),
            key=lambda item: (item[0], item[1].int),
        )
        if unresolved:
            labels = ", ".join(
                f"step {step} / node {source_key}" for step, source_key in unresolved
            )
            self.preview_summary.setText(
                self.preview_summary.text() + f" | Choose resolution for: {labels}"
            )
            return
        self.accept()
