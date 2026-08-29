from __future__ import annotations

from copy import deepcopy
from math import nan
from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.repair.commands import CreateNode, MoveNode


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), source_refs=("A",)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0), source_refs=("B",)),
        _key(3): Node(_key(3), Vec3(8.0, 2.0, 1.0), source_refs=("C",)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2), source_ref="M101", group="Frame"),
    }
    return ProjectModel(
        nodes=nodes,
        members=members,
        metadata=ModelMetadata(
            schema_version=1,
            source_format="test",
            source_file="fixture",
            source_unit="m",
            source_axis="Y-UP",
        ),
        revision=7,
    )


def _invalid_vec3() -> Vec3:
    value = object.__new__(Vec3)
    object.__setattr__(value, "x", nan)
    object.__setattr__(value, "y", 0.0)
    object.__setattr__(value, "z", 0.0)
    return value


def test_create_node_apply_and_revert_restore_exact_model_and_revision() -> None:
    model = _model()
    before = deepcopy(model)
    command = CreateNode(Vec3(2.0, 3.0, 4.0), node_key=_key(50))

    result = command.apply(model)

    assert result.before_revision == 7
    assert result.after_revision == 8
    assert model.revision == 8
    assert model.nodes[_key(50)].position == Vec3(2.0, 3.0, 4.0)
    assert model.members == before.members
    assert model.metadata == before.metadata

    undo = command.revert(model)

    assert undo.after_revision == 7
    assert model == before


def test_create_node_rejects_invalid_position_before_mutation() -> None:
    model = _model()
    before = deepcopy(model)
    command = CreateNode(_invalid_vec3(), node_key=_key(50))

    with pytest.raises(ValueError, match="finite"):
        command.apply(model)

    assert model == before


def test_move_node_apply_and_revert_preserve_uuid_references_and_metadata() -> None:
    model = _model()
    before = deepcopy(model)
    command = MoveNode(_key(2), Vec3(5.0, 6.0, 7.0))

    result = command.apply(model)

    assert result.before_revision == 7
    assert result.after_revision == 8
    assert model.nodes[_key(2)].position == Vec3(5.0, 6.0, 7.0)
    assert model.members[_key(101)].start == _key(1)
    assert model.members[_key(101)].end == _key(2)
    assert model.metadata == before.metadata
    assert set(model.nodes) == set(before.nodes)

    command.revert(model)

    assert model == before


def test_move_node_does_not_implicitly_merge_when_target_matches_existing_node() -> None:
    model = _model()
    command = MoveNode(_key(2), model.nodes[_key(3)].position)

    command.apply(model)

    assert _key(2) in model.nodes
    assert _key(3) in model.nodes
    assert model.nodes[_key(2)].position == model.nodes[_key(3)].position
    assert model.members[_key(101)].end == _key(2)


def test_move_node_rejects_invalid_target_before_mutation() -> None:
    model = _model()
    before = deepcopy(model)
    command = MoveNode(_key(2), _invalid_vec3())

    with pytest.raises(ValueError, match="finite"):
        command.apply(model)

    assert model == before
