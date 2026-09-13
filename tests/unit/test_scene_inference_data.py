from __future__ import annotations

from uuid import UUID

import numpy as np

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer.scene import SceneData


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_scene_exposes_deterministic_member_endpoint_points_for_inference() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(4.0, 3.0, 0.0)),
    }
    members = {
        _key(102): Member(_key(102), _key(2), _key(3)),
        _key(101): Member(_key(101), _key(1), _key(2)),
    }

    scene = SceneData.from_model(ProjectModel(nodes=nodes, members=members))

    assert scene.member_endpoint_points.shape == (2, 2, 3)
    assert np.array_equal(
        scene.member_endpoint_points,
        np.array(
            [
                [[0.0, 0.0, 0.0], [4.0, 0.0, 0.0]],
                [[4.0, 0.0, 0.0], [4.0, 3.0, 0.0]],
            ]
        ),
    )
