"""Immutable viewport interaction state for safe analytical editing workflows."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EditMode(StrEnum):
    SELECT = "SELECT"
    CREATE_NODE = "CREATE_NODE"
    DRAW_MEMBER = "DRAW_MEMBER"
    MOVE_SNAP_NODE = "MOVE_SNAP_NODE"
    DELETE = "DELETE"
    MEASURE = "MEASURE"
    SET_DIRECTION = "SET_DIRECTION"


@dataclass(frozen=True, slots=True)
class SelectionFilter:
    nodes: bool = True
    members: bool = True


@dataclass(frozen=True, slots=True)
class LabelVisibility:
    node_numbers: bool = False
    member_numbers: bool = False
    local_x: bool = False
    coordinates: bool = False


@dataclass(frozen=True, slots=True)
class InteractionState:
    mode: EditMode = EditMode.SELECT
    selection_filter: SelectionFilter = SelectionFilter()
    labels: LabelVisibility = LabelVisibility()

    @property
    def allows_geometry_drag(self) -> bool:
        return self.mode is EditMode.MOVE_SNAP_NODE
