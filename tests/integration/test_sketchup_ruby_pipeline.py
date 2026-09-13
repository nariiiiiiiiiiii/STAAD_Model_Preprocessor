from __future__ import annotations

import json
from pathlib import Path

import pytest

from staadprep.importers.neutral_reader import NeutralReader
from staadprep.topology.builder import TopologyPolicy, build_project
from staadprep.topology.connectivity import connected_components
from staadprep.units.transforms import LengthUnit, transform_batch

GOLDEN = Path("tests/golden_models/11_sketchup_ruby_simple_frame/expected.json")


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def _apply(matrix: list[list[float]], point: list[float]) -> list[float]:
    value = [*point, 1.0]
    return [sum(matrix[r][k] * value[k] for k in range(4)) for r in range(3)]


def test_hand_authored_nested_transform_fixture_is_independently_correct() -> None:
    bundle = json.loads(GOLDEN.read_text(encoding="utf-8"))
    evidence = bundle["transform_fixture"]

    group = [
        [1.0, 0.0, 0.0, 120.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    child = [
        [0.0, -1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 120.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    world = _matmul(group, child)
    start, end = evidence["nested_local_edge"]

    assert _apply(world, start) == evidence["nested_world_edge"][0]
    assert _apply(world, end) == evidence["nested_world_edge"][1]


def test_neutral_to_t06_t07_pipeline_matches_hand_authored_canonical_frame(tmp_path: Path) -> None:
    bundle = json.loads(GOLDEN.read_text(encoding="utf-8"))
    reader = NeutralReader(tmp_path / "project")
    reader.inbox.mkdir(parents=True, exist_ok=True)
    neutral_path = reader.inbox / "nested-frame.json"
    neutral_path.write_text(json.dumps(bundle["neutral"]), encoding="utf-8")

    raw = reader.read(neutral_path)
    assert raw.segments[2].start.as_tuple() == (120.0, 0.0, 120.0)
    assert raw.segments[2].end.as_tuple() == (120.0, 24.0, 120.0)

    canonical_batch = transform_batch(raw, LengthUnit.INCH, raw.source_axis or "")
    model = build_project(canonical_batch, TopologyPolicy())

    actual = sorted(node.position.as_tuple() for node in model.nodes.values())
    expected = sorted(tuple(point) for point in bundle["expected_canonical_nodes_m"])
    assert len(actual) == len(expected)
    for actual_point, expected_point in zip(actual, expected, strict=True):
        assert actual_point == pytest.approx(expected_point, abs=1e-12)
    assert len(model.members) == bundle["expected_member_count"]
    assert len(connected_components(model)) == bundle["expected_structure_count"]
