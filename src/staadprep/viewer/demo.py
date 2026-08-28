"""Development-only synthetic frame used to exercise the real 3D viewport."""

from __future__ import annotations

from uuid import UUID

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel


def build_demo_frame() -> ProjectModel:
    nodes: dict[UUID, Node] = {}
    members: dict[UUID, Member] = {}
    node_id = 1
    member_id = 1001

    levels = (0.0, 4.0)
    xs = (0.0, 6.0, 12.0, 18.0)
    zs = (0.0, 6.0)
    key_by_position: dict[tuple[float, float, float], UUID] = {}

    for z in zs:
        for y in levels:
            for x in xs:
                key = UUID(int=node_id)
                node = Node(key=key, position=Vec3(x, y, z))
                nodes[key] = node
                key_by_position[(x, y, z)] = key
                node_id += 1

    def add_member(start: tuple[float, float, float], end: tuple[float, float, float]) -> None:
        nonlocal member_id
        key = UUID(int=member_id)
        members[key] = Member(key, key_by_position[start], key_by_position[end])
        member_id += 1

    for z in zs:
        for x in xs:
            add_member((x, 0.0, z), (x, 4.0, z))
        for left, right in zip(xs[:-1], xs[1:], strict=True):
            add_member((left, 4.0, z), (right, 4.0, z))

    for x in xs:
        add_member((x, 4.0, 0.0), (x, 4.0, 6.0))

    add_member((0.0, 0.0, 0.0), (6.0, 4.0, 0.0))
    add_member((12.0, 4.0, 6.0), (18.0, 0.0, 6.0))

    return ProjectModel(
        nodes=nodes,
        members=members,
        metadata=ModelMetadata(source_format="demo", source_axis="Y-UP", source_unit="m"),
    )
