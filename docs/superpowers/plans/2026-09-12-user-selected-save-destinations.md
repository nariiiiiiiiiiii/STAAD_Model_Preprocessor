# User-Selected Save Destinations Implementation Plan
> Historical plan record: task-date checkboxes and status are preserved as recorded; for current status see [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users explicitly select any destination for Project JSON first-save/Save As while preserving atomic saves, current-file Save behavior, and the `.STD`/validation-report pairing.

**Architecture:** Keep `ProjectPaths.resolve_user_selected_path()` as the resolver for explicitly chosen locations. Project JSON writes continue through `save_project_atomic`; first Save and Save As use a file chooser with no `Projects` containment guard, while Save on an associated project writes to its current path. `Export STD` keeps one destination chooser and writes its validation report beside that `.STD`.

**Tech Stack:** Python 3.12, PySide6, pytest, existing atomic Project JSON serializer.

**Spec:** `docs/superpowers/specs/2026-09-12-user-selected-save-destinations.md`

## Global Constraints

- Do not change engineering calculations, canonical model data, geometry, ReadyGate semantics, `.STD` serialization, or SketchUp import format.
- Preserve atomic sibling-temp Project JSON replacement and never silently redirect a user-selected path.
- Keep automatic runtime outputs project-local; only explicit user-selected source/output dialogs may use external paths.
- The 2026-09-13 owner screenshot confirms that the first-save UI chooser returns an external target
  but `MainWindow._assert_project_json_path()` blocked it before the serializer was called.
- This is classified HIGH-RISK for data-loss potential. The owner approved the refreshed STRICT /
  Full TDD plan on 2026-09-13; implementation is authorized only within this documented scope.
- No compile, RBZ build, portable assembly, ZIP, or release replacement is part of this source plan.

## Current checkpoint (2026-09-13)

The owner manually tested the Crop to Select / Zoom in Select viewport change and reports it works
well; only Save remained blocked. The exact dialog message was produced by the first-save guard in
`main_window.py`. The owner approved this refreshed plan on 2026-09-13. Strict TDD RED evidence:
the new external First Save test returned `False`, while the new Save As checks failed because the
action/method did not exist (**4 failed, 1 passed** in the focused red run). Implementation is now
in place; the final relevant regression evidence is recorded below. Stop after source verification
and owner app acceptance; do not compile.

---

### Task 1: Lock external-save, Save As, cancellation, and overwrite behavior (STRICT)

**Files:**
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/model/serialization.py` only if atomic-save tests expose a real defect
- Modify: `tests/ui/test_project_save_ui.py`
- Modify: `tests/unit/test_serialization.py`

**Interfaces:**
- `save_current_project() -> bool` saves to the current associated path; for a project with no
  associated path, it opens a destination dialog that can select any directory.
- Add a `save_project_as_action` labeled **Save As…** that opens a destination dialog for any
  selected directory. Place it immediately after **Save Project JSON** on the existing main toolbar;
  atomically write there, then associate the project with the new path only after success.
- Add `save_project_as() -> bool`; it always opens the chooser. The chooser starts in the current
  associated file's parent when one exists, otherwise in `ProjectPaths.projects` with the current
  project display name. Keep the `.staadprep.json` suffix normalization.
- First Save and Save As resolve explicit selections with `ProjectPaths.resolve_user_selected_path()`;
  do not call `_assert_project_json_path()`. Remove that private guard if no callers remain, but keep
  `ProjectPaths.assert_inside_project()` for automatic/runtime-owned paths.
- Keep `open_project_json(path)` associating the exact resolved user-selected file.
- Keep the existing regular Save confirmation. Save As uses the file dialog's native overwrite
  confirmation rather than adding a second generic “Save project?” prompt.

- [x] **Step 1: Add failing UI tests.** Replace `test_first_save_rejects_destination_outside_projects`
  with an assertion that First Save to an external folder succeeds, associates that exact resolved
  file, marks the model saved, and round-trips through `load_project()`. Add tests that Save As
  appears beside Save, is enabled only with a model, saves to a second external folder, and changes
  the associated path only after success. Cover cancellation (no new file, dirty state and previous
  path unchanged), extension normalization, and regular Save writing subsequent edits back only to
  the newly associated path.

- [x] **Step 2: Run those tests and verify they fail specifically on the first-save Projects guard
  or absent Save As action, not on unrelated Qt setup.**

Observed RED: **4 failed, 1 passed**. The First Save test returned `False` at the old guard; action
and Save As tests reported the missing `save_project_as_action` / `save_project_as` members.

- [x] **Step 3: Implement only the path-policy change and Save As action.** Route First Save and Save
  As targets through `resolve_user_selected_path()` and `save_project_atomic()`. Keep regular Save
  pointed at its current associated file. Update `_current_project_path`, `_saved_revision`, title,
  and saved-state UI only after `save_project_atomic()` succeeds; leave all of them unchanged on
  Cancel or failure. Do not change the runtime path resolver or other project-local output rules.

- [x] **Step 4: Add independent serializer safety tests.** Patch the serializer's `os.replace` to
  raise after the sibling temp is written. Assert an existing selected external file remains
  byte-identical, the `.staadprep-*.tmp` sibling is removed, and the UI does not associate the failed
  path or mark the model saved. Separately verify a successful external write round-trips through
  `load_project()`.

Observed GREEN/safety: the repository already had the independent atomic-replace failure regression;
it was retained and run. UI failure cases were added for both First Save and Save As. Core Save UI +
serializer checks: **14/14 PASS**.

### Task 2: Verify the complete desktop file-dialog/write inventory

**Files:**
- Test: `tests/ui/test_export_ui.py`
- Test: `tests/ui/test_import_routes.py`
- Test: `tests/unit/test_paths.py`
- Review: `src/staadprep/ui/main_window.py`, `src/staadprep/importers/neutral_reader.py`,
  `src/staadprep/repair/audit.py`

- [x] **Step 1: Verify import dialogs accept user-selected files outside the project** for Project
  JSON, SketchUp Neutral JSON, and DXF; canceling each dialog must preserve the current model.
- [x] **Step 2: Verify Export STD accepts an external path and its validation report lands in the
  same selected directory with the matching basename.**
- [x] **Step 3: Search all desktop source for file dialogs and write calls; record every user-facing
  output, its chooser, and any intentionally project-local runtime output in HANDOFF/INDEX.
- [x] **Step 4: Run focused save/import/export/path tests, relevant UI tests, Ruff, strict mypy, and
  `git diff --check`; include failure/cancel/overwrite-preservation cases and stop before compile for
  owner testing. Manual acceptance: First Save to an external folder; Save As to another folder;
  regular Save after editing; cancel; and overwrite an existing file only after the native dialog
  confirms. Reopen both saved JSON files to confirm contents. Verify export STD and its validation
  JSON remain together in the chosen external folder.

Observed: **58/58 relevant UI/unit regression tests PASS** (Save, serialization, Open/Import, Export,
project/portable paths, toolbar, and exit confirmation); Ruff PASS; strict mypy **0 issues** in
`main_window.py`; `git diff --check` PASS. No compile was run. Owner manual acceptance of external
First Save and Save As was reported working by the owner on 2026-09-13; individual manual cases
were not itemized. No compile/package authorization was given.

### Task 3: STRICT independent regression, docs, and commit

- [x] Compare the path/action inventory against the spec line by line.
- [x] Run the full relevant unit/UI regression subset, including failure, cancel, and external-file
  overwrite-preservation cases.
- [x] Update README, HANDOFF, INDEX, TASK_BOARD, CHECKLIST, and this plan with exact evidence.
- [x] Commit only after the STRICT verification gate is green; stop for owner manual acceptance.

Checkpoint note: the source/docs commit is the final automated step for this task. The owner reports
the uncompiled Save flow works (2026-09-13). This closes the source-app acceptance gate; compile or
package work still needs separate explicit authorization.
