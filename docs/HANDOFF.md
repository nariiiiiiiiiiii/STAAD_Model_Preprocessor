Status as of **2026-09-13**: T21 is complete; T22 packaging is complete; T23 is PASS by owner report
(2026-09-01). Source version **0.2.0**, matching Windows standalone, SketchUp RBZ, portable folder,
and ZIP have been built. Package gates are **9/9 PASS** and the post-cleanup no-Python/different-CWD
launch smoke is **1/1 PASS**. The owner tested this exact 0.2.0 standalone on 2026-09-13 and
reports that it works well. It remains a **pre-release**; no stable-release approval has been given.
T28/T29 old outputs, three unused logo drafts, and focused-test temp output are recoverably stored
in `DEL/`; no files were deleted. The project-wide audit is in the ignored local report
`artifacts/cleanup/project-wide-storage-audit-20260913.md`. The private repo's unrelated initial
`main` was left untouched. Branch `task/22-portable-packaging` was pushed at commit `47c0b0a`; the
`v0.2.0` pre-release tag points to that commit and has only the portable ZIP as an application asset:
[download](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/download/v0.2.0/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip).
Owner manual test of this exact EXE: **PASS by owner report (2026-09-13)**. Stable-release approval
remains a separate decision.

Local license migration checkpoint (2026-09-13): `LICENSE` now contains the official PolyForm
Noncommercial 1.0.0 text with the separate Required Notice; `README.md` and `pyproject.toml` match.
The change is limited to licensing/documentation and remains uncommitted and unpushed pending owner
review. PolyForm's official funded-organization exception is called out in README for owner review.
The already-published pre-release asset and remote `main` were not changed.

## Current 0.2.0 candidate — build and verification

- Nuitka mode: `standalone`; report says `completion=yes`; Windows file/product version `0.2.0.0`.
- Executable: `build/windows/final/app.dist/STAAD Model Preprocessor.exe`, 160,498,688 bytes,
  SHA-256 `A616C8286DD63C718D821132B37C4C24F82AA2FB75E15BB46A4FC60E004174A2`.
- SketchUp RBZ: `build/sketchup/STAAD_Prep_Bridge_0.2.0.rbz`, 4,211 bytes,
  SHA-256 `655238B3EA983C2A3C76A66BA8C9D44FE030F68BE49A9D8B950CC5CD70234D06`.
- Portable folder: `dist/STAAD_Model_Preprocessor_0.2.0_win64_portable/`, 813 files,
  709,571,303 bytes; manifest has 812 managed-file entries.
- ZIP: `dist/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip`, 226,243,587 bytes,
  SHA-256 `635AF835CE71C211E6FE184EBE05656187E0C4C36D2FA8BC542679802C7B15A7`.
- GitHub pre-release asset: [download the ZIP](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/download/v0.2.0/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip).
- Package tests (manifest, RBZ, packaged paths, workflow smoke): **9/9 PASS**. After quarantine,
  `test_final_package_launches_without_python_from_different_cwd`: **1/1 PASS**.
- Pre-package source evidence: **345 unit+integration passed**, **1 skipped** (RBZ archive test at
  that source-only checkpoint), **3 package tests deselected** before build; affected UI **26/26**,
  the later Save/import/export/path regression **58/58**, Ruff PASS, and strict mypy reported **0**
  issues on affected files. `git diff --check` passed before the packaging/doc checkpoint.
- Owner-reported source-app acceptance: Save and the requested viewport behavior work; T23 earlier
  acceptance is PASS by report. The owner tested the newly built 0.2.0 executable on 2026-09-13 and
  reports it works well. The isolated offscreen VTK smoke remains unavailable after a Win32 OpenGL
  pixel-format error and Python Application Error; this did not prevent the owner's successful app test.

The package is folder-based standalone with a ZIP distribution; it is **not** a one-file executable.
Generated `build/` and `dist/` outputs are ignored and are not GitHub repository commits by default.
The T28/T29 audit has quarantined 23,050 payload files / 15,115,170,070 bytes; because this is a
same-volume move, used disk space is not reclaimed until the owner separately deletes that folder.

This block is authoritative. Older “not built”, “compile pending”, or “Save restricted to
Data/Projects” statements below are dated historical snapshots and must not be read as current.

## Historical source follow-up snapshot — 2026-09-12 (superseded where the current block above differs)

The owner approved version `0.2.0`. Checkpoint 1 is complete in the active T22 worktree: `src/staadprep/version.py` is canonical, `staadprep.__version__` imports from it, and the SketchUp loader declares the same version. The version-contract test is **6/6 PASS**; Ruff passes; strict mypy reports **0 issues** across the three affected Python files; `git diff --check` passes. No RBZ, executable, portable folder, or ZIP was rebuilt. Existing accepted package records remain version `0.1.0`.

Checkpoint 2 is now source-complete with the owner-confirmed `<safe-SKP-stem>_<DDMMYYYY>.json` rule, collision suffixes, safe basename handling, and unchanged `source_file` metadata. Static source-contract verification is **1/1 PASS** (the combined version and naming tests are **7/7 PASS**); no Ruby executable is available, so RBZ-content and real SketchUp checks remain pending. No RBZ or Windows package was rebuilt.

Checkpoint 3 is source-complete: the selected logo is copied byte-for-byte into `assets/branding`, used by the Qt app, and wired into the future Windows build; a 7-size ICO was generated and verified under `build/windows/icon-checkpoint-20260912/`. Focused icon/build/UI checks are **12/12 PASS**, Ruff and strict mypy pass. After the owner reported the old/Python-looking taskbar icon, the source now assigns a stable Windows AppUserModelID before QApplication creation and explicitly applies the app icon to the main window. The additional focused check is **10/10 PASS**, Ruff passes, and strict mypy reports **0 issues** in the two affected source files. The owner confirmed the logo now appears correctly on the source-run app taskbar (2026-09-12). This does not verify the old compiled executable; no Windows executable or RBZ was rebuilt, and the accepted package remains version `0.1.0`.

Checkpoint 4 status at the time (2026-09-12): Project JSON could be opened from any folder and Save wrote back to that selected file; First Save for a new model was then restricted to `Data/Projects/`. That historical restriction was removed in the approved 2026-09-13 Save-path follow-up below. Atomic save stages a hidden unique temp sibling beside the destination; failure tests confirm the old file remains intact and temp files are cleaned. Checkpoint-4 focused serialization/UI checks were **10/10 PASS**. No executable, RBZ, or portable package was rebuilt.

Checkpoint 5 is source-complete after explicit STRICT / Full TDD approval on 2026-09-12. Quick Fix supports multi-row selection and preflights fresh issues/typed mutation footprints; it rejects unsupported, stale, or overlapping batches. `CROSSING_WITHOUT_NODE` routes to the existing intersection splitter. Accepted batches run as one `CompositeRepair` with one confirmation/audit/history item and exact Undo/Redo.

Final evidence: focused planner/repair/UI STRICT suite **61/61 PASS**; full unit+integration **345 PASS**, **1 skipped** (archive-level RBZ check needs an explicit RBZ build), **3 deselected** (portable executable gates need a `0.2.0` build), and **26/26 affected UI PASS**; Ruff PASS; strict mypy **0 issues** for four affected source files; diff check PASS.

Incident: the first full suite invoked a legacy RBZ builder and generated a transient `0.2.0` RBZ; the file was removed. Its old test also refreshed ignored `build/sketchup/stage/` copies, which remain in place. The integration fixtures were changed to remain under `.tmp/tests`; a subsequent full suite run produced no build artifact. Existing accepted package remains `0.1.0`.

Initial owner smoke report (2026-09-12, before the taskbar source fix): **Quick Fix works; Undo and Redo work; app-window icon changed; taskbar icon still showed the old/Python-looking image.** This was partial manual acceptance, not confirmation of every CP1–CP5 scenario or of a packaged executable. The currently present executable is still `0.1.0.0`, last modified 2026-09-06, size 160,240,128 bytes, SHA-256 `41346B2BEDBA637EBDCA43E390B59E257B19397700F95FAFDB346203A7E2E850`; it predates the 0.2.0 source/icon changes. Therefore its embedded icon has **not** been updated or verified. The development launch uses `python.exe`, which may explain the original taskbar image, but that initial screenshot alone did not establish the cause.

Taskbar source follow-up (2026-09-12): `configure_windows_taskbar_identity()` assigns `Dizayn59.STAADModelPreprocessor` before the first QApplication is created; the main window explicitly receives the selected application icon before showing. This targets both Windows taskbar grouping under the Python development host and the window-system icon. Focused tests, Ruff, and strict mypy pass. The computer-use runtime exposed no Windows app window in this session, so a live taskbar screenshot could not be verified here.

Owner retest result (2026-09-12): the selected logo now appears correctly on the source-run app's taskbar. This is owner-confirmed development-app behavior; the compiled `.exe` remains the old `0.1.0.0` and was not rebuilt or tested.

At the time of this source snapshot, manual checks and compile/package authorization were still
pending. The user later authorized the post-compile sequence; the resulting candidate build and
verification are recorded at the top of this handoff.

Development launch for manual source acceptance (PowerShell, from the active worktree):

```powershell
Set-Location -LiteralPath (git rev-parse --show-toplevel)
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -m staadprep.app
```

Save-path manual acceptance: the owner reported on 2026-09-13 that Save works; individual Save As,
cancel, overwrite, and reopen cases were not itemized. Remaining unrelated manual checks include
multi-issue Apply with Undo/Redo and the intersection case. The user has reported Quick Fix and
Undo/Redo working, but did not specify which batch/intersection scenarios were tested. Real SketchUp
export testing needs the owner to install/test the current version-matched RBZ; the 0.2.0 build
exists and passed the archive/package gates.

## 2026-09-12 manual bug follow-up — Crop and Save Blocked

**Crop to Selection:** Real PyVista repro showed a single-Node selection shrinking camera distance
from `40.291960753` to `0.000006692`; selected-Member framing worked. The fixed absolute `1e-6`
padding was replaced by a scale-aware 8% selected-span margin with a 2% full-scene minimum (using
1.0 world unit only when the scene itself has zero span). Regression assertions now verify the
single-Node focal target, non-degenerate zoom, and unchanged model revision. The toolbar action's
selection enable/forward/disable contract is also tested. Combined focused tests: **15/15 PASS**;
Ruff PASS; strict mypy reports **0 issues** in `viewer/widget.py`. The owner later manually tested
Crop to Select / Zoom in Select and reported it works on 2026-09-13.

**Save Blocked diagnosis (before fix):** The owner reported that viewport behavior passed but an
external Project JSON destination still showed Save Blocked. The dialog matched the `ValueError`
raised by `_assert_project_json_path()`, which was called only when `_current_project_path is None`,
after the chooser and before `save_project_atomic()`; it was not a QFileDialog restriction. External
Open→regular Save already used `resolve_user_selected_path()`, while no Save As action existed. The
owner approved the refreshed STRICT plan on 2026-09-13; implementation and evidence are recorded
below. Exact analysis is retained in
`docs/superpowers/specs/2026-09-12-user-selected-save-destinations.md` and
`docs/superpowers/plans/2026-09-12-user-selected-save-destinations.md`.

## 2026-09-12 marquee selection and Save destination follow-up

**Marquee / Zoom in Select:** The former camera-framing button and context-menu action are now named
**Zoom in Select**; the new checkable **Crop to Select** action reuses the Nodes/Members filters and
enables a left-drag rectangle. The rectangle projects Nodes and Member segments into viewport
coordinates, Ctrl-drag adds, a normal drag replaces, and the operation only updates selection and
highlights. The non-renderer event/action/geometry subset is **13/13 PASS**, Ruff PASS, and strict mypy
reports **0 issues** in `main_window.py` and `widget.py`.

The real VTK smoke was not verified in the agent test process: an offscreen attempt reported
`vtkWin32OpenGLRenderWindow: failed to get valid pixel format`, followed by a Python Application
Error. A prior combined same-process UI test also triggered a native VTK access violation; both
attempts used only synthetic in-memory model data and did not open or write user Project JSON. The
owner manually tested the viewport flow and reports it works well on 2026-09-13, so manual viewport
acceptance is complete; only automated offscreen VTK evidence remains unavailable. The later 0.2.0
build result is recorded at the top of this handoff.

**Save destination audit:** Source inventory found three unrestricted open-file dialogs (Project
JSON, SketchUp Neutral JSON, DXF); Export STD already lets the user choose any path and writes its
validation report beside the `.STD`. The remaining explicit save restriction is Project JSON First
Save outside `ProjectPaths.projects`; that guard has now been removed only from the explicitly
user-selected Project JSON flow. Runtime containment remains unchanged. Save As and external-path/
failure tests pass as recorded below.

## 2026-09-13 Save-path STRICT implementation

- First Save and Save As pass the user-selected path through `ProjectPaths.resolve_user_selected_path()`
  and retain the atomic `save_project_atomic()` write.
- Added **Save As…** immediately after **Save Project JSON** in the main toolbar. It starts in the
  current associated file's directory, or the Projects default for a new model.
- The saved path/revision/title state updates only after the atomic write succeeds. Cancel or a save
  error leaves the existing association and dirty state unchanged. `ProjectPaths.assert_inside_project()`
  and all project-local runtime destinations remain intact.
- External Open Project JSON, SketchUp JSON, DXF, and Export STD dialog paths were verified; the STD
  validation report remains beside the selected `.STD`.
- Verification at the source-fix checkpoint: **58/58 relevant UI/unit tests PASS**, Ruff PASS,
  strict mypy **0 issues** in `main_window.py`, `git diff --check` PASS. Compilation followed later.
- Owner manual report (2026-09-13): Save now works in the app. Individual Save As/cancel/overwrite
  cases were not specified. The exact compiled 0.2.0 package still awaits the owner's own manual
  launch/acceptance; build and automated package-gate results are at the top of this handoff.

## Post-compile cleanup and GitHub readiness request (2026-09-13)

After a separately authorized compile, the owner requests: verify the new standalone; re-audit unused
project data and move confirmed old standalone folders/ZIPs to `DEL/` without deletion; update all
tracked Markdown and make the root README suitable for the owner's GitHub repository. Then run a
local repository preflight and hand off without pushing. The owner authorized beginning the sequence
and the compile/package step has completed. Deletion and branch merging remain outside that task.
The license-selection decision was later resolved by the T30 request, but its commit/push still
awaits owner approval. See
`docs/superpowers/specs/2026-09-13-post-compile-cleanup-github-readiness.md` and
`docs/superpowers/plans/2026-09-13-post-compile-cleanup-github-readiness.md`. Moving items to `DEL/`
does not free disk space; final deletion remains owner-controlled.

## Historical post-T22 editing correction checkpoint — 2026-08-31

After real package testing, the user supplied ten desktop editing corrections covering STAAD-axis
Reset View, Node/Member selection and Properties, Delete/keyboard Delete, Crop to Selection,
Merge Members, orphan removal, selected-Member Translational Repeat, duplicate Create Node labels,
and unusable Draw/Move/Delete modes. The user explicitly approved STRICT / Full TDD for the
topology-changing scope on 2026-08-30.

Source implementation and the isolated final package are complete. Current evidence:

- **299/299 unit PASS** and **26/26 integration PASS**;
- **77/77 lightweight UI PASS** and **34/34 isolated VTK UI PASS**;
- Ruff passed for `src`, `tests`, and `scripts`;
- strict mypy passed for all 7 affected source files;
- automated Qt offscreen mode skips VTK grid/axes creation to prevent native test-only access
  violations; the real Windows application still renders the engineering grid and axes;
- real Windows viewport/manual-edit/precision-create smokes pass, including selection, Crop,
  canonical Reset View, Draw, Move/Snap, Delete, Undo, and stable model revision;
- Nuitka report records `mode="standalone" completion="yes"`;
- final editing-correction package gates pass **4/4**, manifest verification is **811/811**, and a
  freshly extracted ZIP launches with Python absent from `PATH`;
- final folder: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/`
  (**812 files**, **708,288,929 bytes**);
- final ZIP: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip`
  (**225,217,293 bytes**, SHA-256
  `5B261CCEC2DD75D88F6DB3456548F15D714190365F5348ADD77481D3CA48E52B`);
- packaged executable is **160,055,296 bytes**, SHA-256
  `8AE21D68F21FFDDCC7A6DEE91D41E7303ECEC090D511760D9973A082928D1D9E`;
- detailed design/plan: `docs/superpowers/specs/2026-08-30-post-t22-editing-corrections-design.md`
  and `docs/superpowers/plans/2026-08-30-post-t22-editing-corrections.md`.

This checkpoint is superseded by the later consolidated refresh-save-final package, which was
accepted by the user. Its source and historical package evidence remain preserved for traceability.

Active incremental follow-up from user testing on 2026-08-31:

- Apply-before-OK dialogs for Delete/Merge/Quick Fix/Auto Fix with automatic final refresh;
- Node/Member engineering Properties without visible UUID/source identity;
- canonical Project JSON Save/Open with atomic project-local writes;
- application exit confirmation.

Design: `docs/superpowers/specs/2026-08-31-post-t22-refresh-properties-save-design.md`.
Plan: `docs/superpowers/plans/2026-08-31-post-t22-refresh-properties-save.md`.
The user explicitly approved STRICT / Full TDD and started item 1 on 2026-08-31. Apply-before-OK
orchestration for Delete, Merge, supported Quick Fix, Auto Fix All, and Auto Fix Selected is now
implemented and source-verified. Apply executes one history command, refreshes immediately, disables
Apply/Cancel, and enables OK; OK performs a final idempotent refresh without re-executing. Cancel
before Apply and rejected commands preserve the exact graph/revision/audit/history. Auto Fix All is
one atomic composite history entry and one Undo restores the complete prior incidence state.

Fresh item-1 evidence: dialog/edge suite **10/10 PASS**; focused UI suite **34/34 PASS**; affected
lightweight/unit regression **61/61 PASS**; new real-VTK refresh **1/1 PASS**; isolated existing
manual-mouse VTK **4/4 PASS**; issue-repair and orientation real smokes **1/1 PASS each**; Ruff and
strict mypy on the two affected source files pass. One deliberately combined VTK process reproduced
the known native access violation after 38 tests; all native files passed when rerun in the required
per-process isolation.

Current stop: **ALL AGREED SOURCE FEATURES USER ACCEPTED / FULL SOURCE VERIFIED**, including
Apply/OK refresh, multi-Orphan repeatability, engineering Properties, Project Explorer selection,
Member Repeat, Member Local Axes, Save/Open Project JSON, and the corrected `X -> Yes` exit path.
Task 7 source verification is complete: **332/332 source unit+integration**, **102/102 lightweight
UI**, **38/38 isolated VTK UI**, six real Windows source smokes, focused Save/Open **5/5**, Ruff,
strict mypy, and diff checks pass. The user authorized compile step 1 and Nuitka produced a fresh
standalone build with `mode="standalone" completion="yes"`. Portable assembly and ZIP creation
are complete under `dist/post-t22-refresh-save-final/`; the fresh package-only verification suite
is **7/7 PASS**.

Current assembled artifacts (step 2):

- folder: `dist/post-t22-refresh-save-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/`
  (**812 files**, **708,473,249 bytes**);
- ZIP: `dist/post-t22-refresh-save-final/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip`
  (**225,277,697 bytes**, SHA-256
  `0EF7933499179284B7FC01B011876BF196F7471D4F8CA5B7B12F46E36059E314`);
- executable: `STAAD Model Preprocessor.exe` (**160,239,616 bytes**, SHA-256
  `1C7BB68D12BEFA8A1DBDC5A8A18B031A1E19AEFCFB91C7567441E79DB88F4470`);
- package manifest: `Update/package-manifest.json`; bundled bridge:
  `SketchUp_Extension/STAAD_Prep_Bridge_0.1.0.rbz`.

Package-only verification against this new package is **7/7 PASS**, including executable launch,
relocation/CWD, no-Python, manifest/hash, packaged workflow, and freshly extracted-ZIP coverage.
The user completed real package testing and reported **PASS** on 2026-08-31.

Item 2 now renders only the requested engineering fields. A single Node shows Node No. and separate
X/Y/Z coordinates in metres. A single Member shows Member No., Start/End Node No. with separate
endpoint X/Y/Z coordinates, Length, and Group / Layer. UUIDs and source references remain internal
and are no longer rendered for selected entities; mixed selection still shows counts only. The
exact-text RED/GREEN contract passes, affected regression is **15/15 PASS**, Ruff passes, and strict
mypy reports **0 issues** for `panels.py`. The user accepted this source checkpoint.

Real development feedback: the user accepted the Apply→OK interaction, then found a repeatability
bug with two or more Orphan Node issues. After the first Quick Fix, the remaining row stayed
visually selected while MainWindow correctly cleared its selected issue, so selecting that same row
did not emit a new signal and Apply stayed disabled. `IssueConsole.set_issues()` now atomically
clears both row selection and current cell before rebuilding. A STRICT regression proves two Orphan
Nodes can be deleted through two separate Apply→OK cycles and restored through two exact Undo
operations. Focused follow-up regression **17/17 PASS**; Ruff and strict mypy for the three affected
source files pass. The user accepted the repeated multi-Orphan sequence on 2026-08-31.

Member Translational Repeat follow-up from real user testing on 2026-08-31:

- Symptom: selecting Member(s) and invoking Translational Repeat showed no 3D ghost preview and was
  reported unusable.
- Root cause: `MemberTranslationalRepeatDialog` calculated numeric preview data but had no
  `preview_requested` signal/viewport forwarding path, unlike Node Translational Repeat.
- Fix: added a member-preview request contract, dialog signal, MainWindow forwarding/preview cleanup,
  and read-only translated Member ghost rendering in `StructuralViewport`.
- STRICT evidence: behavioral RED reproduced missing signal/forwarder; focused core **20/20 PASS**;
  isolated real VTK `test_precision_viewport.py` **7/7 PASS**; member apply remains one atomic history
  operation with exact Undo; Ruff PASS; strict mypy 0 issues in 3 affected source files; `git diff --check`
  PASS. One grouped renderer command hit the known MCP 502 transport issue and was replaced by the
  project-isolated renderer shard, which passed.
- Status: **SOURCE FIX VERIFIED / USER ACCEPTED — 2026-08-31**. No standalone rebuild is authorized yet.
- Follow-up Local Axes request is now implemented at source level and verified; details follow.

Selected-Member Local Axes follow-up from real user testing on 2026-08-31:

- Purpose: show each selected Member's own local coordinate triad so Start→End direction is visually obvious.
- UI: the previous `Local-X` action is now labeled `Local Axes`.
- Rendering: selected Members show midpoint XYZ triads with `X` red, `Y` green, `Z` blue and matching `X/Y/Z` labels at arrow heads.
- Engineering basis: canonical Y-up, STAAD beta=0 convention. Local X follows Start→End; non-vertical Local Y is the +global-Y projection normal to X and Local Z completes the right-handed basis; vertical members keep Local Z parallel to +global Z. Zero-length members render no triad.
- Safety: visualization only; no geometry/topology/numbering/revision mutation and no `.STD` semantic change.
- STRICT basis evidence: 5/5 unit PASS for Beam-X, vertical member, brace orthonormal/right-handed basis, member reversal, and zero-length behavior.
- UI/renderer evidence: focused affected suite 15/15 PASS; isolated real-VTK `test_precision_viewport.py` 8/8 PASS; Ruff PASS; strict mypy 0 issues across 3 affected source files; `git diff --check` PASS.
- Toolbar visibility follow-up: user could not find `Local Axes` because the second-row Edit/View toolbar overflowed horizontally. The toolbar is now split into row 2 `Edit & Selection` and row 3 `View`, with row 3 containing `Nodes`, `Members`, `Node No.`, `Member No.`, `Local Axes`, `Coordinates`, `Fit Model`, `Reset View`, and `Crop to Selection`.
- Toolbar TDD evidence: behavioral RED proved `view_toolbar` did not exist; GREEN passed after the split. Fresh focused verification: **12/12 PASS**, Ruff PASS, `git diff --check` PASS.
- Status: **USER ACCEPTED — 2026-08-31**. The development-app retest confirmed Member Local Axes render correctly.
- Save/Open UX follow-up (source filename-derived default save name, explicit `SAVED/NOT SAVED` title, Ctrl+S confirmation, bright Node/Member/Coordinate labels) is **USER ACCEPTED — 2026-08-31**. Real user retest also confirmed project JSON reopen restores the model.
- Global orientation indicator XYZ labels and application Exit confirmation are **USER ACCEPTED — 2026-08-31**. Exit confirmation prompts once on close, defaults to No, and warns explicitly when unsaved changes exist.
- Source feature scope for this plan is acceptance-complete and Task 7 full verification has passed.
  The mandatory pre-compile approval gate is the current checkpoint; no standalone rebuild is
  authorized yet.

Canonical Project JSON Save/Open checkpoint on 2026-08-31:

- Added centralized `ProjectPaths.projects`: development uses `artifacts/projects`; portable runtime uses `Data/Projects`; `ensure_layout()` creates it.
- Added deterministic atomic project save using project-local temp files, `flush` + `fsync`, and `os.replace`; failed replace leaves an existing destination byte-identical and cleans the temporary file.
- Added `Open Project JSON` under Import Model and `Save Project JSON` on the workflow toolbar with `Ctrl+S`.
- First Save opens in the canonical Projects directory and enforces `.staadprep.json`; Save/Open paths outside Projects are blocked.
- Dirty state tracks canonical project path + exact model revision; imported canonical models start dirty, successful Save clears `*`, later mutation restores `*`, and exact Undo to the saved revision clears it again.
- Opened project JSON preserves canonical nodes, members, numbering, metadata, UUID identity, and revision; Neutral JSON remains input-only and is never overwritten.
- TDD RED reproduced missing `ProjectPaths.projects`, `save_project_atomic`, Save/Open actions, and dirty-state APIs.
- Fresh focused verification: **33/33 PASS** across Save/Open UI, import routes, toolbar, path layout, portable paths, and serialization; Ruff PASS; strict mypy 0 issues across 3 affected source files; `git diff --check` PASS.
- Status: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**. Real user retest confirmed project JSON reopen restores the model.

The next user-requested source-only increment adds canonical entity inventories to Project Explorer.
`Nodes (N)` and `Members (N)` now expand into STAAD-number-sorted child rows; a child click selects
exactly one entity, while a group click expands and highlights every entity of that type. Explorer
requests activate Select mode and the matching Node/Member filter, then reuse the viewport's
existing selection signal so Properties and action state stay synchronized. The implementation does
not mutate coordinates or topology and is classified STANDARD. Focused affected regression is
**16/16 PASS**, a fresh acceptance check is **3/3 PASS**, and Ruff is clean. The user accepted this
source increment on 2026-08-31; there is still no compile authorization and no claim that a new
standalone `.exe` contains it yet. Design/plan:
`docs/superpowers/specs/2026-08-31-project-explorer-entity-selection-design.md` and
`docs/superpowers/plans/2026-08-31-project-explorer-entity-selection.md`.

Execution protocol explicitly confirmed by the user on 2026-08-31:

- implement and verify corrections against source/the project virtual environment first;
- present one user-testable correction at a time, wait for the user's result, and proceed only when
  the user instructs the next step;
- do not run Nuitka, replace a standalone folder, or assemble a new ZIP during source iteration;
- after all agreed source corrections and regression checks pass, **STOP at the pre-compile gate**;
- compile/package only after a new explicit user instruction to compile;
- after compilation, run the standalone-only path, dependency, relocation, no-Python, manifest, and
  extracted-ZIP checks, then stop again for package acceptance.

This source-first protocol is now canonical in `docs/WORKFLOW.md` under
`Development iteration and pre-compile approval gate`. It applies to the active follow-up and later
desktop corrections unless the user explicitly changes it. The separate mandatory high-risk
approval gate remains in force.

On 2026-08-31 the user explicitly requested a recoverable archive of older standalone releases.
The original T22 baseline folder+ZIP and the complete `post-t22-ux-final` checkpoint were moved to
`DEL/standalone-archive-20260831/`; see `DEL/UNUSED_FILES_MANIFEST.md`. The current
the `dist/post-t22-editing-final/` release was preserved under
`DEL/t24-quarantine-20260901/dist/post-t22-editing-final/`, and `build/windows/final/app.dist/` was
preserved in place. This
targeted move does not start the full T24 cleanup and nothing was deleted.

Post-package user testing on 2026-08-30 identified nine usability corrections. Requirements and execution are captured in:

- `docs/superpowers/specs/2026-08-30-post-t22-usability-design.md`;
- `docs/superpowers/plans/2026-08-30-sketchup-bridge-usability.md` (requirements 1-2, execute first);
- `docs/superpowers/plans/2026-08-30-desktop-interaction-usability.md` (requirements 3-9, execute after RBZ acceptance).

Inline execution of the SketchUp checkpoint is accepted in real SketchUp. The earlier desktop
requirements 3-9 rebuild is archived under `DEL/standalone-archive-20260831/post-t22-ux-final/`;
it is superseded for current testing by the active ten-item editing-correction rebuild described
above.

Desktop checkpoint evidence:
- Qt logical coordinates are scaled/flipped once at the VTK picking boundary; real Node and Member clicks select and render highlights;
- right-click provides Node/Member/both selection modes, Focus/Clear where applicable, Fit Model, and Reset View;
- workflow and Edit/View tools are separated into two toolbar rows and checked modes have an explicit active style;
- `scripts/smoke_viewport.py` reports `selection=pass reset_view=pass`;
- final unit + integration regression: **311/311 PASS**;
- UI regression: **100/100 PASS** (**67 lightweight + 33 isolated Windows VTK**);
- the UI runner now gives each invocation a unique project-local basetemp/cache path, avoiding stale Windows pytest locks;
- Ruff and targeted strict mypy passed for the affected source;
- rebuilt Nuitka report: `mode="standalone"`, `completion="yes"`; standalone SHA-256 `96EC7F7B0A74A0C025005E489D1213877C0FA6771C0F3F74D2FAA088E0301ABE`;
- this historical release is now archived under `DEL/standalone-archive-20260831/post-t22-ux-final/`;
- archived rebuilt folder: `DEL/standalone-archive-20260831/post-t22-ux-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/` (**812 files**, **708,051,873 bytes**);
- archived rebuilt ZIP: `DEL/standalone-archive-20260831/post-t22-ux-final/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` (**225,143,099 bytes**, SHA-256 `E1633876C102E5B77E6FD87D9B384235D25844EA6D324F01E9119963E9201AD2`);
- exact rebuilt package passed no-Python/different-CWD, relocation/reopen, and packaged READY/STD/report gates **3/3**;
- exact manifest verified **811/811** with zero size/hash errors; freshly extracted ZIP launched from a different Thai-path CWD with exit code 0.

Post-T22 usability commit:
- `e7ce6ad` — `feat: add SketchUp bridge interface`
- desktop interaction checkpoint: **superseded as a separate acceptance checkpoint**; its
  uncommitted changes are included in the consolidated editing-final/source-follow-up worktree.
  Current source behavior is user accepted and fully verified; the checkpoint remains uncommitted
  while compilation authorization is pending.

## Canonical project root

The canonical project boundary is the repository clone root that owns `.git` and `.worktrees/`;
the active source checkout may be a nested worktree below it. All project-created source/temp/cache/
log/build/test/generated/exported/quarantine files must stay inside that clone or its contained
worktrees. Resolve locations from Git metadata rather than a machine-specific absolute path.

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
- archived original folder: `DEL/standalone-archive-20260831/dist-root/STAAD_Model_Preprocessor_0.1.0_win64_portable/` (historical release evidence);
- archived original ZIP: `DEL/standalone-archive-20260831/dist-root/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` (**225,136,191 bytes**, SHA-256 `D31A70005D7F0B2C09B467D6A5591892868E9E56AC35874434BA38CFC4687115`);
- manifest independently verified **811/811 managed files** with no size/hash errors;
- final `.exe` and freshly extracted ZIP both launched with Python absent from `PATH`, exit code 0;
- different CWD, spaces/Unicode relocation, reopen with existing `Data/`, and packaged T21 READY/STD/report workflow passed;
- package README recommends a reasonably short extraction path because deeply nested paths can exceed the legacy Windows DLL path limit used by bundled VTK modules;
- no Setup/MSI/NSIS/automatic-updater/one-file production artifacts were produced.

Historical note: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/` and
its sibling ZIP preserve the earlier ten-item package evidence but do not contain every later
accepted source follow-up. The consolidated package was accepted by the user, and T23 acceptance
was subsequently reported PASS on 2026-09-01. The next available task is T24 cleanup, which still
requires an explicit user instruction.

### USER ACTION REQUIRED

**T22 package acceptance is complete.** Nuitka compile step 1, isolated portable-folder/ZIP
assembly, package-only verification, and real user acceptance are complete under
`dist/post-t22-refresh-save-final/`. The quarantined
`DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` package is
historical and does not contain every accepted source follow-up. T23 acceptance is recorded as
PASS by user report (2026-09-01); T24 is now active under the user's continuation instruction.

T23 acceptance is **PASS by user report (2026-09-01)**. T24 is now unblocked; its inventory and
reference/evidence map steps are complete. The user approved `DEL/UNUSED_FILES_MANIFEST.md` and
Step 4 moved the superseded standalone package into `DEL/`; no quarantine file was deleted.

T24 Step 2 evidence: `artifacts/cleanup/t24-reference-map-20260901.md`. The map protects current
source/tests/native/vendor/packaging, current build/package/evidence paths, and ambiguous generated
data. The moved package is recorded at
`DEL/t24-quarantine-20260901/dist/post-t22-editing-final/`. Step 5 found no live
source/test/script/config reference to the old path and updated historical documentation links.
Next resume point: use the post-T24 mindmap plan at
`docs/superpowers/plans/2026-09-01-worktree-mindmap.md`; do not move ambiguous candidates.

T24 final audit evidence: `artifacts/cleanup/t24-final-verification-20260901.md`. The only
quarantined item is `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` (814 files,
933,569,500 bytes). Final deletion remains user-controlled.
Checkpoint commit: `chore: quarantine unused project files for review` (hash recorded by Git).

## T24 cleanup boundary

T24 may proceed because T23 acceptance is recorded. It moves only verified-unused/superseded
files into project-local `DEL/`, writes `DEL/UNUSED_FILES_MANIFEST.md`, and never deletes files.
Final deletion remains user-controlled.


## 2026-08-31 source handoff checkpoint

- User-accepted source behavior before handoff: Member Translational Repeat preview, engineering Properties, Project Explorer entity selection, Member Local Axes XYZ, three-row toolbar with visible View controls, Save/Open Project JSON, import-derived save filename, `SAVED` / `NOT SAVED` title state, Ctrl+S save confirmation, readable Node/Member/Coordinate labels, Global Axis X/Y/Z labels, and Exit confirmation UI.
- Latest real-user defect was clicking window `X` and choosing `Yes` without closing the application.
- Latest source fix: exit dialog now compares the native Qt button result with equality (`==`) and the accepted close path delegates to `QMainWindow.closeEvent()`.
- Exit regression evidence after fix: `tests/ui/test_exit_confirmation.py` **4/4 PASS**; Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Status of latest close fix: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**. Real retest confirmed `X -> No` stays open and `X -> Yes` closes.
- Full source verification is **COMPLETE**: **332/332 source unit+integration PASS**, **140/140 UI
  PASS**, six real Windows source smokes exit 0, focused Save/Open **5/5 PASS**, Ruff PASS, strict
  mypy **0 issues in 6 source files**, and `git diff --check` PASS.
- The package-only verification suite was run against the new package after explicit user
  authorization: **7/7 PASS**. Nuitka compilation, portable assembly, ZIP creation, and real user
  package acceptance completed under `dist/post-t22-refresh-save-final/` on 2026-08-31.

## 2026-09-01 post-T24 documentation checkpoint

`docs/WORKTREE_MINDMAP.md` is now the canonical navigation map for this worktree. It records the
tracked-file catalog, source/import/test/build/package relationships, generated and protected
directories, the recoverable T24 quarantine, and the RBZ archive/source/callback/JSON contract.
The document is documentation-only: it does not compile, alter model behavior, or start T25.

T24 remains complete from checkpoint `9f9dc79 chore: quarantine unused project files for review`.
The mindmap plus synchronized current documents are committed in `9751746 docs: add complete
worktree and RBZ mindmap`; stop for user review after this documentation checkpoint.

## 2026-09-01 T25 storage audit checkpoint

The user approved the exact six-item move set after a full project storage recheck. The old package
and five non-current/failed build attempts were moved to `DEL/t25-storage-audit-20260901/`; those
quarantine contents were later removed by the user. The original paths are absent, no live
references point to the old names, and the current package/RBZ/build final remain intact.

Post-move inventory: `build/` is 5,522 files / 2,269,062,384 bytes; `artifacts/` is 6 files /
155,022 bytes; quarantine is 6,329 files / 3,205,802,166 bytes. The largest remaining consumers are
regenerable `.tmp/` (57,412,145,481 bytes) and `.cache/` (506,361,099 bytes); they were deliberately
not touched and require a separate explicit deletion decision. Moving files to `DEL/` does not free
disk space. Manifest: `DEL/UNUSED_FILES_MANIFEST.md`; audit: `artifacts/cleanup/storage-audit-20260901.md`.

Post-move standalone smoke checkpoint (2026-09-01): the current accepted folder
`dist/post-t22-refresh-save-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/` was launched through
`tests/integration/test_packaged_paths.py::test_final_package_launches_without_python_from_different_cwd`.
The test used a sanitized PATH without Python, a different temporary working directory, and the
packaged smoke timeout; result: **1/1 PASS** in 6.29 seconds. No standalone process remained afterward.
The executable hash remains `1C7BB68D12BEFA8A1DBDC5A8A18B031A1E19AEFCFB91C7567441E79DB88F4470`,
the ZIP hash remains `0EF7933499179284B7FC01B011876BF196F7471D4F8CA5B7B12F46E36059E314`, and the
worktree is clean. This was verification only; no Nuitka compile or source change was performed.

## 2026-09-01 T26 space-cleanup move checkpoint

The user approved moving regenerable output and historical worktrees into a project-local DEL
quarantine instead of deleting them. Generated contents from the active `.tmp/` and `.cache/` were
moved to `DEL/t26-storage-cleanup-20260901/generated-tmp/` and
`DEL/t26-storage-cleanup-20260901/generated-cache/`. The source `.tmp/` retains only `.gitkeep` and
an empty pytest skeleton; source `.cache/` retains an empty pytest skeleton.

All 22 historical clean worktrees (maintenance plus T01–T21) were moved to
`DEL/t26-storage-cleanup-20260901/old-worktrees/` using Git worktree operations. Only the current
T22 worktree remains under `.worktrees/`; all branch refs remain available and `git worktree list`
has no prunable entry. Moved quarantine totals are 68,900 temp files / 58,120,618,730 bytes,
10,211 cache files / 506,361,099 bytes, and 67,375 old-worktree files / 5,706,009,647 bytes.

The current accepted portable folder/ZIP, current RBZ, source, tests, final build, and documentation
were retained. Executable and ZIP hashes remain unchanged, no Python or standalone process remains,
and no deletion or compile was performed. The user may delete the quarantine separately after review.

The post-cleanup standalone recheck also passed **1/1 in 6.54 seconds** using the no-Python,
different-CWD packaged launch test. Its generated basetemp/cache were moved into the same T26
quarantine, leaving only the standard empty pytest skeletons in the active `.tmp/` and `.cache/` paths.

## 2026-09-06 T27 free user-selected paths and package checkpoint

The user reported two real-use path restrictions. The source fix separates explicit user-selected
paths from application-managed runtime paths:

- SketchUp Bridge JSON selected in the desktop app may come from any location; the configured inbox
  remains the default chooser location.
- SketchUp RBZ `Choose Inbox...` accepts any existing directory and persists the selection.
- `Export STD` accepts any selected destination and writes the sibling `.validation.json` beside it.
- Project JSON Save/Open, cache, temp, logs, reports, and other implicit runtime writes retain their
  project/portable-local contracts.

Source checkpoint `58dbc3a fix: allow user-selected import and export paths` passed focused regressions
**24/24**, unit+integration **336/336**, Ruff, strict mypy on 3 affected source files, and diff check.
The prior full UI run remains non-authoritative because the existing PyVista/VTK renderer test caused
a native Python access violation; no path-test failure was observed.

The user authorized a fresh package. The previous accepted folder, Nuitka final build, and RBZ were
moved to `DEL/t27-free-path-selection-20260906/old-release/`. Nuitka then completed with
`mode="standalone"` and `completion="yes"`; the new portable folder/ZIP and RBZ were assembled.
Package verification is **9/9 PASS**, including manifest/hash checks, RBZ archive checks, no-Python
different-CWD launch, relocation/reopen, and packaged READY/STD workflow. The new final artifacts are:

- folder: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/` — 812 files / 708,474,179 bytes;
- ZIP: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` — 225,277,088 bytes;
- executable SHA-256: `41346B2BEDBA637EBDCA43E390B59E257B19397700F95FAFDB346203A7E2E850`;
- ZIP SHA-256: `7A163315FD01E42A98D63F6728AB7DCFCA0FF6C05549B91ECBE2396C789A4E11`;
- RBZ SHA-256: `C67349CBE3CB0315926FB69606287835AF981245344DDD48ED5B3FB9D4306701`.

The release was built using PowerShell 7 because Windows PowerShell 5.1 does not define the script's
`$IsWindows` variable. Dependency Walker was downloaded into the project-local Nuitka cache after
the earlier cleanup had removed the old cache. No installer/MSI/NSIS, updater, or one-file build was
created.
Temporary output created during source/package verification was moved to
`DEL/t27-free-path-selection-20260906/test-output/`; the active `.tmp/` retains only its standard
`.gitkeep` and empty pytest skeleton.
