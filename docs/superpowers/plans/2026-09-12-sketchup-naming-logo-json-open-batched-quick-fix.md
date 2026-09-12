# Implementation Plan — Version, SketchUp Naming, Branding, Open JSON, and Batched Quick Fix

> **Status:** Source checkpoints 1–5 are verified; user acceptance and all release builds remain pending.

**Goal:** Implement the four requested usability changes, promote the coordinated app/RBZ version, verify one checkpoint at a time, and stop before compiling or packaging.

**Active checkout:** `.worktrees/task-22-portable-packaging` on `task/22-portable-packaging`.

**Spec:** [`../specs/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md`](../specs/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md)

## Owner decisions and gates

1. **Version:** owner approved `0.2.0` on 2026-09-12; Checkpoint 1 is complete.
2. **SketchUp export name:** owner confirmed `<safe-SKP-stem>_<DDMMYYYY>.json`, date at export time, with `_02`, `_03` collision suffixes; unsaved models use title, then `Untitled`. Checkpoint 2 source implementation is complete; real SketchUp acceptance remains pending.
3. **External Open/Save:** owner confirmed Open from any folder and Save-back to the opened file; first Save for a new/unsaved project remains in `Data/Projects/`. Checkpoint 4 is complete.
4. **Risk gate:** owner explicitly approved STRICT / Full TDD on 2026-09-12 for multi-issue Quick Fix and intersection repair; Checkpoint 5 is source-verified.

## Recommended model by checkpoint

| Checkpoint | Recommended model | Reason |
|---|---|---|
| Version contract, naming, icon, and unrestricted Open | **Luna Max** | Focused source changes with standard, bounded verification. |
| Multi-issue Quick Fix / intersection | **Max** | High-risk topology and graph mutation; requires STRICT / Full TDD and independent regression evidence. |
| Final Windows/RBZ/package build, if separately authorized | **Max** | Release artifact coordination, cleanup/retention, manifests, and package verification have a wider blast radius. |

Use the checkpoints sequentially. After each checkpoint, report the diff and its focused verification, then pause for the owner’s instruction before moving to the next. Never infer compile/package authorization from approval to edit or test source.

## Global constraints

- Keep all project-controlled changes/artifacts inside the canonical project root and work in the active T22 worktree.
- Preserve unrelated working files and historical evidence. Do not delete or move prior release artifacts during source work.
- Keep the original user-selected image at `LOGO/ChatGPT Image Sep 12, 2026, 06_17_26 PM.png` untouched. Copy it into a tracked app asset only when implementing the icon checkpoint.
- Do not change coordinate conversion, validation thresholds, geometry detection, ReadyGate, or `.STD` semantics.
- Do not alter intersection mathematics. Route Quick Fix through the existing intersection-split command.
- Run no Nuitka build, RBZ build, portable assembly, or ZIP creation until the user separately authorizes compile/package. Source/UI tests and image conversion tests are not permission to create a release package.

## Proposed file map

| Path | Planned responsibility |
|---|---|
| `src/staadprep/version.py`, `src/staadprep/__init__.py` | One canonical proposed application version. |
| `extensions/sketchup_staadprep/staadprep_loader.rb` | Match SketchUp extension version to the canonical release. |
| `tests/unit/test_version_contract.py` | Enforce Python/package/Ruby version agreement. |
| `pyproject.toml` | Declare Pillow as a development/build-tool dependency only. |
| `extensions/sketchup_staadprep/staadprep/exporter.rb` | Produce a safe source-based/date-stamped JSON basename with collision handling. |
| `tests/unit/test_sketchup_ruby_contract.py`, `packaging/INSTALL_RBZ.md` | Protect and document the source export-name contract. |
| `assets/branding/staad-model-preprocessor.png` | Tracked copy of the exact selected logo. |
| `scripts/build_windows_icon.py`, `scripts/build_windows.ps1`, `src/staadprep/app.py` | Create a multi-size Windows icon, embed it in later builds, and set the Qt application icon. |
| `tests/unit/test_windows_icon_builder.py`, `tests/unit/test_windows_build_contract.py`, `tests/ui/test_main_window.py` | Verify icon conversion, build flags, and packaged/development app icon resolution. |
| `src/staadprep/ui/main_window.py`, `src/staadprep/model/serialization.py` | Open JSON from any path and safely save to an explicitly opened external path. |
| `tests/ui/test_project_save_ui.py`, `tests/unit/test_serialization.py` | Verify Open/Save-back and atomic-write failure behavior. |
| `src/staadprep/ui/issue_console.py`, `src/staadprep/ui/panels.py`, `src/staadprep/ui/main_window.py`, `src/staadprep/repair/quick_fix_batch.py` | Multi-selection and one atomic, conflict-checked Quick Fix command. |
| `tests/unit/test_quick_fix_batch.py`, `tests/ui/test_issue_console.py`, `tests/ui/test_repair_apply_refresh.py`, `tests/unit/test_manual_split_ops.py` | Strict graph, conflict, rollback, refresh, Undo/Redo, and intersection coverage. |
| `README.md`, `docs/INDEX.md`, `docs/HANDOFF.md`, `docs/TASK_BOARD.md`, `docs/WORKFLOW.md`, `docs/CHECKLIST.md`, `docs/RISK_GATES.md` | Record the accepted version, implementation evidence, and pre-compile pause. |

## Checkpoint 0 — Confirm the change contract

**Risk:** FAST (planning only). **Model:** Luna Max.

- [x] Confirmed target version `0.2.0`.
- [x] Confirmed the filename and external Open/Save-back contracts.
- [ ] Do not start the topology-changing checkpoint until the separate STRICT approval is explicit.

**Stop:** wait for direction after each checkpoint; each behavior is confirmed before its own implementation.

## Checkpoint 1 — Synchronize the version contract

**Risk:** STANDARD. **Model:** Luna Max.

**Files:** `src/staadprep/version.py`, `src/staadprep/__init__.py`, `extensions/sketchup_staadprep/staadprep_loader.rb`, `tests/unit/test_version_contract.py`, and only live-status documentation that states the current version.

- [x] Update the canonical Python version to `0.2.0`; package `__version__` imports that single source.
- [x] Update Ruby `EXTENSION.version` to `0.2.0`; leave historical package records and immutable historical plans unchanged.
- [x] Extend the contract test to assert the approved version and agreement across package Python, canonical Python, project metadata, and Ruby.
- [x] Run `tests/unit/test_version_contract.py` (**6/6 PASS**), Ruff (**PASS**), strict mypy for the three affected Python files (**0 issues**), and `git diff --check` (**PASS**).
- [x] Report the diff and evidence; pause for owner direction before Checkpoint 2.

**Checkpoint 1 files changed:** `src/staadprep/version.py`, `src/staadprep/__init__.py`, `extensions/sketchup_staadprep/staadprep_loader.rb`, `tests/unit/test_version_contract.py`.

## Checkpoint 2 — Name SketchUp JSON after its source model

**Risk:** STANDARD. **Model:** Luna Max.

**Files:** `extensions/sketchup_staadprep/staadprep/exporter.rb`, `tests/unit/test_sketchup_ruby_contract.py`, `packaging/INSTALL_RBZ.md`.

- [x] Build `<safe-source-stem>_<DDMMYYYY>.json` using the local date when Export is clicked.
- [x] Normalize Windows separators, remove the source extension, replace invalid Windows filename characters, trim trailing dots/spaces, handle reserved Windows names, and fall back to the unsaved model title or `Untitled`.
- [x] Preserve `_02`, `_03`, etc. for same-name/same-day collisions and leave `source_file` payload metadata unchanged.
- [x] Extend the source-contract test for source path/title fallback, unsafe/reserved names, date format, and collision suffix behavior.
- [x] Run `tests/unit/test_sketchup_ruby_contract.py` (**1/1 PASS**) and `tests/unit/test_version_contract.py` (**6/6 PASS**); combined **7/7 PASS**; Ruff and `git diff --check` pass.
- [x] Update `packaging/INSTALL_RBZ.md`. Pause for owner direction before Checkpoint 3.

**Checkpoint 2 limitation:** no Ruby executable is available, so verification is static source-contract coverage, not Ruby execution or real SketchUp acceptance. RBZ content tests and real SketchUp smoke remain deferred until a separate build is authorized.

Acceptance example: `13-DIZ-SD11-09-69.skp` exported on 12 September 2026 becomes `13-DIZ-SD11-09-69_12092026.json`; a collision becomes `_02.json`.

## Checkpoint 3 — Apply the selected logo to the app and future executable

**Risk:** STANDARD. **Model:** Luna Max.

**Exact source:** `D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor\LOGO\ChatGPT Image Sep 12, 2026, 06_17_26 PM.png` (1254×1254). Preserve this original.

**Files:** `assets/branding/staad-model-preprocessor.png`, `pyproject.toml`, `scripts/build_windows_icon.py`, `scripts/build_windows.ps1`, `src/staadprep/app.py`, `tests/unit/test_windows_icon_builder.py`, `tests/unit/test_windows_build_contract.py`, `tests/ui/test_main_window.py`.

- [x] Copy the exact selected image into the active worktree’s tracked branding asset; do not substitute the earlier `05_44_55 PM` image. The copy SHA-256 is `EE4F81C3C7C76EEF6B2C262ACA00CB824FEECA025BA6FB5F3756EBE5E2396350`.
- [x] Add Pillow to the development-only dependency list; create a builder that validates the PNG and writes the multi-size ICO (16, 24, 32, 48, 64, 128, 256) only under project-local `build/`.
- [x] Add the ICO option to the later Windows build command and include the PNG beside the executable so Qt can use the same app/window/taskbar icon.
- [x] Test all ICO sizes, development and executable-adjacent logo resolution, build-command contract, and non-null app/window icons.
- [x] Run the focused unit/UI/build-contract suite (**12/12 PASS**), Ruff (**PASS**), strict mypy (**0 issues** for two affected source files), and `git diff --check` (**PASS**).
- [x] Generate and verify the selected-logo ICO at `build/windows/icon-checkpoint-20260912/staad-model-preprocessor.ico` (7 resolutions; 79,047 bytes). Do not invoke Nuitka in this checkpoint.
- [x] Report diff and verification; pause for owner direction before Checkpoint 4.

**Checkpoint 3 boundary:** the development Qt window and build-script contract are verified; no Windows executable was rebuilt, so the compiled executable icon remains to be confirmed after separately authorized packaging.

## Checkpoint 4 — Allow Project JSON Open from any folder

**Risk:** STANDARD. **Model:** Luna Max.

**Files:** `src/staadprep/ui/main_window.py`, `src/staadprep/model/serialization.py`, `tests/ui/test_project_save_ui.py`, `tests/unit/test_serialization.py`.

- [x] Let Open resolve any explicitly selected absolute `.json` path through `ProjectPaths.resolve_user_selected_path` while retaining schema validation and the Projects initial directory.
- [x] After opening, retain the resolved selected path so Save writes back to the same file.
- [x] Keep first Save for a new/imported model constrained to the project’s `Data/Projects/` area; add a regression for rejecting an outside first-save destination.
- [x] Stage atomic-save temp files as unique hidden siblings of the destination, clean them on all paths, and preserve old target bytes if replacement fails.
- [x] Test external Open/edit/Save/reopen, first-Save restriction, malformed schemas, same-directory staging, and replace failure.
- [x] Run focused serialization/UI tests (**10/10 PASS**), Ruff (**PASS**), strict mypy (**0 issues** for two source files), and `git diff --check` (**PASS**).
- [x] Report diff and verification; pause for owner direction before Checkpoint 5.

**Checkpoint 4 boundary:** external files are accessed only after the user explicitly selects them. No Nuitka, RBZ, or portable package build was performed.

## Checkpoint 5 — Multi-issue Quick Fix and intersection handling (HIGH-RISK)

**Status:** APPROVED and SOURCE-VERIFIED; package/user acceptance remains pending. **Model:** Max.

**HIGH-RISK COMPONENT:** selecting and applying multiple automatic graph repairs together, including merge/delete and splitting intersecting structural members.

**Reason:** stale, overlapping, or partially applied commands can change node/member connectivity and analytical topology.

**Failure impact:** incorrect incidences, missing/duplicated members, disconnected or misleading model state, and invalid downstream export.

**Recommended level:** STRICT / Full TDD.

**Proposed verification:** independent before/after graph snapshots; unit tests for two orphan fixes, mixed independent fixes, crossing split, overlapping conflicts, a forced later-child failure and rollback, exactly one audit entry, exact Undo restoration, Redo, fresh issue/viewport refresh, and protected single-issue behavior; targeted isolated UI regression; full unit/integration and relevant UI suite; Ruff, strict mypy, `git diff --check`.

**Expected scope:** `src/staadprep/ui/issue_console.py`, `src/staadprep/ui/panels.py`, `src/staadprep/ui/main_window.py`, new `src/staadprep/repair/quick_fix_batch.py`, and the targeted tests above. Do not change the intersection geometry algorithm or validation meaning.

**Required user approval:** received on 2026-09-12: “Proceed with STRICT / Full TDD for multi-issue Quick Fix and intersection repair?”

After approval:

- [x] Add extended issue-row selection and a stable `selected_issues` interface while preserving one-issue behavior.
- [x] Build commands against the same original model snapshot; reject unsupported, duplicate, stale, or overlapping selections before mutation, with a visible explanation and no silent partial application.
- [x] Route `CROSSING_WITHOUT_NODE` only through the existing `build_split_selected_intersection()` command; do not modify geometric intersection detection/math.
- [x] Apply one `CompositeRepair` with one confirmation, audit/history entry, refresh, and atomic Undo/Redo. Clear stale selection after apply.
- [x] Follow the approved STRICT sequence (expected behavior → tests → RED → minimal implementation → GREEN → independent graph verification → regressions/lint/type-check).
- [x] Pause for owner acceptance before any release build.

**Checkpoint 5 evidence:** focused planner/repair/UI STRICT suite **61/61 PASS**; full unit/integration **345 passed**, **1 skipped** (archive-level RBZ check requires an explicitly built `0.2.0` RBZ), **3 deselected** (portable launch gates require the `0.2.0` executable/package); affected UI suite **26/26 PASS**; Ruff PASS; strict mypy **0 issues** across four affected source files; diff check PASS. No Nuitka or portable release build was run. A legacy integration test briefly produced a transient `0.2.0` RBZ; it was removed; fixture tests now remain under `.tmp/tests`, and existing stage copies were refreshed and left in place.

## Checkpoint 6 — Synchronize documents and stop before compile

**Risk:** STANDARD. **Model:** Luna Max; use Max if reviewing release/package coherence.

**Files:** live `README.md`, `docs/INDEX.md`, `docs/HANDOFF.md`, `docs/TASK_BOARD.md`, `docs/WORKFLOW.md`, `docs/CHECKLIST.md`, `docs/RISK_GATES.md`, `docs/PROJECT_SPEC.md`, `docs/ARCHITECTURE.md`, and `docs/WORKTREE_MINDMAP.md`.

- [x] Record only implemented/verified state; distinguish source-verified, user-tested, and packaged states.
- [x] Record the accepted version and exact selected logo provenance without rewriting immutable historical artifact evidence.
- [x] Record that STRICT approval was granted and the exact evidence for the topology work.
- [x] Provide the user with development launch instructions and request manual source-app acceptance; real SketchUp export acceptance awaits an authorized RBZ build.
- [x] **Stop before compile.** No Nuitka, RBZ rebuild, portable assembly, ZIP creation, release replacement, or old-package move until the user explicitly asks to compile/package.
- [ ] After separate compile authorization, make a dated recoverable backup/move plan first; verify candidate package, manifest/hash, and launch before accepting it. Never delete old artifacts.

## Definition of done for the source phase

- All owner-approved source checkpoints are complete and their focused verification is recorded.
- The user has had the requested opportunity to test the uncompiled development app and the real SketchUp extension where relevant.
- All live `.md` status documents agree on version and actual completion evidence.
- The agent has paused at the pre-compile gate awaiting a separate instruction.
