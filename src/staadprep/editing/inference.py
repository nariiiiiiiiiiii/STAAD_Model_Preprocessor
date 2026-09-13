"""Deterministic canonical-space structural inference primitives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import sqrt
from uuid import UUID

from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


class SnapKind(StrEnum):
    NODE = "NODE"
    ENDPOINT = "ENDPOINT"
    MIDPOINT = "MIDPOINT"
    INTERSECTION = "INTERSECTION"
    AXIS_X = "AXIS_X"
    AXIS_Y = "AXIS_Y"
    AXIS_Z = "AXIS_Z"
    WORK_PLANE = "WORK_PLANE"


class AxisLock(StrEnum):
    NONE = "NONE"
    X = "X"
    Y = "Y"
    Z = "Z"


@dataclass(frozen=True, slots=True)
class InferenceHit:
    position: Vec3
    kind: SnapKind
    entity_keys: tuple[UUID, ...]
    label: str


@dataclass(frozen=True, slots=True)
class _Candidate:
    distance_sq: float
    kind_priority: int
    tie_keys: tuple[int, ...]
    hit: InferenceHit


def _distance_sq(a: Vec3, b: Vec3) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return dx * dx + dy * dy + dz * dz


def _midpoint(a: Vec3, b: Vec3) -> Vec3:
    return Vec3((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, (a.z + b.z) * 0.5)


def _sub(a: Vec3, b: Vec3) -> tuple[float, float, float]:
    return (a.x - b.x, a.y - b.y, a.z - b.z)


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm_sq(value: tuple[float, float, float]) -> float:
    return _dot(value, value)


def _point_on_segment(start: Vec3, direction: tuple[float, float, float], t: float) -> Vec3:
    return Vec3(
        start.x + direction[0] * t,
        start.y + direction[1] * t,
        start.z + direction[2] * t,
    )


def _segment_intersection(start_a: Vec3, end_a: Vec3, start_b: Vec3, end_b: Vec3) -> Vec3 | None:
    """Return an exact 3D segment intersection; near/skew segments are not intersections."""
    u = _sub(end_a, start_a)
    v = _sub(end_b, start_b)
    uu = _norm_sq(u)
    vv = _norm_sq(v)
    if uu == 0.0 or vv == 0.0:
        return None

    uv_cross = _cross(u, v)
    denom = _norm_sq(uv_cross)
    scale_sq = max(uu * vv, 1.0)
    parallel_threshold = 1e-24 * scale_sq
    if denom <= parallel_threshold:
        return None

    w = _sub(start_b, start_a)
    s = _dot(_cross(w, v), uv_cross) / denom
    t = _dot(_cross(w, u), uv_cross) / denom
    parameter_epsilon = 1e-12
    if not (-parameter_epsilon <= s <= 1.0 + parameter_epsilon):
        return None
    if not (-parameter_epsilon <= t <= 1.0 + parameter_epsilon):
        return None

    point_a = _point_on_segment(start_a, u, min(max(s, 0.0), 1.0))
    point_b = _point_on_segment(start_b, v, min(max(t, 0.0), 1.0))
    length_scale = max(sqrt(uu), sqrt(vv), 1.0)
    geometric_epsilon = 1e-9 * length_scale
    if _distance_sq(point_a, point_b) > geometric_epsilon * geometric_epsilon:
        return None
    return _midpoint(point_a, point_b)


class InferenceEngine:
    """Resolve deterministic snaps without mutating the canonical model."""

    _PRIORITY = {
        SnapKind.ENDPOINT: 0,
        SnapKind.NODE: 1,
        SnapKind.INTERSECTION: 2,
        SnapKind.MIDPOINT: 3,
    }

    @classmethod
    def resolve(
        cls,
        model: ProjectModel,
        candidate_position: Vec3,
        *,
        tolerance_m: float,
        axis_lock: AxisLock,
        reference_position: Vec3 | None = None,
    ) -> InferenceHit | None:
        if tolerance_m < 0.0:
            raise ValueError("tolerance_m must be non-negative")

        if axis_lock is not AxisLock.NONE:
            return cls._resolve_axis_lock(candidate_position, axis_lock, reference_position)

        tolerance_sq = tolerance_m * tolerance_m
        candidates: list[_Candidate] = []
        endpoint_nodes: set[UUID] = set()

        for member_key in sorted(model.members, key=lambda key: key.int):
            member = model.members[member_key]
            for node_key in (member.start, member.end):
                node = model.nodes.get(node_key)
                if node is None:
                    continue
                endpoint_nodes.add(node_key)
                cls._append_candidate(
                    candidates,
                    candidate_position,
                    tolerance_sq,
                    InferenceHit(
                        position=node.position,
                        kind=SnapKind.ENDPOINT,
                        entity_keys=(node_key, member_key),
                        label="ENDPOINT",
                    ),
                )

        for node_key in sorted(model.nodes, key=lambda key: key.int):
            if node_key in endpoint_nodes:
                continue
            node = model.nodes[node_key]
            cls._append_candidate(
                candidates,
                candidate_position,
                tolerance_sq,
                InferenceHit(
                    position=node.position,
                    kind=SnapKind.NODE,
                    entity_keys=(node_key,),
                    label="NODE",
                ),
            )

        member_keys = sorted(model.members, key=lambda key: key.int)
        for first_index, first_key in enumerate(member_keys):
            first = model.members[first_key]
            first_start = model.nodes.get(first.start)
            first_end = model.nodes.get(first.end)
            if first_start is None or first_end is None:
                continue
            for second_key in member_keys[first_index + 1 :]:
                second = model.members[second_key]
                second_start = model.nodes.get(second.start)
                second_end = model.nodes.get(second.end)
                if second_start is None or second_end is None:
                    continue
                position = _segment_intersection(
                    first_start.position,
                    first_end.position,
                    second_start.position,
                    second_end.position,
                )
                if position is None:
                    continue
                cls._append_candidate(
                    candidates,
                    candidate_position,
                    tolerance_sq,
                    InferenceHit(
                        position=position,
                        kind=SnapKind.INTERSECTION,
                        entity_keys=(first_key, second_key),
                        label="INTERSECTION",
                    ),
                )

        for member_key in member_keys:
            member = model.members[member_key]
            start = model.nodes.get(member.start)
            end = model.nodes.get(member.end)
            if start is None or end is None:
                continue
            cls._append_candidate(
                candidates,
                candidate_position,
                tolerance_sq,
                InferenceHit(
                    position=_midpoint(start.position, end.position),
                    kind=SnapKind.MIDPOINT,
                    entity_keys=(member_key,),
                    label="MIDPOINT",
                ),
            )

        if not candidates:
            return None
        best = min(
            candidates,
            key=lambda item: (item.distance_sq, item.kind_priority, item.tie_keys),
        )
        return best.hit

    @classmethod
    def _append_candidate(
        cls,
        candidates: list[_Candidate],
        candidate_position: Vec3,
        tolerance_sq: float,
        hit: InferenceHit,
    ) -> None:
        distance_sq = _distance_sq(candidate_position, hit.position)
        if distance_sq > tolerance_sq:
            return
        candidates.append(
            _Candidate(
                distance_sq=distance_sq,
                kind_priority=cls._PRIORITY[hit.kind],
                tie_keys=tuple(key.int for key in hit.entity_keys),
                hit=hit,
            )
        )

    @staticmethod
    def _resolve_axis_lock(
        candidate_position: Vec3,
        axis_lock: AxisLock,
        reference_position: Vec3 | None,
    ) -> InferenceHit | None:
        if reference_position is None:
            return None
        if axis_lock is AxisLock.X:
            position = Vec3(candidate_position.x, reference_position.y, reference_position.z)
            return InferenceHit(position, SnapKind.AXIS_X, (), "X AXIS")
        if axis_lock is AxisLock.Y:
            position = Vec3(reference_position.x, candidate_position.y, reference_position.z)
            return InferenceHit(position, SnapKind.AXIS_Y, (), "Y AXIS")
        if axis_lock is AxisLock.Z:
            position = Vec3(reference_position.x, reference_position.y, candidate_position.z)
            return InferenceHit(position, SnapKind.AXIS_Z, (), "Z AXIS")
        return None

    @staticmethod
    def axis_helper_text(axis_lock: AxisLock) -> str:
        if axis_lock is AxisLock.Y:
            return "Y AXIS — Vertical"
        if axis_lock is AxisLock.X:
            return "X AXIS"
        if axis_lock is AxisLock.Z:
            return "Z AXIS"
        return ""

    @staticmethod
    def resolve_work_plane(
        *,
        ray_origin: Vec3,
        ray_direction: Vec3,
        plane_origin: Vec3,
        plane_normal: Vec3,
    ) -> InferenceHit | None:
        direction = ray_direction.as_tuple()
        normal = plane_normal.as_tuple()
        denominator = _dot(direction, normal)
        direction_length_sq = _norm_sq(direction)
        normal_length_sq = _norm_sq(normal)
        if direction_length_sq == 0.0 or normal_length_sq == 0.0:
            return None
        parallel_limit = 1e-12 * sqrt(direction_length_sq * normal_length_sq)
        if abs(denominator) <= parallel_limit:
            return None

        origin_to_plane = _sub(plane_origin, ray_origin)
        parameter = _dot(origin_to_plane, normal) / denominator
        if parameter < 0.0:
            return None
        position = _point_on_segment(ray_origin, direction, parameter)
        return InferenceHit(position, SnapKind.WORK_PLANE, (), "WORK PLANE")
