# User-Selected Save Destinations — Behavior Specification

## User request

Allow Project JSON and every user-facing export/save action to use a user-selected destination
outside the project. Import dialogs should remain unrestricted. The reported **Save Blocked** dialog
currently rejects a Project JSON path outside `Data/Projects/`.

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

## Risk gate

This scope changes where existing user files can be overwritten. The owner explicitly approved
STRICT / Full TDD on 2026-09-12 after the risk and proposed verification were explained.
Implementation is queued until the current viewport checkpoint has been reviewed, following the
project's one-task-at-a-time rule.
