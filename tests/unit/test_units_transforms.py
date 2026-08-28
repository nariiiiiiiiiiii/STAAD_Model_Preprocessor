from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.model.geometry import Vec3
from staadprep.units.transforms import (
    Extents,
    LengthUnit,
    measure,
    model_extents,
    reference_scale_ratio,
    reference_scale_warning,
    sketchup_z_up_to_staad_y_up,
    to_meters,
    transform_batch,
)

WRONG_SCALE = Path("tests/golden_models/07_wrong_scale/case.json")
WRONG_AXIS = Path("tests/golden_models/08_wrong_axis/case.json")


@pytest.mark.parametrize(
    ("value", "unit", "expected_m"),
    [
        (1.0, LengthUnit.METER, 1.0),
        (1000.0, LengthUnit.MILLIMETER, 1.0),
        (100.0, LengthUnit.CENTIMETER, 1.0),
        (39.37007874015748, LengthUnit.INCH, 1.0),
        (3.280839895013123, LengthUnit.FOOT, 1.0),
    ],
)
def test_to_meters_matches_independent_reference_values(
    value: float,
    unit: LengthUnit,
    expected_m: float,
) -> None:
    assert to_meters(value, unit) == pytest.approx(expected_m, rel=1e-12, abs=1e-12)


def test_to_meters_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError, match="Unknown length unit"):
        to_meters(1.0, LengthUnit.UNKNOWN)


def test_sketchup_z_up_to_staad_y_up_matches_hand_calculated_mapping() -> None:
    assert sketchup_z_up_to_staad_y_up(Vec3(1.0, 2.0, 3.0)) == Vec3(1.0, 3.0, -2.0)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (Vec3(1.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0)),
        (Vec3(0.0, 1.0, 0.0), Vec3(0.0, 0.0, -1.0)),
        (Vec3(0.0, 0.0, 1.0), Vec3(0.0, 1.0, 0.0)),
    ],
)
def test_sketchup_basis_maps_to_expected_staad_basis(source: Vec3, expected: Vec3) -> None:
    assert sketchup_z_up_to_staad_y_up(source) == expected


def test_sketchup_axis_transform_preserves_pairwise_distance() -> None:
    a = Vec3(2.5, -4.0, 7.25)
    b = Vec3(-3.0, 8.5, 1.0)
    transformed_a = sketchup_z_up_to_staad_y_up(a)
    transformed_b = sketchup_z_up_to_staad_y_up(b)

    source_distance = math.dist(a.as_tuple(), b.as_tuple())
    transformed_distance = math.dist(transformed_a.as_tuple(), transformed_b.as_tuple())

    assert transformed_distance == pytest.approx(source_distance, rel=1e-12, abs=1e-12)


def test_axis_transform_matches_hand_authored_golden_case() -> None:
    case = json.loads(WRONG_AXIS.read_text(encoding="utf-8"))
    source = Vec3(*case["source_point"])
    expected = Vec3(*case["expected_staad_y_up"])

    assert sketchup_z_up_to_staad_y_up(source) == expected


def test_axis_transform_inverse_round_trip_using_independent_inverse_formula() -> None:
    source = Vec3(4.25, -2.0, 8.5)
    staad = sketchup_z_up_to_staad_y_up(source)
    reconstructed_source = Vec3(staad.x, -staad.z, staad.y)

    assert reconstructed_source == source


def test_measure_matches_independent_3d_distance() -> None:
    assert measure(Vec3(0.0, 0.0, 0.0), Vec3(3.0, 4.0, 12.0)) == pytest.approx(13.0)


def test_model_extents_returns_minimum_maximum_and_size() -> None:
    extents = model_extents(
        (
            Vec3(-1.0, 2.0, -3.0),
            Vec3(5.0, 7.0, 4.0),
            Vec3(2.0, -2.0, 1.0),
        )
    )

    assert extents == Extents(
        minimum=Vec3(-1.0, -2.0, -3.0),
        maximum=Vec3(5.0, 7.0, 4.0),
        size=Vec3(6.0, 9.0, 7.0),
    )


def test_model_extents_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one point"):
        model_extents(())


def test_reference_scale_ratio_matches_hand_authored_wrong_scale_case() -> None:
    case = json.loads(WRONG_SCALE.read_text(encoding="utf-8"))

    ratio = reference_scale_ratio(case["measured_m"], case["expected_m"])

    assert ratio == pytest.approx(case["expected_ratio"])


@pytest.mark.parametrize("ratio", [10.0, 100.0, 1000.0, 25.4, 304.8])
def test_reference_scale_warning_recognizes_known_suspicious_factors(ratio: float) -> None:
    warning = reference_scale_warning(measured_m=ratio * 6.0, expected_m=6.0)

    assert warning is not None
    assert f"{ratio:g}" in warning


def test_reference_scale_warning_does_not_warn_for_small_normal_difference() -> None:
    assert reference_scale_warning(measured_m=6.01, expected_m=6.0) is None


def test_reference_scale_ratio_rejects_invalid_reference_length() -> None:
    with pytest.raises(ValueError, match="Expected reference length"):
        reference_scale_ratio(measured_m=6.0, expected_m=0.0)


def test_transform_batch_converts_units_before_z_up_to_y_up_mapping() -> None:
    batch = ImportBatch(
        points=(RawPoint(Vec3(1000.0, 2000.0, 3000.0), "P1", "POINTS"),),
        segments=(
            RawSegment(
                Vec3(1000.0, 2000.0, 3000.0),
                Vec3(2000.0, 2000.0, 3000.0),
                "M1",
                "BEAM",
            ),
        ),
        source_format="dxf",
        declared_unit="mm",
        metadata={"source_file": "frame.dxf"},
        warnings=("source warning",),
    )

    transformed = transform_batch(batch, LengthUnit.MILLIMETER, "Z-UP")

    assert transformed.points[0].position == Vec3(1.0, 3.0, -2.0)
    assert transformed.segments[0].start == Vec3(1.0, 3.0, -2.0)
    assert transformed.segments[0].end == Vec3(2.0, 3.0, -2.0)
    assert measure(transformed.segments[0].start, transformed.segments[0].end) == pytest.approx(1.0)
    assert transformed.declared_unit == "m"
    assert transformed.source_format == "dxf"
    assert transformed.warnings == ("source warning",)
    assert transformed.metadata["source_unit"] == "mm"
    assert transformed.metadata["source_axis"] == "Z-UP"
    assert transformed.metadata["coordinate_unit"] == "m"
    assert transformed.metadata["coordinate_axis"] == "Y-UP"


def test_transform_batch_preserves_y_up_orientation_and_only_scales_units() -> None:
    batch = ImportBatch(
        segments=(RawSegment(Vec3(0.0, 1000.0, 2000.0), Vec3(0.0, 2000.0, 2000.0), "M1"),),
        source_format="dxf",
        declared_unit="mm",
    )

    transformed = transform_batch(batch, LengthUnit.MILLIMETER, "Y-UP")

    assert transformed.segments[0].start == Vec3(0.0, 1.0, 2.0)
    assert transformed.segments[0].end == Vec3(0.0, 2.0, 2.0)


def test_transform_batch_does_not_mutate_or_auto_rescale_source_batch() -> None:
    batch = ImportBatch(
        segments=(RawSegment(Vec3(0.0, 0.0, 0.0), Vec3(6000.0, 0.0, 0.0), "M1"),),
        source_format="dxf",
        declared_unit="mm",
    )

    transformed = transform_batch(batch, LengthUnit.MILLIMETER, "Y-UP")

    assert batch.segments[0].end == Vec3(6000.0, 0.0, 0.0)
    assert transformed.segments[0].end == Vec3(6.0, 0.0, 0.0)


def test_transform_batch_rejects_unknown_axis() -> None:
    with pytest.raises(ValueError, match="Unsupported source axis"):
        transform_batch(ImportBatch(), LengthUnit.METER, "SIDEWAYS")


def test_transform_batch_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError, match="Unknown length unit"):
        transform_batch(ImportBatch(), LengthUnit.UNKNOWN, "Y-UP")
