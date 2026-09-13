# User-Selected Save Destinations — Behavior Specification

## User request

Allow Project JSON and every user-facing export/save action to use a user-selected destination
outside the project. Import dialogs should remain unrestricted. On 2026-09-13 the owner confirmed
the other tested viewport features pass, but Project JSON First Save outside the project still
shows **Save Blocked**.

## Confirmed Save Blocked cause (2026-09-13)

Before the fix, the dialog text matched the `ValueError` raised by
`MainWindow._assert_project_json_path()` in `src/staadprep/ui/main_window.py`.
`save_current_project()` opened `QFileDialog.getSaveFileName()`; after the user chose a file, the
first-save branch called that guard, restricting the target to `ProjectPaths.projects`. The chooser
could return an external path; the application rejected it after selection and before
`save_project_atomic()` was called. Saving an already-open external JSON worked because
`open_project_json()` associated its resolved path and regular Save used
`resolve_user_selected_path()` instead. No Save As action existed.

The fix bypasses/removes only this user-selected Project JSON containment guard. Do not weaken
`ProjectPaths.assert_inside_project()` or redirect/churn the paths used for automatic runtime data.

## Read-only source inventory before the fix (2026-09-12)

- `Open Project JSON`, `Import SketchUp Bridge JSON`, and `Import DXF` each use an open-file dialog;
  the starting folder is only a default and `resolve_user_selected_path()` does not restrict their
  selected path.
- `Export STD` uses a save-file dialog and `export_current_std()` accepts any explicitly selected
  path. Its validation/audit JSON is automatically written beside the selected `.STD` file.
- Before implementation, `Save Project JSON` was the only explicit save-file dialog. On first save, it called
  `_assert_project_json_path()` and rejected destinations outside `ProjectPaths.projects`. After a
  Project JSON has been opened, Save writes atomically back to that selected path.
- No other `QFileDialog` save destinations were found in the desktop UI source. Runtime logs,
  caches, temp files, portable `Data/`, and internal build artifacts are not user-selected exports.

## Proposed expected behavior

- A new/imported model's first Project JSON Save may target any folder explicitly chosen in the
  Save dialog; the `.staadprep.json` extension and atomic write behavior remain.
- Save on an already-open Project JSON writes back to its current associated file. A distinct
  **Save As** command should open a chooser to switch the associated file to any selected folder.
- Export STD remains user-selected; its validation report stays co-located with the `.STD` file.
- Import file dialogs continue accepting files in any folder.
- Cancel leaves the model dirty and does not create or replace a file; failures preserve the old
  target file and display an actionable error.

## Implementation result (2026-09-13)

- First Save and Save As now pass explicitly chosen targets through
  `ProjectPaths.resolve_user_selected_path()` and continue writing via `save_project_atomic()`.
- Added **Save As…** next to **Save Project JSON** in the main toolbar. It starts in the currently
  associated file's folder, or the normal Projects default for a new model.
- The application associates the new path and marks the current revision saved only after the atomic
  write succeeds. Cancel and save errors leave path association and dirty state unchanged.
- Runtime path containment and the `.STD`/validation-report co-location contract are unchanged.
- Relevant regression: **58/58 UI/unit tests PASS**, Ruff PASS, strict mypy **0 issues** in
  `main_window.py`, `git diff --check` PASS. The owner reports the Save flow works in the app on
  2026-09-13 (individual cases not itemized); no compile/package build was run.

## Risk gate and approval state

This scope changes where existing user files can be overwritten. The owner explicitly approved
STRICT / Full TDD on 2026-09-12 after the risk and proposed verification were explained. The owner
requested a refreshed plan on 2026-09-13 and explicitly approved that plan before implementation
started. The owner reports the uncompiled Save flow works on 2026-09-13. Any compile/package task
still requires separate explicit authorization.
