"""Pure specifications and command factories for precise Node creation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import dist, isfinite
from uuid import UUID, uuid4

from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import ConnectNodes, CreateNode, RepairCommand
from staadprep.repair.composite import CompositeRepair


@dataclass(frozen=True, slots=True)
class ExactNodeSpec:
    x: float
    y: float
    z: float


@dataclass(frozen=True, slots=True)
class RelativeNodeSpec:
    reference_node: UUID
    dx: float
    dy: float
    dz: float
    create_member: bool


@dataclass(frozen=True, slots=True)
class ExistingNodeCollision:
    node_key: UUID
    position: Vec3


class RepeatConnectionMode(StrEnum):
    NONE = "none"
    CONSECUTIVE = "consecutive"
    FROM_REFERENCE = "from_reference"


class ExistingNodeResolution(StrEnum):
    USE_EXISTING = "use_existing"
    SKIP_STEP = "skip_step"
    CANCEL = "cancel"


@dataclass(frozen=True, slots=True)
class TranslationalRepeatSpec:
    reference_node: UUID
    dx: float
    dy: float
    dz: float
    repeats: int
    connection_mode: RepeatConnectionMode


@dataclass(frozen=True, slots=True)
class RepeatStepPreview:
    index: int
    position: Vec3
    existing_node: UUID | None = None


@dataclass(frozen=True, slots=True)
class TranslationalRepeatPreview:
    steps: tuple[RepeatStepPreview, ...]
    new_node_count: int
    new_member_count: int
    reused_node_count: int
    skipped_count: int
    final_coordinate: Vec3
    collisions: dict[int, UUID]


@dataclass(frozen=True, slots=True)
class RepeatResolutionRequired:
    collisions: dict[int, UUID]


type CreateNodeBuildResult = RepairCommand | ExistingNodeCollision
type RepeatBuildResult = CompositeRepair | RepeatResolutionRequired | None


def _validate_tolerance(tolerance_m: float) -> float:
    tolerance = float(tolerance_m)
    if not isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("Node collision tolerance must be finite and non-negative")
    return tolerance


def _finite_vec3(x: float, y: float, z: float) -> Vec3:
    values = (float(x), float(y), float(z))
    if not all(isfinite(value) for value in values):
        raise ValueError("Node coordinates must be finite")
    return Vec3(*values)


def exact_position(spec: ExactNodeSpec) -> Vec3:
    return _finite_vec3(spec.x, spec.y, spec.z)


def relative_position(model: ProjectModel, spec: RelativeNodeSpec) -> Vec3:
    try:
        reference = model.nodes[spec.reference_node]
    except KeyError as exc:
        raise ValueError(f"Reference node {spec.reference_node} does not exist") from exc
    offset = _finite_vec3(spec.dx, spec.dy, spec.dz)
    return Vec3(
        reference.position.x + offset.x,
        reference.position.y + offset.y,
        reference.position.z + offset.z,
    )


def _find_collision(
    model: ProjectModel,
    target: Vec3,
    tolerance_m: float,
) -> ExistingNodeCollision | None:
    tolerance = _validate_tolerance(tolerance_m)
    candidates: list[tuple[float, UUID, Vec3]] = []
    for key, node in model.nodes.items():
        distance = dist(node.position.as_tuple(), target.as_tuple())
        if distance <= tolerance:
            candidates.append((distance, key, node.position))
    if not candidates:
        return None
    _, key, position = min(candidates, key=lambda item: (item[0], item[1].int))
    return ExistingNodeCollision(key, position)


def build_exact_create(
    model: ProjectModel,
    spec: ExactNodeSpec,
    tolerance_m: float,
) -> CreateNodeBuildResult:
    target = exact_position(spec)
    collision = _find_collision(model, target, tolerance_m)
    if collision is not None:
        return collision
    return CreateNode(target)


def build_relative_create(
    model: ProjectModel,
    spec: RelativeNodeSpec,
    tolerance_m: float,
) -> CreateNodeBuildResult:
    offset = _finite_vec3(spec.dx, spec.dy, spec.dz)
    if offset == Vec3(0.0, 0.0, 0.0):
        raise ValueError("zero relative offset would duplicate the reference node")
    target = relative_position(model, spec)
    collision = _find_collision(model, target, tolerance_m)
    if collision is not None:
        return collision
    if not spec.create_member:
        return CreateNode(target)

    new_key = uuid4()
    return CompositeRepair(
        (
            CreateNode(target, node_key=new_key),
            ConnectNodes(spec.reference_node, new_key),
        ),
        label="relative create node and member",
    )


def _repeat_positions(
    model: ProjectModel,
    spec: TranslationalRepeatSpec,
) -> tuple[Vec3, ...]:
    try:
        reference = model.nodes[spec.reference_node]
    except KeyError as exc:
        raise ValueError(f"Reference node {spec.reference_node} does not exist") from exc
    delta = _finite_vec3(spec.dx, spec.dy, spec.dz)
    if delta == Vec3(0.0, 0.0, 0.0):
        raise ValueError("Translational Repeat step vector must not be zero")
    if isinstance(spec.repeats, bool) or not isinstance(spec.repeats, int) or spec.repeats < 1:
        raise ValueError("Translational Repeat count must be a positive integer")
    if not isinstance(spec.connection_mode, RepeatConnectionMode):
        raise ValueError("Invalid Translational Repeat connection mode")
    start = reference.position
    return tuple(
        Vec3(
            start.x + spec.dx * step,
            start.y + spec.dy * step,
            start.z + spec.dz * step,
        )
        for step in range(1, spec.repeats + 1)
    )


def analyze_translational_repeat(
    model: ProjectModel,
    spec: TranslationalRepeatSpec,
    tolerance_m: float,
    resolutions: Mapping[int, ExistingNodeResolution] | None = None,
) -> TranslationalRepeatPreview:
    positions = _repeat_positions(model, spec)
    resolution_map = resolutions or {}
    steps: list[RepeatStepPreview] = []
    collisions: dict[int, UUID] = {}
    new_nodes = 0
    new_members = 0
    reused = 0
    skipped = 0
    previous_existing_key: UUID | None = spec.reference_node

    for index, position in enumerate(positions, start=1):
        collision = _find_collision(model, position, tolerance_m)
        existing = collision.node_key if collision is not None else None
        steps.append(RepeatStepPreview(index, position, existing))

        current_existing_key: UUID | None
        if collision is None:
            new_nodes += 1
            current_existing_key = None
        else:
            collisions[index] = collision.node_key
            resolution = resolution_map.get(index)
            if resolution is ExistingNodeResolution.USE_EXISTING:
                reused += 1
                current_existing_key = collision.node_key
            elif resolution is ExistingNodeResolution.SKIP_STEP:
                skipped += 1
                continue
            else:
                continue

        if spec.connection_mode is not RepeatConnectionMode.NONE:
            source_existing_key = (
                spec.reference_node
                if spec.connection_mode is RepeatConnectionMode.FROM_REFERENCE
                else previous_existing_key
            )
            should_count = True
            if source_existing_key is not None and current_existing_key is not None:
                if source_existing_key == current_existing_key:
                    should_count = False
                elif _has_incidence(model, source_existing_key, current_existing_key):
                    should_count = False
            if should_count:
                new_members += 1

        if spec.connection_mode is RepeatConnectionMode.CONSECUTIVE:
            previous_existing_key = current_existing_key

    return TranslationalRepeatPreview(
        steps=tuple(steps),
        new_node_count=new_nodes,
        new_member_count=new_members,
        reused_node_count=reused,
        skipped_count=skipped,
        final_coordinate=positions[-1],
        collisions=collisions,
    )


def _has_incidence(model: ProjectModel, first: UUID, second: UUID) -> bool:
    return any({member.start, member.end} == {first, second} for member in model.members.values())


def build_translational_repeat(
    model: ProjectModel,
    spec: TranslationalRepeatSpec,
    resolutions: Mapping[int, ExistingNodeResolution],
    tolerance_m: float,
) -> RepeatBuildResult:
    positions = _repeat_positions(model, spec)
    collisions: dict[int, ExistingNodeCollision] = {}
    for index, position in enumerate(positions, start=1):
        collision = _find_collision(model, position, tolerance_m)
        if collision is not None:
            collisions[index] = collision

    unresolved = {
        index: collision.node_key
        for index, collision in collisions.items()
        if index not in resolutions
    }
    if unresolved:
        return RepeatResolutionRequired(unresolved)
    if any(resolutions[index] is ExistingNodeResolution.CANCEL for index in collisions):
        return None

    commands: list[RepairCommand] = []
    reference_key = spec.reference_node
    previous_key = reference_key
    planned_edges: set[frozenset[UUID]] = set()

    for index, position in enumerate(positions, start=1):
        collision = collisions.get(index)
        if collision is not None:
            resolution = resolutions[index]
            if resolution is ExistingNodeResolution.SKIP_STEP:
                continue
            if resolution is not ExistingNodeResolution.USE_EXISTING:
                raise ValueError(f"Unsupported collision resolution at repeat step {index}")
            current_key = collision.node_key
        else:
            current_key = uuid4()
            commands.append(CreateNode(position, node_key=current_key))

        if spec.connection_mode is RepeatConnectionMode.CONSECUTIVE:
            source_key = previous_key
        elif spec.connection_mode is RepeatConnectionMode.FROM_REFERENCE:
            source_key = reference_key
        else:
            source_key = None

        if source_key is not None and source_key != current_key:
            edge = frozenset((source_key, current_key))
            if edge not in planned_edges and not _has_incidence(model, source_key, current_key):
                commands.append(ConnectNodes(source_key, current_key))
                planned_edges.add(edge)

        previous_key = current_key

    if not commands:
        return None
    return CompositeRepair(tuple(commands), label="translational repeat")
