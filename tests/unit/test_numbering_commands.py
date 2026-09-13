from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.numbering.commands import (
    RenumberAllCommand,
    RenumberMembersCommand,
    RenumberNodesCommand,
)
from staadprep.numbering.renumber import NumberingPolicy, renumber_members, renumber_nodes
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model(*, reverse_insertion: bool = False) -> ProjectModel:
    node_rows = [
        (_key(1), Vec3(5.0, 3.0, 2.0), 91),
        (_key(2), Vec3(0.0, 0.0, 0.0), 17),
        (_key(3), Vec3(5.0, 0.0, 0.0), 44),
        (_key(4), Vec3(0.0, 3.0, 0.0), 8),
    ]
    member_rows = [
        (_key(101), _key(2), _key(3), 700),
        (_key(102), _key(2), _key(4), 300),
        (_key(103), _key(4), _key(1), 900),
    ]
    if reverse_insertion:
        node_rows.reverse()
        member_rows.reverse()
    return ProjectModel(
        nodes={key: Node(key, point, number=number) for key, point, number in node_rows},
        members={
            key: Member(key, start, end, number=number) for key, start, end, number in member_rows
        },
        revision=12,
    )


def _geometry_signature(model: ProjectModel) -> tuple[object, ...]:
    return (
        tuple(
            sorted(
                (key.int, node.position.as_tuple(), node.source_refs)
                for key, node in model.nodes.items()
            )
        ),
        tuple(
            sorted(
                (
                    key.int,
                    member.start.int,
                    member.end.int,
                    member.source_ref,
                    member.group,
                )
                for key, member in model.members.items()
            )
        ),
    )


def _numbers(model: ProjectModel) -> tuple[dict[UUID, int | None], dict[UUID, int | None]]:
    return (
        {key: node.number for key, node in model.nodes.items()},
        {key: member.number for key, member in model.members.items()},
    )


def test_node_preview_matches_direct_t12_map_and_apply_changes_numbers_only() -> None:
    model = _model()
    policy = NumberingPolicy()
    direct = deepcopy(model)
    expected = renumber_nodes(direct, policy).node_numbers
    command = RenumberNodesCommand(policy)
    before_geometry = _geometry_signature(model)
    before_numbers = _numbers(model)
    before_revision = model.revision

    assert command.preview(model).node_numbers == expected
    result = command.apply(model)

    assert {key: node.number for key, node in model.nodes.items()} == expected
    assert _geometry_signature(model) == before_geometry
    assert model.revision == before_revision + 1
    assert result.after_revision == before_revision + 1

    command.revert(model)
    assert _numbers(model) == before_numbers
    assert _geometry_signature(model) == before_geometry
    assert model.revision == before_revision


def test_member_preview_matches_direct_t12_map_and_preserves_endpoint_uuids() -> None:
    model = _model()
    policy = NumberingPolicy()
    direct = deepcopy(model)
    expected = renumber_members(direct, policy).member_numbers
    command = RenumberMembersCommand(policy)
    endpoints = {key: (member.start, member.end) for key, member in model.members.items()}
    before_numbers = _numbers(model)
    before_revision = model.revision

    assert command.preview(model).member_numbers == expected
    command.apply(model)

    assert {key: member.number for key, member in model.members.items()} == expected
    assert {key: (member.start, member.end) for key, member in model.members.items()} == endpoints
    assert model.revision == before_revision + 1

    command.revert(model)
    assert _numbers(model) == before_numbers
    assert model.revision == before_revision


def test_renumber_all_is_one_history_item_and_one_undo_restores_all_numbers() -> None:
    model = _model()
    before = _numbers(model)
    revision = model.revision
    history = RepairHistory(model)
    command = RenumberAllCommand(NumberingPolicy())
    preview = command.preview(model)

    history.execute(command)

    assert len(history.undo_stack) == 1
    assert {key: node.number for key, node in model.nodes.items()} == preview.node_numbers
    assert {key: member.number for key, member in model.members.items()} == preview.member_numbers
    assert model.revision == revision + 1

    history.undo()
    assert _numbers(model) == before
    assert model.revision == revision


def test_numbering_preview_is_independent_of_dictionary_insertion_order() -> None:
    policy = NumberingPolicy()
    first = _model(reverse_insertion=False)
    second = _model(reverse_insertion=True)

    first_preview = RenumberAllCommand(policy).preview(first)
    second_preview = RenumberAllCommand(policy).preview(second)

    assert first_preview.node_numbers == second_preview.node_numbers
    assert first_preview.member_numbers == second_preview.member_numbers
