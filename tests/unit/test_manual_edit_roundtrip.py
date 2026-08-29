from __future__ import annotations

from uuid import UUID

from staadprep.editing.manual_ops import (
    build_delete_member,
    build_draw_member_existing,
    build_move_or_snap_node,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.history import RepairHistory


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
            _key(102): Member(_key(102), _key(1), _key(2)),
        },
    )


def _signature(model: ProjectModel) -> tuple[object, ...]:
    nodes = tuple(
        sorted(
            (key.int, node.position.as_tuple(), node.number, node.source_refs)
            for key, node in model.nodes.items()
        )
    )
    members = tuple(
        sorted(
            (
                key.int,
                member.start.int,
                member.end.int,
                member.number,
                member.source_ref,
                member.group,
            )
            for key, member in model.members.items()
        )
    )
    return nodes, members, model.metadata, model.revision


def test_draw_move_delete_three_undo_round_trip_restores_exact_graph() -> None:
    model = _model()
    before = _signature(model)
    history = RepairHistory(model)

    history.execute(build_draw_member_existing(_key(2), _key(3)))
    history.execute(build_move_or_snap_node(_key(4), Vec3(21.0, 2.0, 0.0)))
    history.execute(build_delete_member(_key(102)))

    assert len(history.undo_stack) == 3
    assert _signature(model) != before

    history.undo()
    history.undo()
    history.undo()

    assert _signature(model) == before
    assert not history.undo_stack
    assert len(history.redo_stack) == 3
