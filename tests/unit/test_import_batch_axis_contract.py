from staadprep.importers.contracts import ImportBatch


def test_import_batch_exposes_source_axis_metadata() -> None:
    batch = ImportBatch(source_axis="Z-UP")

    assert batch.source_axis == "Z-UP"
