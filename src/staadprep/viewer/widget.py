from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import replace
from typing import Any
from uuid import UUID

import numpy as np
import pyvista as pv
from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMenu, QVBoxLayout, QWidget
from pyvistaqt import QtInteractor
from vtkmodules.vtkRenderingCore import vtkCellPicker

from staadprep.editing.inference import AxisLock, InferenceEngine, InferenceHit
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer.interaction import (
    EditMode,
    InteractionState,
    LabelVisibility,
    SelectionFilter,
)
from staadprep.viewer.scene import SceneData
from staadprep.viewer.selection import (
    SelectionCandidate,
    SelectionEntity,
    SelectionState,
    filter_candidates,
    next_overlap_candidate,
)


class StructuralViewport(QWidget):
    """Interactive 3D view with stable member/node highlight mappings."""

    member_selected = Signal(object)
    node_selected = Signal(object)
    axis_lock_changed = Signal(object, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("viewport_host")
        self.setMinimumSize(480, 360)

        self.scene: SceneData | None = None
        self._model: ProjectModel | None = None
        self.selection = SelectionState()
        self.interaction_state = InteractionState()
        self.axis_lock = AxisLock.NONE
        self._member_actor: Any | None = None
        self._node_actor: Any | None = None
        self._member_highlight_actor: Any | None = None
        self._node_highlight_actor: Any | None = None
        self._local_x_actor: Any | None = None
        self._label_actors: list[Any] = []
        self._navigation_mode: str | None = None
        self._last_mouse_pos: tuple[float, float] | None = None
        self._left_press_pos: tuple[float, float] | None = None
        self._last_overlap_candidates: tuple[SelectionCandidate, ...] = ()
        self._last_overlap_choice: SelectionCandidate | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._off_screen = os.getenv("QT_QPA_PLATFORM", "").lower() == "offscreen"
        self.plotter: Any = QtInteractor(self, off_screen=self._off_screen)
        layout.addWidget(self.plotter.interactor)
        self.plotter.interactor.installEventFilter(self)
        self.plotter.interactor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._configure_scene()

    def _configure_scene(self) -> None:
        self.plotter.set_background("#0d1319")
        self.plotter.add_axes(line_width=2)
        self.plotter.show_grid(
            color="#2b3641",
            xtitle="X",
            ytitle="Y",
            ztitle="Z",
            grid="back",
            location="outer",
        )

    def set_model(self, model: ProjectModel) -> None:
        self._model = model
        self.scene = SceneData.from_model(model)
        self.selection.clear()
        self._last_overlap_candidates = ()
        self._last_overlap_choice = None
        if not self._off_screen:
            self.plotter.disable_picking()
        self.plotter.clear()
        self._configure_scene()
        self._member_actor = None
        self._node_actor = None
        self._member_highlight_actor = None
        self._node_highlight_actor = None
        self._local_x_actor = None
        self._clear_label_actors()

        if self.scene.points.size == 0:
            self.plotter.render()
            return

        point_cloud = pv.PolyData(self.scene.points)
        point_count = len(self.scene.point_keys)
        point_cloud.verts = np.column_stack(
            (np.ones(point_count, dtype=np.int64), np.arange(point_count, dtype=np.int64))
        ).ravel()
        self._node_actor = self.plotter.add_mesh(
            point_cloud,
            color="#6fcf97",
            point_size=8,
            render_points_as_spheres=True,
            style="points",
            pickable=True,
        )

        if self.scene.lines.size:
            line_mesh = pv.PolyData(
                self.scene.points,
                lines=self.scene.lines.ravel(),
            )
            line_mesh.cell_data["member_index"] = np.arange(
                len(self.scene.member_keys), dtype=np.int64
            )
            self._member_actor = self.plotter.add_mesh(
                line_mesh,
                color="#b7c2cc",
                line_width=2,
                pickable=True,
            )

        if self.interaction_state.labels.local_x:
            self._render_local_x_arrows()
        self._render_labels()
        self.plotter.reset_camera()
        self.plotter.render()

    def set_edit_mode(self, mode: EditMode) -> None:
        self.interaction_state = replace(self.interaction_state, mode=EditMode(mode))

    def set_axis_lock(self, axis_lock: AxisLock) -> None:
        self.axis_lock = AxisLock(axis_lock)
        if self.axis_lock is AxisLock.NONE:
            helper_text = "Axis lock cleared"
        else:
            helper_text = InferenceEngine.axis_helper_text(self.axis_lock)
        self.axis_lock_changed.emit(self.axis_lock, helper_text)

    def resolve_inference(
        self,
        candidate_position: Vec3,
        *,
        tolerance_m: float,
        reference_position: Vec3 | None = None,
    ) -> InferenceHit | None:
        if self._model is None:
            return None
        return InferenceEngine.resolve(
            self._model,
            candidate_position,
            tolerance_m=tolerance_m,
            axis_lock=self.axis_lock,
            reference_position=reference_position,
        )

    @staticmethod
    def resolve_work_plane_inference(
        *,
        ray_origin: Vec3,
        ray_direction: Vec3,
        plane_origin: Vec3,
        plane_normal: Vec3,
    ) -> InferenceHit | None:
        return InferenceEngine.resolve_work_plane(
            ray_origin=ray_origin,
            ray_direction=ray_direction,
            plane_origin=plane_origin,
            plane_normal=plane_normal,
        )

    def set_selection_filter(self, selection_filter: SelectionFilter) -> None:
        self.interaction_state = replace(
            self.interaction_state,
            selection_filter=selection_filter,
        )
        if not selection_filter.nodes:
            self.highlight_nodes(())
        if not selection_filter.members:
            self.highlight_members(())

    def set_label_visibility(self, visibility: LabelVisibility) -> None:
        self.interaction_state = replace(self.interaction_state, labels=visibility)
        self._remove_actor(self._local_x_actor)
        self._local_x_actor = None
        self._clear_label_actors()
        if visibility.local_x:
            self._render_local_x_arrows()
        self._render_labels()
        self.plotter.render()

    def show_local_x_arrows(self, visible: bool) -> None:
        """Backward-compatible T11 hook routed through T16 label visibility state."""
        self.set_label_visibility(replace(self.interaction_state.labels, local_x=bool(visible)))

    def _clear_label_actors(self) -> None:
        for actor in self._label_actors:
            self._remove_actor(actor)
        self._label_actors = []

    def _render_labels(self) -> None:
        if self.scene is None or self._model is None or not len(self.scene.point_keys):
            return
        visibility = self.interaction_state.labels
        if visibility.node_numbers or visibility.coordinates:
            labels: list[str] = []
            for index, key in enumerate(self.scene.point_keys):
                parts: list[str] = []
                node = self._model.nodes[key]
                if visibility.node_numbers:
                    parts.append(f"N{node.number if node.number is not None else '?'}")
                if visibility.coordinates:
                    x, y, z = self.scene.points[index]
                    parts.append(f"({x:.3f}, {y:.3f}, {z:.3f})")
                labels.append("\n".join(parts))
            actor = self.plotter.add_point_labels(
                self.scene.points,
                labels,
                point_size=0,
                font_size=11,
                shape=None,
                always_visible=True,
                show_points=False,
            )
            self._label_actors.append(actor)

        if visibility.member_numbers and len(self.scene.member_keys):
            labels = []
            for key in self.scene.member_keys:
                number = self._model.members[key].number
                labels.append(f"M{number if number is not None else '?'}")
            actor = self.plotter.add_point_labels(
                self.scene.member_midpoints,
                labels,
                point_size=0,
                font_size=11,
                shape=None,
                always_visible=True,
                show_points=False,
            )
            self._label_actors.append(actor)

    def _render_local_x_arrows(self) -> None:
        if self.scene is None or not len(self.scene.member_keys):
            return
        lengths = np.linalg.norm(self.scene.local_x_vectors, axis=1)
        mask = lengths > 0.0
        if not bool(np.any(mask)):
            return
        span = np.ptp(self.scene.points, axis=0) if len(self.scene.points) else np.zeros(3)
        reference = max(float(np.max(span)), 1.0)
        self._local_x_actor = self.plotter.add_arrows(
            self.scene.member_midpoints[mask],
            self.scene.local_x_vectors[mask],
            mag=reference * 0.04,
            color="#ffb347",
        )

    def _on_cells_picked(self, picked: Any) -> None:
        blocks = picked if isinstance(picked, pv.MultiBlock) else (picked,)
        for block in blocks:
            if block is None or getattr(block, "n_cells", 0) == 0:
                continue
            if "member_index" not in block.cell_data:
                continue
            member_index = int(np.asarray(block.cell_data["member_index"])[0])
            self.select_member_by_cell(member_index)
            return

    def select_member_by_cell(self, cell_index: int, *, additive: bool = False) -> UUID | None:
        if self.scene is None:
            raise RuntimeError("No model is loaded")
        if not self.interaction_state.selection_filter.members:
            return None
        member_key = self.scene.member_key_for_cell(cell_index)
        self.selection.select_member(member_key, additive=additive)
        self._render_selection_highlights()
        self.member_selected.emit(member_key)
        return member_key

    def select_node_by_index(self, point_index: int, *, additive: bool = False) -> UUID | None:
        if self.scene is None:
            raise RuntimeError("No model is loaded")
        if not self.interaction_state.selection_filter.nodes:
            return None
        node_key = self.scene.point_keys[point_index]
        self.selection.select_node(node_key, additive=additive)
        self._render_selection_highlights()
        self.node_selected.emit(node_key)
        return node_key

    def select_overlap_candidates(
        self,
        candidates: tuple[SelectionCandidate, ...],
        *,
        additive: bool = False,
    ) -> SelectionCandidate | None:
        allowed = filter_candidates(candidates, self.interaction_state.selection_filter)
        current = self._last_overlap_choice if allowed == self._last_overlap_candidates else None
        choice = next_overlap_candidate(allowed, current)
        self._last_overlap_candidates = allowed
        self._last_overlap_choice = choice
        if choice is None:
            return None
        if choice.entity is SelectionEntity.NODE:
            if self.scene is None:
                return None
            self.selection.select_node(choice.key, additive=additive)
            self.node_selected.emit(choice.key)
        else:
            self.selection.select_member(choice.key, additive=additive)
            self.member_selected.emit(choice.key)
        self._render_selection_highlights()
        return choice

    def clear_selection(self) -> None:
        self.selection.clear()
        self._last_overlap_candidates = ()
        self._last_overlap_choice = None
        self._render_selection_highlights()

    def _render_selection_highlights(self) -> None:
        node_keys = self.selection.selected_nodes
        member_keys = self.selection.selected_members
        self.highlight_nodes(node_keys)
        self.highlight_members(member_keys)

    def highlight_members(self, keys: Iterable[UUID]) -> None:
        selected = tuple(keys)
        self.selection.set_members(selected)
        self._remove_actor(self._member_highlight_actor)
        self._member_highlight_actor = None

        if self.scene is None or not selected:
            self.plotter.render()
            return

        selected_set = set(selected)
        rows = [
            self.scene.lines[index]
            for index, key in enumerate(self.scene.member_keys)
            if key in selected_set
        ]
        if not rows:
            self.plotter.render()
            return

        mesh = pv.PolyData(
            self.scene.points,
            lines=np.asarray(rows, dtype=np.int64).reshape(-1),
        )
        self._member_highlight_actor = self.plotter.add_mesh(
            mesh,
            color="#4da3ff",
            line_width=5,
            pickable=False,
        )
        self.plotter.render()

    def highlight_nodes(self, keys: Iterable[UUID]) -> None:
        selected = tuple(keys)
        self.selection.set_nodes(selected)
        self._remove_actor(self._node_highlight_actor)
        self._node_highlight_actor = None

        if self.scene is None or not selected:
            self.plotter.render()
            return

        point_indices = [
            self.scene.point_index_by_key[key]
            for key in selected
            if key in self.scene.point_index_by_key
        ]
        if not point_indices:
            self.plotter.render()
            return

        mesh = pv.PolyData(self.scene.points[point_indices])
        self._node_highlight_actor = self.plotter.add_mesh(
            mesh,
            color="#ffb347",
            point_size=14,
            render_points_as_spheres=True,
            style="points",
            pickable=False,
        )
        self.plotter.render()

    def begin_navigation(self, *, shift: bool) -> str:
        self._navigation_mode = "pan" if shift else "orbit"
        if self._navigation_mode == "orbit":
            pivot = self._selection_center()
            if pivot is not None:
                self.plotter.camera.SetFocalPoint(*pivot)
        return self._navigation_mode

    def navigate_drag(self, dx: float, dy: float) -> None:
        if self._navigation_mode is None:
            return
        camera = self.plotter.camera
        if self._navigation_mode == "orbit":
            camera.Azimuth(float(dx) * 0.45)
            camera.Elevation(float(-dy) * 0.45)
            camera.OrthogonalizeViewUp()
        else:
            position = np.asarray(camera.GetPosition(), dtype=float)
            focal = np.asarray(camera.GetFocalPoint(), dtype=float)
            up = np.asarray(camera.GetViewUp(), dtype=float)
            view = focal - position
            view_norm = float(np.linalg.norm(view))
            if view_norm <= 0.0:
                return
            view /= view_norm
            up_norm = float(np.linalg.norm(up))
            if up_norm <= 0.0:
                return
            up /= up_norm
            right = np.cross(view, up)
            right_norm = float(np.linalg.norm(right))
            if right_norm <= 0.0:
                return
            right /= right_norm
            scene_scale = self._scene_reference_span() * 0.0015
            delta = (-float(dx) * right + float(dy) * up) * scene_scale
            camera.SetPosition(*(position + delta))
            camera.SetFocalPoint(*(focal + delta))
        self.plotter.renderer.ResetCameraClippingRange()
        self.plotter.render()

    def end_navigation(self) -> None:
        self._navigation_mode = None
        self._last_mouse_pos = None

    def zoom_by_steps(self, steps: float, anchor: tuple[float, float, float] | None = None) -> None:
        if steps == 0.0:
            return
        camera = self.plotter.camera
        factor = 1.2 ** float(steps)
        if camera.GetParallelProjection():
            camera.SetParallelScale(camera.GetParallelScale() / factor)
        elif anchor is None:
            camera.Dolly(factor)
        else:
            anchor_v: np.ndarray = np.asarray(anchor, dtype=float)
            position = np.asarray(camera.GetPosition(), dtype=float)
            focal = np.asarray(camera.GetFocalPoint(), dtype=float)
            camera.SetPosition(*(anchor_v + (position - anchor_v) / factor))
            camera.SetFocalPoint(*(anchor_v + (focal - anchor_v) / factor))
        self.plotter.renderer.ResetCameraClippingRange()
        self.plotter.render()

    def fit_model(self) -> None:
        if self.scene is None or not len(self.scene.point_keys):
            return
        self.plotter.reset_camera()
        self.plotter.render()

    def focus_selection(self) -> None:
        self.focus_entities(self.selection.selected_nodes, self.selection.selected_members)

    def _scene_reference_span(self) -> float:
        if self.scene is None or not len(self.scene.point_keys):
            return 1.0
        span = np.ptp(self.scene.points, axis=0)
        return max(float(np.max(span)), 1.0)

    def _selection_center(self) -> tuple[float, float, float] | None:
        if self.scene is None:
            return None
        coordinates: list[np.ndarray] = []
        for key in self.selection.selected_nodes:
            index = self.scene.point_index_by_key.get(key)
            if index is not None:
                coordinates.append(self.scene.points[index])
        member_set = set(self.selection.selected_members)
        for index, key in enumerate(self.scene.member_keys):
            if key in member_set:
                row = self.scene.lines[index]
                coordinates.extend((self.scene.points[int(row[1])], self.scene.points[int(row[2])]))
        if not coordinates:
            return None
        center = np.asarray(coordinates, dtype=float).mean(axis=0)
        return (float(center[0]), float(center[1]), float(center[2]))

    def focus_entities(
        self,
        node_keys: Iterable[UUID],
        member_keys: Iterable[UUID],
        location: Vec3 | None = None,
    ) -> None:
        """Fit the camera around selected issue entities without changing the model."""
        if self.scene is None:
            return
        coordinates: list[np.ndarray] = []
        for key in node_keys:
            index = self.scene.point_index_by_key.get(key)
            if index is not None:
                coordinates.append(self.scene.points[index])

        member_set = set(member_keys)
        for index, key in enumerate(self.scene.member_keys):
            if key not in member_set:
                continue
            row = self.scene.lines[index]
            coordinates.append(self.scene.points[int(row[1])])
            coordinates.append(self.scene.points[int(row[2])])

        if location is not None:
            coordinates.append(np.asarray(location.as_tuple(), dtype=float))
        if not coordinates:
            return

        points = np.asarray(coordinates, dtype=float)
        minimum = points.min(axis=0)
        maximum = points.max(axis=0)
        span = maximum - minimum
        reference = max(float(span.max()), 0.1)
        padding = reference * 0.2
        bounds = (
            float(minimum[0] - padding),
            float(maximum[0] + padding),
            float(minimum[1] - padding),
            float(maximum[1] + padding),
            float(minimum[2] - padding),
            float(maximum[2] + padding),
        )
        self.plotter.reset_camera(bounds=bounds)
        self.plotter.render()

    def isolate_entities(self, keys: Iterable[UUID]) -> None:
        """Temporarily hide the base model and display only the selected issue entities."""
        if self.scene is None:
            return
        key_set = set(keys)
        node_keys = tuple(key for key in self.scene.point_keys if key in key_set)
        member_keys = tuple(key for key in self.scene.member_keys if key in key_set)
        self.highlight_nodes(node_keys)
        self.highlight_members(member_keys)
        self._set_actor_visibility(self._node_actor, False)
        self._set_actor_visibility(self._member_actor, False)
        self._set_actor_visibility(self._local_x_actor, False)
        self.focus_entities(node_keys, member_keys)
        self.plotter.render()

    def clear_isolation(self) -> None:
        self._set_actor_visibility(self._node_actor, True)
        self._set_actor_visibility(self._member_actor, True)
        self._set_actor_visibility(self._local_x_actor, self.interaction_state.labels.local_x)
        self.highlight_nodes(())
        self.highlight_members(())
        if self.scene is not None and self.scene.points.size:
            self.plotter.reset_camera()
        self.plotter.render()

    def _pick_candidate_for_actor(
        self,
        actor: Any | None,
        x: float,
        y: float,
        entity: SelectionEntity,
    ) -> SelectionCandidate | None:
        if actor is None or self.scene is None:
            return None
        picker = vtkCellPicker()
        picker.SetTolerance(0.01)
        picker.PickFromListOn()
        picker.AddPickList(actor)
        display_y = float(self.plotter.interactor.height()) - float(y)
        if not picker.Pick(float(x), display_y, 0.0, self.plotter.renderer):
            return None
        cell_id = int(picker.GetCellId())
        if cell_id < 0:
            return None
        if entity is SelectionEntity.NODE:
            if cell_id >= len(self.scene.point_keys):
                return None
            return SelectionCandidate(entity, self.scene.point_keys[cell_id])
        if cell_id >= len(self.scene.member_keys):
            return None
        return SelectionCandidate(entity, self.scene.member_keys[cell_id])

    def _pick_candidates_at(self, x: float, y: float) -> tuple[SelectionCandidate, ...]:
        candidates: list[SelectionCandidate] = []
        node = self._pick_candidate_for_actor(self._node_actor, x, y, SelectionEntity.NODE)
        member = self._pick_candidate_for_actor(self._member_actor, x, y, SelectionEntity.MEMBER)
        if node is not None:
            candidates.append(node)
        if member is not None:
            candidates.append(member)
        return tuple(candidates)

    def _pick_world_at(self, x: float, y: float) -> tuple[float, float, float] | None:
        picker = vtkCellPicker()
        picker.SetTolerance(0.01)
        display_y = float(self.plotter.interactor.height()) - float(y)
        if not picker.Pick(float(x), display_y, 0.0, self.plotter.renderer):
            return None
        position = picker.GetPickPosition()
        return (float(position[0]), float(position[1]), float(position[2]))

    def _show_context_menu(self, global_position: Any) -> None:
        menu = QMenu(self)
        has_nodes = bool(self.selection.selected_nodes)
        has_members = bool(self.selection.selected_members)
        if has_nodes and has_members:
            focus_text = "Focus Selected Entities"
        elif has_nodes:
            focus_text = "Focus Selected Node(s)"
        elif has_members:
            focus_text = "Focus Selected Member(s)"
        else:
            focus_text = "Focus Selected"
        focus_action = menu.addAction(focus_text)
        focus_action.setEnabled(has_nodes or has_members)
        fit_action = menu.addAction("Fit Model")
        clear_action = menu.addAction("Clear Selection")
        clear_action.setEnabled(has_nodes or has_members)
        chosen = menu.exec(global_position)
        if chosen is focus_action:
            self.focus_selection()
        elif chosen is fit_action:
            self.fit_model()
        elif chosen is clear_action:
            self.clear_selection()

    def eventFilter(self, watched: QObject, event: Any) -> bool:  # noqa: N802
        if watched is not self.plotter.interactor:
            return bool(super().eventFilter(watched, event))

        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress:
            position = event.position()
            point = (float(position.x()), float(position.y()))
            if event.button() == Qt.MouseButton.MiddleButton:
                self.begin_navigation(
                    shift=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
                )
                self._last_mouse_pos = point
                return True
            if (
                event.button() == Qt.MouseButton.LeftButton
                and self.interaction_state.mode is EditMode.SELECT
            ):
                self._left_press_pos = point
                return True
            if event.button() == Qt.MouseButton.RightButton:
                self._show_context_menu(event.globalPosition().toPoint())
                return True

        if event_type == QEvent.Type.MouseMove and self._navigation_mode is not None:
            position = event.position()
            point = (float(position.x()), float(position.y()))
            if self._last_mouse_pos is not None:
                self.navigate_drag(
                    point[0] - self._last_mouse_pos[0],
                    point[1] - self._last_mouse_pos[1],
                )
            self._last_mouse_pos = point
            return True

        if (
            event_type == QEvent.Type.MouseMove
            and self.interaction_state.mode is EditMode.SELECT
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            return True

        if event_type == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.MiddleButton and self._navigation_mode is not None:
                self.end_navigation()
                return True
            if (
                event.button() == Qt.MouseButton.LeftButton
                and self.interaction_state.mode is EditMode.SELECT
            ):
                position = event.position()
                point = (float(position.x()), float(position.y()))
                pressed = self._left_press_pos
                self._left_press_pos = None
                if pressed is not None:
                    distance = ((point[0] - pressed[0]) ** 2 + (point[1] - pressed[1]) ** 2) ** 0.5
                    if distance <= 4.0:
                        candidates = self._pick_candidates_at(*point)
                        additive = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
                        if candidates:
                            self.select_overlap_candidates(candidates, additive=additive)
                        elif not additive:
                            self.clear_selection()
                return True

        if event_type == QEvent.Type.MouseButtonDblClick:
            if event.button() == Qt.MouseButton.LeftButton:
                self.focus_selection()
                return True

        if event_type == QEvent.Type.Wheel:
            position = event.position()
            anchor = self._pick_world_at(float(position.x()), float(position.y()))
            steps = float(event.angleDelta().y()) / 120.0
            self.zoom_by_steps(steps, anchor)
            return True

        if event_type == QEvent.Type.KeyPress:
            if (
                event.key() == Qt.Key.Key_Z
                and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            ):
                self.fit_model()
                return True
            if event.key() == Qt.Key.Key_X:
                self.set_axis_lock(AxisLock.X)
                return True
            if event.key() == Qt.Key.Key_Y:
                self.set_axis_lock(AxisLock.Y)
                return True
            if event.key() == Qt.Key.Key_Z:
                self.set_axis_lock(AxisLock.Z)
                return True
            if event.key() == Qt.Key.Key_Escape:
                self.set_axis_lock(AxisLock.NONE)
                return True

        return bool(super().eventFilter(watched, event))

    @staticmethod
    def _set_actor_visibility(actor: Any, visible: bool) -> None:
        if actor is not None:
            actor.SetVisibility(bool(visible))

    def _remove_actor(self, actor: Any) -> None:
        if actor is not None:
            self.plotter.remove_actor(actor, render=False)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.plotter.close()
        super().closeEvent(event)
