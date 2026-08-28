# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T01 implemented on `task/01-bootstrap`; awaiting user approval before T02.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source files, temp, logs, cache, build output, artifacts, test output, generated reports, worktrees, and staged dependencies must remain inside this root.

## User goal

Eliminate repetitive structural-geometry cleanup between SketchUp and STAAD.Pro so design work can begin with little or no manual model cleanup in STAAD.Pro.

Primary workflow:

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 is a geometry/topology preprocessor, not a structural solver or mini STAAD.

## Approved baselines

Technology:
- Python 3.12+ primary application language.
- PySide6 desktop UI.
- PyVista/VTK 3D viewport.
- NumPy/SciPy for indexed numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- Nuitka preferred for Windows packaging after runtime compatibility is proven.

UI:
- `docs/UI_BASELINE.md`
- `docs/ui/main_dashboard.svg`
- `docs/ui/unit_check.svg`
- `docs/ui/issue_repair.svg`

Do not redesign V1 unless explicitly requested.

## Approval state

User explicitly approved on 2026-08-28:
1. current Project Spec,
2. STRICT / Full TDD for HR-1 through HR-4.

Approved high-risk areas:
- HR-1 unit/scale/coordinate/axis transformations,
- HR-2 topology/connectivity detection and structural graph repair,
- HR-3 STAAD `.STD` exporter semantics,
- HR-4 deterministic node/member numbering and mapping integrity.

Do not request this approval again for the same scoped V1 behavior. Request a new approval only if a new high-risk area outside HR-1..HR-4 appears.

## Execution mode

Execute exactly one numbered Task at a time.

Detailed plan:
`docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`

Operational board:
`docs/TASK_BOARD.md`

End-of-Task sequence:
1. targeted verification,
2. update TASK_BOARD/CHECKLIST/HANDOFF,
3. Git commit,
4. report to user,
5. STOP until explicit instruction to run the next Task.

## T01 — completed deliverables

Branch/worktree:
- branch: `task/01-bootstrap`
- worktree: `.worktrees/task-01-bootstrap`
- base commit: `d897b91`

Created:
- `pyproject.toml` with src-layout package/test/tool configuration,
- `src/staadprep/__init__.py`,
- `src/staadprep/paths.py`,
- `tests/unit/test_paths.py`,
- `scripts/run_dev.ps1`,
- tracked `.tmp/.gitkeep` parent anchor for project-local pytest temp.

Updated:
- `.gitignore`,
- `docs/TASK_BOARD.md`,
- `docs/CHECKLIST.md`,
- this handoff,
- T01 checkboxes in the detailed implementation plan.

`ProjectPaths` contract now provides:
- `ProjectPaths.from_root(root: Path) -> ProjectPaths`,
- `ProjectPaths.ensure_layout() -> None`,
- `ProjectPaths.assert_inside_project(path: Path) -> Path`.

Owned runtime directories:
- `.tmp/`,
- `.cache/`,
- `.logs/`,
- `artifacts/`,
- `build/`,
- `dist/`,
- `vendor/`.

Relative paths are interpreted from the canonical project root. Paths are resolved before the containment check so `..` traversal cannot escape the project.

## T01 verification

Required test command:
`python -m pytest tests/unit/test_paths.py -v --basetemp=.tmp/pytest`

Required lint command:
`python -m ruff check src tests`

Additional smoke checks:
- instantiate `ProjectPaths` against the real task worktree and create the runtime layout,
- verify all owned generated directories resolve under the project root,
- parse `scripts/run_dev.ps1` as a PowerShell script block.

Environment observation:
- only Python `3.14.3` is currently registered through the Windows `py` launcher,
- T01 uses a project-local `.venv`,
- only `pytest` and `ruff` were needed/used for T01 verification,
- PySide6/PyVista/VTK compatibility with Python 3.14 has not yet been exercised; T02 must verify this before UI implementation proceeds.

## Known issues / constraints

- `scripts/run_dev.ps1` intentionally targets `python -m staadprep.app`; the `staadprep.app` entry point belongs to T02 and therefore is not created in T01.
- No engineering/geometry semantics were implemented in T01.
- No files were intentionally created outside the canonical project root.

## Next Task

**T02 — Approved Desktop UI Shell**

Risk: FAST/STANDARD.

T02 must:
- verify/install compatible UI dependencies inside the project-local `.venv`,
- create the desktop entry point,
- reproduce the approved dark engineering shell,
- keep engineering actions disabled until their backing Tasks exist.

Do not start T02 until the user explicitly says `เริ่ม Task 2` / `Run T02`.

## Resume instruction

1. Open the canonical project root.
2. Use the T01 worktree/branch for review: `.worktrees/task-01-bootstrap`, branch `task/01-bootstrap`.
3. After user approval, integrate T01 as appropriate and execute only T02 from the detailed plan.
