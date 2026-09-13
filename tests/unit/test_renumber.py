from __future__ import annotations

from dataclasses import replace
from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.numbering.renumber import (
    NumberingPolicy,
    renumber_members,
    renumber_nodes,
)


def _key(value: int) -> UUID:
    return UUID(int=value)


def _node(value: int, xyz: tuple[float, float, float]) -> Node:
    return Node(_key(value), Vec3(*xyz))


def _member(value: int, start: int, end: int) -> Member:
    return Member(_key(value), _key(start), _key(end))


def test_node_order_is_y_then_x_then_z_then_uuid_at_policy_precision() -> None:
    nodes = [
        _node(5, (5.0, 3.0, 0.0)),
        _node(4, (1.0, 3.0, 2.0)),
        _node(3, (1.0, 3.0, 1.0)),
        _node(2, (9.0, 0.0, 0.0)),
        _node(1, (0.0, 0.0, 0.0)),
        # Same quantized Y/X/Z as node 3: UUID is the final tie-break only.
        _node(6, (1.0 + 0.4e-9, 3.0, 1.0)),
    ]
    model = ProjectModel(nodes={node.key: node for node in nodes})

    result = renumber_nodes(model, NumberingPolicy(node_precision_m=1e-9))

    assert result.node_numbers == {
        _key(1): 1,
        _key(2): 2,
        _key(3): 3,
        _key(6): 4,
        _key(4): 5,
        _key(5): 6,
    }
    assert {key: node.number for key, node in model.nodes.items()} == result.node_numbers
    assert result.member_numbers == {}


def test_member_order_is_class_then_midpoint_y_x_z_then_uuid() -> None:
    nodes = [
        _node(1, (0.0, 0.0, 0.0)),
        _node(2, (0.0, 4.0, 0.0)),
        _node(3, (5.0, 0.0, 0.0)),
        _node(4, (5.0, 4.0, 0.0)),
        _node(5, (0.0, 2.0, 0.0)),
        _node(6, (4.0, 2.0, 0.0)),
        _node(7, (0.0, 2.0, 3.0)),
        _node(8, (0.0, 2.0, 7.0)),
        _node(9, (0.0, 0.0, 0.0)),
        _node(10, (4.0, 4.0, 2.0)),
        _node(11, (8.0, 0.0, 0.0)),
        _node(12, (8.0, 0.0, 0.0)),
    ]
    members = [
        _member(105, 11, 12),  # OTHER (zero length)
        _member(104, 9, 10),  # BRACE
        _member(103, 7, 8),  # BEAM_Z
        _member(102, 5, 6),  # BEAM_X
        _member(101, 1, 2),  # COLUMN midpoint Y=2 X=0
        _member(100, 3, 4),  # COLUMN midpoint Y=2 X=5
    ]
    model = ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )

    result = renumber_members(model, NumberingPolicy())

    assert result.member_numbers == {
        _key(101): 1,
        _key(100): 2,
        _key(102): 3,
        _key(103): 4,
        _key(104): 5,
        _key(105): 6,
    }
    assert {key: member.number for key, member in model.members.items()} == result.member_numbers
    assert result.node_numbers == {}


def test_renumbering_changes_only_sta_ad_facing_numbers_and_revision() -> None:
    n1 = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=90, source_refs=("A",))
    n2 = Node(_key(2), Vec3(4.0, 0.0, 0.0), number=80, source_refs=("B",))
    member = Member(
        _key(101),
        n1.key,
        n2.key,
        number=70,
        source_ref="LINE:1",
        group="BEAM",
    )
    model = ProjectModel(
        nodes={n1.key: n1, n2.key: n2},
        members={member.key: member},
        revision=7,
    )
    node_keys_before = tuple(model.nodes)
    member_keys_before = tuple(model.members)
    positions_before = {key: node.position for key, node in model.nodes.items()}
    refs_before = {key: (m.start, m.end, m.source_ref, m.group) for key, m in model.members.items()}

    node_map = renumber_nodes(model, NumberingPolicy())
    member_map = renumber_members(model, NumberingPolicy())

    assert model.revision == 9
    assert tuple(model.nodes) == node_keys_before
    assert tuple(model.members) == member_keys_before
    assert {key: node.position for key, node in model.nodes.items()} == positions_before
    assert {
        key: (m.start, m.end, m.source_ref, m.group) for key, m in model.members.items()
    } == refs_before
    assert node_map.node_numbers == {_key(1): 1, _key(2): 2}
    assert member_map.member_numbers == {_key(101): 1}


def test_numbering_is_deterministic_across_dictionary_insertion_order_and_repeats() -> None:
    nodes = [
        _node(1, (0.0, 0.0, 0.0)),
        _node(2, (4.0, 0.0, 0.0)),
        _node(3, (0.0, 3.0, 0.0)),
        _node(4, (4.0, 3.0, 0.0)),
    ]
    members = [_member(101, 1, 3), _member(102, 2, 4), _member(103, 3, 4)]
    first = ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )
    second = ProjectModel(
        nodes={node.key: replace(node) for node in reversed(nodes)},
        members={member.key: replace(member) for member in reversed(members)},
    )

    first_nodes = renumber_nodes(first, NumberingPolicy())
    first_members = renumber_members(first, NumberingPolicy())
    second_nodes = renumber_nodes(second, NumberingPolicy())
    second_members = renumber_members(second, NumberingPolicy())
    repeated_nodes = renumber_nodes(first, NumberingPolicy())
    repeated_members = renumber_members(first, NumberingPolicy())

    assert first_nodes.node_numbers == second_nodes.node_numbers == repeated_nodes.node_numbers
    assert (
        first_members.member_numbers
        == second_members.member_numbers
        == repeated_members.member_numbers
    )


def test_policy_rejects_invalid_precision_and_class_order() -> None:
    with pytest.raises(ValueError, match="node_precision_m"):
        NumberingPolicy(node_precision_m=0.0)
    with pytest.raises(ValueError, match="class_order"):
        NumberingPolicy(class_order=("COLUMN", "COLUMN"))
