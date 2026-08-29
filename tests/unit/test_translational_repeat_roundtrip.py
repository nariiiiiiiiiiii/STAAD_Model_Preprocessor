from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from staadprep.editing.create_node import (
    RepeatConnectionMode,
    TranslationalRepeatSpec,
    build_translational_repeat,
)
from staadprep.model.entities import Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _graph_signature(
    model: ProjectModel,
) -> tuple[tuple[tuple[int, tuple[float, float, float]], ...], tuple[tuple[int, int], ...], int]:
    nodes = tuple(sorted((key.int, node.position.as_tuple()) for key, node in model.nodes.items()))
    incidences = tuple(
        sorted(
            tuple(sorted((member.start.int, member.end.int))) for member in model.members.values()
        )
    )
    return nodes, incidences, model.revision


def test_independent_frame_line_repeat_matches_exact_uuid_coordinate_incidence_and_undo(
    monkeypatch,
) -> None:
    model = ProjectModel(nodes={_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))})
    before = deepcopy(model)
    generated = iter((_key(10), _key(11), _key(12)))
    monkeypatch.setattr(
        "staadprep.editing.create_node.uuid4",
        lambda: next(generated),
    )
    spec = TranslationalRepeatSpec(
        reference_node=_key(1),
        dx=2.0,
        dy=1.0,
        dz=0.0,
        repeats=3,
        connection_mode=RepeatConnectionMode.CONSECUTIVE,
    )

    command = build_translational_repeat(model, spec, resolutions={}, tolerance_m=1e-9)
    assert isinstance(command, CompositeRepair)
    history = RepairHistory(model)
    history.execute(command)

    expected_nodes = (
        (1, (0.0, 0.0, 0.0)),
        (10, (2.0, 1.0, 0.0)),
        (11, (4.0, 2.0, 0.0)),
        (12, (6.0, 3.0, 0.0)),
    )
    expected_incidences = ((1, 10), (10, 11), (11, 12))
    nodes, incidences, revision = _graph_signature(model)
    assert nodes == expected_nodes
    assert incidences == expected_incidences
    assert revision == 6
    assert len(history.undo_stack) == 1

    history.undo()

    assert _graph_signature(model) == _graph_signature(before)
    assert history.undo_stack == ()
    assert len(history.redo_stack) == 1
