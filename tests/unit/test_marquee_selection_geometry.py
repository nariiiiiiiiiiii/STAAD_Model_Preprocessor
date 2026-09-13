from __future__ import annotations

from PySide6.QtCore import QRectF

from staadprep.viewer.widget import StructuralViewport


def test_screen_segment_intersection_handles_crossing_inside_and_outside() -> None:
    rectangle = QRectF(10.0, 10.0, 20.0, 20.0)

    assert StructuralViewport._segment_intersects_rectangle(
        (0.0, 20.0), (40.0, 20.0), rectangle
    )
    assert StructuralViewport._segment_intersects_rectangle(
        (15.0, 15.0), (25.0, 25.0), rectangle
    )
    assert not StructuralViewport._segment_intersects_rectangle(
        (0.0, 0.0), (5.0, 5.0), rectangle
    )
    assert not StructuralViewport._segment_intersects_rectangle(
        (0.0, 5.0), (40.0, 5.0), rectangle
    )
