"""Selection state shared by viewport picking and programmatic highlighting."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class SelectionState:
    selected_nodes: tuple[UUID, ...] = ()
    selected_members: tuple[UUID, ...] = ()

    def set_nodes(self, keys: tuple[UUID, ...]) -> None:
        self.selected_nodes = keys

    def set_members(self, keys: tuple[UUID, ...]) -> None:
        self.selected_members = keys

    def clear(self) -> None:
        self.selected_nodes = ()
        self.selected_members = ()
