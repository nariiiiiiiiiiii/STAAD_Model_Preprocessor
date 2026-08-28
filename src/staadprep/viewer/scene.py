"""Deterministic render-scene arrays derived from the canonical model."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import numpy as np

from staadprep.model.project import ProjectModel


@dataclass(slots=True)
class SceneData:
    points: np.ndarray
    lines: np.ndarray
    point_keys: tuple[UUID, ...]
    member_keys: tuple[UUID, ...]
    point_index_by_key: dict[UUID, int]

    @classmethod
    def from_model(cls, model: ProjectModel) -> SceneData:
        point_keys = tuple(sorted(model.nodes, key=str))
        point_index_by_key = {key: index for index, key in enumerate(point_keys)}
        if point_keys:
            points = np.array(
                [model.nodes[key].position.as_tuple() for key in point_keys],
                dtype=float,
            )
        else:
            points = np.empty((0, 3), dtype=float)

        member_keys = tuple(sorted(model.members, key=str))
        line_rows: list[tuple[int, int, int]] = []
        for member_key in member_keys:
            member = model.members[member_key]
            try:
                start_index = point_index_by_key[member.start]
                end_index = point_index_by_key[member.end]
            except KeyError as exc:
                raise ValueError(
                    f"Member {member.key} references missing node {exc.args[0]}"
                ) from exc
            line_rows.append((2, start_index, end_index))

        lines = (
            np.array(line_rows, dtype=np.int64)
            if line_rows
            else np.empty((0, 3), dtype=np.int64)
        )
        return cls(
            points=points,
            lines=lines,
            point_keys=point_keys,
            member_keys=member_keys,
            point_index_by_key=point_index_by_key,
        )

    def member_key_for_cell(self, cell_index: int) -> UUID:
        return self.member_keys[cell_index]
