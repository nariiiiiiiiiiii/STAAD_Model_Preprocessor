from __future__ import annotations

from uuid import UUID

import numpy as np

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer.scene import SceneData


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_scene_data_exposes_member_midpoints_and_unit_local_x_vectors() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(4.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(0.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, 0.0, 0.0)),
        _key(4): Node(_key(4), Vec3(0.0, 3.0, 4.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    scene = SceneData.from_model(ProjectModel(nodes=nodes, members=members))

    index_101 = scene.member_keys.index(_key(101))
    index_102 = scene.member_keys.index(_key(102))

    assert np.allclose(scene.member_midpoints[index_101], [2.0, 0.0, 0.0])
    assert np.allclose(scene.local_x_vectors[index_101], [-1.0, 0.0, 0.0])
    assert np.allclose(scene.member_midpoints[index_102], [0.0, 1.5, 2.0])
    assert np.allclose(scene.local_x_vectors[index_102], [0.0, 0.6, 0.8])


def test_scene_data_uses_zero_vector_for_zero_length_member() -> None:
    node = Node(_key(1), Vec3(2.0, 3.0, 4.0))
    member = Member(_key(101), node.key, node.key)

    scene = SceneData.from_model(
        ProjectModel(nodes={node.key: node}, members={member.key: member})
    )

    assert np.allclose(scene.member_midpoints[0], [2.0, 3.0, 4.0])
    assert np.allclose(scene.local_x_vectors[0], [0.0, 0.0, 0.0])
