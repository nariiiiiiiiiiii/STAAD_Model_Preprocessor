from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import (
    ConnectNodes,
    DeleteMember,
    DeleteNode,
    MergeNodes,
    ReverseMember,
    ScaleModel,
    SnapNode,
    SplitMember,
    TransformModel,
)


def _key(value: int) -> UUID:
    return UUID(int=value)


def _node(value: int, x: float, y: float = 0.0, z: float = 0.0, *refs: str) -> Node:
    return Node(_key(value), Vec3(x, y, z), source_refs=tuple(refs))


def _member(value: int, start: int, end: int, *, source_ref: str | None = None) -> Member:
    return Member(_key(value), _key(start), _key(end), source_ref=source_ref)


def _assert_integrity(model: ProjectModel) -> None:
    for member in model.members.values():
        assert member.start in model.nodes
        assert member.end in model.nodes


def test_merge_nodes_redirects_all_incidence_and_aggregates_source_refs() -> None:
    a = _node(1, 0.0, 0.0, 0.0, "A")
    b = _node(2, 0.0005, 0.0, 0.0, "B")
    c = _node(3, 2.0)
    member = _member(101, 2, 3, source_ref="M")
    model = ProjectModel(nodes={n.key: n for n in (a, b, c)}, members={member.key: member})

    result = MergeNodes(keep=a.key, remove=b.key).apply(model)

    assert b.key not in model.nodes
    assert model.members[member.key].start == a.key
    assert model.nodes[a.key].source_refs == ("A", "B")
    assert result.before_revision == 0
    assert result.after_revision == 1
    assert model.revision == 1
    _assert_integrity(model)


def test_snap_node_changes_only_target_position() -> None:
    a = _node(1, 0.0)
    b = _node(2, 1.0)
    model = ProjectModel(nodes={a.key: a, b.key: b})

    SnapNode(a.key, Vec3(0.25, 0.5, -0.75)).apply(model)

    assert model.nodes[a.key].position == Vec3(0.25, 0.5, -0.75)
    assert model.nodes[b.key].position == Vec3(1.0, 0.0, 0.0)
    assert model.revision == 1


def test_delete_node_only_allows_orphan_nodes() -> None:
    a = _node(1, 0.0)
    b = _node(2, 1.0)
    member = _member(101, 1, 2)
    model = ProjectModel(nodes={a.key: a, b.key: b}, members={member.key: member})

    with pytest.raises(ValueError, match="connected node"):
        DeleteNode(a.key).apply(model)

    assert a.key in model.nodes
    assert model.revision == 0

    orphan = _node(3, 3.0)
    model.nodes[orphan.key] = orphan
    DeleteNode(orphan.key).apply(model)
    assert orphan.key not in model.nodes
    assert model.revision == 1
    _assert_integrity(model)


def test_delete_member_removes_only_requested_member() -> None:
    a = _node(1, 0.0)
    b = _node(2, 1.0)
    c = _node(3, 2.0)
    m1 = _member(101, 1, 2)
    m2 = _member(102, 2, 3)
    model = ProjectModel(
        nodes={n.key: n for n in (a, b, c)},
        members={m.key: m for m in (m1, m2)},
    )

    DeleteMember(m1.key).apply(model)

    assert set(model.members) == {m2.key}
    assert model.revision == 1
    _assert_integrity(model)


def test_connect_nodes_adds_member_without_modifying_nodes() -> None:
    a = _node(1, 0.0)
    b = _node(2, 2.0)
    model = ProjectModel(nodes={a.key: a, b.key: b})

    command = ConnectNodes(a.key, b.key, source_ref="manual-connect")
    command.apply(model)

    assert len(model.nodes) == 2
    assert len(model.members) == 1
    created = next(iter(model.members.values()))
    assert (created.start, created.end) == (a.key, b.key)
    assert created.source_ref == "manual-connect"
    assert command.created_member_key == created.key
    assert model.revision == 1
    _assert_integrity(model)


def test_split_member_preserves_original_key_and_creates_two_valid_members() -> None:
    a = _node(1, 0.0)
    b = _node(2, 10.0)
    original = _member(101, 1, 2, source_ref="beam-A")
    model = ProjectModel(nodes={a.key: a, b.key: b}, members={original.key: original})

    command = SplitMember(original.key, Vec3(4.0, 0.0, 0.0))
    command.apply(model)

    assert len(model.nodes) == 3
    assert len(model.members) == 2
    assert command.created_node_key is not None
    assert command.created_member_key is not None
    split_node = model.nodes[command.created_node_key]
    first = model.members[original.key]
    second = model.members[command.created_member_key]
    assert split_node.position == Vec3(4.0, 0.0, 0.0)
    assert (first.start, first.end) == (a.key, split_node.key)
    assert (second.start, second.end) == (split_node.key, b.key)
    assert first.source_ref == second.source_ref == "beam-A"
    assert model.revision == 1
    _assert_integrity(model)


def test_split_member_rejects_endpoint_and_off_member_positions() -> None:
    a = _node(1, 0.0)
    b = _node(2, 10.0)
    original = _member(101, 1, 2)
    model = ProjectModel(nodes={a.key: a, b.key: b}, members={original.key: original})

    with pytest.raises(ValueError, match="strictly inside"):
        SplitMember(original.key, Vec3(0.0, 0.0, 0.0)).apply(model)
    with pytest.raises(ValueError, match="on the member"):
        SplitMember(original.key, Vec3(4.0, 1.0, 0.0)).apply(model)
    assert model.revision == 0


def test_reverse_member_swaps_incidence_without_changing_identity() -> None:
    a = _node(1, 0.0)
    b = _node(2, 3.0)
    member = _member(101, 1, 2)
    model = ProjectModel(nodes={a.key: a, b.key: b}, members={member.key: member})

    ReverseMember(member.key).apply(model)

    assert model.members[member.key].key == member.key
    assert (model.members[member.key].start, model.members[member.key].end) == (b.key, a.key)
    assert model.revision == 1
    _assert_integrity(model)


def test_scale_model_scales_all_coordinates_about_origin() -> None:
    a = _node(1, 1.0, -2.0, 3.0)
    b = _node(2, -4.0, 5.0, -6.0)
    model = ProjectModel(nodes={a.key: a, b.key: b})

    ScaleModel(2.5).apply(model)

    assert model.nodes[a.key].position == Vec3(2.5, -5.0, 7.5)
    assert model.nodes[b.key].position == Vec3(-10.0, 12.5, -15.0)
    assert model.revision == 1


def test_scale_model_rejects_nonpositive_factor() -> None:
    model = ProjectModel(nodes={_key(1): _node(1, 1.0)})
    with pytest.raises(ValueError, match="positive"):
        ScaleModel(0.0).apply(model)
    assert model.revision == 0


def test_transform_model_applies_explicit_3x3_matrix_to_all_nodes() -> None:
    node = _node(1, 1.0, 2.0, 3.0)
    model = ProjectModel(nodes={node.key: node})
    matrix = (
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.0, -1.0, 0.0),
    )

    TransformModel(matrix).apply(model)

    assert model.nodes[node.key].position == Vec3(1.0, 3.0, -2.0)
    assert model.revision == 1
