from __future__ import annotations

from staadprep.viewer.widget import StructuralViewport


def test_qt_to_vtk_coordinates_scale_and_flip_y() -> None:
    assert StructuralViewport._scaled_vtk_display_coordinates(
        100.0,
        50.0,
        widget_size=(400, 200),
        render_size=(800, 400),
    ) == (200.0, 300.0)


def test_qt_to_vtk_coordinates_preserve_one_to_one_display() -> None:
    assert StructuralViewport._scaled_vtk_display_coordinates(
        125.0,
        20.0,
        widget_size=(500, 300),
        render_size=(500, 300),
    ) == (125.0, 280.0)


def test_qt_to_vtk_coordinates_fail_closed_for_zero_size() -> None:
    assert (
        StructuralViewport._scaled_vtk_display_coordinates(
            10.0,
            10.0,
            widget_size=(0, 200),
            render_size=(800, 400),
        )
        is None
    )
    assert (
        StructuralViewport._scaled_vtk_display_coordinates(
            10.0,
            10.0,
            widget_size=(400, 200),
            render_size=(800, 0),
        )
        is None
    )
