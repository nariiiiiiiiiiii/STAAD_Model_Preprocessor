Status: **T18 COMPLETE on `task/18-manual-edit`; T19 is READY and has not started.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source/temp/cache/log/build/test/generated/exported/quarantine files remain inside this root.

## Completed baseline

- T01-T13: canonical model, validation/repair, local-X normalization, numbering, deterministic `.STD` geometry export.
- T14: future-optional native direct-SKP bridge contract; C SDK is not a V1 dependency.
- T15: lightweight SketchUp Ruby Bridge + Direct DXF -> shared T06/T07 canonical import.
- T16: safe SketchUp-style navigation + selection/filter/label foundation.
- T17: deterministic snap/inference + axis lock + explicit work-plane foundation.
- T24 remains post-acceptance move-only quarantine to project-local `DEL/`; never auto-delete.

Canonical continuation docs:
- `docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`
- `docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md`
- `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md`
- `docs/superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`

## T17 — Snap / Inference + Axis Lock Engine

Branch/worktree:
- branch: `task/17-snap-inference`
- worktree: `.worktrees/task-17-snap-inference`
- base: `43636af` (T16 merged to master before T17)
- task commit subject: `feat: add deterministic structural snap inference`

Risk: **STRICT HR-1 / HR-2**, already covered by the approved high-risk envelope.

### Implemented inference contract

Created:
- `src/staadprep/editing/__init__.py`
- `src/staadprep/editing/inference.py`
- `tests/unit/test_inference.py`
- `tests/unit/test_axis_lock.py`
- `tests/unit/test_inference_advanced.py`
- `tests/unit/test_inference_independent_check.py`
- `tests/unit/test_scene_inference_data.py`
- `tests/ui/test_inference_viewport.py`

Modified:
- `src/staadprep/viewer/scene.py`
- `src/staadprep/viewer/widget.py`
- `scripts/smoke_viewport.py`
- `tests/ui/test_structural_viewport.py`

Core types:
- `SnapKind`: `NODE`, `ENDPOINT`, `MIDPOINT`, `INTERSECTION`, `AXIS_X`, `AXIS_Y`, `AXIS_Z`, `WORK_PLANE`.
- `AxisLock`: `NONE`, `X`, `Y`, `Z`.
- frozen `InferenceHit(position, kind, entity_keys, label)`.
- `InferenceEngine.resolve(...)` is canonical-space deterministic and does not mutate the model.

### Deterministic geometry behavior

- Member endpoints snap exactly to canonical endpoint coordinates.
- Standalone Nodes snap exactly when within the caller-supplied `tolerance_m`.
- Member midpoints are exact arithmetic midpoints.
- True finite 3D segment intersections resolve exactly.
- Parallel or skew/non-intersecting segments do not fabricate an intersection.
- Candidate priority for equal geometric distance is `ENDPOINT -> NODE -> INTERSECTION -> MIDPOINT`; stable UUID integer order resolves remaining ties.
- The caller must supply `tolerance_m`; the viewport does not invent an engineering tolerance.
- X lock changes only canonical X and preserves reference Y/Z.
- Y lock changes only canonical vertical Y and preserves reference X/Z.
- Z lock changes only canonical Z and preserves reference X/Y.
- Axis labels are exactly `X AXIS`, `Y AXIS`, `Z AXIS`; Y helper text is `Y AXIS — Vertical`.
- Work-plane inference requires an explicit forward ray/plane intersection. Parallel rays, zero vectors, or intersections behind the ray origin return `None`; unresolved 3D depth is never guessed.

### Viewport integration

- `StructuralViewport.set_axis_lock(...)`.
- `StructuralViewport.resolve_inference(...)`.
- `StructuralViewport.resolve_work_plane_inference(...)`.
- Keyboard `X`, `Y`, `Z` sets the corresponding axis lock.
- `Esc` clears the axis lock.
- Existing `Shift+Z` Fit Model behavior remains authoritative and does not accidentally set Z lock.
- Inference, axis locking, keyboard constraints and work-plane resolution are non-mutating preview/foundation behavior only; T17 does not create/move/delete structural geometry.

`SceneData.member_endpoint_points` exposes deterministic per-member endpoint arrays for future T18 viewer inference without duplicating canonical coordinates.

### Independent verification

Hand-calculated 3D diagonal case:
- member A: `(0,0,0) -> (6,6,6)`;
- member B: `(0,6,6) -> (6,0,0)`;
- solving both parametric lines gives `t=u=0.5`;
- exact expected intersection = `(3,3,3)`;
- T17 inference returned exactly `(3,3,3)` as `INTERSECTION`;
- canonical `ProjectModel.revision` remained unchanged.

Real Windows Qt/VTK smoke output:

`VIEWPORT_SMOKE_PASS nodes=16 members=20 focus=pass isolate=pass navigation=pass selection=pass labels=pass inference=pass axis_lock=pass work_plane=pass revision=stable`

### Verification evidence

Fresh pre-commit verification:
- unit: **188 passed**;
- UI: **32 passed** (29 non-smoke + 3 subprocess smoke);
- integration: **5 passed**;
- total: **225 tests passed**;
- real Windows Qt/VTK inference/axis/work-plane smoke: passed;
- Ruff on all T17 changed/new source/tests: passed;
- targeted mypy (`editing/inference.py`, `viewer/scene.py`): passed;
- `git diff --check`: passed.

Qt/VTK UI inference tests emit 20 third-party `vtkmodules.util.numpy_support` NumPy 2.5 deprecation warnings; they are external warnings and do not indicate T17 behavior failure.

Pre-T18 maintenance removed the inherited `viewer/widget.py` typing debt without changing runtime behavior. `QtInteractor`/PyVista is now explicitly isolated as a third-party dynamic typing boundary, actor fields are typed, redundant casts were removed, and `eventFilter` follows the Qt `QObject` contract. Strict mypy now reports **0 errors** for `viewer/widget.py` and **0 errors across all 7 `staadprep.viewer` modules plus `editing/inference.py`**. Runtime verification remains 225 tests passed with the same real Qt/VTK smoke output.

## Pre-T18 maintenance — viewport typing baseline

Branch/worktree:
- branch: `maintenance/widget-typing-cleanup`
- base: `be9c651` (T17 merged to master before maintenance)
- scope: typing/annotation cleanup only in `src/staadprep/viewer/widget.py`; no geometry, camera, picking, inference, repair, or model-mutation behavior changed.
- baseline RED: strict mypy reported 19 errors in `viewer/widget.py`.
- final GREEN: strict mypy reports 0 errors in `viewer/widget.py`, and 0 errors across `src/staadprep/viewer` + `editing/inference.py`.
- regression: 188 unit + 32 UI + 5 integration = 225 tests passed; real Qt/VTK smoke remains `inference=pass axis_lock=pass work_plane=pass revision=stable`.
- VTK/NumPy deprecation warnings remain third-party warnings and are intentionally not suppressed or patched here.

## T18 — Manual Node / Member Editing + Atomic Repair UI

Branch/worktree:
- branch: `task/18-manual-edit`;
- base: `ca6dabf` (T17 + pre-T18 typing cleanup merged before T18);
- task commit subject: `feat: edit analytical nodes and members in viewport`.

Risk: **STRICT HR-2**, already covered by the approved high-risk envelope.

Implemented and verified:
- reversible `CreateNode` / `MoveNode` with exact revision restoration and finite-coordinate guards;
- `CompositeRepair` all-or-nothing rollback, one history item, one Undo, child audit detail;
- duplicate-incidence guard in `ConnectNodes`;
- viewport Draw Member, Move/Snap, exact Delete with confirmation, and Split at midpoint/percentage/distance/intersection;
- ghost line/node + connected-member preview only; canonical model stays unchanged until commit;
- `Esc` cancel and MMB navigation during active previews;
- all canonical mutation flows through reversible commands + `RepairHistory`, not direct UI/viewer dictionary mutation;
- independent Draw -> Move -> Delete -> Undo graph round-trip restored the exact canonical graph;
- real Windows Qt/VTK manual-edit smoke passed on `10_combined_dirty_frame`.

Fresh verified regression before docs close:
- unit: **210 passed**;
- UI: **50 passed**;
- integration: **5 passed**;
- total: **265 tests passed**;
- Ruff: passed;
- targeted strict mypy for T18 source: **0 errors**;
- `git diff --check`: passed.

VTK/NumPy deprecation warnings remain third-party only.

## Next Task

**T19 — Precision Create Node + Translational Repeat**

T19 is READY. Do not start it until the user explicitly continues after the T18 checkpoint.

## T24 cleanup boundary

T24 runs only after T23 acceptance. It moves only verified-unused/superseded files into project-local `DEL/`, writes `DEL/UNUSED_FILES_MANIFEST.md`, and never deletes files. Final deletion remains user-controlled.
