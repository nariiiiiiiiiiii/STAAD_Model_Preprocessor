# Free User-Selected Import and STD Export Paths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Allow explicit user-selected SketchUp input/output directories and STD export destinations without weakening project-local runtime path controls.

**Architecture:** Add a resolver dedicated to paths deliberately selected by the user. Keep `assert_inside_project()` for application-managed output. Make the Python neutral reader accept a selected file from any location, make MainWindow use the new resolver for STD export, and remove the Ruby suffix-only inbox allow-list while preserving the default path and preference.

**Tech Stack:** Python 3.14, PySide6, pytest/pytest-qt, Ruff, mypy, SketchUp Ruby API, Nuitka standalone packaging.

**Spec:** `docs/superpowers/specs/2026-09-06-free-user-selected-paths-spec.md`

## Global Constraints

- Preserve default project/portable paths and application-managed cache, log, temp, and report routing.
- Keep Project JSON Save/Open under the existing `Projects` contract.
- Do not change geometry, topology, validation, ReadyGate, numbering, or `.STD` serialization.
- Run source tests and checks before compiling; compile/package only after source verification.
- Move the previous accepted package and RBZ into project-local `DEL/`; do not delete them.

---

### Task 1: Explicit user-selected path resolver

**Files:** `src/staadprep/paths.py`, `tests/unit/test_paths.py`

- [x] Add `ProjectPaths.resolve_user_selected_path(path: Path) -> Path` and a regression proving a
  path outside the project resolves successfully.
- [x] Run `tests/unit/test_paths.py` and retain the existing project-boundary rejection tests.

### Task 2: External SketchUp Bridge JSON import

**Files:** `src/staadprep/importers/neutral_reader.py`, `tests/unit/test_neutral_reader.py`,
`tests/ui/test_import_routes.py`

- [x] Change only the selected-file containment rule; retain inbox as the default dialog location
  and retain all protocol/schema validation.
- [x] Add a valid external JSON regression and run the neutral-reader/import-route tests.

### Task 3: External STD export

**Files:** `src/staadprep/ui/main_window.py`, `tests/ui/test_export_ui.py`

- [x] Use the explicit resolver only in `export_current_std()`.
- [x] Add a regression proving external `.std` and sibling `.validation.json` are written.
- [x] Run export and validation-report regressions; leave Project JSON restrictions unchanged.

### Task 4: Arbitrary SketchUp RBZ output folder

**Files:** `extensions/sketchup_staadprep/staadprep/exporter.rb`,
`tests/unit/test_sketchup_ruby_contract.py`

- [x] Replace the suffix-only directory allow-list with `File.directory?` on the selected directory.
- [x] Run the Ruby contract test and preserve the atomic writer/protocol contract.

### Task 5: Source verification, package rebuild, and archival

**Files:** affected source/tests and current status documents.

- [x] Run focused source tests, Ruff, strict mypy, and `git diff --check`.
- [x] Update the current handoff/task/index documents with the new path scope.
- [x] Move the old accepted portable package and old RBZ to dated `DEL/` quarantine.
- [x] Compile/assemble the new standalone package and updated RBZ, then run package verification.
- [x] Record hashes and final package paths; do not delete the archived release.
