# STAAD Model Preprocessor

A Windows desktop tool for preparing and editing analytical line geometry before it is opened in
STAAD.Pro. It imports geometry from the SketchUp STAAD Prep Bridge or DXF, helps inspect and repair
the Node/Member model, validates readiness, and exports a STAAD `.STD` model.

> **Current status (2026-09-13):** source and version-matched `0.2.0` Windows portable / SketchUp
> RBZ artifacts have been built. The package verification gates pass **9/9**, including a
> no-Python launch smoke after cleanup. The owner has not yet reported manual testing of this exact
> `0.2.0` standalone build, so treat it as a verified candidate—not a publicly accepted release.
> No GitHub release has been published.

## What it does

- Import Neutral JSON exported by the SketchUp extension, or import DXF line geometry.
- Inspect Nodes and Members in a 3D viewport and Project Explorer; create, move, split, merge, or
  remove analytical entities with undo/redo support.
- Validate model geometry/connectivity, inspect issues, and apply supported single or batched fixes.
- Save and open Project JSON in user-selected locations; use **Save As** to change the destination.
- Export a STAAD `.STD` file to a user-selected location. A matching validation report is written
  beside the selected `.STD` file.
- Package as a no-install Windows x64 standalone folder and ZIP, with the optional SketchUp `.rbz`
  extension included in the portable package.

This is a geometry-preparation tool. It does **not** perform structural analysis, load calculations,
member design, or design-code compliance checks. Review and verify the exported model in STAAD.Pro
before engineering use.

## Workflow

```text
SketchUp STAAD Prep Bridge JSON ─┐
                                ├─> Import -> Inspect/Repair -> Validate -> Export .STD -> STAAD.Pro
DXF line geometry ──────────────┘
```

The SketchUp bridge transfers visible edge geometry only. It does not read arbitrary SketchUp solid
geometry as structural members. Direct `.skp` reading through the optional native SDK scaffold is
not enabled in this V1 workflow.

## Run from source (Windows)

Requirements: 64-bit Windows, Python **3.12 or newer**, and Git. The compiled Windows package does
not require Python on the target machine.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\run_dev.ps1
```

Alternatively, after installing the editable package, launch with:

```powershell
.\.venv\Scripts\python.exe -m staadprep.app
```

Development runtime data, temporary files, caches, and build outputs are kept under project-local
directories as configured by the application and scripts.

## Verify changes

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check src tests
```

For a focused strict type check of the main UI entry point:

```powershell
.\.venv\Scripts\mypy.exe --strict src/staadprep/ui/main_window.py
```

Some UI/VTK checks require a real Windows display/OpenGL context; an offscreen renderer failure is
not equivalent to a model-validation failure. See the handoff for the exact verification evidence
and remaining manual checks.

## Build packages (Windows)

The portable build uses Nuitka standalone mode; it is a folder-based standalone package, **not a
single-file `.exe`**. Build the matching SketchUp extension and Windows executable, then assemble the
portable folder/ZIP with the repository scripts:

```powershell
.\.venv\Scripts\python.exe scripts/build_sketchup_rbz.py
.\scripts\build_windows.ps1 -Python .\.venv\Scripts\python.exe
.\.venv\Scripts\python.exe scripts/assemble_portable.py `
  --standalone-dir build/windows/final/app.dist `
  --rbz build/sketchup/STAAD_Prep_Bridge_0.2.0.rbz `
  --dist-root dist
```

The current scripts derive the version from `src/staadprep/version.py`; check the generated
filename/version before distributing a future build. `build/` and `dist/` outputs are ignored by
Git. Do not commit the large portable binaries to the source repository by default; if desired,
publish a separately reviewed archive through GitHub Releases after owner acceptance.

## Install the SketchUp extension

The portable package contains `SketchUp_Extension/STAAD_Prep_Bridge_0.2.0.rbz`. Install it in
SketchUp through **Extension Manager → Install Extension**. The bridge window lets you choose an
inbox folder; the portable `Data/Inbox/SketchUp/` is only the initial default. See
[`packaging/INSTALL_RBZ.md`](packaging/INSTALL_RBZ.md) for details.

## Data and updates

The portable app keeps application-managed state under `Data/` next to the executable. Files the
user explicitly opens or saves may be outside the portable folder. External Project JSON files are
not automatically copied or backed up when replacing a portable app; keep your own backups. The
manual update procedure is in [`packaging/UPDATE_MANUAL.md`](packaging/UPDATE_MANUAL.md), and the
portable runtime notes are in [`packaging/README_PORTABLE.md`](packaging/README_PORTABLE.md).

## Project documentation

- [Project index and current status](docs/INDEX.md)
- [Current handoff and exact release evidence](docs/HANDOFF.md)
- [Task board](docs/TASK_BOARD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Workflow](docs/WORKFLOW.md)
- [Risk and approval gates](docs/RISK_GATES.md)
- [Worktree/file relationship mindmap](docs/WORKTREE_MINDMAP.md)
- [Recoverable storage-move manifest](DEL/UNUSED_FILES_MANIFEST.md)

## License

No `LICENSE` file is currently included. The repository owner must choose and add a license before
others are granted permission to reuse or redistribute the project. Do not assume that public
visibility on GitHub makes the code open source.
