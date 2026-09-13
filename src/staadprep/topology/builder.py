"""Build canonical structural topology from metre/Y-Up raw geometry."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor, isfinite
from uuid import UUID

from staadprep.importers.contracts import ImportBatch
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel


@dataclass(frozen=True, slots=True)
class TopologyPolicy:
    coincident_tolerance_m: float = 1e-9

    def __post_init__(self) -> None:
        if not isfinite(self.coincident_tolerance_m) or self.coincident_tolerance_m <= 0.0:
            raise ValueError("coincident_tolerance_m must be finite and positive")


class _NodeRegistry:
    def __init__(self, tolerance_m: float) -> None:
        self._tolerance_m = tolerance_m
        self._tolerance_sq = tolerance_m * tolerance_m
        self.nodes: dict[UUID, Node] = {}
        self._buckets: dict[tuple[int, int, int], list[UUID]] = {}
        self._order: dict[UUID, int] = {}

    def _bucket(self, point: Vec3) -> tuple[int, int, int]:
        size = self._tolerance_m
        return (
            floor(point.x / size),
            floor(point.y / size),
            floor(point.z / size),
        )

    @staticmethod
    def _distance_sq(a: Vec3, b: Vec3) -> float:
        dx = a.x - b.x
        dy = a.y - b.y
        dz = a.z - b.z
        return dx * dx + dy * dy + dz * dz

    def _candidate_keys(self, point: Vec3) -> list[UUID]:
        bx, by, bz = self._bucket(point)
        result: list[UUID] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    result.extend(self._buckets.get((bx + dx, by + dy, bz + dz), ()))
        return result

    def get_or_create(self, point: Vec3, source_ref: str | None) -> UUID:
        candidates: list[tuple[float, int, UUID]] = []
        for key in self._candidate_keys(point):
            distance_sq = self._distance_sq(point, self.nodes[key].position)
            if distance_sq <= self._tolerance_sq:
                candidates.append((distance_sq, self._order[key], key))

        if candidates:
            _, _, key = min(candidates)
            node = self.nodes[key]
            if source_ref is not None and source_ref not in node.source_refs:
                node.source_refs = (*node.source_refs, source_ref)
            return key

        refs = () if source_ref is None else (source_ref,)
        node = Node.new(point, source_refs=refs)
        self.nodes[node.key] = node
        self._order[node.key] = len(self._order)
        self._buckets.setdefault(self._bucket(point), []).append(node.key)
        return node.key


def _require_canonical_batch(batch: ImportBatch) -> None:
    coordinate_unit = batch.metadata.get("coordinate_unit", batch.declared_unit)
    coordinate_axis = batch.metadata.get("coordinate_axis")
    if coordinate_axis is None and batch.source_axis == "Y-UP":
        coordinate_axis = "Y-UP"
    if coordinate_unit != "m":
        raise ValueError("Topology builder requires canonical metre coordinates")
    if coordinate_axis != "Y-UP":
        raise ValueError("Topology builder requires canonical Y-UP coordinates")


def build_project(batch: ImportBatch, policy: TopologyPolicy) -> ProjectModel:
    """Build Node/Member incidence without repair or near-node snapping."""
    _require_canonical_batch(batch)
    registry = _NodeRegistry(policy.coincident_tolerance_m)
    members: dict[UUID, Member] = {}

    for point in batch.points:
        registry.get_or_create(point.position, point.source_ref)

    for segment in batch.segments:
        start_key = registry.get_or_create(segment.start, segment.source_ref)
        end_key = registry.get_or_create(segment.end, segment.source_ref)
        member = Member.new(
            start_key,
            end_key,
            source_ref=segment.source_ref,
            group=segment.layer,
        )
        members[member.key] = member

    source_file_value = batch.metadata.get("source_file")
    metadata = ModelMetadata(
        source_format=batch.source_format or None,
        source_file=None if source_file_value is None else str(source_file_value),
        source_unit=str(batch.metadata.get("source_unit", batch.declared_unit)),
        source_axis=str(batch.metadata.get("source_axis", batch.source_axis)),
    )
    return ProjectModel(nodes=registry.nodes, members=members, metadata=metadata)
