from __future__ import annotations

from pathlib import Path

import pytest

from staadprep.importers.contracts import ImportBatch
from staadprep.importers.dxf_reader import DxfReader
from staadprep.importers.pipeline import ImportPipelineError, canonicalize_import_batch
from staadprep.topology.connectivity import connected_components

DXF_FIXTURE = Path("tests/golden_models/01_dxf_lines/source.dxf")


def test_direct_dxf_reuses_t06_t07_to_build_canonical_model() -> None:
    raw = DxfReader().read(DXF_FIXTURE)

    model = canonicalize_import_batch(raw)

    coordinates = {node.position.as_tuple() for node in model.nodes.values()}
    assert (6.0, 4.0, -3.0) in coordinates
    assert (1.234, 0.089, -0.5670000000000001) in coordinates
    assert len(model.members) == 3
    assert len(connected_components(model)) == 2
    assert model.metadata.source_format == "dxf"
    assert model.metadata.source_unit == "mm"
    assert model.metadata.source_axis == "Z-UP"


def test_canonical_import_fails_closed_when_source_unit_is_unknown() -> None:
    raw = ImportBatch(source_format="dxf", declared_unit=None, source_axis="Z-UP")

    with pytest.raises(ImportPipelineError, match="source unit"):
        canonicalize_import_batch(raw)
