from __future__ import annotations

import json
from pathlib import Path

import pytest

from staadprep.importers.neutral_reader import NeutralReader, NeutralReaderError


def _valid_payload() -> dict[str, object]:
    return {
        "protocol_version": 1,
        "source_file": "frame.skp",
        "source_unit": "in",
        "source_axis": "Z-UP",
        "points": [],
        "segments": [
            {
                "start": [0, 0, 0],
                "end": [12, 0, 0],
                "source_ref": "group:20/component:30/edge:40",
                "tag": "Structure",
                "group_path": ["Frame"],
                "component_path": ["Beam"],
            }
        ],
        "groups": ["Frame"],
        "tags": ["Structure"],
        "warnings": [],
    }


def _write_inbox(
    reader: NeutralReader, payload: dict[str, object], name: str = "frame.json"
) -> Path:
    reader.inbox.mkdir(parents=True, exist_ok=True)
    path = reader.inbox / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_reads_protocol_v1_from_project_local_inbox(tmp_path: Path) -> None:
    root = tmp_path / "project"
    reader = NeutralReader(root)
    path = _write_inbox(reader, _valid_payload())

    batch = reader.read(path)

    assert batch.source_format == "skp"
    assert batch.declared_unit == "in"
    assert batch.source_axis == "Z-UP"
    assert len(batch.segments) == 1
    assert batch.segments[0].start.as_tuple() == (0.0, 0.0, 0.0)
    assert batch.segments[0].end.as_tuple() == (12.0, 0.0, 0.0)
    assert batch.segments[0].layer == "Structure"
    assert batch.metadata["source_transport"] == "sketchup-ruby"
    assert batch.metadata["segment_group_paths"]["group:20/component:30/edge:40"] == ["Frame"]
    assert batch.metadata["segment_component_paths"]["group:20/component:30/edge:40"] == ["Beam"]


def test_rejects_protocol_mismatch(tmp_path: Path) -> None:
    reader = NeutralReader(tmp_path / "project")
    payload = _valid_payload()
    payload["protocol_version"] = 2
    path = _write_inbox(reader, payload)

    with pytest.raises(NeutralReaderError, match="protocol version"):
        reader.read(path)


def test_rejects_neutral_file_outside_inbox(tmp_path: Path) -> None:
    root = tmp_path / "project"
    reader = NeutralReader(root)
    outside = root / "artifacts" / "not-inbox.json"
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.write_text(json.dumps(_valid_payload()), encoding="utf-8")

    with pytest.raises(ValueError, match="SketchUp inbox"):
        reader.read(outside)


def test_rejects_string_or_non_finite_coordinates(tmp_path: Path) -> None:
    reader = NeutralReader(tmp_path / "project")
    payload = _valid_payload()
    payload["segments"][0]["start"] = ["0", 0, 0]  # type: ignore[index]
    path = _write_inbox(reader, payload, "string-coordinate.json")
    with pytest.raises(NeutralReaderError, match="coordinates"):
        reader.read(path)

    payload = _valid_payload()
    payload["segments"][0]["start"] = [float("nan"), 0, 0]  # type: ignore[index]
    path = _write_inbox(reader, payload, "nan-coordinate.json")
    with pytest.raises(NeutralReaderError, match="coordinates"):
        reader.read(path)


def test_requires_protocol_top_level_fields_and_string_lists(tmp_path: Path) -> None:
    reader = NeutralReader(tmp_path / "project")
    payload = _valid_payload()
    payload.pop("source_axis")
    path = _write_inbox(reader, payload, "missing-axis.json")
    with pytest.raises(NeutralReaderError, match="source_axis"):
        reader.read(path)

    payload = _valid_payload()
    payload["tags"] = ["Structure", 5]
    path = _write_inbox(reader, payload, "bad-tags.json")
    with pytest.raises(NeutralReaderError, match="tags"):
        reader.read(path)
