from __future__ import annotations

from uuid import UUID

from staadprep.editing.create_node import (
    ExistingNodeResolution,
    RepeatConnectionMode,
    TranslationalRepeatSpec,
    analyze_translational_repeat,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_use_existing_preview_does_not_count_already_existing_connection_as_new_member() -> None:
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    spec = TranslationalRepeatSpec(
        _key(1),
        1.0,
        0.0,
        0.0,
        2,
        RepeatConnectionMode.FROM_REFERENCE,
    )

    preview = analyze_translational_repeat(
        model,
        spec,
        tolerance_m=1e-6,
        resolutions={2: ExistingNodeResolution.USE_EXISTING},
    )

    assert preview.new_node_count == 1
    assert preview.reused_node_count == 1
    assert preview.new_member_count == 1
