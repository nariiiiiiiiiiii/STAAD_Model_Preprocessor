from __future__ import annotations

from math import nan
from uuid import UUID

import pytest

from staadprep.editing.create_node import (
    ExactNodeSpec,
    ExistingNodeCollision,
    RelativeNodeSpec,
    build_exact_create,
    build_relative_create,
    exact_position,
    relative_position,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import CreateNode
from staadprep.repair.composite import CompositeRepair


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(10.0, 4.0, 3.0)),
            _key(2): Node(_key(2), Vec3(14.0, 4.0, 3.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
        },
    )


def test_exact_xyz_position_is_canonical_staadd_xyz() -> None:
    spec = ExactNodeSpec(x=11.0, y=4.0, z=3.0)

    assert exact_position(spec) == Vec3(11.0, 4.0, 3.0)


def test_relative_math_uses_canonical_y_as_vertical() -> None:
    model = _model()
    spec = RelativeNodeSpec(
        reference_node=_key(1),
        dx=1.0,
        dy=-0.0,
        dz=0.0,
        create_member=False,
    )

    assert relative_position(model, spec) == Vec3(11.0, 4.0, 3.0)


@pytest.mark.parametrize(
    "spec",
    [
        ExactNodeSpec(x=nan, y=0.0, z=0.0),
        RelativeNodeSpec(_key(1), dx=nan, dy=0.0, dz=0.0, create_member=False),
    ],
)
def test_non_finite_coordinate_input_is_rejected_before_command_creation(spec: object) -> None:
    model = _model()

    with pytest.raises(ValueError, match="finite"):
        if isinstance(spec, ExactNodeSpec):
            build_exact_create(model, spec, tolerance_m=1e-6)
        else:
            assert isinstance(spec, RelativeNodeSpec)
            build_relative_create(model, spec, tolerance_m=1e-6)

    assert model.revision == 0


def test_zero_relative_offset_is_rejected_instead_of_duplicating_reference_node() -> None:
    model = _model()
    spec = RelativeNodeSpec(_key(1), 0.0, 0.0, 0.0, create_member=False)

    with pytest.raises(ValueError, match="zero relative offset"):
        build_relative_create(model, spec, tolerance_m=1e-6)

    assert model.revision == 0
    assert len(model.nodes) == 2


def test_exact_target_collision_returns_resolution_result_without_mutation() -> None:
    model = _model()
    spec = ExactNodeSpec(x=14.0, y=4.0, z=3.0)

    result = build_exact_create(model, spec, tolerance_m=1e-6)

    assert result == ExistingNodeCollision(_key(2), Vec3(14.0, 4.0, 3.0))
    assert model.revision == 0
    assert len(model.nodes) == 2


def test_non_colliding_exact_target_builds_reversible_create_node() -> None:
    model = _model()

    command = build_exact_create(model, ExactNodeSpec(12.0, 5.0, 3.0), tolerance_m=1e-6)

    assert isinstance(command, CreateNode)
    assert model.revision == 0


def test_relative_create_member_is_atomic_and_collision_is_reported_first() -> None:
    model = _model()
    create_spec = RelativeNodeSpec(_key(1), 0.0, 2.0, 0.0, create_member=True)

    command = build_relative_create(model, create_spec, tolerance_m=1e-6)
    assert isinstance(command, CompositeRepair)
    assert model.revision == 0

    collision_spec = RelativeNodeSpec(_key(1), 4.0, 0.0, 0.0, create_member=True)
    collision = build_relative_create(model, collision_spec, tolerance_m=1e-6)
    assert collision == ExistingNodeCollision(_key(2), Vec3(14.0, 4.0, 3.0))
    assert model.revision == 0
