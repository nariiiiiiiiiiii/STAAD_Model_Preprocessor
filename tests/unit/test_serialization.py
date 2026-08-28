from pathlib import Path

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.model.serialization import load_project, save_project


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
