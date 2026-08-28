from __future__ import annotations

from copy import deepcopy
from math import dist
from uuid import UUID

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import needs_reverse, normalization_commands
from staadprep.repair.history import RepairHistory
from staadprep.topology.connectivity import connected_components
from staadprep.validation.validators import validate_model


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(4.0, 0.0, 0.0), number=10, source_refs=("N1",)),
        _key(2): Node(_key(2), Vec3(0.0, 0.0, 0.0), number=20, source_refs=("N2",)),
        _key(3): Node(_key(3), Vec3(0.0, 5.0, 0.0), number=30, source_refs=("N3",)),
        _key(4): Node(_key(4), Vec3(0.0, 5.0, 8.0), number=40, source_refs=("N4",)),
    }
    members = {
        _key(101): Member(
            _key(101), _key(1), _key(2), number=101, source_ref="M101", group="FRAME"
        ),
        _key(102): Member(
            _key(102), _key(2), _key(3), number=102, source_ref="M102", group="FRAME"
        ),
        _key(103): Member(
            _key(103), _key(4), _key(3), number=103, source_ref="M103", group="FRAME"
        ),
    }
    return ProjectModel(nodes=nodes, members=members)


def _lengths(model: ProjectModel) -> dict[UUID, float]:
    result: dict[UUID, float] = {}
    for key, member in model.members.items():
        start = model.nodes[member.start].position
        end = model.nodes[member.end].position
        result[key] = dist(start.as_tuple(), end.as_tuple())
    return result


def test_normalization_preserves_geometry_identity_metadata_and_connectivity() -> None:
    model = _model()
    before_nodes = deepcopy(model.nodes)
    before_members = deepcopy(model.members)
    before_lengths = _lengths(model)
    before_components = [
        (set(component.node_keys), set(component.member_keys))
        for component in connected_components(model)
    ]
    before_issue_types = [issue.type for issue in validate_model(model)]
    history = RepairHistory(model)

    commands = normalization_commands(model)
    assert [command.member_key for command in commands] == [_key(101), _key(103)]
    for command in commands:
        history.execute(command)

    assert model.nodes == before_nodes
    assert set(model.members) == set(before_members)
    assert _lengths(model) == before_lengths
    assert [
        (set(component.node_keys), set(component.member_keys))
        for component in connected_components(model)
    ] == before_components
    assert [issue.type for issue in validate_model(model)] == before_issue_types
    assert all(not needs_reverse(model, member) for member in model.members.values())
    for key, before in before_members.items():
        after = model.members[key]
        assert after.number == before.number
        assert after.source_ref == before.source_ref
        assert after.group == before.group
        if key in {_key(101), _key(103)}:
            assert (after.start, after.end) == (before.end, before.start)
        else:
            assert (after.start, after.end) == (before.start, before.end)


def test_normalize_then_undo_all_restores_exact_model_state() -> None:
    model = _model()
    original = deepcopy(model)
    history = RepairHistory(model)
    commands = normalization_commands(model)

    for command in commands:
        history.execute(command)
    for _ in commands:
        history.undo()

    assert model == original
    assert model.revision == original.revision
