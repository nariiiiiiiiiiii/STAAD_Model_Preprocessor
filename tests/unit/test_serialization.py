from pathlib import Path

import pytest

import staadprep.model.serialization as serialization_module
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.model.serialization import load_project, save_project, save_project_atomic


def test_project_serialization_round_trip_preserves_identity_and_metadata(tmp_path: Path) -> None:
    a = Node.new(Vec3(0.0, 1.5, 2.0), source_refs=("DXF:LINE:10:start",))
    b = Node.new(Vec3(6.0, 1.5, 2.0), source_refs=("DXF:LINE:10:end",))
    a.number = 11
    b.number = 12
    member = Member.new(
        a.key,
        b.key,
        source_ref="DXF:LINE:10",
        group="Roof",
    )
    member.number = 101
    model = ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
        metadata=ModelMetadata(
            schema_version=1,
            source_format="dxf",
            source_file="warehouse.dxf",
            source_unit="mm",
            source_axis="Z-UP",
        ),
        revision=7,
    )
    target = tmp_path / "project.json"

    save_project(model, target)
    loaded = load_project(target)

    assert loaded == model
    assert target.exists()
    assert loaded.metadata.schema_version == 1
    assert loaded.nodes[a.key].source_refs == ("DXF:LINE:10:start",)
    assert loaded.members[member.key].source_ref == "DXF:LINE:10"


def test_serialized_project_uses_schema_version_one(tmp_path: Path) -> None:
    model = ProjectModel(metadata=ModelMetadata())
    target = tmp_path / "project.json"

    save_project(model, target)

    text = target.read_text(encoding="utf-8")
    assert '"schema_version": 1' in text


def test_atomic_project_save_round_trips_exact_model_and_cleans_temp(tmp_path: Path) -> None:
    node_a = Node.new(Vec3(1.0, 2.0, 3.0), source_refs=("source:a",))
    node_b = Node.new(Vec3(4.0, 5.0, 6.0), source_refs=("source:b",))
    node_a.number = 21
    node_b.number = 22
    member = Member.new(node_a.key, node_b.key, source_ref="source:m", group="G1")
    member.number = 201
    model = ProjectModel(
        nodes={node_a.key: node_a, node_b.key: node_b},
        members={member.key: member},
        metadata=ModelMetadata(source_format="neutral", source_file="model.json"),
        revision=9,
    )
    target = tmp_path / "Projects" / "sample.staadprep.json"
    temp_dir = tmp_path / "Temp"

    save_project_atomic(model, target, temp_dir=temp_dir)

    assert load_project(target) == model
    assert list(temp_dir.glob("*.tmp")) == []


def test_atomic_project_save_preserves_existing_destination_when_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "Projects" / "sample.staadprep.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"existing-project-bytes\n")
    before = target.read_bytes()
    temp_dir = tmp_path / "Temp"
    model = ProjectModel(metadata=ModelMetadata(), revision=3)

    def fail_replace(_source: Path, _destination: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(serialization_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        save_project_atomic(model, target, temp_dir=temp_dir)

    assert target.read_bytes() == before
    assert list(temp_dir.glob("*.tmp")) == []
