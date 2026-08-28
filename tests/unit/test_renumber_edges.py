from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.numbering.renumber import NumberingPolicy, renumber_members, renumber_nodes
from staadprep.orientation.normalize import MemberClass


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_member_renumber_fails_atomically_on_missing_node_reference() -> None:
    n1 = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=11)
    good = Member(_key(101), _key(1), _key(1), number=21)
    bad = Member(_key(102), _key(1), _key(999), number=22)
    model = ProjectModel(
        nodes={n1.key: n1},
        members={good.key: good, bad.key: bad},
        revision=4,
    )

    with pytest.raises(ValueError, match="references missing node"):
        renumber_members(model, NumberingPolicy())

    assert model.revision == 4
    assert model.members[_key(101)].number == 21
    assert model.members[_key(102)].number == 22
    assert model.members[_key(102)].end == _key(999)


def test_custom_class_order_is_honoured_without_rewriting_member_references() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(0.0, 4.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, 2.0, 0.0)),
        _key(4): Node(_key(4), Vec3(5.0, 2.0, 0.0)),
    }
    column = Member(_key(101), _key(1), _key(2), number=99)
    beam_x = Member(_key(102), _key(3), _key(4), number=98)
    model = ProjectModel(
        nodes=nodes,
        members={column.key: column, beam_x.key: beam_x},
    )
    refs_before = {key: (member.start, member.end) for key, member in model.members.items()}
    policy = NumberingPolicy(
        class_order=(
            MemberClass.BEAM_X,
            MemberClass.COLUMN,
            MemberClass.BEAM_Z,
            MemberClass.BRACE,
            MemberClass.OTHER,
        )
    )

    mapping = renumber_members(model, policy)

    assert mapping.member_numbers == {_key(102): 1, _key(101): 2}
    assert {key: (member.start, member.end) for key, member in model.members.items()} == refs_before


def test_renumber_overwrites_stale_duplicate_numbers_with_positive_unique_sequence() -> None:
    nodes = {
        _key(3): Node(_key(3), Vec3(2.0, 0.0, 0.0), number=7),
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), number=7),
        _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0), number=-4),
    }
    model = ProjectModel(nodes=nodes)

    mapping = renumber_nodes(model, NumberingPolicy())

    assert mapping.node_numbers == {_key(1): 1, _key(2): 2, _key(3): 3}
    assert sorted(node.number for node in model.nodes.values() if node.number is not None) == [
        1,
        2,
        3,
    ]


def test_numbering_map_is_an_auditable_uuid_to_sta_ad_number_mapping() -> None:
    n1 = Node(_key(10), Vec3(0.0, 0.0, 0.0), number=500)
    n2 = Node(_key(20), Vec3(2.0, 0.0, 0.0), number=100)
    member = Member(_key(200), n2.key, n1.key, number=900)
    model = ProjectModel(
        nodes={n2.key: n2, n1.key: n1},
        members={member.key: member},
    )

    node_map = renumber_nodes(model, NumberingPolicy())
    member_map = renumber_members(model, NumberingPolicy())

    assert node_map.node_numbers == {_key(10): 1, _key(20): 2}
    assert member_map.member_numbers == {_key(200): 1}
    assert model.members[_key(200)].start == _key(20)
    assert model.members[_key(200)].end == _key(10)
