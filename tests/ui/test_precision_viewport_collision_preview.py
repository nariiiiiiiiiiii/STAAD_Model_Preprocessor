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
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def test_repeat_ghost_member_count_matches_preview_when_existing_incidence_is_reused(qtbot) -> None:
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )
    spec = TranslationalRepeatSpec(
        reference_node=_key(1),
        dx=1.0,
        dy=0.0,
        dz=0.0,
        repeats=2,
        connection_mode=RepeatConnectionMode.FROM_REFERENCE,
    )
    resolutions = {2: ExistingNodeResolution.USE_EXISTING}
    preview = analyze_translational_repeat(
        model,
        spec,
        tolerance_m=1e-9,
        resolutions=resolutions,
    )
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    viewport.set_model(model)

    viewport.show_translational_repeat_preview(preview, spec, resolutions)

    assert preview.new_member_count == 1
    assert viewport._precision_ghost_member_count == preview.new_member_count
    assert model.revision == 0
