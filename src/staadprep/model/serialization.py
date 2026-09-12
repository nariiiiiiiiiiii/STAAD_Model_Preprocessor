"""Versioned JSON serialization for the canonical project model."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from .entities import Member, Node
from .geometry import Vec3
from .project import ModelMetadata, ProjectModel

_SCHEMA_VERSION = 1


def _node_to_dict(node: Node) -> dict[str, Any]:
    return {
        "key": str(node.key),
        "position": list(node.position.as_tuple()),
        "number": node.number,
        "source_refs": list(node.source_refs),
    }


def _member_to_dict(member: Member) -> dict[str, Any]:
    return {
        "key": str(member.key),
        "start": str(member.start),
        "end": str(member.end),
        "number": member.number,
        "source_ref": member.source_ref,
        "group": member.group,
    }


def _metadata_to_dict(metadata: ModelMetadata) -> dict[str, Any]:
    return {
        "source_format": metadata.source_format,
        "source_file": metadata.source_file,
        "source_unit": metadata.source_unit,
        "source_axis": metadata.source_axis,
    }


def _project_json_text(model: ProjectModel) -> str:
    """Return deterministic schema-version-1 project JSON text."""
    if model.metadata.schema_version != _SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version: {model.metadata.schema_version}")
    payload = {
        "schema_version": _SCHEMA_VERSION,
        "revision": model.revision,
        "metadata": _metadata_to_dict(model.metadata),
        "nodes": [_node_to_dict(model.nodes[key]) for key in sorted(model.nodes, key=str)],
        "members": [
            _member_to_dict(model.members[key]) for key in sorted(model.members, key=str)
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def save_project_atomic(model: ProjectModel, path: Path) -> None:
    """Atomically serialize *model* without risking a partial destination file."""
    destination = path.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.parent / f".staadprep-{uuid4().hex}.tmp"
    try:
        with temp_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(_project_json_text(model))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, destination)
    finally:
        temp_path.unlink(missing_ok=True)


def save_project(model: ProjectModel, path: Path) -> None:
    """Serialize *model* to deterministic UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_project_json_text(model), encoding="utf-8")


def _load_node(data: dict[str, Any]) -> Node:
    position = data["position"]
    return Node(
        key=UUID(data["key"]),
        position=Vec3(float(position[0]), float(position[1]), float(position[2])),
        number=data["number"],
        source_refs=tuple(data["source_refs"]),
    )


def _load_member(data: dict[str, Any]) -> Member:
    return Member(
        key=UUID(data["key"]),
        start=UUID(data["start"]),
        end=UUID(data["end"]),
        number=data["number"],
        source_ref=data["source_ref"],
        group=data["group"],
    )


def load_project(path: Path) -> ProjectModel:
    """Load a project JSON document using the supported schema version."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema_version = int(payload["schema_version"])
    if schema_version != _SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version: {schema_version}")

    metadata_data = payload["metadata"]
    metadata = ModelMetadata(
        schema_version=schema_version,
        source_format=metadata_data["source_format"],
        source_file=metadata_data["source_file"],
        source_unit=metadata_data["source_unit"],
        source_axis=metadata_data["source_axis"],
    )
    nodes = {node.key: node for node in (_load_node(item) for item in payload["nodes"])}
    members = {
        member.key: member for member in (_load_member(item) for item in payload["members"])
    }
    return ProjectModel(
        nodes=nodes,
        members=members,
        metadata=metadata,
        revision=int(payload["revision"]),
    )
