from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.topology.builder import TopologyPolicy, build_project
from staadprep.topology.connectivity import connected_components

GOLDEN = Path("tests/golden_models/06_disconnected_structures/case.json")


def _vec(values: list[float]) -> Vec3:
    return Vec3(float(values[0]), float(values[1]), float(values[2]))


def test_connected_components_match_hand_authored_disconnected_structure_case() -> None:
    case = json.loads(GOLDEN.read_text(encoding="utf-8"))
    batch = ImportBatch(
        segments=tuple(
            RawSegment(_vec(start), _vec(end), source_ref)
            for start, end, source_ref in case["segments"]
        ),
        declared_unit=case["unit"],
        source_axis=case["axis"],
    )
    model = build_project(batch, TopologyPolicy())

    components = connected_components(model)

    actual_counts = [(len(c.node_keys), len(c.member_keys)) for c in components]
    expected_counts = [
        (item["nodes"], item["members"]) for item in case["expected_components"]
    ]
    assert actual_counts == expected_counts
    assert set().union(*(set(c.node_keys) for c in components)) == set(model.nodes)
    assert set().union(*(set(c.member_keys) for c in components)) == set(model.members)


def test_isolated_raw_point_is_its_own_zero_member_component() -> None:
    batch = ImportBatch(
        points=(RawPoint(Vec3(50.0, 0.0, 0.0), "P1"),),
        segments=(RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0), "M1"),),
        declared_unit="m",
        source_axis="Y-UP",
    )
    model = build_project(batch, TopologyPolicy())

    components = connected_components(model)

    assert [(len(c.node_keys), len(c.member_keys)) for c in components] == [(2, 1), (1, 0)]


def test_connected_components_rejects_dangling_member_reference() -> None:
    node = Node(UUID(int=1), Vec3(0.0, 0.0, 0.0))
    dangling = Member(UUID(int=101), node.key, UUID(int=999))
    model = ProjectModel(nodes={node.key: node}, members={dangling.key: dangling})

    with pytest.raises(ValueError, match="missing node"):
        connected_components(model)


def test_zero_length_member_remains_in_single_node_component() -> None:
    batch = ImportBatch(
        segments=(RawSegment(Vec3(2.0, 2.0, 2.0), Vec3(2.0, 2.0, 2.0), "ZERO"),),
        declared_unit="m",
        source_axis="Y-UP",
    )
    model = build_project(batch, TopologyPolicy())

    components = connected_components(model)

    assert len(components) == 1
    assert len(components[0].node_keys) == 1
    assert len(components[0].member_keys) == 1
