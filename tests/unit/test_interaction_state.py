from __future__ import annotations

from staadprep.viewer.interaction import (
    EditMode,
    InteractionState,
    LabelVisibility,
    SelectionFilter,
)


def test_select_is_default_and_not_geometry_editing() -> None:
    state = InteractionState()
    assert state.mode is EditMode.SELECT
    assert not state.allows_geometry_drag


def test_move_snap_is_the_only_node_drag_mode() -> None:
    for mode in EditMode:
        state = InteractionState(mode=mode)
        assert state.allows_geometry_drag is (mode is EditMode.MOVE_SNAP_NODE)


def test_selection_filter_can_restrict_entity_types() -> None:
    members_only = SelectionFilter(nodes=False, members=True)
    assert not members_only.nodes
    assert members_only.members

    nodes_only = SelectionFilter(nodes=True, members=False)
    assert nodes_only.nodes
    assert not nodes_only.members


def test_label_visibility_defaults_off_and_is_immutable() -> None:
    labels = LabelVisibility()
    assert not labels.node_numbers
    assert not labels.member_numbers
    assert not labels.local_x
    assert not labels.coordinates
