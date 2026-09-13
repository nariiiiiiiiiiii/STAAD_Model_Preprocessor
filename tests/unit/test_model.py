from math import inf, nan

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel


def test_member_references_stable_node_keys_independent_from_numbers() -> None:
    a = Node.new(Vec3(0.0, 0.0, 0.0))
    b = Node.new(Vec3(1.0, 0.0, 0.0))
    member = Member.new(a.key, b.key)

    a.number = 100
    b.number = 200

    assert member.start == a.key
    assert member.end == b.key
    assert member.start != a.number
    assert member.end != b.number


def test_vec3_rejects_non_finite_coordinates() -> None:
    for bad_value in (nan, inf, -inf):
        with pytest.raises(ValueError, match="finite"):
            Vec3(bad_value, 0.0, 0.0)


def test_project_model_keeps_entities_by_stable_uuid_key() -> None:
    a = Node.new(Vec3(0.0, 0.0, 0.0), source_refs=("SKP:edge:1:start",))
    b = Node.new(Vec3(1.0, 0.0, 0.0), source_refs=("SKP:edge:1:end",))
    member = Member.new(a.key, b.key, source_ref="SKP:edge:1", group="Frame-A")
    model = ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
        metadata=ModelMetadata(source_format="skp", source_file="frame.skp"),
    )

    assert model.nodes[a.key] is a
    assert model.members[member.key] is member
    assert model.revision == 0
