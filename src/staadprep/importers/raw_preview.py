"""Temporary raw-geometry preview adapter for T05.

This adapter is intentionally *not* the canonical topology builder. Every raw
segment receives its own start/end nodes even when coordinates are identical.
That preserves source geometry without silently merging, snapping, scaling, or
transforming it before the later STRICT tasks.
"""

from __future__ import annotations

from staadprep.importers.contracts import ImportBatch
from staadprep.model.entities import Member, Node
from staadprep.model.project import ModelMetadata, ProjectModel


def raw_batch_to_preview_model(batch: ImportBatch) -> ProjectModel:
    nodes = {}
    members = {}

    for point in batch.points:
        node = Node.new(point.position, source_refs=(point.source_ref,))
        nodes[node.key] = node

    for segment in batch.segments:
        start = Node.new(segment.start, source_refs=(segment.source_ref,))
        end = Node.new(segment.end, source_refs=(segment.source_ref,))
        member = Member.new(
            start.key,
            end.key,
            source_ref=segment.source_ref,
            group=segment.layer,
        )
        nodes[start.key] = start
        nodes[end.key] = end
        members[member.key] = member

    source_file = batch.metadata.get("source_file")
    return ProjectModel(
        nodes=nodes,
        members=members,
        metadata=ModelMetadata(
            source_format=f"{batch.source_format}-raw",
            source_file=str(source_file) if source_file is not None else None,
            source_unit=batch.declared_unit,
        ),
    )
