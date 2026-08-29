from __future__ import annotations

from uuid import UUID

from staadprep.editing.create_node import (
    RepeatConnectionMode,
    TranslationalRepeatSpec,
    analyze_translational_repeat,
)
from staadprep.editing.inference import InferenceHit, SnapKind
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import CreateNode, SplitMember
from staadprep.repair.composite import CompositeRepair
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _single_member_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )


def _crossing_model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, -2.0, 0.0)),
            _key(4): Node(_key(4), Vec3(0.0, 2.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(3), _key(4)),
        },
    )


def test_precision_node_preview_is_ghost_only_and_can_include_reference_member(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _single_member_model()
    viewport.set_model(model)
    revision = model.revision

    viewport.show_precise_node_preview(
        Vec3(0.0, 2.0, 0.0),
        reference_node=_key(1),
        create_member=True,
    )

    assert viewport._precision_ghost_node_count == 1
    assert viewport._precision_ghost_member_count == 1
    assert model.revision == revision
    assert len(model.nodes) == 2
    assert len(model.members) == 1

    viewport.clear_precision_preview()
    assert viewport._precision_ghost_node_count == 0
    assert viewport._precision_ghost_member_count == 0


def test_repeat_preview_renders_all_ghost_nodes_and_consecutive_members_without_mutation(
    qtbot,
) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = ProjectModel(nodes={_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))})
    viewport.set_model(model)
    revision = model.revision
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.CONSECUTIVE)
    preview = analyze_translational_repeat(model, spec, tolerance_m=1e-6)

    viewport.show_translational_repeat_preview(preview, spec, resolutions={})

    assert viewport._precision_ghost_node_count == 3
    assert viewport._precision_ghost_member_count == 3
    assert model.revision == revision
    assert len(model.nodes) == 1
    assert not model.members


def test_create_node_hit_reuses_existing_node_without_emitting_mutation(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _single_member_model()
    viewport.set_model(model)
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)

    viewport.request_create_node_hit(
        InferenceHit(Vec3(0.0, 0.0, 0.0), SnapKind.NODE, (_key(1),), "NODE")
    )

    assert viewport.selection.selected_nodes == (_key(1),)
    assert emitted == []
    assert model.revision == 0


def test_create_node_midpoint_emits_split_member_command_only(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _single_member_model()
    viewport.set_model(model)
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)

    viewport.request_create_node_hit(
        InferenceHit(Vec3(2.0, 0.0, 0.0), SnapKind.MIDPOINT, (_key(101),), "MIDPOINT")
    )

    assert isinstance(emitted[-1], SplitMember)
    assert model.revision == 0
    assert len(model.nodes) == 2


def test_create_node_intersection_emits_one_atomic_composite(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _crossing_model()
    viewport.set_model(model)
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)

    viewport.request_create_node_hit(
        InferenceHit(
            Vec3(0.0, 0.0, 0.0),
            SnapKind.INTERSECTION,
            (_key(101), _key(102)),
            "INTERSECTION",
        )
    )

    assert isinstance(emitted[-1], CompositeRepair)
    assert model.revision == 0
    assert len(model.nodes) == 4


def test_create_node_work_plane_hit_emits_create_node_without_direct_mutation(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _single_member_model()
    viewport.set_model(model)
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)

    viewport.request_create_node_hit(
        InferenceHit(Vec3(1.0, 2.0, 3.0), SnapKind.WORK_PLANE, (), "WORK PLANE")
    )

    assert isinstance(emitted[-1], CreateNode)
    assert model.revision == 0
    assert len(model.nodes) == 2
