from __future__ import annotations

from copy import deepcopy
from uuid import UUID

import pytest

from staadprep.editing.create_node import (
    ExistingNodeResolution,
    MemberRepeatResolutionRequired,
    MemberTranslationalRepeatSpec,
    analyze_member_translational_repeat,
    build_member_translational_repeat,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _chain() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(8.0, 0.0, 0.0)),
        },
        members={
            _key(101): Member(
                _key(101), _key(1), _key(2), source_ref="A", group="Roof"
            ),
            _key(102): Member(
                _key(102), _key(2), _key(3), source_ref="B", group="Roof"
            ),
        },
        revision=4,
    )


def _incidence_positions(
    model: ProjectModel,
) -> set[tuple[tuple[float, float, float], tuple[float, float, float]]]:
    return {
        (
            model.nodes[member.start].position.as_tuple(),
            model.nodes[member.end].position.as_tuple(),
        )
        for member in model.members.values()
    }


def test_member_repeat_preview_preserves_shared_nodes_and_exact_counts() -> None:
    model = _chain()
    spec = MemberTranslationalRepeatSpec(
        (_key(101), _key(102)),
        dx=0.0,
        dy=3.0,
        dz=0.0,
        repeats=2,
    )

    preview = analyze_member_translational_repeat(model, spec, tolerance_m=1e-6)

    assert preview.source_node_count == 3
    assert preview.new_node_count == 6
    assert preview.new_member_count == 4
    assert preview.reused_node_count == 0
    assert preview.collisions == {}


def test_member_repeat_is_atomic_preserves_incidence_metadata_and_undoes_exactly() -> None:
    model = _chain()
    before = deepcopy(model)
    spec = MemberTranslationalRepeatSpec(
        (_key(101), _key(102)), 0.0, 3.0, 0.0, 2
    )
    command = build_member_translational_repeat(
        model,
        spec,
        resolutions={},
        tolerance_m=1e-6,
    )

    assert isinstance(command, CompositeRepair)
    history = RepairHistory(model)
    history.execute(command)

    assert len(model.nodes) == 9
    assert len(model.members) == 6
    assert _incidence_positions(model) == {
        ((0.0, 0.0, 0.0), (4.0, 0.0, 0.0)),
        ((4.0, 0.0, 0.0), (8.0, 0.0, 0.0)),
        ((0.0, 3.0, 0.0), (4.0, 3.0, 0.0)),
        ((4.0, 3.0, 0.0), (8.0, 3.0, 0.0)),
        ((0.0, 6.0, 0.0), (4.0, 6.0, 0.0)),
        ((4.0, 6.0, 0.0), (8.0, 6.0, 0.0)),
    }
    copied = [member for key, member in model.members.items() if key not in before.members]
    assert sorted((member.source_ref, member.group) for member in copied) == [
        ("A", "Roof"),
        ("A", "Roof"),
        ("B", "Roof"),
        ("B", "Roof"),
    ]
    assert all(member.number is None for member in copied)
    assert len(history.undo_stack) == 1

    history.undo()
    assert model == before


def test_member_repeat_collision_requires_explicit_resolution_and_can_reuse_node() -> None:
    model = _chain()
    model.nodes[_key(20)] = Node(_key(20), Vec3(0.0, 3.0, 0.0))
    spec = MemberTranslationalRepeatSpec((_key(101),), 0.0, 3.0, 0.0, 1)

    unresolved = build_member_translational_repeat(
        model,
        spec,
        resolutions={},
        tolerance_m=1e-6,
    )

    assert isinstance(unresolved, MemberRepeatResolutionRequired)
    collision_key = (1, _key(1))
    assert unresolved.collisions == {collision_key: _key(20)}

    command = build_member_translational_repeat(
        model,
        spec,
        resolutions={collision_key: ExistingNodeResolution.USE_EXISTING},
        tolerance_m=1e-6,
    )
    assert isinstance(command, CompositeRepair)
    RepairHistory(model).execute(command)
    assert len(model.nodes) == 5
    assert ((0.0, 3.0, 0.0), (4.0, 3.0, 0.0)) in _incidence_positions(model)


def test_member_repeat_rejects_duplicate_incidence_and_invalid_specs_without_mutation() -> None:
    model = _chain()
    model.nodes[_key(20)] = Node(_key(20), Vec3(0.0, 3.0, 0.0))
    model.nodes[_key(21)] = Node(_key(21), Vec3(4.0, 3.0, 0.0))
    model.members[_key(120)] = Member(_key(120), _key(20), _key(21))
    before = deepcopy(model)
    spec = MemberTranslationalRepeatSpec((_key(101),), 0.0, 3.0, 0.0, 1)
    resolutions = {
        (1, _key(1)): ExistingNodeResolution.USE_EXISTING,
        (1, _key(2)): ExistingNodeResolution.USE_EXISTING,
    }

    with pytest.raises(ValueError, match="duplicate incidence"):
        build_member_translational_repeat(
            model,
            spec,
            resolutions=resolutions,
            tolerance_m=1e-6,
        )
    assert model == before

    with pytest.raises(ValueError, match="step vector"):
        analyze_member_translational_repeat(
            model,
            MemberTranslationalRepeatSpec((_key(101),), 0.0, 0.0, 0.0, 1),
            tolerance_m=1e-6,
        )
    with pytest.raises(ValueError, match="does not exist"):
        analyze_member_translational_repeat(
            model,
            MemberTranslationalRepeatSpec((_key(999),), 1.0, 0.0, 0.0, 1),
            tolerance_m=1e-6,
        )


def test_member_repeat_reuses_coincident_targets_between_repeat_steps() -> None:
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    spec = MemberTranslationalRepeatSpec((_key(101),), 4.0, 0.0, 0.0, 2)
    resolutions = {
        (1, _key(1)): ExistingNodeResolution.USE_EXISTING,
    }

    preview = analyze_member_translational_repeat(
        model,
        spec,
        tolerance_m=1e-6,
        resolutions=resolutions,
    )
    command = build_member_translational_repeat(
        model,
        spec,
        resolutions=resolutions,
        tolerance_m=1e-6,
    )

    assert preview.new_node_count == 2
    assert preview.reused_node_count == 1
    assert isinstance(command, CompositeRepair)
    RepairHistory(model).execute(command)
    assert len(model.nodes) == 4
    assert len(model.members) == 3
    assert ((4.0, 0.0, 0.0), (8.0, 0.0, 0.0)) in _incidence_positions(model)
    assert ((8.0, 0.0, 0.0), (12.0, 0.0, 0.0)) in _incidence_positions(model)
