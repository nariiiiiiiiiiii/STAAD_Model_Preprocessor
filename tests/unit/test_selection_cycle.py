from __future__ import annotations

from uuid import UUID

from staadprep.viewer.interaction import SelectionFilter
from staadprep.viewer.selection import (
    SelectionCandidate,
    SelectionEntity,
    SelectionState,
    filter_candidates,
    next_overlap_candidate,
)

NODE_A = UUID("00000000-0000-0000-0000-000000000001")
NODE_B = UUID("00000000-0000-0000-0000-000000000002")
MEMBER_A = UUID("00000000-0000-0000-0000-000000000003")


def test_overlap_candidates_cycle_in_entity_type_then_uuid_order() -> None:
    candidates = (
        SelectionCandidate(SelectionEntity.MEMBER, MEMBER_A),
        SelectionCandidate(SelectionEntity.NODE, NODE_B),
        SelectionCandidate(SelectionEntity.NODE, NODE_A),
    )

    first = next_overlap_candidate(candidates, None)
    second = next_overlap_candidate(candidates, first)
    third = next_overlap_candidate(candidates, second)
    wrapped = next_overlap_candidate(candidates, third)

    assert first == SelectionCandidate(SelectionEntity.NODE, NODE_A)
    assert second == SelectionCandidate(SelectionEntity.NODE, NODE_B)
    assert third == SelectionCandidate(SelectionEntity.MEMBER, MEMBER_A)
    assert wrapped == first


def test_selection_filter_removes_disallowed_candidate_types() -> None:
    candidates = (
        SelectionCandidate(SelectionEntity.NODE, NODE_A),
        SelectionCandidate(SelectionEntity.MEMBER, MEMBER_A),
    )
    assert filter_candidates(candidates, SelectionFilter(nodes=False, members=True)) == (
        SelectionCandidate(SelectionEntity.MEMBER, MEMBER_A),
    )


def test_additive_toggle_selection_is_deterministic() -> None:
    state = SelectionState()
    state.select_member(MEMBER_A, additive=False)
    assert state.selected_members == (MEMBER_A,)

    state.select_node(NODE_A, additive=True)
    assert state.selected_nodes == (NODE_A,)
    assert state.selected_members == (MEMBER_A,)

    state.select_node(NODE_A, additive=True)
    assert state.selected_nodes == ()
    assert state.selected_members == (MEMBER_A,)
