from __future__ import annotations

import math
from uuid import UUID

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.local_axes import member_local_axes


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model(end: Vec3) -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), end),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )


def _dot(a: Vec3, b: Vec3) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return Vec3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )


def _norm(a: Vec3) -> float:
    return math.sqrt(_dot(a, a))


def test_beta_zero_beam_x_matches_staad_y_up_basis() -> None:
    model = _model(Vec3(4.0, 0.0, 0.0))

    axes = member_local_axes(model, model.members[_key(101)])

    assert axes.x == Vec3(1.0, 0.0, 0.0)
    assert axes.y == Vec3(0.0, 1.0, 0.0)
    assert axes.z == Vec3(0.0, 0.0, 1.0)


def test_beta_zero_vertical_member_keeps_local_z_positive_global_z() -> None:
    model = _model(Vec3(0.0, 4.0, 0.0))

    axes = member_local_axes(model, model.members[_key(101)])

    assert axes.x == Vec3(0.0, 1.0, 0.0)
    assert axes.y == Vec3(-1.0, 0.0, 0.0)
    assert axes.z == Vec3(0.0, 0.0, 1.0)


def test_brace_basis_is_orthonormal_right_handed_and_local_y_points_upward() -> None:
    model = _model(Vec3(3.0, 4.0, 5.0))

    axes = member_local_axes(model, model.members[_key(101)])

    assert math.isclose(_norm(axes.x), 1.0, abs_tol=1e-12)
    assert math.isclose(_norm(axes.y), 1.0, abs_tol=1e-12)
    assert math.isclose(_norm(axes.z), 1.0, abs_tol=1e-12)
    assert math.isclose(_dot(axes.x, axes.y), 0.0, abs_tol=1e-12)
    assert math.isclose(_dot(axes.x, axes.z), 0.0, abs_tol=1e-12)
    assert math.isclose(_dot(axes.y, axes.z), 0.0, abs_tol=1e-12)
    cross = _cross(axes.x, axes.y)
    assert math.isclose(cross.x, axes.z.x, abs_tol=1e-12)
    assert math.isclose(cross.y, axes.z.y, abs_tol=1e-12)
    assert math.isclose(cross.z, axes.z.z, abs_tol=1e-12)
    assert axes.y.y > 0.0


def test_reversing_member_reverses_local_x_without_mutating_model() -> None:
    model = _model(Vec3(4.0, 0.0, 0.0))
    member = model.members[_key(101)]
    before_revision = model.revision
    forward = member_local_axes(model, member)
    reversed_member = Member(member.key, member.end, member.start)

    reverse = member_local_axes(model, reversed_member)

    assert reverse.x == Vec3(-forward.x.x, -forward.x.y, -forward.x.z)
    assert model.revision == before_revision


def test_zero_length_member_has_no_local_axis_basis() -> None:
    model = _model(Vec3(0.0, 0.0, 0.0))

    assert member_local_axes(model, model.members[_key(101)]) is None
