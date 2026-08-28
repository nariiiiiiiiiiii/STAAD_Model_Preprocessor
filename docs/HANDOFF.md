# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T02 implemented on `task/02-ui`; awaiting user approval before T03.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source files, worktrees, temp, logs, cache, build output, artifacts, test output, generated reports, and staged dependencies must remain inside this root.

## Product goal

Eliminate repetitive structural-geometry cleanup between SketchUp and STAAD.Pro.

Primary workflow:

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 is a geometry/topology preprocessor, not a solver or mini STAAD.

## Locked baselines

Technology:
- Python 3.12+ application target.
- PySide6 desktop UI.
- PyVista/VTK real 3D viewport planned for T04.
- NumPy/SciPy for indexed numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- Nuitka preferred for Windows packaging after compatibility is proven.

UI references:
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

Do not request this approval again for the same scoped V1 behavior. Request a new approval only for a new high-risk area outside HR-1..HR-4.

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

## Completed T01

Commit merged into master before T02:
- `4a7551b chore: bootstrap project-local Python runtime`

Delivered:
- `pyproject.toml`,
- `src/staadprep/paths.py`,
- project-local runtime path guard,
- project-local `.venv` workflow,
- path escape tests,
- `scripts/run_dev.ps1`.

## T02 — completed deliverables

Branch/worktree:
- branch: `task/02-ui`
- worktree: `.worktrees/task-02-ui`
- base commit: `4a7551b`

Created:
- `src/staadprep/app.py`
- `src/staadprep/ui/__init__.py`
- `src/staadprep/ui/main_window.py`
- `src/staadprep/ui/theme.py`
- `src/staadprep/ui/panels.py`
- `tests/ui/test_main_window.py`

Updated:
- `scripts/run_dev.ps1`
- `docs/TASK_BOARD.md`
- `docs/CHECKLIST.md`
- implementation-plan T02 checkboxes
- this handoff

UI shell includes:
- top toolbar: Import Model / Unit Check / Repair / Normalize Axis / Renumber / Validate / Export STD,
- left Project Explorer + model summary,
- central dark structural viewport placeholder,
- right Properties / Validation / Quick Fix panels,
- bottom Issue Console,
- persistent `MODEL STATUS: NO MODEL` summary.

All engineering actions remain intentionally disabled until the corresponding functional Tasks are implemented.

The temporary viewport is a lightweight painted structural frame/grid only. The real PyVista/VTK 3D viewport belongs to T04.

## T02 runtime verification

Observed environment:
- Windows Python: `3.14.3`
- PySide6: `6.11.2`
- Qt runtime: `6.11.2`

PySide6 imports and runs on the current Python 3.14.3 environment.

Verification performed:
- UI tests for approved regions,
- disabled-action safety test,
- QApplication factory reuse test,
- T01 path regression tests,
- Ruff lint,
- headless app launch with timed auto-exit,
- `scripts/run_dev.ps1` launch path,
- project-local UI screenshot generation.

Generated review artifact (ignored by Git, remains inside project):
- `artifacts/t02_ui_shell.png`

Important test-environment note:
- Qt tests must set `QT_QPA_PLATFORM=offscreen` when run non-interactively.
- An early shell command failed to pass the setting correctly and displayed a Qt window; the corrected PowerShell environment syntax is now used for automated smoke tests.

## Known constraints

- No real model data exists yet.
- No importer is enabled yet.
- No structural or engineering semantics were added in T02.
- PyVista/VTK were not exercised in T02; their runtime compatibility is verified in T04.
- Toolbar/Quick Fix controls are visible but disabled until their backing Tasks exist.

## Next Task

**T03 — Canonical Node/Member/Project Model + Project Serialization**

Risk: STANDARD.

T03 will define stable internal identities and versioned project serialization. It must not implement topology merge/repair semantics; those remain under later STRICT Tasks.

Do not start T03 until the user explicitly says `เริ่ม Task 3` / `Run T03`.

## Resume instruction

1. Review branch `task/02-ui` / worktree `.worktrees/task-02-ui` if needed.
2. When the user approves by starting T03, integrate T02 into master.
3. Create a new isolated T03 worktree.
4. Execute only Task 03 from the detailed implementation plan.
