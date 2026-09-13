from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import UUID

import pytest

from staadprep.exporters.staad_std import StaadExportError, export_staad_std
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel

GOLDEN = Path("tests/golden_models/01_clean_frame/expected.std")
OUTPUT_ROOT = Path(".tmp/tests/t13")


def _output(name: str) -> Path:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    return OUTPUT_ROOT / name


def _key(value: int) -> UUID:
    return UUID(int=value)


def _clean_model() -> ProjectModel:
    node_1 = Node(_key(1), Vec3(0.0, 0.0, -0.0), number=1)
    node_2 = Node(_key(2), Vec3(6.0, 0.0, 0.0), number=2)
    member = Member(_key(101), node_1.key, node_2.key, number=1)
    return ProjectModel(
        nodes={node_1.key: node_1, node_2.key: node_2},
        members={member.key: member},
    )


def _parse_std_geometry(
    text: str,
) -> tuple[dict[int, tuple[float, float, float]], dict[int, tuple[int, int]]]:
    """Independent test-only parser for the exact geometry subset emitted by T13."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    joint_start = lines.index("JOINT COORDINATES") + 1
    member_start = lines.index("MEMBER INCIDENCES")
    finish = lines.index("FINISH")

    joints: dict[int, tuple[float, float, float]] = {}
    for line in lines[joint_start:member_start]:
        fields = line.removesuffix(";").split()
        joints[int(fields[0])] = (float(fields[1]), float(fields[2]), float(fields[3]))

    members: dict[int, tuple[int, int]] = {}
    for line in lines[member_start + 1 : finish]:
        fields = line.removesuffix(";").split()
        members[int(fields[0])] = (int(fields[1]), int(fields[2]))
    return joints, members


def test_export_matches_exact_golden_text() -> None:
    path = _output("clean.std")

    report = export_staad_std(_clean_model(), path)

    assert path.read_text(encoding="utf-8") == GOLDEN.read_text(encoding="utf-8")
    assert report.path == path.resolve()
    assert report.node_count == 2
    assert report.member_count == 1


def test_numeric_format_is_locale_independent_compact_and_normalizes_negative_zero() -> None:
    node_1 = Node(_key(1), Vec3(-0.0, 1.250000000000000, 0.000001), number=1)
    node_2 = Node(_key(2), Vec3(1234.5, -2.5, 3.125), number=2)
    member = Member(_key(101), node_1.key, node_2.key, number=1)
    model = ProjectModel(
        nodes={node_2.key: node_2, node_1.key: node_1},
        members={member.key: member},
    )
    path = _output("numbers.std")

    export_staad_std(model, path)
    text = path.read_text(encoding="utf-8")

    assert "1 0 1.25 0.000001;" in text
    assert "e-" not in text.lower()
    assert "2 1234.5 -2.5 3.125;" in text
    assert " -0 " not in text
    assert "1,25" not in text


def test_export_order_uses_staad_numbers_not_dictionary_insertion_order() -> None:
    node_1 = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1)
    node_2 = Node(_key(2), Vec3(1.0, 0.0, 0.0), number=2)
    node_3 = Node(_key(3), Vec3(2.0, 0.0, 0.0), number=3)
    member_1 = Member(_key(101), node_1.key, node_2.key, number=1)
    member_2 = Member(_key(102), node_2.key, node_3.key, number=2)
    model = ProjectModel(
        nodes={node_3.key: node_3, node_1.key: node_1, node_2.key: node_2},
        members={member_2.key: member_2, member_1.key: member_1},
    )
    path = _output("ordered.std")

    export_staad_std(model, path)
    lines = path.read_text(encoding="utf-8").splitlines()

    assert lines[3:6] == ["1 0 0 0;", "2 1 0 0;", "3 2 0 0;"]
    assert lines[7:9] == ["1 1 2;", "2 2 3;"]


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda model: setattr(model.nodes[_key(1)], "number", None), "node.*number"),
        (
            lambda model: setattr(model.members[_key(101)], "number", None),
            "member.*number",
        ),
        (lambda model: setattr(model.nodes[_key(1)], "number", 0), "node.*positive"),
        (
            lambda model: setattr(model.members[_key(101)], "number", -1),
            "member.*positive",
        ),
        (lambda model: setattr(model.nodes[_key(2)], "number", 1), "duplicate node"),
    ],
)
def test_export_rejects_invalid_staad_numbers_without_touching_target(
    mutator: Callable[[ProjectModel], None],
    message: str,
) -> None:
    model = _clean_model()
    mutator(model)
    path = _output("existing.std")
    path.write_text("KEEP\n", encoding="utf-8")

    with pytest.raises(StaadExportError, match=message):
        export_staad_std(model, path)

    assert path.read_text(encoding="utf-8") == "KEEP\n"


def test_export_rejects_duplicate_member_numbers() -> None:
    model = _clean_model()
    second = Member(_key(102), _key(2), _key(1), number=1)
    model.members[second.key] = second

    with pytest.raises(StaadExportError, match="duplicate member"):
        export_staad_std(model, _output("duplicate_member.std"))


def test_export_rejects_dangling_member_reference_before_writing() -> None:
    model = _clean_model()
    model.members[_key(101)].end = _key(999)
    path = _output("dangling.std")

    with pytest.raises(StaadExportError, match="missing node"):
        export_staad_std(model, path)

    assert not path.exists()


def test_export_rejects_critical_validation_error() -> None:
    model = _clean_model()
    duplicate = Member(_key(102), _key(2), _key(1), number=2)
    model.members[duplicate.key] = duplicate

    with pytest.raises(StaadExportError, match="validation.*ERROR"):
        export_staad_std(model, _output("dirty.std"))


def test_export_rejects_empty_model() -> None:
    path = _output("empty.std")
    with pytest.raises(StaadExportError, match="at least one node"):
        export_staad_std(ProjectModel(), path)


def test_decimal_format_round_trips_tricky_float_without_scientific_notation() -> None:
    a = Node(_key(1), Vec3(0.1 + 0.2, 1e-12, 1e12), number=1)
    b = Node(_key(2), Vec3(1.0, 2.0, 3.0), number=2)
    member = Member(_key(101), a.key, b.key, number=1)
    model = ProjectModel(nodes={a.key: a, b.key: b}, members={member.key: member})
    path = _output("tricky.std")

    export_staad_std(model, path)
    text = path.read_text(encoding="utf-8")
    joints, _ = _parse_std_geometry(text)

    joint_section = text.split("JOINT COORDINATES\n", 1)[1].split("MEMBER INCIDENCES", 1)[0]
    assert "e" not in joint_section.lower()
    assert joints[1] == a.position.as_tuple()


def test_independent_parser_round_trips_canonical_coordinates_and_incidences() -> None:
    model = _clean_model()
    path = _output("roundtrip.std")

    export_staad_std(model, path)
    joints, incidences = _parse_std_geometry(path.read_text(encoding="utf-8"))

    expected_joints = {
        node.number: node.position.as_tuple()
        for node in model.nodes.values()
        if node.number is not None
    }
    expected_incidences = {
        member.number: (
            model.nodes[member.start].number,
            model.nodes[member.end].number,
        )
        for member in model.members.values()
        if member.number is not None
    }
    assert joints == expected_joints
    assert incidences == expected_incidences
