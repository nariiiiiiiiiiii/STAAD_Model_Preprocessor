from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = PROJECT_ROOT / "scripts" / "test_ui_isolated.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("staadprep_ui_isolated_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load isolated UI runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_classification_covers_every_ui_file_once_and_detects_native_renderer_tests() -> None:
    runner = _load_runner()
    files = sorted((PROJECT_ROOT / "tests" / "ui").glob("test_*.py"))

    lightweight, renderer_heavy = runner.classify_ui_test_files(files)

    assert set(lightweight).isdisjoint(renderer_heavy)
    assert set(lightweight) | set(renderer_heavy) == set(files)

    heavy_names = {path.name for path in renderer_heavy}
    assert {
        "test_inference_viewport.py",
        "test_issue_repair_smoke.py",
        "test_manual_edit_mouse.py",
        "test_manual_edit_real_smoke.py",
        "test_manual_edit_smoke.py",
        "test_orientation_smoke.py",
        "test_precision_create_real_smoke.py",
        "test_precision_mouse.py",
        "test_precision_viewport.py",
        "test_precision_viewport_collision_preview.py",
        "test_set_direction_viewport.py",
        "test_structural_viewport.py",
    } <= heavy_names
    assert "test_ready_gate_ui.py" in {path.name for path in lightweight}
    assert "test_export_ui.py" in {path.name for path in lightweight}


def test_summary_reports_exact_green_counts() -> None:
    runner = _load_runner()

    summary = runner.format_summary(
        lightweight_total=62,
        lightweight_passed=62,
        renderer_total=30,
        renderer_passed=30,
        failed_files=(),
    )

    assert "Lightweight: 62/62 PASS" in summary
    assert "VTK isolated: 30/30 PASS" in summary
    assert "Total: 92/92 PASS" in summary


def test_saved_mcp_shards_aggregate_to_one_complete_summary(tmp_path: Path) -> None:
    runner = _load_runner()
    renderer_counts = {"a.py": 4, "b.py": 3}

    runner.save_result(tmp_path, "lightweight", passed=5, total=5)
    runner.save_result(tmp_path, "renderer-a.py", passed=4, total=4)
    runner.save_result(tmp_path, "renderer-b.py", passed=3, total=3)

    light_passed, renderer_passed, failed = runner.aggregate_saved_results(
        tmp_path,
        lightweight_total=5,
        renderer_counts=renderer_counts,
    )

    assert light_passed == 5
    assert renderer_passed == 7
    assert failed == ()


def test_saved_mcp_summary_reports_missing_renderer_shard(tmp_path: Path) -> None:
    runner = _load_runner()
    renderer_counts = {"a.py": 4, "b.py": 3}
    runner.save_result(tmp_path, "lightweight", passed=5, total=5)
    runner.save_result(tmp_path, "renderer-a.py", passed=4, total=4)

    _, _, failed = runner.aggregate_saved_results(
        tmp_path,
        lightweight_total=5,
        renderer_counts=renderer_counts,
    )

    assert failed == ("missing:renderer-b.py",)
