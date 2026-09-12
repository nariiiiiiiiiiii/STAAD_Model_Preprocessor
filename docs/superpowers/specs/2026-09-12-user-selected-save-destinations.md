# User-Selected Save Destinations — Behavior Specification

## User request

Allow Project JSON and every user-facing export/save action to use a user-selected destination
outside the project. Import dialogs should remain unrestricted. On 2026-09-13 the owner confirmed
the other tested viewport features pass, but Project JSON First Save outside the project still
shows **Save Blocked**.

## Confirmed Save Blocked cause (2026-09-13)

The dialog text matches the `ValueError` raised by `MainWindow._assert_project_json_path()` in
`src/staadprep/ui/main_window.py`. `save_current_project()` opens `QFileDialog.getSaveFileName()`;
after the user chooses a file, the first-save branch calls that guard, which restricts the target to
`ProjectPaths.projects`. Thus the chooser can return the external path; the application rejects it
after selection and before `save_project_atomic()` is called. Saving an already-open external JSON
works because `open_project_json()` associates its resolved path and the regular Save path uses
`resolve_user_selected_path()` instead. There is currently no Save As action.

The fix should bypass/remove only this user-selected Project JSON containment guard. Do not weaken
`ProjectPaths.assert_inside_project()` or redirect/churn the paths used for automatic runtime data.

## Read-only source inventory (2026-09-12)

- `Open Project JSON`, `Import SketchUp Bridge JSON`, and `Import DXF` each use an open-file dialog;
  the starting folder is only a default and `resolve_user_selected_path()` does not restrict their
  selected path.
- `Export STD` uses a save-file dialog and `export_current_std()` accepts any explicitly selected
  path. Its validation/audit JSON is automatically written beside the selected `.STD` file.
- `Save Project JSON` is the only explicit save-file dialog. On first save, it calls
  `_assert_project_json_path()` and rejects destinations outside `ProjectPaths.projects`. After a
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

## Risk gate and approval state

This scope changes where existing user files can be overwritten. The owner explicitly approved
STRICT / Full TDD on 2026-09-12 after the risk and proposed verification were explained. The owner
manually accepted the viewport checkpoint on 2026-09-13, then requested this plan/root-cause refresh
and said they would approve before work starts. Respect that latest instruction: implementation is
currently awaiting the owner's approval of the refreshed plan, despite the historical approval.
