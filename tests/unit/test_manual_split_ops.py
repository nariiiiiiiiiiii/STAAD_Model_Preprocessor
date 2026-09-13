from __future__ import annotations

from copy import deepcopy
from uuid import UUID

import pytest

from staadprep.editing.manual_ops import (
    build_split_member_distance,
    build_split_member_midpoint,
    build_split_member_percentage,
    build_split_selected_intersection,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _line_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(10.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )


def _crossing_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, -2.0, 0.0)),
            _key(4): Node(_key(4), Vec3(0.0, 2.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(3), _key(4)),
        },
    )


def test_split_midpoint_and_precision_factories_use_exact_member_geometry() -> None:
    model = _line_model()
    midpoint = build_split_member_midpoint(model, _key(101))
    percentage = build_split_member_percentage(model, _key(101), 25.0)
    distance = build_split_member_distance(model, _key(101), 3.0)

    assert midpoint.position == Vec3(5.0, 0.0, 0.0)
    assert percentage.position == Vec3(2.5, 0.0, 0.0)
    assert distance.position == Vec3(3.0, 0.0, 0.0)
    assert model.revision == 0


@pytest.mark.parametrize("percentage", [0.0, 100.0, -1.0, 101.0, float("nan")])
def test_split_percentage_rejects_endpoints_invalid_or_nonfinite(percentage: float) -> None:
    model = _line_model()
    with pytest.raises(ValueError):
        build_split_member_percentage(model, _key(101), percentage)
    assert model.revision == 0


@pytest.mark.parametrize("distance", [0.0, 10.0, -1.0, 11.0, float("inf")])
def test_split_distance_rejects_endpoints_invalid_or_nonfinite(distance: float) -> None:
    model = _line_model()
    with pytest.raises(ValueError):
        build_split_member_distance(model, _key(101), distance)
    assert model.revision == 0


def test_split_selected_intersection_is_atomic_and_one_undo_restores_graph() -> None:
    model = _crossing_model()
    before = deepcopy(model)
    command = build_split_selected_intersection(model, _key(101), _key(102))
    assert isinstance(command, CompositeRepair)
    history = RepairHistory(model)

    history.execute(command)
    intersection_nodes = [
        node for node in model.nodes.values() if node.position == Vec3(0.0, 0.0, 0.0)
    ]
    assert len(intersection_nodes) == 1
    assert len(model.members) == 4
    assert len(history.undo_stack) == 1

    history.undo()
    assert model == before
