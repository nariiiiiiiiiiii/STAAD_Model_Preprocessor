"""Shared raw-import -> canonical-model orchestration.

This module deliberately delegates all unit/axis math to T06 and all endpoint/topology
construction to T07. It adds no alternative engineering rules.
"""

from __future__ import annotations

from staadprep.importers.contracts import ImportBatch
from staadprep.model.project import ProjectModel
from staadprep.topology.builder import TopologyPolicy, build_project
from staadprep.units.transforms import LengthUnit, transform_batch


class ImportPipelineError(RuntimeError):
    """Raised when raw source metadata is insufficient for canonical conversion."""


_UNIT_BY_TOKEN = {
    LengthUnit.METER.value: LengthUnit.METER,
    LengthUnit.MILLIMETER.value: LengthUnit.MILLIMETER,
    LengthUnit.CENTIMETER.value: LengthUnit.CENTIMETER,
    LengthUnit.INCH.value: LengthUnit.INCH,
    LengthUnit.FOOT.value: LengthUnit.FOOT,
}


def canonicalize_import_batch(
    batch: ImportBatch,
    *,
    topology_policy: TopologyPolicy | None = None,
) -> ProjectModel:
    """Convert a raw batch through the existing T06 -> T07 canonical path."""
    unit_token = batch.declared_unit
    if not isinstance(unit_token, str) or unit_token not in _UNIT_BY_TOKEN:
        raise ImportPipelineError(f"source unit is unknown or unsupported: {unit_token!r}")
    if not isinstance(batch.source_axis, str) or not batch.source_axis.strip():
        raise ImportPipelineError("source axis is unknown")

    try:
        canonical_batch = transform_batch(
            batch,
            _UNIT_BY_TOKEN[unit_token],
            batch.source_axis,
        )
        return build_project(canonical_batch, topology_policy or TopologyPolicy())
    except ValueError as exc:
        raise ImportPipelineError(str(exc)) from exc
