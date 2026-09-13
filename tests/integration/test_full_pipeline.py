from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from staadprep.editing.create_node import (
    RelativeNodeSpec,
    RepeatConnectionMode,
    TranslationalRepeatSpec,
    build_relative_create,
    build_translational_repeat,
)
from staadprep.editing.manual_ops import (
    build_delete_member,
    build_delete_node,
    build_draw_member_existing,
    build_move_or_snap_node,
    build_split_selected_intersection,
)
from staadprep.exporters.staad_std import export_staad_std
from staadprep.importers.contracts import ImportBatch, RawSegment
from staadprep.importers.neutral_reader import NeutralReader
from staadprep.importers.pipeline import canonicalize_import_batch
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.numbering.commands import RenumberAllCommand
from staadprep.numbering.renumber import NumberingPolicy
from staadprep.orientation.commands import SetMemberStart, build_auto_fix_all
from staadprep.repair.audit import write_validation_report
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory
from staadprep.units.transforms import (
    LengthUnit,
    reference_scale_ratio,
    reference_scale_warning,
    transform_batch,
)
from staadprep.validation.issues import IssueSeverity, IssueType
from staadprep.validation.ready_gate import ReadyGate, ReadyPolicy
from staadprep.validation.validators import validate_model

GOLDEN = Path("tests/golden_models")


def _key(value: int) -> UUID:
    return UUID(int=value)


def _raw_case_model(name: str) -> ProjectModel:
    case = json.loads((GOLDEN / name / "case.json").read_text(encoding="utf-8"))
    segments = tuple(
        RawSegment(Vec3(*start), Vec3(*end), source_ref)
        for start, end, source_ref in case["segments"]
    )
    batch = ImportBatch(
        segments=segments,
        source_format="golden",
        declared_unit=case.get("unit", "m"),
        source_axis=case.get("axis", "Y-UP"),
    )
    return canonicalize_import_batch(batch)


def _canonical_dirty_model(name: str) -> ProjectModel:
    case = json.loads((GOLDEN / name / "case.json").read_text(encoding="utf-8"))
    nodes = {_key(item["id"]): Node(_key(item["id"]), Vec3(*item["xyz"])) for item in case["nodes"]}
    members = {
        _key(item["id"]): Member(
            _key(item["id"]),
            _key(item["start"]),
            _key(item["end"]),
        )
        for item in case["members"]
    }
    return ProjectModel(
        nodes=nodes,
        members=members,
        metadata=ModelMetadata(
            source_format="golden-canonical",
            source_unit="m",
            source_axis="Y-UP",
        ),
    )


def _issue_pairs(model: ProjectModel) -> set[tuple[IssueType, IssueSeverity]]:
    return {(issue.type, issue.severity) for issue in validate_model(model)}


def test_clean_frame_runs_import_transform_topology_validate_without_issues() -> None:
    model = _raw_case_model("01_clean_frame")

    assert len(model.nodes) == 4
    assert len(model.members) == 4
    assert validate_model(model) == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("02_orphan_node", {(IssueType.ORPHAN_NODE, IssueSeverity.ERROR)}),
        (
            "03_near_nodes",
            {
                (IssueType.NEAR_NODE, IssueSeverity.WARNING),
                (IssueType.UNCONNECTED_GAP, IssueSeverity.ERROR),
                (IssueType.DISCONNECTED_STRUCTURE, IssueSeverity.WARNING),
            },
        ),
        ("04_duplicate_member", {(IssueType.DUPLICATE_MEMBER, IssueSeverity.ERROR)}),
        (
            "05_short_member",
            {
                (IssueType.SHORT_MEMBER, IssueSeverity.WARNING),
                (IssueType.ZERO_LENGTH_MEMBER, IssueSeverity.ERROR),
                (IssueType.DISCONNECTED_STRUCTURE, IssueSeverity.WARNING),
            },
        ),
        (
            "09_crossing_without_node",
            {
                (IssueType.CROSSING_WITHOUT_NODE, IssueSeverity.ERROR),
                (IssueType.DISCONNECTED_STRUCTURE, IssueSeverity.WARNING),
            },
        ),
        (
            "10_combined_dirty_frame",
            {
                (IssueType.DUPLICATE_NODE, IssueSeverity.ERROR),
                (IssueType.NEAR_NODE, IssueSeverity.WARNING),
                (IssueType.ORPHAN_NODE, IssueSeverity.ERROR),
                (IssueType.ZERO_LENGTH_MEMBER, IssueSeverity.ERROR),
                (IssueType.SHORT_MEMBER, IssueSeverity.WARNING),
                (IssueType.DUPLICATE_MEMBER, IssueSeverity.ERROR),
                (IssueType.UNCONNECTED_GAP, IssueSeverity.ERROR),
                (IssueType.CROSSING_WITHOUT_NODE, IssueSeverity.ERROR),
                (IssueType.DISCONNECTED_STRUCTURE, IssueSeverity.WARNING),
            },
        ),
    ],
)
def test_canonical_dirty_golden_issue_sets_are_exact(
    name: str,
    expected: set[tuple[IssueType, IssueSeverity]],
) -> None:
    # These fixtures intentionally represent canonical dirty states after T07.
    # Exact coincident raw endpoints would be merged by T07 and therefore cannot
    # exercise T08 DUPLICATE_NODE detection as raw-source fixtures.
    model = _canonical_dirty_model(name)

    assert _issue_pairs(model) == expected


def test_disconnected_raw_fixture_runs_full_pipeline_and_is_policy_blocking_warning() -> None:
    model = _raw_case_model("06_disconnected_structures")
    issues = validate_model(model)

    assert _issue_pairs(model) == {(IssueType.DISCONNECTED_STRUCTURE, IssueSeverity.WARNING)}
    for index, node in enumerate(model.nodes.values(), start=1):
        node.number = index
    for index, member in enumerate(model.members.values(), start=1):
        member.number = index
    status = ReadyGate(ReadyPolicy(block_disconnected_structure=True)).evaluate(model, issues)
    assert not status.ready
    assert "disconnected-structure" in status.blockers


def test_wrong_scale_fixture_requires_reference_verification_before_ready() -> None:
    case = json.loads((GOLDEN / "07_wrong_scale" / "case.json").read_text(encoding="utf-8"))

    ratio = reference_scale_ratio(case["measured_m"], case["expected_m"])
    warning = reference_scale_warning(case["measured_m"], case["expected_m"])

    assert ratio == pytest.approx(case["expected_ratio"])
    assert warning is not None
    assert f"{case['expected_warning_factor']:g}" in warning

    model = _raw_case_model("01_clean_frame")
    for index, node in enumerate(model.nodes.values(), start=1):
        node.number = index
    for index, member in enumerate(model.members.values(), start=1):
        member.number = index
    blocked = ReadyGate(
        ReadyPolicy(require_reference_dimension=True),
        reference_dimension_verified=False,
    ).evaluate(model, validate_model(model))
    verified = ReadyGate(
        ReadyPolicy(require_reference_dimension=True),
        reference_dimension_verified=True,
    ).evaluate(model, validate_model(model))

    assert not blocked.ready
    assert verified.ready


def test_wrong_axis_fixture_maps_source_to_staad_y_up_before_topology() -> None:
    case = json.loads((GOLDEN / "08_wrong_axis" / "case.json").read_text(encoding="utf-8"))
    source = Vec3(*case["source_point"])
    batch = ImportBatch(
        segments=(RawSegment(Vec3(0.0, 0.0, 0.0), source, "M1"),),
        source_format="golden",
        declared_unit="m",
        source_axis="Z-UP",
    )

    canonical = transform_batch(batch, LengthUnit.METER, "Z-UP")
    model = canonicalize_import_batch(batch)

    assert canonical.segments[0].end.as_tuple() == pytest.approx(case["expected_staad_y_up"])
    assert {node.position.as_tuple() for node in model.nodes.values()} == {
        (0.0, 0.0, 0.0),
        tuple(case["expected_staad_y_up"]),
    }
    assert validate_model(model) == []


def test_sketchup_neutral_golden_runs_reader_transform_topology_validate(tmp_path: Path) -> None:
    bundle = json.loads(
        (GOLDEN / "11_sketchup_ruby_simple_frame" / "expected.json").read_text(encoding="utf-8")
    )
    reader = NeutralReader(tmp_path / "project")
    reader.inbox.mkdir(parents=True, exist_ok=True)
    path = reader.inbox / "frame.json"
    path.write_text(json.dumps(bundle["neutral"]), encoding="utf-8")

    model = canonicalize_import_batch(reader.read(path))

    assert len(model.nodes) == len(bundle["expected_canonical_nodes_m"])
    assert len(model.members) == bundle["expected_member_count"]
    assert validate_model(model) == []


def _parse_std_geometry(
    path: Path,
) -> tuple[
    dict[int, tuple[float, float, float]],
    dict[int, tuple[int, int]],
]:
    nodes: dict[int, tuple[float, float, float]] = {}
    members: dict[int, tuple[int, int]] = {}
    section: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "JOINT COORDINATES":
            section = "nodes"
            continue
        if line == "MEMBER INCIDENCES":
            section = "members"
            continue
        if line == "FINISH":
            break
        if not line or line.startswith("STAAD ") or line.startswith("UNIT "):
            continue
        fields = line.rstrip(";").split()
        if section == "nodes":
            number, x, y, z = fields
            nodes[int(number)] = (float(x), float(y), float(z))
        elif section == "members":
            number, start, end = fields
            members[int(number)] = (int(start), int(end))
    return nodes, members


def _position_key(point: Vec3) -> tuple[float, float, float]:
    return point.as_tuple()


def _member_position_key(
    model: ProjectModel, member: Member
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    endpoints = sorted(
        (
            model.nodes[member.start].position.as_tuple(),
            model.nodes[member.end].position.as_tuple(),
        )
    )
    return endpoints[0], endpoints[1]


def test_combined_dirty_fixture_repairs_through_history_to_hand_authored_graph() -> None:
    model = _canonical_dirty_model("10_combined_dirty_frame")
    history = RepairHistory(model)

    # Exact duplicate-member deletion.
    history.execute(build_delete_member(_key(104)))
    # Near-node Move/Snap uses the existing MergeNodes command path.
    history.execute(
        build_move_or_snap_node(
            _key(3),
            model.nodes[_key(2)].position,
            snap_node_key=_key(2),
        )
    )
    # Remove zero/short artifacts and their now-orphaned nodes.
    history.execute(build_delete_member(_key(105)))
    history.execute(build_delete_member(_key(106)))
    history.execute(build_delete_node(_key(13)))
    history.execute(build_delete_member(_key(109)))
    history.execute(build_delete_node(_key(7)))
    history.execute(build_delete_node(_key(8)))

    # Resolve the unsplit crossing through the existing intersection command.
    history.execute(build_split_selected_intersection(model, _key(107), _key(108)))

    # Draw missing members to join both detached structural regions to the primary structure.
    history.execute(build_draw_member_existing(_key(4), _key(5)))
    history.execute(build_draw_member_existing(_key(1), _key(9)))

    # Relative Node + Member creation.
    relative = build_relative_create(
        model,
        RelativeNodeSpec(
            reference_node=_key(6),
            dx=0.0,
            dy=2.0,
            dz=0.0,
            create_member=True,
        ),
        tolerance_m=1e-9,
    )
    assert isinstance(relative, CompositeRepair)
    history.execute(relative)
    relative_key = next(
        key for key, node in model.nodes.items() if node.position == Vec3(21.0, 2.0, 0.0)
    )

    # Translational Repeat, connected consecutively, remains one atomic history item.
    repeat = build_translational_repeat(
        model,
        TranslationalRepeatSpec(
            reference_node=relative_key,
            dx=2.0,
            dy=0.0,
            dz=0.0,
            repeats=2,
            connection_mode=RepeatConnectionMode.CONSECUTIVE,
        ),
        resolutions={},
        tolerance_m=1e-9,
    )
    assert isinstance(repeat, CompositeRepair)
    history.execute(repeat)

    expected = json.loads(
        (GOLDEN / "10_combined_dirty_frame" / "expected_manual_clean.json").read_text(
            encoding="utf-8"
        )
    )
    expected_positions = {tuple(point) for point in expected["node_positions"]}
    expected_edges = {
        tuple(sorted((tuple(pair[0]), tuple(pair[1]))))
        for pair in expected["member_endpoint_positions"]
    }
    actual_positions = {_position_key(node.position) for node in model.nodes.values()}
    actual_edges = {_member_position_key(model, member) for member in model.members.values()}

    assert actual_positions == expected_positions
    assert actual_edges == expected_edges
    assert validate_model(model) == []
    assert len(history.audit.entries) == len(history.undo_stack)

    # Direction control changes incidence only; geometry/identity/numbering are untouched.
    before_direction_positions = {
        key: node.position.as_tuple() for key, node in model.nodes.items()
    }
    before_direction_numbers = (
        {key: node.number for key, node in model.nodes.items()},
        {key: member.number for key, member in model.members.items()},
    )
    member_101 = model.members[_key(101)]
    original_101 = (member_101.start, member_101.end)
    direction = SetMemberStart(_key(101), original_101[1]).build(model)
    assert direction is not None
    history.execute(direction)
    assert set(model.nodes) == set(before_direction_positions)
    assert {
        key: node.position.as_tuple() for key, node in model.nodes.items()
    } == before_direction_positions
    assert (
        {key: node.number for key, node in model.nodes.items()},
        {key: member.number for key, member in model.members.items()},
    ) == before_direction_numbers
    assert (model.members[_key(101)].start, model.members[_key(101)].end) == (
        original_101[1],
        original_101[0],
    )

    auto_fix = build_auto_fix_all(model)
    assert auto_fix is not None
    history.execute(auto_fix)
    assert (model.members[_key(101)].start, model.members[_key(101)].end) == original_101
    assert {
        key: node.position.as_tuple() for key, node in model.nodes.items()
    } == before_direction_positions

    # Numbering control changes numbers only and preserves UUID keys/incidence.
    before_numbering_positions = {
        key: node.position.as_tuple() for key, node in model.nodes.items()
    }
    before_numbering_incidence = {
        key: (member.start, member.end) for key, member in model.members.items()
    }
    node_keys = set(model.nodes)
    member_keys = set(model.members)
    history.execute(RenumberAllCommand(NumberingPolicy()))
    assert set(model.nodes) == node_keys
    assert set(model.members) == member_keys
    assert {
        key: node.position.as_tuple() for key, node in model.nodes.items()
    } == before_numbering_positions
    assert {
        key: (member.start, member.end) for key, member in model.members.items()
    } == before_numbering_incidence
    assert all(node.number is not None and node.number > 0 for node in model.nodes.values())
    assert all(member.number is not None and member.number > 0 for member in model.members.values())
    final_issues = validate_model(model)
    ready_status = ReadyGate().evaluate(model, final_issues)
    assert ready_status.ready

    # Export then parse with a test-only parser independent from exporter formatting helpers.
    std_path = Path(".tmp/tests/t21/full_pipeline.std")
    export_report = export_staad_std(model, std_path)
    parsed_nodes, parsed_members = _parse_std_geometry(export_report.path)
    expected_numbered_nodes = {
        node.number: node.position.as_tuple()
        for node in model.nodes.values()
        if node.number is not None
    }
    expected_numbered_members = {
        member.number: (
            model.nodes[member.start].number,
            model.nodes[member.end].number,
        )
        for member in model.members.values()
        if member.number is not None
    }
    assert parsed_nodes == expected_numbered_nodes
    assert parsed_members == expected_numbered_members

    report_path = write_validation_report(
        Path(".tmp/tests/t21/full_pipeline_report.json"),
        model=model,
        issues=final_issues,
        ready_status=ready_status,
        audit_entries=history.audit.entries,
        export_report=export_report,
    )
    report_payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_payload["readiness"]["ready"] is True
    assert report_payload["issue_summary"] == {"ERROR": 0, "WARNING": 0, "INFO": 0}
    assert report_payload["direction_status"]["normalized"] is True
    assert report_payload["export_status"]["exported"] is True
