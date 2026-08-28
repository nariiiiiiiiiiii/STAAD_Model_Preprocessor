# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T03 complete on `task/03-model`; T04 authorized by user and next in this execution.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry; it is not a structural solver or mini STAAD.

## Locked baselines

- Python 3.12+ application target.
- PySide6 desktop UI.
- PyVista/VTK 3D viewport.
- NumPy/SciPy for numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- UI baseline: `docs/UI_BASELINE.md` and `docs/ui/*.svg`.
- STRICT approval already granted for HR-1 through HR-4.

## Execution rule

Normally execute one Task at a time. For the current run, the user explicitly requested `Task 3 + 4`; therefore T03 and T04 may execute sequentially, each with its own verification and commit. Stop after T04.

## Completed T01

Commit: `4a7551b chore: bootstrap project-local Python runtime`

Key outputs:
- project-local Python/runtime path guard,
- `.tmp/.cache/.logs/artifacts/build/dist/vendor` ownership,
- path escape tests,
- `scripts/run_dev.ps1`.

## Completed T02

Commit: `8e4c2f8 feat: add approved desktop UI shell`

Key outputs:
- locked desktop shell layout,
- toolbar/project explorer/viewport host/right panels/issue console/status,
- engineering actions disabled until backing Tasks exist,
- PySide6 6.11.2 verified on current Python 3.14.3 environment.

## T03 — completed deliverables

Branch/worktree:
- branch: `task/03-model`
- worktree: `.worktrees/task-03-model`
- base commit: `8e4c2f8`

Created:
- `src/staadprep/model/__init__.py`
- `src/staadprep/model/geometry.py`
- `src/staadprep/model/entities.py`
- `src/staadprep/model/project.py`
- `src/staadprep/model/serialization.py`
- `tests/unit/test_model.py`
- `tests/unit/test_serialization.py`

Canonical contracts:
- `Vec3(x, y, z)` rejects NaN/Infinity.
- `Node.key` and `Member.key` are stable UUID identities.
- STAAD-facing `.number` is independent from UUID identity.
- Members reference node UUIDs, not node numbers.
- `ProjectModel` stores node/member dictionaries, metadata, and revision.
- project JSON schema version is `1`.
- project JSON preserves identities, source refs, numbers, coordinates, metadata, and revision.

Important scope boundary:
- T03 does **not** merge nodes, determine connectivity, repair topology, convert units, transform axes, or assign engineering semantics.

## T03 verification

TDD RED observed:
- `ModuleNotFoundError: No module named 'staadprep.model'` before implementation.

GREEN targeted verification:
- model/serialization tests: 5 passed.
- Ruff: pass.

Environment/setup note:
- worktree dependencies are installed in project-local `.venv`.
- all subsequent install/build/test commands must explicitly use project-local `TEMP/TMP`; an early pip build used a parent-workshop temporary cache which pip removed automatically (`OUTSIDE_TEMP_CLEAN` confirmed). Do not repeat this.

## Next Task

**T04 — 3D Viewport + Synthetic Frame + Selection**

Risk: STANDARD.

T04 must:
- create deterministic `SceneData` from `ProjectModel`,
- embed a PyVista/VTK Qt viewport,
- render a synthetic frame only in development/demo mode,
- provide Y-Up axes,
- support member selection/highlighting interfaces,
- replace the temporary painted viewport host from T02.

After T04 verification + commit: STOP. Do not begin T05.
