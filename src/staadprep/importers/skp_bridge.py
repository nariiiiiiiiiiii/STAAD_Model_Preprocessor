"""Isolated process bridge for the native SketchUp reader helper.

T14 defines only the process/neutral-data contract. The native helper does not
extract real SketchUp geometry until T15 wires the official SketchUp C API.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.model.geometry import Vec3
from staadprep.paths import ProjectPaths

PROTOCOL_VERSION = 1
UNAVAILABLE_MESSAGE = "SKP importer unavailable — DXF remains available"


class SkpBridgeError(RuntimeError):
    """Base error for helper/process/neutral-contract failures."""


class SkpBridgeUnavailable(SkpBridgeError):
    """Raised when no ready native SketchUp reader is available."""


@dataclass(frozen=True, slots=True)
class SkpCapability:
    protocol_version: int | None
    sketchup_sdk: bool
    reader_ready: bool
    message: str


def _as_vec3(value: Any, field_name: str) -> Vec3:
    if not isinstance(value, list | tuple) or len(value) != 3:
        raise SkpBridgeError(f"neutral JSON field {field_name} must contain exactly 3 coordinates")
    try:
        return Vec3(float(value[0]), float(value[1]), float(value[2]))
    except (TypeError, ValueError) as exc:
        raise SkpBridgeError(
            f"neutral JSON field {field_name} contains invalid coordinates"
        ) from exc


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SkpBridgeError(f"neutral JSON field {field_name} must be a string list")
    return list(value)


class SkpBridge:
    """Invoke a versioned native helper without exposing SDK types to Python."""

    def __init__(
        self,
        project_root: Path,
        *,
        helper_command: Sequence[str] | None = None,
        output_dir: Path | None = None,
        timeout_s: float = 30.0,
    ) -> None:
        self.paths = ProjectPaths.from_root(project_root)
        self.paths.ensure_layout()
        default_helper = self.paths.build / "native" / "skp_reader" / "skp_reader.exe"
        self.helper_command = tuple(helper_command or (str(default_helper),))
        if not self.helper_command:
            raise ValueError("helper_command must not be empty")
        candidate_output = output_dir or (self.paths.tmp / "skp_bridge")
        self.output_dir = self.paths.assert_inside_project(candidate_output)
        if timeout_s <= 0.0:
            raise ValueError("timeout_s must be positive")
        self.timeout_s = timeout_s

    def _command_exists(self) -> bool:
        executable = self.helper_command[0]
        path = Path(executable)
        if path.is_absolute() or path.parent != Path("."):
            return path.exists()
        return shutil.which(executable) is not None

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [*self.helper_command, *args],
                cwd=self.paths.root,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_s,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SkpBridgeError(f"SKP helper process failed: {exc}") from exc

    def capability(self) -> SkpCapability:
        """Probe native reader readiness without reading a model or downloading anything."""
        if not self._command_exists():
            return SkpCapability(None, False, False, UNAVAILABLE_MESSAGE)

        completed = self._run("--capabilities")
        if completed.returncode != 0:
            return SkpCapability(None, False, False, UNAVAILABLE_MESSAGE)
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise SkpBridgeError("SKP helper returned invalid capability JSON") from exc
        if not isinstance(payload, dict):
            raise SkpBridgeError("SKP helper capability JSON must be an object")

        protocol = payload.get("protocol_version")
        if not isinstance(protocol, int):
            raise SkpBridgeError("SKP helper capability is missing protocol version")
        if protocol != PROTOCOL_VERSION:
            raise SkpBridgeError(
                f"SKP helper protocol version {protocol} does not match required {PROTOCOL_VERSION}"
            )

        sdk = payload.get("sketchup_sdk") is True
        ready = payload.get("reader_ready") is True
        message = "SKP native reader ready" if ready else UNAVAILABLE_MESSAGE
        return SkpCapability(protocol, sdk, ready, message)

    def is_available(self) -> bool:
        """Return False for any capability failure; callers can remain DXF-capable."""
        try:
            return self.capability().reader_ready
        except SkpBridgeError:
            return False

    def read(self, path: Path) -> ImportBatch:
        """Read one SKP into raw source-space neutral geometry through the helper."""
        capability = self.capability()
        if not capability.reader_ready:
            raise SkpBridgeUnavailable(capability.message)

        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise SkpBridgeError(f"SKP source file does not exist: {source}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output = self.paths.assert_inside_project(self.output_dir / f"neutral-{uuid4().hex}.json")
        completed = self._run("--input", str(source), "--output", str(output))
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip() or "unknown helper error"
            raise SkpBridgeError(f"SKP helper read failed: {details}")
        if not output.is_file():
            raise SkpBridgeError("SKP helper did not create the requested neutral JSON")

        try:
            payload = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SkpBridgeError("SKP helper produced invalid neutral JSON") from exc
        return self._to_import_batch(payload, output)

    def _to_import_batch(self, payload: Any, neutral_file: Path) -> ImportBatch:
        if not isinstance(payload, dict):
            raise SkpBridgeError("neutral JSON must be an object")
        protocol = payload.get("protocol_version")
        if protocol != PROTOCOL_VERSION:
            raise SkpBridgeError(
                "neutral JSON protocol version "
                f"{protocol!r} does not match required {PROTOCOL_VERSION}"
            )

        source_file = payload.get("source_file")
        source_unit = payload.get("source_unit")
        source_axis = payload.get("source_axis")
        if not isinstance(source_file, str):
            raise SkpBridgeError("neutral JSON source_file must be a string")
        if source_unit is not None and not isinstance(source_unit, str):
            raise SkpBridgeError("neutral JSON source_unit must be a string or null")
        if source_axis is not None and not isinstance(source_axis, str):
            raise SkpBridgeError("neutral JSON source_axis must be a string or null")

        point_payloads = payload.get("points", [])
        segment_payloads = payload.get("segments", [])
        if not isinstance(point_payloads, list) or not isinstance(segment_payloads, list):
            raise SkpBridgeError("neutral JSON points/segments must be arrays")

        points: list[RawPoint] = []
        for index, item in enumerate(point_payloads):
            if not isinstance(item, dict) or not isinstance(item.get("source_ref"), str):
                raise SkpBridgeError(f"neutral JSON point {index} is malformed")
            tag = item.get("tag")
            if tag is not None and not isinstance(tag, str):
                raise SkpBridgeError(f"neutral JSON point {index} tag must be a string or null")
            points.append(
                RawPoint(
                    position=_as_vec3(item.get("position"), f"points[{index}].position"),
                    source_ref=item["source_ref"],
                    layer=tag,
                )
            )

        segments: list[RawSegment] = []
        group_paths: dict[str, list[str]] = {}
        for index, item in enumerate(segment_payloads):
            if not isinstance(item, dict) or not isinstance(item.get("source_ref"), str):
                raise SkpBridgeError(f"neutral JSON segment {index} is malformed")
            source_ref = item["source_ref"]
            tag = item.get("tag")
            if tag is not None and not isinstance(tag, str):
                raise SkpBridgeError(f"neutral JSON segment {index} tag must be a string or null")
            group_path = item.get("group_path", [])
            group_paths[source_ref] = _string_list(group_path, f"segments[{index}].group_path")
            segments.append(
                RawSegment(
                    start=_as_vec3(item.get("start"), f"segments[{index}].start"),
                    end=_as_vec3(item.get("end"), f"segments[{index}].end"),
                    source_ref=source_ref,
                    layer=tag,
                )
            )

        groups = _string_list(payload.get("groups", []), "groups")
        tags = _string_list(payload.get("tags", []), "tags")
        warnings = _string_list(payload.get("warnings", []), "warnings")
        return ImportBatch(
            points=tuple(points),
            segments=tuple(segments),
            source_format="skp",
            declared_unit=source_unit,
            source_axis=source_axis,
            metadata={
                "source_file": source_file,
                "neutral_file": str(neutral_file),
                "groups": groups,
                "tags": tags,
                "segment_group_paths": group_paths,
            },
            warnings=tuple(warnings),
        )
