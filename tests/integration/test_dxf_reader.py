from pathlib import Path

from staadprep.importers.dxf_reader import DxfReader
from staadprep.model.geometry import Vec3

FIXTURE = Path("tests/golden_models/01_dxf_lines/source.dxf")


def test_reads_raw_line_polyline_point_and_insunits_without_conversion() -> None:
    batch = DxfReader().read(FIXTURE)

    assert batch.source_format == "dxf"
    assert batch.declared_unit == "mm"
    assert batch.source_axis == "Z-UP"
    assert batch.metadata["insunits_code"] == 4
    assert len(batch.segments) == 3
    assert len(batch.points) == 1

    assert batch.segments[0].start == Vec3(0.0, 0.0, 0.0)
    assert batch.segments[0].end == Vec3(6000.0, 0.0, 0.0)
    assert batch.segments[0].layer == "BEAM"

    assert batch.segments[1].start == Vec3(6000.0, 0.0, 0.0)
    assert batch.segments[1].end == Vec3(6000.0, 3000.0, 0.0)
    assert batch.segments[1].layer == "FRAME"

    assert batch.segments[2].start == Vec3(6000.0, 3000.0, 0.0)
    assert batch.segments[2].end == Vec3(6000.0, 3000.0, 4000.0)
    assert batch.segments[2].layer == "FRAME"

    assert batch.points[0].position == Vec3(1234.0, 567.0, 89.0)
    assert batch.points[0].layer == "POINTS"
