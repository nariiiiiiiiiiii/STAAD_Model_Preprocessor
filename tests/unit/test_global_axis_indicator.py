from staadprep.viewer.widget import StructuralViewport


class RecordingPlotter:
    def __init__(self) -> None:
        self.axes_kwargs: dict[str, object] | None = None

    def set_background(self, _color: str) -> None:
        pass

    def add_axes(self, **kwargs: object) -> None:
        self.axes_kwargs = kwargs

    def show_grid(self, **_kwargs: object) -> None:
        pass


def test_global_axis_indicator_labels_xyz() -> None:
    viewport = StructuralViewport.__new__(StructuralViewport)
    viewport.plotter = RecordingPlotter()
    viewport._off_screen = False

    viewport._configure_scene()

    assert viewport.plotter.axes_kwargs is not None
    assert viewport.plotter.axes_kwargs["xlabel"] == "X"
    assert viewport.plotter.axes_kwargs["ylabel"] == "Y"
    assert viewport.plotter.axes_kwargs["zlabel"] == "Z"
    assert viewport.plotter.axes_kwargs["labels_off"] is False
    assert viewport.plotter.axes_kwargs["color"] == "#f2f2f2"
