from __future__ import annotations

import pytest

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.model.geometry import Vec3
from staadprep.topology.builder import TopologyPolicy, build_project


def test_shared_and_sub_tolerance_endpoints_become_one_canonical_node() -> None:
    batch = ImportBatch(
        segments=(
            RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), "M1"),
            RawSegment(Vec3(1.0 + 5e-10, 0.0, 0.0), Vec3(2.0, 0.0, 0.0), "M2"),
        ),
        declared_unit="m",
        source_axis="Y-UP",
    )

    model = build_project(batch, TopologyPolicy())

    assert len(model.nodes) == 3
    assert len(model.members) == 2
    first, second = tuple(model.members.values())
    assert first.end == second.start


def test_half_millimetre_gap_remains_disconnected_at_import() -> None:
    batch = ImportBatch(
        segments=(
            RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), "M1"),
            RawSegment(Vec3(1.0005, 0.0, 0.0), Vec3(2.0, 0.0, 0.0), "M2"),
        ),
        declared_unit="m",
        source_axis="Y-UP",
    )

    model = build_project(batch, TopologyPolicy())

    assert len(model.nodes) == 4
    first, second = tuple(model.members.values())
    assert first.end != second.start


def test_raw_points_are_retained_and_source_refs_are_auditable() -> None:
    batch = ImportBatch(
        points=(RawPoint(Vec3(10.0, 0.0, 0.0), "P1", "POINTS"),),
        segments=(
            RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), "M1", "BEAM"),
            RawSegment(Vec3(1.0, 0.0, 0.0), Vec3(2.0, 0.0, 0.0), "M2", "BEAM"),
        ),
        source_format="dxf",
        declared_unit="m",
        source_axis="Y-UP",
        metadata={"source_file": "frame.dxf"},
    )

    model = build_project(batch, TopologyPolicy())

    assert len(model.nodes) == 4
    assert len(model.members) == 2
    shared = next(node for node in model.nodes.values() if node.position == Vec3(1.0, 0.0, 0.0))
    assert shared.source_refs == ("M1", "M2")
    orphan = next(node for node in model.nodes.values() if node.position == Vec3(10.0, 0.0, 0.0))
    assert orphan.source_refs == ("P1",)
    assert {member.source_ref for member in model.members.values()} == {"M1", "M2"}
    assert {member.group for member in model.members.values()} == {"BEAM"}
    assert model.metadata.source_format == "dxf"
    assert model.metadata.source_file == "frame.dxf"
    assert model.metadata.source_unit == "m"
    assert model.metadata.source_axis == "Y-UP"


def test_zero_length_segment_is_retained_for_later_validation() -> None:
    batch = ImportBatch(
        segments=(RawSegment(Vec3(3.0, 2.0, 1.0), Vec3(3.0, 2.0, 1.0), "ZERO"),),
        declared_unit="m",
        source_axis="Y-UP",
    )

    model = build_project(batch, TopologyPolicy())

    assert len(model.nodes) == 1
    assert len(model.members) == 1
    member = next(iter(model.members.values()))
    assert member.start == member.end
    assert member.source_ref == "ZERO"


def test_build_project_rejects_noncanonical_unit_or_axis() -> None:
    raw_mm = ImportBatch(
        segments=(RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(1000.0, 0.0, 0.0), "M1"),),
        declared_unit="mm",
        source_axis="Y-UP",
    )
    raw_z_up = ImportBatch(
        segments=(RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), "M1"),),
        declared_unit="m",
        source_axis="Z-UP",
    )

    with pytest.raises(ValueError, match="canonical metre"):
        build_project(raw_mm, TopologyPolicy())
    with pytest.raises(ValueError, match="Y-UP"):
        build_project(raw_z_up, TopologyPolicy())


def test_topology_policy_rejects_nonpositive_tolerance() -> None:
    with pytest.raises(ValueError, match="positive"):
        TopologyPolicy(coincident_tolerance_m=0.0)


def test_tolerance_search_merges_across_negative_bucket_boundary() -> None:
    batch = ImportBatch(
        points=(
            RawPoint(Vec3(-4e-10, 0.0, 0.0), "P1"),
            RawPoint(Vec3(4e-10, 0.0, 0.0), "P2"),
        ),
        declared_unit="m",
        source_axis="Y-UP",
    )

    model = build_project(batch, TopologyPolicy())

    assert len(model.nodes) == 1
    node = next(iter(model.nodes.values()))
    assert node.source_refs == ("P1", "P2")
