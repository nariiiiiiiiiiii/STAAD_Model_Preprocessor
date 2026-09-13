from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pytest

from staadprep.importers.skp_bridge import (
    PROTOCOL_VERSION,
    SkpBridge,
    SkpBridgeError,
    SkpBridgeUnavailable,
)


def _case_dir(name: str) -> Path:
    path = Path(".tmp/tests/t14") / f"{name}-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_fake_helper(case: Path, *, protocol_version: int = PROTOCOL_VERSION) -> Path:
    helper = case / "fake_skp_helper.py"
    payload = {
        "protocol_version": protocol_version,
        "source_file": "SOURCE_PLACEHOLDER",
        "source_unit": "m",
        "source_axis": "Z-UP",
        "points": [
            {
                "position": [1.0, 2.0, 3.0],
                "source_ref": "POINT:1",
                "tag": "NODES",
            }
        ],
        "segments": [
            {
                "start": [0.0, 0.0, 0.0],
                "end": [6.0, 0.0, 0.0],
                "source_ref": "EDGE:1",
                "tag": "STRUCTURE",
                "group_path": ["FRAME", "GRID-A"],
            }
        ],
        "groups": ["FRAME", "FRAME/GRID-A"],
        "tags": ["NODES", "STRUCTURE"],
        "warnings": ["fake warning"],
    }
    helper.write_text(
        "from __future__ import annotations\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n\n"
        f"PROTOCOL = {protocol_version}\n"
        f"PAYLOAD = {payload!r}\n\n"
        "if '--capabilities' in sys.argv:\n"
        "    print(json.dumps({'protocol_version': PROTOCOL, "
        "'sketchup_sdk': True, 'reader_ready': True}))\n"
        "    raise SystemExit(0)\n"
        "args = sys.argv[1:]\n"
        "input_path = Path(args[args.index('--input') + 1]).resolve()\n"
        "output_path = Path(args[args.index('--output') + 1]).resolve()\n"
        "data = dict(PAYLOAD)\n"
        "data['source_file'] = str(input_path)\n"
        "output_path.parent.mkdir(parents=True, exist_ok=True)\n"
        "output_path.write_text(json.dumps(data), encoding='utf-8')\n",
        encoding="utf-8",
    )
    return helper


def test_missing_native_helper_reports_unavailable_without_crashing() -> None:
    root = Path.cwd()
    bridge = SkpBridge(root, helper_command=(str(root / "native/missing-skp-reader.exe"),))

    assert not bridge.is_available()
    assert bridge.capability().message == "SKP importer unavailable — DXF remains available"

    with pytest.raises(SkpBridgeUnavailable, match="DXF remains available"):
        bridge.read(root / "does-not-matter.skp")


def test_fake_helper_capability_and_neutral_payload_convert_to_import_batch() -> None:
    root = Path.cwd()
    case = _case_dir("happy")
    helper = _write_fake_helper(case)
    source = case / "frame.skp"
    source.write_bytes(b"fake-skp")
    bridge = SkpBridge(
        root,
        helper_command=(sys.executable, str(helper.resolve())),
        output_dir=case / "neutral",
    )

    capability = bridge.capability()
    batch = bridge.read(source)

    assert capability.protocol_version == PROTOCOL_VERSION
    assert capability.sketchup_sdk
    assert capability.reader_ready
    assert bridge.is_available()
    assert batch.source_format == "skp"
    assert batch.declared_unit == "m"
    assert batch.source_axis == "Z-UP"
    assert len(batch.points) == 1
    assert batch.points[0].position.as_tuple() == (1.0, 2.0, 3.0)
    assert batch.points[0].layer == "NODES"
    assert len(batch.segments) == 1
    assert batch.segments[0].start.as_tuple() == (0.0, 0.0, 0.0)
    assert batch.segments[0].end.as_tuple() == (6.0, 0.0, 0.0)
    assert batch.segments[0].layer == "STRUCTURE"
    assert batch.metadata["groups"] == ["FRAME", "FRAME/GRID-A"]
    assert batch.metadata["tags"] == ["NODES", "STRUCTURE"]
    assert batch.metadata["segment_group_paths"]["EDGE:1"] == ["FRAME", "GRID-A"]
    assert batch.warnings == ("fake warning",)


def test_protocol_mismatch_fails_closed_before_read() -> None:
    root = Path.cwd()
    case = _case_dir("protocol")
    helper = _write_fake_helper(case, protocol_version=PROTOCOL_VERSION + 1)
    bridge = SkpBridge(root, helper_command=(sys.executable, str(helper.resolve())))

    with pytest.raises(SkpBridgeError, match="protocol version"):
        bridge.capability()

    assert not bridge.is_available()


def test_helper_output_directory_must_stay_inside_project() -> None:
    root = Path.cwd()
    outside = root.parent / "outside-skp-neutral"

    with pytest.raises(ValueError, match="escapes project root"):
        SkpBridge(root, output_dir=outside)


def test_malformed_neutral_payload_fails_closed() -> None:
    root = Path.cwd()
    case = _case_dir("malformed")
    helper = case / "bad_helper.py"
    helper.write_text(
        "from __future__ import annotations\n"
        "import json, sys\n"
        "from pathlib import Path\n"
        "if '--capabilities' in sys.argv:\n"
        "    print(json.dumps({'protocol_version': 1, "
        "'sketchup_sdk': True, 'reader_ready': True}))\n"
        "    raise SystemExit(0)\n"
        "args = sys.argv[1:]\n"
        "out = Path(args[args.index('--output') + 1])\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text('{not-json', encoding='utf-8')\n",
        encoding="utf-8",
    )
    source = case / "bad.skp"
    source.write_bytes(b"fake")
    bridge = SkpBridge(root, helper_command=(sys.executable, str(helper.resolve())))

    with pytest.raises(SkpBridgeError, match="neutral JSON"):
        bridge.read(source)
