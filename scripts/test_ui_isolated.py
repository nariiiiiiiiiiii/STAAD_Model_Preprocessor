from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path

_NATIVE_RENDERER_MARKERS = (
    "StructuralViewport",
    "pyvista",
    "vtk",
    "QtInteractor",
    "smoke_",
)


def classify_ui_test_files(files: Iterable[Path]) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    """Split UI test files into normal Qt and native-renderer isolation groups."""
    lightweight: list[Path] = []
    renderer_heavy: list[Path] = []
    for path in sorted(files):
        text = path.read_text(encoding="utf-8")
        target = (
            renderer_heavy
            if any(marker in text for marker in _NATIVE_RENDERER_MARKERS)
            else lightweight
        )
        target.append(path)
    return tuple(lightweight), tuple(renderer_heavy)


def format_summary(
    *,
    lightweight_total: int,
    lightweight_passed: int,
    renderer_total: int,
    renderer_passed: int,
    failed_files: Sequence[str],
) -> str:
    total = lightweight_total + renderer_total
    passed = lightweight_passed + renderer_passed
    light_state = "PASS" if lightweight_passed == lightweight_total else "FAIL"
    renderer_state = "PASS" if renderer_passed == renderer_total else "FAIL"
    total_state = "PASS" if passed == total and not failed_files else "FAIL"
    lines = [
        "UI Verification",
        f"Lightweight: {lightweight_passed}/{lightweight_total} {light_state}",
        f"VTK isolated: {renderer_passed}/{renderer_total} {renderer_state}",
        f"Total: {passed}/{total} {total_state}",
    ]
    if failed_files:
        lines.append("Failed: " + ", ".join(failed_files))
    return "\n".join(lines)


def _result_path(result_dir: Path, key: str) -> Path:
    safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
    return result_dir / f"{safe_key}.json"


def save_result(result_dir: Path, key: str, *, passed: int, total: int) -> Path:
    """Persist one verification result without deleting prior run data."""
    result_dir.mkdir(parents=True, exist_ok=True)
    path = _result_path(result_dir, key)
    payload = {"key": key, "passed": passed, "total": total}
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _load_result(result_dir: Path, key: str) -> tuple[int, int] | None:
    path = _result_path(result_dir, key)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("key") != key:
        return None
    passed = payload.get("passed")
    total = payload.get("total")
    if not isinstance(passed, int) or not isinstance(total, int):
        return None
    return passed, total


def aggregate_saved_results(
    result_dir: Path,
    *,
    lightweight_total: int,
    renderer_counts: dict[str, int],
) -> tuple[int, int, tuple[str, ...]]:
    """Aggregate MCP-safe shard results for a single run id."""
    failed: list[str] = []
    lightweight_passed = 0
    renderer_passed = 0

    if lightweight_total:
        result = _load_result(result_dir, "lightweight")
        if result is None:
            failed.append("missing:lightweight")
        else:
            passed, total = result
            if total != lightweight_total or passed != total:
                failed.append("lightweight")
            else:
                lightweight_passed = passed

    for file_name, expected_total in sorted(renderer_counts.items()):
        key = f"renderer-{file_name}"
        result = _load_result(result_dir, key)
        if result is None:
            failed.append(f"missing:{key}")
            continue
        passed, total = result
        if total != expected_total or passed != total:
            failed.append(key)
            continue
        renderer_passed += passed

    return lightweight_passed, renderer_passed, tuple(failed)


def _project_environment(project_root: Path) -> dict[str, str]:
    tmp_root = project_root / ".tmp"
    temp_root = tmp_root / "temp"
    cache_root = project_root / ".cache"
    log_root = project_root / ".logs"
    for directory in (tmp_root, temp_root, cache_root, log_root):
        directory.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "windows"
    env["TEMP"] = str(temp_root)
    env["TMP"] = str(temp_root)
    env["PYTHONPYCACHEPREFIX"] = str(cache_root / "pycache")
    env["STAADPREP_PROJECT_ROOT"] = str(project_root)
    env["STAADPREP_CACHE_DIR"] = str(cache_root)
    env["STAADPREP_LOG_DIR"] = str(log_root)
    env["PYTHONPATH"] = str(project_root / "src")
    env["PYTHONUTF8"] = "1"
    return env


def _relative_test_arg(project_root: Path, path: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _collect_node_ids(
    project_root: Path,
    files: Sequence[Path],
    *,
    env: dict[str, str],
) -> tuple[str, ...]:
    if not files:
        return ()
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        *(_relative_test_arg(project_root, path) for path in files),
    ]
    completed = subprocess.run(
        command,
        cwd=project_root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise RuntimeError("pytest collection failed for isolated UI runner")
    return tuple(line.strip() for line in completed.stdout.splitlines() if "::" in line)


def _count_by_file(node_ids: Sequence[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for node_id in node_ids:
        file_part = node_id.split("::", 1)[0].replace("\\", "/")
        counts[Path(file_part).name] += 1
    return counts


def _run_pytest(project_root: Path, files: Sequence[Path], *, env: dict[str, str]) -> int:
    if not files:
        return 0
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        *(_relative_test_arg(project_root, path) for path in files),
    ]
    return subprocess.run(command, cwd=project_root, env=env, check=False).returncode


def _renderer_shard(files: Sequence[Path], index: int, count: int) -> tuple[Path, ...]:
    if count < 1:
        raise ValueError("shard count must be positive")
    if index < 1 or index > count:
        raise ValueError("shard index must be between 1 and shard count")
    return tuple(path for offset, path in enumerate(files) if offset % count == index - 1)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Qt UI tests while isolating native VTK/renderer test files by subprocess."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root containing tests/ui and src.",
    )
    parser.add_argument(
        "--scope",
        choices=("all", "lightweight", "renderer"),
        default="all",
        help="Run all UI tests, only the lightweight group, or only renderer-heavy tests.",
    )
    parser.add_argument("--shard-index", type=int, default=1)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument(
        "--run-id",
        default="default",
        help="Checkpoint id shared by MCP-safe lightweight/renderer invocations.",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Collect and show the selected test plan without executing tests.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Aggregate saved results for --run-id without executing UI tests.",
    )
    return parser.parse_args(argv)


def _result_dir(project_root: Path, run_id: str) -> Path:
    if not run_id or any(not (char.isalnum() or char in "-_.") for char in run_id):
        raise ValueError("run id may contain only letters, digits, dash, underscore, and dot")
    return project_root / ".tmp" / "ui-isolated-results" / run_id


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    project_root = args.project_root.resolve()
    ui_root = project_root / "tests" / "ui"
    files = tuple(sorted(ui_root.glob("test_*.py")))
    if not files:
        print(f"No UI tests found under {ui_root}", file=sys.stderr)
        return 2

    try:
        result_dir = _result_dir(project_root, args.run_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    all_lightweight, all_renderer = classify_ui_test_files(files)
    env = _project_environment(project_root)

    if args.summary_only:
        try:
            all_node_ids = _collect_node_ids(project_root, files, env=env)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        all_counts = _count_by_file(all_node_ids)
        lightweight_total = sum(all_counts[path.name] for path in all_lightweight)
        renderer_counts = {path.name: all_counts[path.name] for path in all_renderer}
        lightweight_passed, renderer_passed, summary_failed_files = aggregate_saved_results(
            result_dir,
            lightweight_total=lightweight_total,
            renderer_counts=renderer_counts,
        )
        renderer_total = sum(renderer_counts.values())
        print(
            format_summary(
                lightweight_total=lightweight_total,
                lightweight_passed=lightweight_passed,
                renderer_total=renderer_total,
                renderer_passed=renderer_passed,
                failed_files=summary_failed_files,
            )
        )
        return (
            0
            if not summary_failed_files
            and lightweight_passed == lightweight_total
            and renderer_passed == renderer_total
            else 1
        )

    lightweight = all_lightweight
    renderer_heavy = all_renderer
    if args.scope != "renderer" and (args.shard_index != 1 or args.shard_count != 1):
        print("Renderer sharding is valid only with --scope renderer", file=sys.stderr)
        return 2
    if args.scope == "renderer":
        try:
            renderer_heavy = _renderer_shard(
                renderer_heavy,
                args.shard_index,
                args.shard_count,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        lightweight = ()
    elif args.scope == "lightweight":
        renderer_heavy = ()

    selected = (*lightweight, *renderer_heavy)
    try:
        node_ids = _collect_node_ids(project_root, selected, env=env)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    count_by_file = _count_by_file(node_ids)
    lightweight_total = sum(count_by_file[path.name] for path in lightweight)
    renderer_total = sum(count_by_file[path.name] for path in renderer_heavy)

    print(
        f"Plan: {lightweight_total} lightweight test(s), "
        f"{renderer_total} renderer test(s) across {len(renderer_heavy)} isolated file(s)"
    )
    if args.scope == "renderer" and args.shard_count > 1:
        print(f"Renderer shard: {args.shard_index}/{args.shard_count}")
    if args.list_only:
        for path in lightweight:
            print(f"LIGHT  {_relative_test_arg(project_root, path)}")
        for path in renderer_heavy:
            print(f"VTK    {_relative_test_arg(project_root, path)}")
        return 0

    lightweight_passed = 0
    renderer_passed = 0
    failed_files: list[str] = []

    if lightweight:
        print("\n[1/2] Running lightweight UI tests in one process...")
        if _run_pytest(project_root, lightweight, env=env) != 0:
            failed_files.append("lightweight-group")
            save_result(result_dir, "lightweight", passed=0, total=lightweight_total)
        else:
            lightweight_passed = lightweight_total
            save_result(
                result_dir,
                "lightweight",
                passed=lightweight_total,
                total=lightweight_total,
            )

    if not failed_files and renderer_heavy:
        print("\n[2/2] Running renderer-heavy UI files in isolated subprocesses...")
        for index, path in enumerate(renderer_heavy, start=1):
            relative = _relative_test_arg(project_root, path)
            print(f"[{index}/{len(renderer_heavy)}] {relative}")
            test_count = count_by_file[path.name]
            result_key = f"renderer-{path.name}"
            if _run_pytest(project_root, (path,), env=env) != 0:
                save_result(result_dir, result_key, passed=0, total=test_count)
                failed_files.append(path.name)
                break
            renderer_passed += test_count
            save_result(result_dir, result_key, passed=test_count, total=test_count)

    print()
    print(
        format_summary(
            lightweight_total=lightweight_total,
            lightweight_passed=lightweight_passed,
            renderer_total=renderer_total,
            renderer_passed=renderer_passed,
            failed_files=tuple(failed_files),
        )
    )
    return (
        0
        if not failed_files
        and lightweight_passed == lightweight_total
        and renderer_passed == renderer_total
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
