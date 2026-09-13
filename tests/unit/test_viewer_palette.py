from staadprep.viewer.palette import VIEWPORT_LABEL_TEXT_COLOR


def test_viewport_label_text_color_is_light_for_dark_background() -> None:
    assert VIEWPORT_LABEL_TEXT_COLOR == "#f2f2f2"
