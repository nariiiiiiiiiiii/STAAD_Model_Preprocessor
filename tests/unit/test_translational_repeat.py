from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from staadprep.editing.create_node import (
    ExistingNodeResolution,
    RepeatConnectionMode,
    RepeatResolutionRequired,
    TranslationalRepeatSpec,
    analyze_translational_repeat,
    build_translational_repeat,
)
from staadprep.model.entities import Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model(*, collision_at_two: bool = False) -> ProjectModel:
    nodes = {_key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0))}
    if collision_at_two:
        nodes[_key(2)] = Node(_key(2), Vec3(2.0, 0.0, 0.0))
    return ProjectModel(nodes=nodes)


def _positions(model: ProjectModel) -> set[tuple[float, float, float]]:
    return {node.position.as_tuple() for node in model.nodes.values()}


def _incidence_positions(model: ProjectModel) -> set[frozenset[tuple[float, float, float]]]:
    return {
        frozenset(
            (
                model.nodes[member.start].position.as_tuple(),
                model.nodes[member.end].position.as_tuple(),
            )
        )
        for member in model.members.values()
    }


def test_repeat_positions_are_exact_and_count_excludes_reference_node() -> None:
    model = _model()
    spec = TranslationalRepeatSpec(
        reference_node=_key(1),
        dx=1.0,
        dy=0.0,
        dz=0.0,
        repeats=5,
        connection_mode=RepeatConnectionMode.CONSECUTIVE,
    )

    preview = analyze_translational_repeat(model, spec, tolerance_m=1e-6)

    assert [step.position for step in preview.steps] == [
        Vec3(1.0, 0.0, 0.0),
        Vec3(2.0, 0.0, 0.0),
        Vec3(3.0, 0.0, 0.0),
        Vec3(4.0, 0.0, 0.0),
        Vec3(5.0, 0.0, 0.0),
    ]
    assert preview.new_node_count == 5
    assert preview.new_member_count == 5
    assert preview.final_coordinate == Vec3(5.0, 0.0, 0.0)


def test_repeat_supports_exact_diagonal_step_vector() -> None:
    model = _model()
    spec = TranslationalRepeatSpec(
        _key(1),
        dx=1.0,
        dy=2.0,
        dz=-0.5,
        repeats=3,
        connection_mode=RepeatConnectionMode.NONE,
    )

    preview = analyze_translational_repeat(model, spec, tolerance_m=1e-6)

    assert [step.position for step in preview.steps] == [
        Vec3(1.0, 2.0, -0.5),
        Vec3(2.0, 4.0, -1.0),
        Vec3(3.0, 6.0, -1.5),
    ]
    assert preview.new_member_count == 0


def test_consecutive_repeat_builds_chain_as_one_history_item_and_one_undo() -> None:
    model = _model()
    before = deepcopy(model)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 5, RepeatConnectionMode.CONSECUTIVE)
    command = build_translational_repeat(model, spec, resolutions={}, tolerance_m=1e-6)
    assert isinstance(command, CompositeRepair)
    history = RepairHistory(model)

    history.execute(command)

    assert _positions(model) == {(float(x), 0.0, 0.0) for x in range(6)}
    assert _incidence_positions(model) == {
        frozenset(((float(x), 0.0, 0.0), (float(x + 1), 0.0, 0.0))) for x in range(5)
    }
    assert len(history.undo_stack) == 1

    history.undo()
    assert model == before


def test_from_reference_repeat_builds_star_incidence() -> None:
    model = _model()
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.FROM_REFERENCE)
    command = build_translational_repeat(model, spec, resolutions={}, tolerance_m=1e-6)
    assert isinstance(command, CompositeRepair)

    RepairHistory(model).execute(command)

    assert _incidence_positions(model) == {
        frozenset(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))),
        frozenset(((0.0, 0.0, 0.0), (2.0, 0.0, 0.0))),
        frozenset(((0.0, 0.0, 0.0), (3.0, 0.0, 0.0))),
    }


def test_collision_without_resolution_returns_required_result_before_mutation() -> None:
    model = _model(collision_at_two=True)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.CONSECUTIVE)

    result = build_translational_repeat(model, spec, resolutions={}, tolerance_m=1e-6)

    assert isinstance(result, RepeatResolutionRequired)
    assert result.collisions == {2: _key(2)}
    assert model.revision == 0
    assert not model.members


def test_use_existing_reuses_uuid_without_duplicate_and_preserves_chain() -> None:
    model = _model(collision_at_two=True)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.CONSECUTIVE)

    command = build_translational_repeat(
        model,
        spec,
        resolutions={2: ExistingNodeResolution.USE_EXISTING},
        tolerance_m=1e-6,
    )
    assert isinstance(command, CompositeRepair)
    RepairHistory(model).execute(command)

    assert _positions(model) == {
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (2.0, 0.0, 0.0),
        (3.0, 0.0, 0.0),
    }
    assert sum(node.position == Vec3(2.0, 0.0, 0.0) for node in model.nodes.values()) == 1
    assert _incidence_positions(model) == {
        frozenset(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))),
        frozenset(((1.0, 0.0, 0.0), (2.0, 0.0, 0.0))),
        frozenset(((2.0, 0.0, 0.0), (3.0, 0.0, 0.0))),
    }


def test_skip_step_creates_nothing_for_collision_step_but_later_position_is_unchanged() -> None:
    model = _model(collision_at_two=True)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.CONSECUTIVE)

    command = build_translational_repeat(
        model,
        spec,
        resolutions={2: ExistingNodeResolution.SKIP_STEP},
        tolerance_m=1e-6,
    )
    assert isinstance(command, CompositeRepair)
    RepairHistory(model).execute(command)

    assert _positions(model) == {
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (2.0, 0.0, 0.0),
        (3.0, 0.0, 0.0),
    }
    assert _incidence_positions(model) == {
        frozenset(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))),
        frozenset(((1.0, 0.0, 0.0), (3.0, 0.0, 0.0))),
    }


def test_cancel_resolution_returns_no_command_and_leaves_model_unchanged() -> None:
    model = _model(collision_at_two=True)
    before = deepcopy(model)
    spec = TranslationalRepeatSpec(_key(1), 1.0, 0.0, 0.0, 3, RepeatConnectionMode.CONSECUTIVE)

    result = build_translational_repeat(
        model,
        spec,
        resolutions={2: ExistingNodeResolution.CANCEL},
        tolerance_m=1e-6,
    )

    assert result is None
    assert model == before
