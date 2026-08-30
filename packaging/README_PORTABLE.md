# STAAD Model Preprocessor <VERSION> — Portable Windows

This release is a no-install portable Windows x64 application.

## Start

1. Extract the ZIP into any writable folder or drive.
2. Open the extracted folder.
3. Double-click `STAAD Model Preprocessor.exe`.

Keep the extraction path reasonably short, for example `D:\STAAD_Preprocessor\`.
Some bundled Windows/VTK DLLs can hit the legacy Windows path-length limit when
the package is nested below an unusually deep folder hierarchy.

Python, pip, PySide6, VTK, and the source repository are not required on the target machine.

## Portable data

Application-managed writable state remains below `Data/` beside the executable. Keep this directory when moving or updating the application.

Important subfolders include:

- `Data/Projects/`
- `Data/Inbox/SketchUp/`
- `Data/Exports/`
- `Data/Reports/`
- `Data/Logs/`
- `Data/Cache/`
- `Data/Temp/`
- `Data/Backups/`

The extracted release must be placed in a location where the current Windows user can write files. The app intentionally does not fall back to hidden AppData or system Temp locations.

## SketchUp

The matching SketchUp extension is in `SketchUp_Extension/STAAD_Prep_Bridge_<VERSION>.rbz`. See `SketchUp_Extension/INSTALL_RBZ.md` for one-time installation instructions.

## Updates

T22 uses manual portable updates. See `Update/UPDATE_MANUAL.md`. `Update/package-manifest.json` records package version, preserved roots, and SHA-256 hashes for future update tooling.
