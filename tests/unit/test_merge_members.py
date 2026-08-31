from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.editing.manual_ops import build_merge_selected_members
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import MergeMembers


def _key(value: int) -> UUID:
    return UUID(int=value)


def _chain(*, reverse_primary: bool = False) -> ProjectModel:
    primary_start, primary_end = (
        (_key(2), _key(1)) if reverse_primary else (_key(1), _key(2))
    )
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0), number=2),
            _key(3): Node(_key(3), Vec3(9.0, 0.0, 0.0), number=3),
        },
        members={
            _key(101): Member(
                _key(101),
                primary_start,
                primary_end,
                number=11,
                source_ref="primary",
                group="Roof",
            ),
            _key(102): Member(_key(102), _key(2), _key(3), number=12),
        },
        revision=5,
    )


def test_merge_members_retains_primary_identity_metadata_and_undoes_exactly() -> None:
    model = _chain()
    before_nodes = dict(model.nodes)
    before_members = dict(model.members)
    command = build_merge_selected_members(model, _key(102), _key(101))

    assert isinstance(command, MergeMembers)
    result = command.apply(model)

    assert set(model.nodes) == {_key(1), _key(3)}
    assert set(model.members) == {_key(101)}
    merged = model.members[_key(101)]
    assert (merged.start, merged.end) == (_key(1), _key(3))
    assert merged.number == 11
    assert merged.source_ref == "primary"
    assert merged.group == "Roof"
    assert result.before_revision == 5
    assert result.after_revision == 6

    command.revert(model)
    assert model.nodes == before_nodes
    assert model.members == before_members
    assert model.revision == 5


def test_merge_members_preserves_primary_direction_when_shared_node_is_start() -> None:
    model = _chain(reverse_primary=True)

    MergeMembers(_key(101), _key(102)).apply(model)

    assert (model.members[_key(101)].start, model.members[_key(101)].end) == (
        _key(3),
        _key(1),
    )


def test_merge_members_rejects_non_collinear_or_branched_selection_without_mutation() -> None:
    non_collinear = _chain()
    non_collinear.nodes[_key(3)] = Node(_key(3), Vec3(9.0, 1.0, 0.0), number=3)
    before = (dict(non_collinear.nodes), dict(non_collinear.members), non_collinear.revision)
    with pytest.raises(ValueError, match="collinear"):
        MergeMembers(_key(101), _key(102)).apply(non_collinear)
    assert (non_collinear.nodes, non_collinear.members, non_collinear.revision) == before

    branched = _chain()
    branched.nodes[_key(4)] = Node(_key(4), Vec3(4.0, 2.0, 0.0))
    branched.members[_key(103)] = Member(_key(103), _key(2), _key(4))
    before = (dict(branched.nodes), dict(branched.members), branched.revision)
    with pytest.raises(ValueError, match="degree exactly two"):
        MergeMembers(_key(101), _key(102)).apply(branched)
    assert (branched.nodes, branched.members, branched.revision) == before


def test_merge_members_requires_two_distinct_members_with_one_shared_node() -> None:
    model = _chain()
    with pytest.raises(ValueError, match="two different"):
        MergeMembers(_key(101), _key(101)).apply(model)

    model.nodes[_key(4)] = Node(_key(4), Vec3(20.0, 0.0, 0.0))
    model.nodes[_key(5)] = Node(_key(5), Vec3(24.0, 0.0, 0.0))
    model.members[_key(103)] = Member(_key(103), _key(4), _key(5))
    with pytest.raises(ValueError, match="one shared Node"):
        MergeMembers(_key(101), _key(103)).apply(model)
