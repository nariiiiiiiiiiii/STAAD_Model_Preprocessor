from __future__ import annotations

from staadprep.editing.inference import AxisLock, InferenceEngine, SnapKind
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel


def test_x_axis_lock_changes_only_x_and_preserves_reference_yz() -> None:
    hit = InferenceEngine.resolve(
        ProjectModel(),
        Vec3(8.0, 99.0, -77.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.X,
        reference_position=Vec3(1.0, 2.0, 3.0),
    )

    assert hit is not None
    assert hit.kind is SnapKind.AXIS_X
    assert hit.position == Vec3(8.0, 2.0, 3.0)
    assert hit.label == "X AXIS"


def test_y_axis_lock_changes_only_vertical_y() -> None:
    hit = InferenceEngine.resolve(
        ProjectModel(),
        Vec3(88.0, 9.0, -66.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.Y,
        reference_position=Vec3(1.0, 2.0, 3.0),
    )

    assert hit is not None
    assert hit.kind is SnapKind.AXIS_Y
    assert hit.position == Vec3(1.0, 9.0, 3.0)
    assert hit.label == "Y AXIS"
    assert "Vertical" in InferenceEngine.axis_helper_text(AxisLock.Y)


def test_z_axis_lock_changes_only_z() -> None:
    hit = InferenceEngine.resolve(
        ProjectModel(),
        Vec3(88.0, 77.0, 10.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.Z,
        reference_position=Vec3(1.0, 2.0, 3.0),
    )

    assert hit is not None
    assert hit.kind is SnapKind.AXIS_Z
    assert hit.position == Vec3(1.0, 2.0, 10.0)
    assert hit.label == "Z AXIS"


def test_axis_lock_without_reference_is_non_committable() -> None:
    hit = InferenceEngine.resolve(
        ProjectModel(),
        Vec3(8.0, 9.0, 10.0),
        tolerance_m=0.01,
        axis_lock=AxisLock.X,
    )

    assert hit is None
