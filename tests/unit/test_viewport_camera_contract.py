from __future__ import annotations

from staadprep.viewer.widget import StructuralViewport


def test_staad_isometric_camera_is_y_up_and_looks_from_positive_xyz() -> None:
    position, focal, view_up = StructuralViewport._staad_isometric_camera(
        (0.0, 8.0, -2.0, 4.0, 1.0, 5.0)
    )

    assert focal == (4.0, 1.0, 3.0)
    assert all(position[index] > focal[index] for index in range(3))
    assert view_up == (0.0, 1.0, 0.0)


def test_staad_isometric_camera_handles_zero_span_bounds() -> None:
    position, focal, view_up = StructuralViewport._staad_isometric_camera(
        (2.0, 2.0, 3.0, 3.0, 4.0, 4.0)
    )

    assert focal == (2.0, 3.0, 4.0)
    assert position == (3.0, 4.0, 5.0)
    assert view_up == (0.0, 1.0, 0.0)
