from uuid import UUID

import numpy as np
import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer.scene import SceneData


def _node(key_int: int, x: float, y: float, z: float) -> Node:
    return Node(UUID(int=key_int), Vec3(x, y, z))


def _member(key_int: int, start: int, end: int) -> Member:
    return Member(UUID(int=key_int), UUID(int=start), UUID(int=end))


def test_scene_data_builds_stable_points_lines_and_member_mapping() -> None:
    n1 = _node(1, 0.0, 0.0, 0.0)
    n2 = _node(2, 6.0, 0.0, 0.0)
    n3 = _node(3, 6.0, 3.0, 0.0)
    m1 = _member(101, 1, 2)
    m2 = _member(102, 2, 3)
    model = ProjectModel(
        nodes={n3.key: n3, n1.key: n1, n2.key: n2},
        members={m2.key: m2, m1.key: m1},
    )

    scene = SceneData.from_model(model)

    assert scene.points.shape == (3, 3)
    assert np.array_equal(
        scene.points,
        np.array([[0.0, 0.0, 0.0], [6.0, 0.0, 0.0], [6.0, 3.0, 0.0]]),
    )
    assert scene.lines.shape == (2, 3)
    assert np.array_equal(scene.lines, np.array([[2, 0, 1], [2, 1, 2]]))
    assert scene.member_keys == (m1.key, m2.key)
    assert scene.member_key_for_cell(0) == m1.key
    assert scene.member_key_for_cell(1) == m2.key


def test_scene_data_rejects_member_referencing_missing_node() -> None:
    n1 = _node(1, 0.0, 0.0, 0.0)
    broken = _member(101, 1, 99)
    model = ProjectModel(nodes={n1.key: n1}, members={broken.key: broken})

    with pytest.raises(ValueError, match="missing node"):
        SceneData.from_model(model)
