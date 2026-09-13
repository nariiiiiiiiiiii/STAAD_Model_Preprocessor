from __future__ import annotations

from uuid import UUID

from staadprep.editing.inference import AxisLock, InferenceEngine, SnapKind
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_hand_calculated_3d_diagonals_intersect_at_three_three_three_without_mutation() -> None:
    # Line A: P(t) = (0,0,0) + t(6,6,6)
    # Line B: Q(u) = (0,6,6) + u(6,-6,-6)
    # Solving P(t) = Q(u) gives t = u = 0.5 -> (3,3,3).
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(6.0, 6.0, 6.0)),
        _key(3): Node(_key(3), Vec3(0.0, 6.0, 6.0)),
        _key(4): Node(_key(4), Vec3(6.0, 0.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)
    initial_revision = model.revision

    hit = InferenceEngine.resolve(
        model,
        Vec3(3.001, 2.999, 3.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.NONE,
    )

    assert hit is not None
    assert hit.kind is SnapKind.INTERSECTION
    assert hit.position == Vec3(3.0, 3.0, 3.0)
    assert hit.entity_keys == (_key(101), _key(102))
    assert model.revision == initial_revision
