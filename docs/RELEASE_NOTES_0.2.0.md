# STAAD Model Preprocessor 0.2.0 — Pre-release

Status: **owner-tested pre-release**. The owner reported on 2026-09-13 that this exact `0.2.0`
executable works well; no stable-release approval has been given.

Repository source/license changes are proposed in [PR #1](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/pull/1);
the PR is open and the default branch has not been changed.

## Download and run

Download the [portable ZIP asset](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/download/v0.2.0/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip)
from the repository's [v0.2.0 pre-release page](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/tag/v0.2.0). This is a folder-based
standalone package, not a single-file executable: extract the ZIP as a whole, keep its `Data/`
directory beside the executable, then run `STAAD Model Preprocessor.exe`. Do not upload or distribute
the extracted folder as a separate repository artifact; the ZIP is the application download.

## Verification

- Nuitka standalone build; Windows file/product version `0.2.0.0`.
- Package verification: **9/9 PASS** (manifest/hash, RBZ archive, path/relocation, and packaged
  workflow checks).
- No-Python/different-working-directory launch after cleanup: **1/1 PASS**.
- Owner manual testing of this exact compiled executable has not yet been reported.

Portable ZIP: `STAAD_Model_Preprocessor_0.2.0_win64_portable.zip`<br>
SHA-256: `635AF835CE71C211E6FE184EBE05656187E0C4C36D2FA8BC542679802C7B15A7`

## Included application changes

- User-selectable Project JSON Open, First Save, and Save As destinations.
- User-selectable SketchUp JSON/DXF import and STAAD `.STD` export paths.
- SketchUp bridge export naming based on the SketchUp model name and date.
- Updated application branding and Windows taskbar identity.
- Crop to Select marquee, Zoom in Select, and multi-issue Quick Fix/intersection routing.

## Scope and limitations

The application prepares analytical line geometry and exports `.STD`; it does not run structural
analysis, member design, load calculations, or design-code compliance checks. Verify models in
STAAD.Pro before engineering use. The optional SketchUp extension is included as an `.rbz` file
inside the portable package.
