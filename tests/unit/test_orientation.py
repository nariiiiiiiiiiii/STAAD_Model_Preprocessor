from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import (
    MemberClass,
    NormalizeMemberDirection,
    classify_member,
    needs_reverse,
    normalization_commands,
)
from staadprep.repair.commands import ReverseMember


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model(start: Vec3, end: Vec3) -> tuple[ProjectModel, Member]:
    a = Node(_key(1), start)
    b = Node(_key(2), end)
    member = Member(_key(101), a.key, b.key)
    return ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
    ), member


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (Vec3(0.0, 0.0, 0.0), Vec3(0.0, 3.0, 0.0), MemberClass.COLUMN),
        (Vec3(0.0, 0.0, 0.0), Vec3(4.0, 0.0, 0.0), MemberClass.BEAM_X),
        (Vec3(0.0, 0.0, 0.0), Vec3(0.0, 0.0, 5.0), MemberClass.BEAM_Z),
        (Vec3(0.0, 0.0, 0.0), Vec3(3.0, 2.0, 0.0), MemberClass.BRACE),
        (Vec3(1.0, 1.0, 1.0), Vec3(1.0, 1.0, 1.0), MemberClass.OTHER),
    ],
)
def test_classify_member_uses_y_up_geometric_classes(
    start: Vec3,
    end: Vec3,
    expected: MemberClass,
) -> None:
    model, member = _model(start, end)

    assert classify_member(model, member, tolerance_m=1e-9) is expected


def test_classify_member_treats_sub_tolerance_residual_as_axis_aligned() -> None:
    model, member = _model(Vec3(0.0, 0.0, 0.0), Vec3(4.0, 5e-10, -5e-10))

    assert classify_member(model, member, tolerance_m=1e-9) is MemberClass.BEAM_X


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        # Columns: low Y -> high Y.
        (Vec3(0.0, 3.0, 0.0), Vec3(0.0, 0.0, 0.0), True),
        (Vec3(0.0, 0.0, 0.0), Vec3(0.0, 3.0, 0.0), False),
        # X dominant: low X -> high X.
        (Vec3(5.0, 0.0, 0.0), Vec3(1.0, 2.0, 0.0), True),
        (Vec3(1.0, 2.0, 0.0), Vec3(5.0, 0.0, 0.0), False),
        # Z dominant: low Z -> high Z.
        (Vec3(0.0, 0.0, 6.0), Vec3(1.0, 0.0, 1.0), True),
        (Vec3(1.0, 0.0, 1.0), Vec3(0.0, 0.0, 6.0), False),
        # Tie X/Y: X has priority, even though Y is positive.
        (Vec3(2.0, 0.0, 0.0), Vec3(0.0, 2.0, 0.0), True),
        # Tie Y/Z with X absent: Y has priority.
        (Vec3(0.0, 2.0, 0.0), Vec3(0.0, 0.0, 2.0), True),
        # Zero length has no meaningful direction.
        (Vec3(1.0, 1.0, 1.0), Vec3(1.0, 1.0, 1.0), False),
    ],
)
def test_needs_reverse_follows_dominant_axis_with_xyz_tie_priority(
    start: Vec3,
    end: Vec3,
    expected: bool,
) -> None:
    model, member = _model(start, end)

    assert needs_reverse(model, member) is expected


def test_normalize_member_direction_factory_returns_reversible_command_only_when_needed() -> None:
    model, member = _model(Vec3(4.0, 0.0, 0.0), Vec3(0.0, 0.0, 0.0))

    factory = NormalizeMemberDirection(member.key)
    command = factory.build(model)

    assert isinstance(command, ReverseMember)
    assert command.member_key == member.key

    model.members[member.key] = Member(member.key, member.end, member.start)
    assert factory.build(model) is None


def test_normalization_commands_are_deterministic_and_only_include_reversed_members() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(5.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(0.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, 0.0, 0.0)),
        _key(4): Node(_key(4), Vec3(0.0, 4.0, 0.0)),
        _key(5): Node(_key(5), Vec3(0.0, 0.0, 9.0)),
        _key(6): Node(_key(6), Vec3(0.0, 0.0, 1.0)),
    }
    members = {
        _key(103): Member(_key(103), _key(5), _key(6)),
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)

    commands = normalization_commands(model)

    assert [command.member_key for command in commands] == [_key(101), _key(103)]
