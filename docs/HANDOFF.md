# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T10 complete on `task/10-issue-ui`; awaiting user approval before T11.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Completed task commits before T10

- T01 `4a7551b` — project-local Python/runtime bootstrap and path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical Node/Member/Project model + serialization.
- T04 `a38fc97` — real PyVista/VTK viewport + selection/highlight.
- T05 `9fcf6be` — raw DXF import + preview.
- T06 `8bf1b25` — STRICT unit/scale/axis transform engine.
- T07 `ce24224` — STRICT canonical topology + connected structures.
- T08 `adde44b` — STRICT read-only geometry/topology validators.
- T09 `7bfeb94` — STRICT reversible repair commands + undo/redo + audit.

## T10 — Issue Console + Quick-Fix UI

Branch/worktree:
- branch: `task/10-issue-ui`
- worktree: `.worktrees/task-10-issue-ui`
- base commit: `7bfeb94`

Created:
- `src/staadprep/ui/issue_console.py`
- `tests/ui/test_issue_console.py`
- `tests/ui/test_issue_repair_smoke.py`
- `scripts/smoke_issue_repair.py`

Modified:
- `src/staadprep/ui/main_window.py`
- `src/staadprep/ui/panels.py`
- `src/staadprep/viewer/widget.py`
- `scripts/smoke_viewport.py`
- `tests/ui/test_structural_viewport.py`
- Task/checklist/plan docs.

Note: the original plan listed `viewer/scene.py` for T10. Camera focus and isolate behavior were implemented in `viewer/widget.py` instead because they are renderer state, not canonical scene-data transformation.

## T10 behavior

Issue Console:
- exact `Issue.id` stored on every row,
- severity filter: ALL / ERROR / WARNING / INFO,
- ERROR/WARNING/INFO counts,
- selecting an issue highlights exact canonical node/member UUIDs,
- selecting an issue fits the camera to its entities/location,
- disconnected-structure issue can isolate the affected structure in the real viewport.

Quick Fix dispatch uses only T09 `RepairCommand` objects through `RepairHistory`.

Supported selected-issue quick fixes:
- DUPLICATE_NODE -> `MergeNodes`,
- NEAR_NODE -> `MergeNodes`,
- UNCONNECTED_GAP -> `MergeNodes`,
- ORPHAN_NODE -> `DeleteNode`,
- ZERO_LENGTH_MEMBER -> `DeleteMember`,
- SHORT_MEMBER -> `DeleteMember`,
- DUPLICATE_MEMBER -> delete one duplicate member.

Delete commands require user confirmation before execution.

CROSSING_WITHOUT_NODE is inspect/highlight only in T10. It is intentionally not auto-fixed by a non-atomic UI sequence because a correct crossing repair requires two splits plus canonical-node unification; no composite STRICT repair command exists yet. Do not hide this limitation.

Undo/Redo:
- Ctrl+Z / Ctrl+Y actions exist,
- Quick Fix panel exposes Undo / Redo buttons,
- execute/undo/redo automatically re-renders and re-runs validation,
- Project Explorer, Validation panel, status bar, issue counts and history controls refresh after every mutation.

## Runtime issue found and fixed during T10

Real Qt/VTK smoke exposed a PyVista picking lifecycle bug after repair refresh:

`PyVistaPickingError: Picking is already enabled`

Root cause: `StructuralViewport.set_model()` rebound picking after every model refresh without disabling the prior picking session.

Fix: disable active picking before clearing/rebuilding the viewport, then enable picking on the new member actor.

Regression coverage is in the real Windows Qt/VTK issue-repair smoke test.

## T10 verification evidence

TDD RED evidence:
- `staadprep.ui.issue_console` initially missing.
- viewport focus/isolate smoke initially lacked required behavior markers.
- combined dirty-model smoke initially failed because `smoke_issue_repair.py` did not exist.
- after the smoke harness existed, it exposed the real repeated-picking lifecycle failure described above.

Targeted UI verification:
- 11 UI tests passed.
- real viewport focus/isolate smoke passed.
- combined dirty fixture real Qt/VTK repair smoke passed.

Full regression before documentation update:
- 116 tests passed.
- Ruff passed.
- targeted mypy for T10 UI modules passed after adding Qt callback/variadic annotations.

## Current UI/product boundary

The app can now inspect, highlight, isolate, repair and undo/redo a canonical `ProjectModel` interactively.

The raw DXF import path still stops at `RAW DXF PREVIEW — NOT VALIDATED`; Unit Check/reference-dimension UI has not yet been wired to convert raw DXF into canonical metre/Y-Up topology automatically. Do not silently assume source axis/scale to bypass that gate.

## Next task

**T11 — Member Incidence / Local-X Normalization**

Risk: **STRICT HR-2 / Full TDD already approved by user.**

T11 owns deterministic member-direction classification/normalization and viewer direction arrows. It must not change T10 issue/repair semantics except where required to expose orientation-specific UI state.

Do not start T11 until the user explicitly requests it.
