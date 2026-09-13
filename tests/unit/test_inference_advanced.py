from __future__ import annotations

from uuid import UUID

from staadprep.editing.inference import AxisLock, InferenceEngine, SnapKind
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_two_crossing_members_return_exact_3d_intersection() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, -2.0, 0.0)),
        _key(4): Node(_key(4), Vec3(0.0, 2.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)

    hit = InferenceEngine.resolve(
        model,
        Vec3(0.001, -0.001, 0.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is not None
    assert hit.kind is SnapKind.INTERSECTION
    assert hit.position == Vec3(0.0, 0.0, 0.0)
    assert hit.entity_keys == (_key(101), _key(102))


def test_skew_segments_do_not_fabricate_intersection() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, -2.0, 1.0)),
        _key(4): Node(_key(4), Vec3(0.0, 2.0, 1.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)

    hit = InferenceEngine.resolve(
        model,
        Vec3(0.0, 0.0, 0.5),
        tolerance_m=0.1,
        axis_lock=AxisLock.NONE,
    )

    assert hit is None


def test_parallel_segments_do_not_fabricate_intersection() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(-2.0, 1.0, 0.0)),
        _key(4): Node(_key(4), Vec3(2.0, 1.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)

    hit = InferenceEngine.resolve(
        model,
        Vec3(0.0, 0.5, 0.0),
        tolerance_m=0.1,
        axis_lock=AxisLock.NONE,
    )

    assert hit is None


def test_work_plane_requires_explicit_forward_ray_plane_intersection() -> None:
    hit = InferenceEngine.resolve_work_plane(
        ray_origin=Vec3(1.0, 2.0, 10.0),
        ray_direction=Vec3(0.0, 0.0, -1.0),
        plane_origin=Vec3(0.0, 0.0, 4.0),
        plane_normal=Vec3(0.0, 0.0, 1.0),
    )

    assert hit is not None
    assert hit.kind is SnapKind.WORK_PLANE
    assert hit.position == Vec3(1.0, 2.0, 4.0)
    assert hit.label == "WORK PLANE"


def test_unresolved_parallel_work_plane_ray_returns_none() -> None:
    hit = InferenceEngine.resolve_work_plane(
        ray_origin=Vec3(1.0, 2.0, 10.0),
        ray_direction=Vec3(1.0, 0.0, 0.0),
        plane_origin=Vec3(0.0, 0.0, 4.0),
        plane_normal=Vec3(0.0, 0.0, 1.0),
    )

    assert hit is None
