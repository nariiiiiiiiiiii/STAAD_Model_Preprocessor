# User-Selected Save Destinations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users explicitly select any destination for Project JSON first-save/Save As while preserving atomic saves, current-file Save behavior, and the `.STD`/validation-report pairing.

**Architecture:** Keep `ProjectPaths.resolve_user_selected_path()` as the resolver for explicitly chosen locations. Project JSON writes continue through `save_project_atomic`; first Save and Save As use a file chooser with no `Projects` containment guard, while Save on an associated project writes to its current path. `Export STD` keeps one destination chooser and writes its validation report beside that `.STD`.

**Tech Stack:** Python 3.12, PySide6, pytest, existing atomic Project JSON serializer.

**Spec:** `docs/superpowers/specs/2026-09-12-user-selected-save-destinations.md`

## Global Constraints

- Do not change engineering calculations, canonical model data, geometry, ReadyGate semantics, `.STD` serialization, or SketchUp import format.
- Preserve atomic sibling-temp Project JSON replacement and never silently redirect a user-selected path.
- Keep automatic runtime outputs project-local; only explicit user-selected source/output dialogs may use external paths.
- This is classified HIGH-RISK for data-loss potential. The owner approved STRICT / Full TDD on
  2026-09-12; do not start implementation until the current viewport checkpoint is owner-reviewed.
- No compile, RBZ build, portable assembly, ZIP, or release replacement is part of this source plan.

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
  selected directory, atomically writes there, then associates the project with the new path.
- Keep `open_project_json(path)` associating the exact resolved user-selected file.

- [ ] **Step 1: Add failing UI tests.** Test first Save to an external directory and re-open the
  written file; Save As from an internally or externally opened JSON to a second external
  destination; cancellation preserves dirty state and creates no file; regular Save after Save As
  writes only to the newly associated path; and extension normalization remains `.staadprep.json`.

- [ ] **Step 2: Run those tests and verify they fail specifically on the first-save Projects guard
  or absent Save As action, not on unrelated Qt setup.**

- [ ] **Step 3: Implement only the path-policy change and Save As action.** For selected targets,
  call `resolve_user_selected_path`; keep `save_project_atomic`, update `_current_project_path` and
  `_saved_revision` only after a successful replace, and leave current state unchanged on Cancel or
  failure.

- [ ] **Step 4: Add independent serializer safety tests.** Force serialization/replace failure and
  assert an existing selected external file remains byte-identical and the temporary sibling is
  cleaned; verify successful external writes round-trip through `load_project`.

### Task 2: Verify the complete desktop file-dialog/write inventory

**Files:**
- Test: `tests/ui/test_export_ui.py`
- Test: `tests/ui/test_import_routes.py`
- Test: `tests/unit/test_paths.py`
- Review: `src/staadprep/ui/main_window.py`, `src/staadprep/importers/neutral_reader.py`,
  `src/staadprep/repair/audit.py`

- [ ] **Step 1: Verify import dialogs accept user-selected files outside the project** for Project
  JSON, SketchUp Neutral JSON, and DXF; canceling each dialog must preserve the current model.
- [ ] **Step 2: Verify Export STD accepts an external path and its validation report lands in the
  same selected directory with the matching basename.**
- [ ] **Step 3: Search all desktop source for file dialogs and write calls; record every user-facing
  output, its chooser, and any intentionally project-local runtime output in HANDOFF/INDEX.
- [ ] **Step 4: Run focused save/import/export/path tests, relevant UI tests, Ruff, strict mypy, and
  `git diff --check`; stop before compile for owner testing.**

### Task 3: STRICT independent regression, docs, and commit

- [ ] Compare the path/action inventory against the spec line by line.
- [ ] Run the full relevant unit/UI regression subset, including failure, cancel, and external-file
  overwrite-preservation cases.
- [ ] Update README, HANDOFF, INDEX, TASK_BOARD, CHECKLIST, and this plan with exact evidence.
- [ ] Commit only after the STRICT verification gate is green; stop for owner manual acceptance.
