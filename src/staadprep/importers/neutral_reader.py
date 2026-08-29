"""Read project-local SketchUp neutral JSON into raw ImportBatch geometry.

This module is transport/schema only. It must not scale, transform, merge, repair,
renumber, or otherwise mutate structural meaning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.importers.skp_bridge import PROTOCOL_VERSION
from staadprep.model.geometry import Vec3
from staadprep.paths import ProjectPaths


class NeutralReaderError(RuntimeError):
    """Raised when a neutral envelope is missing, malformed, or incompatible."""


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise NeutralReaderError(f"neutral JSON {field_name} must be a non-empty string")
    return value


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise NeutralReaderError(f"neutral JSON {field_name} must be a string list")
    return list(value)


def _vec3(value: Any, field_name: str) -> Vec3:
    if not isinstance(value, list) or len(value) != 3:
        raise NeutralReaderError(f"neutral JSON {field_name} coordinates must contain 3 numbers")
    if not all(type(item) in (int, float) for item in value):
        raise NeutralReaderError(f"neutral JSON {field_name} coordinates must be JSON numbers")
    try:
        return Vec3(float(value[0]), float(value[1]), float(value[2]))
    except ValueError as exc:
        raise NeutralReaderError(f"neutral JSON {field_name} coordinates must be finite") from exc


class NeutralReader:
    """Read protocol-v1 neutral envelopes from the project-local SketchUp inbox."""

    def __init__(
        self,
        project_root: Path | None = None,
        *,
        paths: ProjectPaths | None = None,
        inbox: Path | None = None,
    ) -> None:
        if project_root is not None and paths is not None:
            raise ValueError("Pass either project_root or paths, not both")
        if paths is None:
            if project_root is None:
                raise ValueError("project_root or paths is required")
            paths = ProjectPaths.from_root(project_root)

        self.paths = paths
        self.paths.ensure_layout()
        default_inbox = self.paths.artifacts / "sketchup_bridge" / "inbox"
        self.inbox = self.paths.assert_inside_project(inbox or default_inbox)
        self.inbox.mkdir(parents=True, exist_ok=True)

    def _assert_inbox_file(self, path: Path) -> Path:
        candidate: Path = self.paths.assert_inside_project(path)
        inbox = self.inbox.resolve()
        if not candidate.is_relative_to(inbox):
            raise ValueError(f"Neutral JSON must be inside SketchUp inbox: {inbox}")
        return candidate

    def read(self, path: Path) -> ImportBatch:
        neutral_file = self._assert_inbox_file(path)
        if not neutral_file.is_file():
            raise NeutralReaderError(f"neutral JSON does not exist: {neutral_file}")
        try:
            payload = json.loads(neutral_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise NeutralReaderError("neutral JSON cannot be read or parsed") from exc
        return self._to_import_batch(payload, neutral_file)

    def _to_import_batch(self, payload: Any, neutral_file: Path) -> ImportBatch:
        if not isinstance(payload, dict):
            raise NeutralReaderError("neutral JSON must be an object")

        protocol = payload.get("protocol_version")
        if type(protocol) is not int or protocol != PROTOCOL_VERSION:
            raise NeutralReaderError(
                f"neutral JSON protocol version {protocol!r} does not match "
                f"required {PROTOCOL_VERSION}"
            )

        source_file = _require_string(payload.get("source_file"), "source_file")
        source_unit = _require_string(payload.get("source_unit"), "source_unit")
        source_axis = _require_string(payload.get("source_axis"), "source_axis")

        point_payloads = payload.get("points")
        segment_payloads = payload.get("segments")
        if not isinstance(point_payloads, list):
            raise NeutralReaderError("neutral JSON points must be an array")
        if not isinstance(segment_payloads, list):
            raise NeutralReaderError("neutral JSON segments must be an array")

        groups = _string_list(payload.get("groups"), "groups")
        tags = _string_list(payload.get("tags"), "tags")
        warnings = _string_list(payload.get("warnings"), "warnings")

        points: list[RawPoint] = []
        for index, item in enumerate(point_payloads):
            if not isinstance(item, dict):
                raise NeutralReaderError(f"neutral JSON point {index} must be an object")
            source_ref = _require_string(item.get("source_ref"), f"points[{index}].source_ref")
            tag = item.get("tag")
            if tag is not None and not isinstance(tag, str):
                raise NeutralReaderError(
                    f"neutral JSON points[{index}].tag must be a string or null"
                )
            points.append(
                RawPoint(
                    position=_vec3(item.get("position"), f"points[{index}].position"),
                    source_ref=source_ref,
                    layer=tag,
                )
            )

        segments: list[RawSegment] = []
        group_paths: dict[str, list[str]] = {}
        component_paths: dict[str, list[str]] = {}
        for index, item in enumerate(segment_payloads):
            if not isinstance(item, dict):
                raise NeutralReaderError(f"neutral JSON segment {index} must be an object")
            source_ref = _require_string(item.get("source_ref"), f"segments[{index}].source_ref")
            tag = item.get("tag")
            if tag is not None and not isinstance(tag, str):
                raise NeutralReaderError(
                    f"neutral JSON segments[{index}].tag must be a string or null"
                )
            group_paths[source_ref] = _string_list(
                item.get("group_path", []), f"segments[{index}].group_path"
            )
            component_paths[source_ref] = _string_list(
                item.get("component_path", []), f"segments[{index}].component_path"
            )
            segments.append(
                RawSegment(
                    start=_vec3(item.get("start"), f"segments[{index}].start"),
                    end=_vec3(item.get("end"), f"segments[{index}].end"),
                    source_ref=source_ref,
                    layer=tag,
                )
            )

        return ImportBatch(
            points=tuple(points),
            segments=tuple(segments),
            source_format="skp",
            declared_unit=source_unit,
            source_axis=source_axis,
            metadata={
                "source_file": source_file,
                "neutral_file": str(neutral_file),
                "source_transport": "sketchup-ruby",
                "groups": groups,
                "tags": tags,
                "segment_group_paths": group_paths,
                "segment_component_paths": component_paths,
            },
            warnings=tuple(warnings),
        )
