from __future__ import annotations

from pathlib import Path

from staadprep.importers.dxf_reader import DxfReader
from staadprep.model.geometry import Vec3
from staadprep.topology.builder import TopologyPolicy, build_project
from staadprep.topology.connectivity import connected_components
from staadprep.units.transforms import LengthUnit, transform_batch

FIXTURE = Path("tests/golden_models/01_dxf_lines/source.dxf")


def test_dxf_to_canonical_topology_matches_independent_expected_geometry() -> None:
    raw = DxfReader().read(FIXTURE)
    canonical_batch = transform_batch(raw, LengthUnit.MILLIMETER, "Z-UP")

    model = build_project(canonical_batch, TopologyPolicy())
    components = connected_components(model)

    expected_positions = {
        Vec3(0.0, 0.0, 0.0),
        Vec3(6.0, 0.0, 0.0),
        Vec3(6.0, 0.0, -3.0),
        Vec3(6.0, 4.0, -3.0),
        Vec3(1.234, 0.089, -0.5670000000000001),
    }
    assert {node.position for node in model.nodes.values()} == expected_positions
    assert len(model.nodes) == 5
    assert len(model.members) == 3
    assert [(len(c.node_keys), len(c.member_keys)) for c in components] == [(4, 3), (1, 0)]

    for member in model.members.values():
        assert member.start in model.nodes
        assert member.end in model.nodes
