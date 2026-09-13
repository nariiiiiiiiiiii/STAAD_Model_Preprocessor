# STAAD Model Preprocessor

A Windows desktop tool for preparing and editing analytical line geometry before it is opened in
STAAD.Pro. It imports geometry from the SketchUp STAAD Prep Bridge or DXF, helps inspect and repair
the Node/Member model, validates readiness, and exports a STAAD `.STD` model.

> **Current status (2026-09-13):** source and version-matched `0.2.0` Windows portable / SketchUp
> RBZ artifacts have been built. The package verification gates pass **9/9**, including a
> no-Python launch smoke after cleanup. The owner tested this exact `0.2.0` standalone on
> 2026-09-13 and reports that it works well. It remains a pre-release candidate; no stable-release
> approval has been given. [PR #1](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/pull/1)
> records the project tree and license update proposed for `main`. The
> [portable ZIP is available for download](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/download/v0.2.0/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip);
> it is the only application asset uploaded, not the extracted folder or standalone EXE. This
> existing ZIP predates the license update and has not been rebuilt or replaced. See the
> [v0.2.0 pre-release notes](docs/RELEASE_NOTES_0.2.0.md) and [release page](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/tag/v0.2.0).

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
Git. For this 0.2.0 candidate, offer only the ZIP as a GitHub pre-release download so the owner can
test it; do not commit the ZIP or extracted folder into normal Git history. Mark later stable releases
only after owner acceptance.

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
- [0.2.0 pre-release notes](docs/RELEASE_NOTES_0.2.0.md)
- [Recoverable storage-move manifest](DEL/UNUSED_FILES_MANIFEST.md)

## License

License: PolyForm Noncommercial 1.0.0

Free for personal, educational, research, and other noncommercial use only.

Commercial use is not permitted without separate written permission from the copyright holder.
This includes work for pay, freelance or consultancy services, compensated deliverables, selling the
software, and making commercial products from it.

The official license also expressly permits use by specified organizations—including educational
institutions and public research organizations—regardless of funding sources or obligations resulting
from that funding. This exception is part of the license terms; review the **Noncommercial
Organizations** section in [`LICENSE`](LICENSE), especially if you intend to prohibit every funded or
compensated institutional use.

See [`LICENSE`](LICENSE) for the complete terms and required notice.
