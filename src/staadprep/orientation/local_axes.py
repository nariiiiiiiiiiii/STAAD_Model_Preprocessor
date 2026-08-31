from __future__ import annotations

import math
from dataclasses import dataclass

from staadprep.model.entities import Member
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel

_EPS = 1e-12


@dataclass(frozen=True, slots=True)
class MemberLocalAxes:
    """STAAD beta=0 member-local orthonormal basis in canonical Y-up space."""

    x: Vec3
    y: Vec3
    z: Vec3


def _dot(a: Vec3, b: Vec3) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return Vec3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )


def _scale(value: Vec3, factor: float) -> Vec3:
    return Vec3(value.x * factor, value.y * factor, value.z * factor)


def _subtract(a: Vec3, b: Vec3) -> Vec3:
    return Vec3(a.x - b.x, a.y - b.y, a.z - b.z)


def _normalize(value: Vec3) -> Vec3 | None:
    length = math.sqrt(_dot(value, value))
    if length <= _EPS:
        return None
    return _scale(value, 1.0 / length)


def member_local_axes(model: ProjectModel, member: Member) -> MemberLocalAxes | None:
    """Return STAAD beta=0 local axes for one member without mutating the model.

    The canonical project is Y-up. Local X follows start -> end. For a non-vertical
    member, local Y is the projection of +global Y onto the plane normal to local X;
    local Z completes the right-handed basis. For a vertical member, STAAD beta=0
    keeps local Z parallel to +global Z.
    """

    start = model.nodes[member.start].position
    end = model.nodes[member.end].position
    local_x = _normalize(Vec3(end.x - start.x, end.y - start.y, end.z - start.z))
    if local_x is None:
        return None

    global_y = Vec3(0.0, 1.0, 0.0)
    global_z = Vec3(0.0, 0.0, 1.0)
    vertical_alignment = abs(_dot(local_x, global_y))

    if 1.0 - vertical_alignment <= _EPS:
        local_z = global_z
        local_y = _normalize(_cross(local_z, local_x))
        if local_y is None:
            return None
    else:
        projected_y = _subtract(global_y, _scale(local_x, _dot(global_y, local_x)))
        local_y = _normalize(projected_y)
        if local_y is None:
            return None
        local_z_candidate = _normalize(_cross(local_x, local_y))
        if local_z_candidate is None:
            return None
        local_z = local_z_candidate

    return MemberLocalAxes(x=local_x, y=local_y, z=local_z)
