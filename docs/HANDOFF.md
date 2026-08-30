Status: **T21 COMPLETE and merged to `master`; T22 Portable Standalone Windows Packaging is COMPLETE on `task/22-portable-packaging`; T23 is not started.**

Post-package user testing on 2026-08-30 identified nine usability corrections. Requirements and execution are captured in:

- `docs/superpowers/specs/2026-08-30-post-t22-usability-design.md`;
- `docs/superpowers/plans/2026-08-30-sketchup-bridge-usability.md` (requirements 1-2, execute first);
- `docs/superpowers/plans/2026-08-30-desktop-interaction-usability.md` (requirements 3-9, execute after RBZ acceptance).

Inline execution of the first checkpoint is accepted in real SketchUp. The RBZ bridge window opened and was usable; source/package contract tests passed 3/3, Ruff and `git diff --check` passed, and the accepted artifact is `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz`. Record the checkpoint commits below, then stop. Do not change or rebuild the desktop executable until the user explicitly starts the desktop checkpoint.

Post-T22 usability commit:
- `e7ce6ad` — `feat: add SketchUp bridge interface`

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source/temp/cache/log/build/test/generated/exported/quarantine files remain inside this root.

## Completed baseline

- T01-T13: canonical model, validation/repair, local-X normalization, numbering, deterministic `.STD` geometry export.
- T14: future-optional native direct-SKP bridge contract; C SDK is not a V1 dependency.
- T15: lightweight SketchUp Ruby Bridge + Direct DXF -> shared T06/T07 canonical import.
- T16: safe SketchUp-style navigation + selection/filter/label foundation.
- T17: deterministic snap/inference + axis lock + explicit work-plane foundation.
- T18: reversible manual analytical Node/Member editing with exact Undo.
- T19: exact/relative Node creation + Translational Repeat.
- T20: numbering/member-direction controls with stable UUID identity.
- T21: authoritative READY gate, golden end-to-end suite, independent STD round-trip, validation/audit report, and MCP-safe isolated UI runner.
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

VTK/NumPy deprecation warnings remain third-party only. One grouped offscreen Qt/VTK verification invocation hit a native VTK access violation during renderer/grid setup; rerunning every affected viewport test in isolated Windows-renderer processes (`QT_QPA_PLATFORM=windows`) passed, so the final UI result remains 79/79 PASS without a behavioral assertion failure.

## T19 — Precision Create Node + Translational Repeat

Branch/worktree:
- branch: `task/19-precision-create-repeat`
- worktree: `.worktrees/task-19-precision-create-repeat`
- base: `60da4dc` (T18 merged to master before T19)
- task commit subject: `feat: create precise repeated structural nodes`

Risk: **STRICT HR-2**, already covered by the approved high-risk envelope.

Implemented and verified:
- Create Node by click/snap, exact STAAD XYZ, and relative-to-reference XYZ; canonical Y remains vertical;
- unresolved free-space click remains fail-closed; no arbitrary depth guess;
- exact/relative collision analysis occurs before mutation and never creates a co-located duplicate Node;
- optional Reference -> New/Existing Member creation is atomic and one Undo;
- `TranslationalRepeatSpec` supports deterministic ΔX/ΔY/ΔZ, repeat count excluding reference, `NONE`, `CONSECUTIVE`, and `FROM_REFERENCE` connection modes;
- collision resolutions are explicit `USE_EXISTING`, `SKIP_STEP`, or `CANCEL`; later step positions remain deterministic;
- repeat preview reports actual new/reused/skipped Node counts, actual new Member count, and final coordinate;
- repeat ghost preview suppresses existing incidence rather than displaying a member that will not be committed;
- entire repeat is built before apply and executes as one `CompositeRepair` / one history item / one Undo;
- independent frame-line test locked exact UUID-coordinate/incidence sets and exact graph/revision restoration after Undo;
- a CREATE_NODE mouse-routing regression was found and fixed: Create Node no longer falls through to Delete behavior;
- real Windows Qt/VTK precision smoke passed Exact, Relative+Member, Repeat, preview, Undo, navigation, and exact graph restoration.

Fresh verification before docs close:
- unit: **231 passed**;
- UI: **79 passed**;
- integration: **5 passed**;
- total: **315 tests passed**;
- real smoke: `PRECISION_CREATE_SMOKE_PASS exact=pass relative=pass repeat=pass preview=pass undo=pass navigation=pass graph=restored`;
- Ruff: passed;
- strict mypy on T19 source boundary: **0 errors**;
- `git diff --check`: passed.

VTK/NumPy deprecation warnings remain third-party only.

## Completed Task

**T20 — Numbering + Member Direction Controls**

Risk: **STRICT HR-2 / HR-4**, covered by the approved high-risk envelope.

Branch/worktree:
- branch: `task/20-model-controls`
- worktree: `.worktrees/task-20-model-controls`
- base: `16acb70` (`feat: create precise repeated structural nodes`)
- feature commit: `93f99b4` — `feat: control STAAD numbering and member direction`

Implemented:
- deterministic Old -> New preview plus reversible `RenumberNodesCommand`, `RenumberMembersCommand`, and atomic `RenumberAllCommand` using T12 ordering;
- `SetMemberStart`, Flip Selected, Auto Fix Selected, and Auto Fix All using T11/`ReverseMember` direction rules;
- numbering/model-direction UI actions and preview dialog;
- endpoint-driven Set Direction viewport flow with Local-X preview;
- independent invariant, unit, UI, and real Qt/VTK coverage.

Final verification:
- T20 targeted unit/UI: **21 passed**;
- T11/T12 + manual-edit targeted unit regression: **54 passed**;
- full regression: **243 unit + 88 UI + 5 integration = 336 passed**;
- VTK-heavy UI tests verified in isolated Windows-renderer processes where required;
- Ruff on affected source/tests: **passed**;
- T20-local strict mypy: **0 issues in 5 affected source files** using `--follow-imports=silent`;
- four inherited `importers/dxf_reader.py` typing errors remain outside T20 under full import-graph reporting;
- `git diff --check`: **passed**.

Verified invariants:
- numbering changes STAAD-facing numbers only; UUID identities and member endpoint UUID references remain stable;
- direction controls change incidence only; geometry coordinates remain unchanged;
- batch controls are atomic history operations with exact Undo restoration;
- UI routes mutations through commands/history and does not directly assign `.number`, `.start`, or `.end`.

Existing VTK/NumPy 2.5 deprecation warnings remain third-party warnings and are not behavioral failures.

Post-commit workspace note:
- tracked T20 tree is clean;
- `.serena/` remains as known untracked Serena tool metadata created by project activation and was intentionally excluded from T20 commits; it was not modified or deleted.

## Completed Task — T21

**T21 — End-to-End READY Gate + Golden Suite + Audit Report**

Risk: **STRICT HR-1 through HR-4**, covered by the approved high-risk envelope.

Branch/worktree:
- branch: `task/21-ready-gate`
- worktree: `.worktrees/task-21-ready-gate`
- base: `810e5dc` (`chore: ignore Serena metadata`; T20 integrated to `master` before T21)
- feature commit: `bddd177` — `test: verify end-to-end clean model readiness`

Implemented:
- authoritative `ReadyGate` / `ReadyPolicy` / `ReadyStatus` for validation errors, policy-critical disconnected structures, source-unit verification, optional reference-dimension verification, and complete positive unique numbering;
- golden 01-11 end-to-end coverage with validator-boundary handling for canonical dirty fixtures and reference-scale verification for wrong-scale evidence;
- combined dirty-frame repair/manual-edit workflow through `RepairHistory`, including duplicate Member delete, Move/Snap, crossing split, Draw Member, Relative Create, and Translational Repeat;
- independent final coordinate/incidence graph comparison plus T20 direction/numbering invariants;
- independent test-only STAAD `.STD` parser round-trip;
- project-local validation/audit JSON containing import/transform metadata, issues, command history, numbering, direction status, readiness, and export status;
- UI `READY FOR STAAD` and export availability controlled only by `ReadyGate`, including direct export re-evaluation;
- permanent MCP-safe UI runner (`scripts/test_ui_isolated.py` + `.ps1`) with automatic lightweight/native-renderer classification, isolated renderer subprocesses, sharding, checkpointed `run-id`, and aggregate `--summary-only` reporting;
- circular-import regression discovered by real orientation smoke was fixed at the audit/orientation dependency boundary with lazy import.

Final verification on the final code tree:
- unit + integration: **275/275 passed**;
- UI: **62 lightweight + 30 VTK/renderer = 92/92 passed** using fresh checkpoint `t21-final2`;
- total fresh regression: **367/367 passed**;
- Ruff on T21 affected source/tests/runner: **passed**;
- T21-local strict mypy: **0 issues in 4 affected source/runner files** using `--follow-imports=silent`;
- `git diff --check`: **passed**;
- VTK/NumPy 2.5 deprecation warnings remain third-party warnings only.

Operational note:
- running multiple renderer-heavy files inside one MCP request can return transport HTTP 502 even when individual tests are healthy; the permanent runner therefore supports one renderer file per MCP-safe shard while local execution may run `--scope all`.
- T21 implementation is committed; this HANDOFF/docs-close update is the final checkpoint documentation step.

## Current Task — T22 Portable Standalone Windows Packaging

Status: **COMPLETE** on branch `task/22-portable-packaging` in worktree `.worktrees/task-22-portable-packaging`.

User-approved packaging contract:
- portable/no-install Windows x64 release;
- extract into any writable folder and launch `STAAD Model Preprocessor.exe` directly;
- no Python/pip/PySide6/VTK installation required on the target machine;
- all implicit writable state stays below package-local `Data/`;
- version-matched SketchUp `.rbz` ships inside the same portable package;
- manual patch/update contract + machine-readable SHA-256 manifest are included now;
- Setup/MSI/NSIS, automatic updater, registry install, and production one-file mode remain deferred.

Detailed implementation plan:
- `docs/superpowers/plans/2026-08-29-t22-portable-standalone-packaging.md`
- synchronized project index: `docs/INDEX.md`

Completed T22 checkpoints and commits:
- `7d0ee2b` — `feat: add portable runtime path boundary`
- `ec04b46` — `build: establish portable release version contract`
- `6afaea9` — `build: package SketchUp bridge extension`
- `22510bc` — `build: assemble update-ready portable release`
- `056d906` — `fix: support portable SketchUp inbox`
- `dcc2d6e` — `build: package Windows desktop application`

Final implementation and verification:
- `PortablePaths` resolves compiled runtime from the executable/compiled containing directory, never launch CWD;
- package-local writable hierarchy: `Data/Config`, `Projects`, `Inbox/SketchUp`, `Exports`, `Reports`, `Logs`, `Cache`, `Temp`, `Backups`;
- development `ProjectPaths` remains backward-compatible and packaged runtime does not auto-create development `build/dist/vendor` directories under `Data/`;
- app/RBZ/package version contract is currently `0.1.0` and does not prematurely claim production V1 acceptance;
- deterministic `.rbz` builder produces `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz`;
- SketchUp exporter accepts both legacy development `artifacts/sketchup_bridge/inbox` and portable `Data/Inbox/SketchUp` paths;
- portable assembler, ZIP layout, `Update/package-manifest.json`, per-file SHA-256, preserved `Data/`, and manual update documentation are implemented;
- source-level packaged workflow smoke exercises Neutral import -> existing `ConnectNodes` repair -> renumber -> ReadyGate -> `.STD` -> `.validation.json` using production paths;
- final source regression: **307/307 PASS** for unit+integration;
- T22-local strict mypy: **0 issues in 4 affected source files**;
- relevant Ruff checks: passed;
- affected UI regression: **3/3 PASS**;
- final-package integration gates: **6/6 PASS**;
- Nuitka standalone build completed and emitted `build/windows/final/app.dist/STAAD Model Preprocessor.exe`.

Final build and release evidence:
- Nuitka 4.2, Python 3.14.3 x64, and MSVC `cl 14.5` completed the real standalone build;
- `build/windows/final/nuitka-report.xml` records `mode="standalone"` and `completion="yes"`;
- emitted executable: `build/windows/final/app.dist/STAAD Model Preprocessor.exe`;
- executable size: **159,788,032 bytes**;
- executable SHA-256: `2401E9C0689CE6ACFDA0E7E7BBE6859F6848780CD79792322CCCADAC2ADB1A57`;
- `scripts/build_windows.ps1` now establishes the project-local Nuitka cache before preflight and uses non-interactive download acceptance;
- Dependency Walker is cached under project-local `.cache/nuitka/downloads/depends/x86_64/`;
- final folder: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/` (**812 files**, **708,028,512 bytes**);
- final ZIP: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` (**225,136,191 bytes**, SHA-256 `D31A70005D7F0B2C09B467D6A5591892868E9E56AC35874434BA38CFC4687115`);
- manifest independently verified **811/811 managed files** with no size/hash errors;
- final `.exe` and freshly extracted ZIP both launched with Python absent from `PATH`, exit code 0;
- different CWD, spaces/Unicode relocation, reopen with existing `Data/`, and packaged T21 READY/STD/report workflow passed;
- package README recommends a reasonably short extraction path because deeply nested paths can exceed the legacy Windows DLL path limit used by bundled VTK modules;
- no Setup/MSI/NSIS/automatic-updater/one-file production artifacts were produced.

Next action: review/use the final folder or ZIP. Start T23 real-project and target STAAD.Pro acceptance only after an explicit user instruction.

### USER ACTION REQUIRED

**None currently.** Do not install/download Python, Nuitka, Visual Studio/MSVC, PySide6, VTK, or other packaging tools unless a later build error proves a specific missing component. If a future step genuinely requires a manual download/install that is easier or safer for the user to perform, record the exact item/version/link/reason here before proceeding.

T23 remains **not started**. Its T22 prerequisite is satisfied, but its STRICT acceptance work must not start automatically.

## T24 cleanup boundary

T24 runs only after T23 acceptance. It moves only verified-unused/superseded files into project-local `DEL/`, writes `DEL/UNUSED_FILES_MANIFEST.md`, and never deletes files. Final deletion remains user-controlled.
