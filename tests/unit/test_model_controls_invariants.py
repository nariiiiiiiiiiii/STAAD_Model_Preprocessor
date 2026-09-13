from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.numbering.commands import RenumberAllCommand
from staadprep.numbering.renumber import NumberingPolicy
from staadprep.orientation.commands import SetMemberStart
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), number=90),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0), number=10),
            _key(3): Node(_key(3), Vec3(4.0, 3.0, 0.0), number=60),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2), number=800),
            _key(102): Member(_key(102), _key(2), _key(3), number=200),
        },
        revision=20,
    )


def _coordinates(model: ProjectModel) -> dict[UUID, tuple[float, float, float]]:
    return {key: node.position.as_tuple() for key, node in model.nodes.items()}


def _incidence(model: ProjectModel) -> dict[UUID, tuple[UUID, UUID]]:
    return {key: (member.start, member.end) for key, member in model.members.items()}


def _numbers(model: ProjectModel) -> tuple[dict[UUID, int | None], dict[UUID, int | None]]:
    return (
        {key: node.number for key, node in model.nodes.items()},
        {key: member.number for key, member in model.members.items()},
    )


def test_numbering_changes_only_staad_numbers_and_undo_restores_exact_state() -> None:
    model = _model()
    before = deepcopy(model)
    history = RepairHistory(model)

    history.execute(RenumberAllCommand(NumberingPolicy()))

    assert set(model.nodes) == set(before.nodes)
    assert set(model.members) == set(before.members)
    assert _coordinates(model) == _coordinates(before)
    assert _incidence(model) == _incidence(before)
    assert _numbers(model) != _numbers(before)

    history.undo()
    assert _coordinates(model) == _coordinates(before)
    assert _incidence(model) == _incidence(before)
    assert _numbers(model) == _numbers(before)
    assert model.revision == before.revision


def test_direction_change_changes_only_member_incidence_and_undo_restores_exact_state() -> None:
    model = _model()
    before = deepcopy(model)
    history = RepairHistory(model)
    command = SetMemberStart(_key(101), _key(2)).build(model)
    assert command is not None

    history.execute(command)

    assert set(model.nodes) == set(before.nodes)
    assert set(model.members) == set(before.members)
    assert _coordinates(model) == _coordinates(before)
    assert _numbers(model) == _numbers(before)
    assert _incidence(model)[_key(101)] == (_key(2), _key(1))
    assert _incidence(model)[_key(102)] == _incidence(before)[_key(102)]

    history.undo()
    assert _coordinates(model) == _coordinates(before)
    assert _numbers(model) == _numbers(before)
    assert _incidence(model) == _incidence(before)
    assert model.revision == before.revision
