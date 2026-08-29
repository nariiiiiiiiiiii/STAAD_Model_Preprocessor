from __future__ import annotations

from uuid import UUID

from staadprep.editing.inference import AxisLock, InferenceEngine, SnapKind
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(10.0, 3.0, 2.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
    }
    return ProjectModel(nodes=nodes, members=members)


def test_standalone_node_within_tolerance_snaps_to_exact_node_coordinate() -> None:
    model = _model()
    revision = model.revision

    hit = InferenceEngine.resolve(
        model,
        Vec3(10.004, 3.0, 2.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is not None
    assert hit.kind is SnapKind.NODE
    assert hit.position == Vec3(10.0, 3.0, 2.0)
    assert hit.entity_keys == (_key(3),)
    assert model.revision == revision


def test_member_endpoint_is_reachable_and_wins_same_coordinate_node_candidate() -> None:
    model = _model()

    hit = InferenceEngine.resolve(
        model,
        Vec3(4.003, 0.0, 0.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is not None
    assert hit.kind is SnapKind.ENDPOINT
    assert hit.position == Vec3(4.0, 0.0, 0.0)
    assert hit.entity_keys == (_key(2), _key(101))


def test_member_midpoint_hit_returns_exact_hand_calculated_midpoint() -> None:
    model = _model()

    hit = InferenceEngine.resolve(
        model,
        Vec3(2.002, 0.0, 0.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is not None
    assert hit.kind is SnapKind.MIDPOINT
    assert hit.position == Vec3(2.0, 0.0, 0.0)
    assert hit.entity_keys == (_key(101),)


def test_outside_tolerance_does_not_fabricate_snap() -> None:
    hit = InferenceEngine.resolve(
        _model(),
        Vec3(2.1, 0.0, 0.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is None


def test_equal_distance_midpoints_tie_break_by_stable_member_uuid() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(-2.0, -1.0, 0.0)),
        _key(2): Node(_key(2), Vec3(2.0, -1.0, 0.0)),
        _key(3): Node(_key(3), Vec3(-2.0, 1.0, 0.0)),
        _key(4): Node(_key(4), Vec3(2.0, 1.0, 0.0)),
    }
    members = {
        _key(202): Member(_key(202), _key(1), _key(2)),
        _key(201): Member(_key(201), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)

    hit = InferenceEngine.resolve(
        model,
        Vec3(0.0, 0.0, 0.0),
        tolerance_m=1.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is not None
    assert hit.kind is SnapKind.MIDPOINT
    assert hit.entity_keys == (_key(201),)
