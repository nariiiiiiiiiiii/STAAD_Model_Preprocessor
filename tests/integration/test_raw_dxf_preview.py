from pathlib import Path

from staadprep.importers.dxf_reader import DxfReader
from staadprep.importers.raw_preview import raw_batch_to_preview_model
from staadprep.model.geometry import Vec3

FIXTURE = Path("tests/golden_models/01_dxf_lines/source.dxf")


def test_raw_preview_does_not_merge_shared_segment_endpoints() -> None:
    batch = DxfReader().read(FIXTURE)
    model = raw_batch_to_preview_model(batch)

    assert len(model.members) == 3
    assert len(model.nodes) == 7
    assert model.metadata.source_format == "dxf-raw"
    assert model.metadata.source_unit == "mm"

    shared_position = Vec3(6000.0, 0.0, 0.0)
    assert sum(node.position == shared_position for node in model.nodes.values()) == 2
