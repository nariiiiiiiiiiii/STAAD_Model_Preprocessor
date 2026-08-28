"""Verified length-unit conversions and coordinate transforms."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from math import dist, isclose, isfinite

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.model.geometry import Vec3


class LengthUnit(Enum):
    METER = "m"
    MILLIMETER = "mm"
    CENTIMETER = "cm"
    INCH = "in"
    FOOT = "ft"
    UNKNOWN = "unknown"


_TO_METERS = {
    LengthUnit.METER: 1.0,
    LengthUnit.MILLIMETER: 0.001,
    LengthUnit.CENTIMETER: 0.01,
    LengthUnit.INCH: 0.0254,
    LengthUnit.FOOT: 0.3048,
}

_SUSPICIOUS_SCALE_FACTORS = (10.0, 25.4, 100.0, 304.8, 1000.0)


@dataclass(frozen=True, slots=True)
class Extents:
    minimum: Vec3
    maximum: Vec3
    size: Vec3


def _meter_factor(unit: LengthUnit) -> float:
    try:
        return _TO_METERS[unit]
    except KeyError as exc:
        raise ValueError(f"Unknown length unit: {unit.value}") from exc


def to_meters(value: float, unit: LengthUnit) -> float:
    """Convert a finite scalar length to metres; unknown units fail closed."""
    if not isfinite(value):
        raise ValueError("Length value must be finite")
    return value * _meter_factor(unit)


def sketchup_z_up_to_staad_y_up(point: Vec3) -> Vec3:
    """Map SketchUp Z-up source coordinates into STAAD Y-up coordinates."""
    return Vec3(point.x, point.z, -point.y)


def measure(a: Vec3, b: Vec3) -> float:
    """Return Euclidean point-to-point distance in the coordinates' current unit."""
    return dist(a.as_tuple(), b.as_tuple())


def model_extents(points: Iterable[Vec3]) -> Extents:
    """Return axis-aligned extents for a non-empty point collection."""
    values = tuple(points)
    if not values:
        raise ValueError("model_extents requires at least one point")

    minimum = Vec3(
        min(point.x for point in values),
        min(point.y for point in values),
        min(point.z for point in values),
    )
    maximum = Vec3(
        max(point.x for point in values),
        max(point.y for point in values),
        max(point.z for point in values),
    )
    return Extents(
        minimum=minimum,
        maximum=maximum,
        size=Vec3(
            maximum.x - minimum.x,
            maximum.y - minimum.y,
            maximum.z - minimum.z,
        ),
    )


def reference_scale_ratio(measured_m: float, expected_m: float) -> float:
    """Return measured/expected reference-length ratio without modifying geometry."""
    if not isfinite(measured_m) or measured_m < 0.0:
        raise ValueError("Measured reference length must be finite and non-negative")
    if not isfinite(expected_m) or expected_m <= 0.0:
        raise ValueError("Expected reference length must be finite and greater than zero")
    return measured_m / expected_m


def reference_scale_warning(measured_m: float, expected_m: float) -> str | None:
    """Report common unit-scale mismatches without applying any automatic rescale."""
    ratio = reference_scale_ratio(measured_m, expected_m)
    for factor in _SUSPICIOUS_SCALE_FACTORS:
        if isclose(ratio, factor, rel_tol=0.02, abs_tol=0.0):
            return f"Possible scale mismatch: measured/reference ratio is near {factor:g}"
    return None


def _scale_point_to_meters(point: Vec3, unit: LengthUnit) -> Vec3:
    factor = _meter_factor(unit)
    return Vec3(point.x * factor, point.y * factor, point.z * factor)


def _normalize_axis(source_axis: str) -> str:
    normalized = source_axis.strip().upper().replace("_", "-")
    if normalized in {"Z-UP", "SKETCHUP-Z-UP"}:
        return "Z-UP"
    if normalized in {"Y-UP", "STAAD-Y-UP"}:
        return "Y-UP"
    raise ValueError(f"Unsupported source axis: {source_axis}")


def _transform_point(point: Vec3, unit: LengthUnit, source_axis: str) -> Vec3:
    scaled = _scale_point_to_meters(point, unit)
    if source_axis == "Z-UP":
        return sketchup_z_up_to_staad_y_up(scaled)
    return scaled


def transform_batch(
    batch: ImportBatch,
    source_unit: LengthUnit,
    source_axis: str,
) -> ImportBatch:
    """Convert raw coordinates to metres/Y-up without topology edits or auto-rescaling."""
    _meter_factor(source_unit)
    normalized_axis = _normalize_axis(source_axis)

    points = tuple(
        RawPoint(
            position=_transform_point(point.position, source_unit, normalized_axis),
            source_ref=point.source_ref,
            layer=point.layer,
        )
        for point in batch.points
    )
    segments = tuple(
        RawSegment(
            start=_transform_point(segment.start, source_unit, normalized_axis),
            end=_transform_point(segment.end, source_unit, normalized_axis),
            source_ref=segment.source_ref,
            layer=segment.layer,
        )
        for segment in batch.segments
    )

    metadata = dict(batch.metadata)
    metadata.update(
        {
            "source_unit": source_unit.value,
            "source_axis": normalized_axis,
            "coordinate_unit": LengthUnit.METER.value,
            "coordinate_axis": "Y-UP",
        }
    )

    return ImportBatch(
        points=points,
        segments=segments,
        source_format=batch.source_format,
        declared_unit=LengthUnit.METER.value,
        source_axis=normalized_axis,
        metadata=metadata,
        warnings=batch.warnings,
    )
