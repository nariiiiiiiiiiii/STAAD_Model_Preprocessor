"""Windows-render smoke test for the T05 raw DXF preview pipeline."""

# ruff: noqa: E402, I001

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.environ.setdefault("QT_API", "pyside6")

from staadprep.app import create_application
from staadprep.ui.main_window import MainWindow

FIXTURE = PROJECT_ROOT / "tests/golden_models/01_dxf_lines/source.dxf"


def main() -> int:
    app = create_application()
    window = MainWindow(confirm_exit=lambda _dirty: True)
    batch = window.load_raw_dxf(FIXTURE)
    window.show()
    app.processEvents()

    scene = window.viewport_host.scene
    if scene is None:
        raise RuntimeError("DXF preview did not populate viewport SceneData")
    if len(batch.segments) != 3 or len(batch.points) != 1:
        raise RuntimeError("Unexpected raw DXF entity counts")
    if len(scene.member_keys) != 3 or len(scene.point_keys) != 7:
        raise RuntimeError("Raw preview changed endpoint topology unexpectedly")
    if window.model_status.text() != "RAW DXF PREVIEW — NOT VALIDATED":
        raise RuntimeError("Raw preview status is not explicitly marked NOT VALIDATED")

    window.close()
    app.processEvents()
    print(
        "DXF_PREVIEW_SMOKE_PASS",
        f"segments={len(batch.segments)}",
        f"points={len(batch.points)}",
        f"render_nodes={len(scene.point_keys)}",
        f"render_members={len(scene.member_keys)}",
        f"unit={batch.declared_unit}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
