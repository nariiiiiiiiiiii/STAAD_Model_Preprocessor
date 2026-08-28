"""Real Qt/VTK smoke flow for issue inspection, quick fix, undo, and redo."""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID

os.environ.setdefault("QT_API", "pyside6")

from staadprep.app import create_application
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.main_window import MainWindow
from staadprep.validation.issues import IssueType

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/golden_models/10_combined_dirty_frame/case.json"


def _load_fixture() -> ProjectModel:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    nodes = {
        UUID(int=item["id"]): Node(
            key=UUID(int=item["id"]),
            position=Vec3(*item["xyz"]),
        )
        for item in payload["nodes"]
    }
    members = {
        UUID(int=item["id"]): Member(
            key=UUID(int=item["id"]),
            start=UUID(int=item["start"]),
            end=UUID(int=item["end"]),
        )
        for item in payload["members"]
    }
    return ProjectModel(nodes=nodes, members=members)


def main() -> int:
    app = create_application()
    window = MainWindow(confirm_delete=lambda _message: True)
    window.set_canonical_model(_load_fixture())
    app.processEvents()

    initial_count = len(window.current_issues)
    expected = {
        IssueType.DUPLICATE_NODE,
        IssueType.NEAR_NODE,
        IssueType.ORPHAN_NODE,
        IssueType.ZERO_LENGTH_MEMBER,
        IssueType.SHORT_MEMBER,
        IssueType.DUPLICATE_MEMBER,
        IssueType.UNCONNECTED_GAP,
        IssueType.CROSSING_WITHOUT_NODE,
        IssueType.DISCONNECTED_STRUCTURE,
    }
    if not expected.issubset({issue.type for issue in window.current_issues}):
        raise RuntimeError("Combined dirty fixture did not expose all expected issue types")

    detached = next(
        issue for issue in window.current_issues if issue.type is IssueType.DISCONNECTED_STRUCTURE
    )
    window.issue_console.select_issue(detached.id)
    window.issue_console.request_isolate_selected()
    app.processEvents()
    viewport = window.viewport_host
    if viewport._member_actor is None or viewport._member_actor.GetVisibility() != 0:
        raise RuntimeError("Disconnected structure isolation did not hide the base member actor")
    viewport.clear_isolation()

    gap = next(issue for issue in window.current_issues if issue.type is IssueType.UNCONNECTED_GAP)
    window.issue_console.select_issue(gap.id)
    window.apply_selected_quick_fix()
    app.processEvents()
    if any(issue.id == gap.id for issue in window.current_issues):
        raise RuntimeError("Gap issue remained after MergeNodes quick fix")

    window.undo_repair()
    app.processEvents()
    if not any(issue.type is IssueType.UNCONNECTED_GAP for issue in window.current_issues):
        raise RuntimeError("Undo did not restore the unconnected gap")

    window.redo_repair()
    app.processEvents()
    if any(issue.type is IssueType.UNCONNECTED_GAP for issue in window.current_issues):
        raise RuntimeError("Redo did not reapply the gap repair")

    window.close()
    app.processEvents()
    print(
        "ISSUE_REPAIR_SMOKE_PASS",
        f"initial_issues={initial_count}",
        f"final_issues={len(window.current_issues)}",
        "undo=pass",
        "redo=pass",
        "isolate=pass",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
