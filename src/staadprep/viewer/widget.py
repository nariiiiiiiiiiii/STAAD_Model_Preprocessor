"""Qt/PyVista structural viewport for canonical analytical models."""

from __future__ import annotations

import os
from collections.abc import Iterable
from uuid import UUID

import numpy as np
import pyvista as pv
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
from pyvistaqt import QtInteractor

from staadprep.model.project import ProjectModel
from staadprep.viewer.scene import SceneData
from staadprep.viewer.selection import SelectionState


class StructuralViewport(QWidget):
    """Interactive 3D view with stable member/node highlight mappings."""

    member_selected = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("viewport_host")
        self.setMinimumSize(480, 360)

        self.scene: SceneData | None = None
        self.selection = SelectionState()
        self._member_actor = None
        self._node_actor = None
        self._member_highlight_actor = None
        self._node_highlight_actor = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._off_screen = os.getenv("QT_QPA_PLATFORM", "").lower() == "offscreen"
        self.plotter = QtInteractor(self, off_screen=self._off_screen)
        layout.addWidget(self.plotter.interactor)
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
        self.scene = SceneData.from_model(model)
        self.selection.clear()
        self.plotter.clear()
        self._configure_scene()
        self._member_highlight_actor = None
        self._node_highlight_actor = None

        if self.scene.points.size == 0:
            self.plotter.render()
            return

        point_cloud = pv.PolyData(self.scene.points)
        self._node_actor = self.plotter.add_mesh(
            point_cloud,
            color="#6fcf97",
            point_size=8,
            render_points_as_spheres=True,
            style="points",
            pickable=False,
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
            if not self._off_screen:
                self.plotter.enable_cell_picking(
                    callback=self._on_cells_picked,
                    through=False,
                    show=False,
                    show_message=False,
                    start=False,
                )

        self.plotter.reset_camera()
        self.plotter.render()

    def _on_cells_picked(self, picked) -> None:
        blocks = picked if isinstance(picked, pv.MultiBlock) else (picked,)
        for block in blocks:
            if block is None or getattr(block, "n_cells", 0) == 0:
                continue
            if "member_index" not in block.cell_data:
                continue
            member_index = int(np.asarray(block.cell_data["member_index"])[0])
            self.select_member_by_cell(member_index)
            return

    def select_member_by_cell(self, cell_index: int) -> UUID:
        if self.scene is None:
            raise RuntimeError("No model is loaded")
        member_key = self.scene.member_key_for_cell(cell_index)
        self.highlight_members((member_key,))
        self.member_selected.emit(member_key)
        return member_key

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

    def _remove_actor(self, actor) -> None:
        if actor is not None:
            self.plotter.remove_actor(actor, render=False)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.plotter.close()
        super().closeEvent(event)
