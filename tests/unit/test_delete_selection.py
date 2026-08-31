from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.editing.manual_ops import build_delete_selection
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(8.0, 0.0, 0.0)),
            _key(4): Node(_key(4), Vec3(20.0, 0.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(2), _key(3)),
        },
        revision=7,
    )


def test_delete_selection_removes_members_then_newly_orphaned_nodes_and_undoes_exactly() -> None:
    model = _model()
    before_nodes = dict(model.nodes)
    before_members = dict(model.members)
    command = build_delete_selection(
        model,
        node_keys=(_key(2), _key(4)),
        member_keys=(_key(101), _key(102)),
    )

    result = command.apply(model)

    assert model.nodes == {_key(1): before_nodes[_key(1)], _key(3): before_nodes[_key(3)]}
    assert model.members == {}
    assert result.before_revision == 7
    command.revert(model)
    assert model.nodes == before_nodes
    assert model.members == before_members
    assert model.revision == 7


def test_delete_selection_rejects_node_with_unselected_incident_member_without_mutation() -> None:
    model = _model()
    before_nodes = dict(model.nodes)
    before_members = dict(model.members)

    with pytest.raises(ValueError, match="unselected incident Member"):
        build_delete_selection(model, node_keys=(_key(2),), member_keys=(_key(101),))

    assert model.nodes == before_nodes
    assert model.members == before_members
    assert model.revision == 7


def test_delete_selection_requires_at_least_one_existing_entity() -> None:
    model = _model()

    with pytest.raises(ValueError, match="requires selected"):
        build_delete_selection(model, node_keys=(), member_keys=())
    with pytest.raises(ValueError, match="does not exist"):
        build_delete_selection(model, node_keys=(_key(99),), member_keys=())
