# T24 Quarantine Manifest

Status: **T24 COMPLETE — moved, scanned, verified, and documented**
Prepared: 2026-09-01
Worktree: `task/22-portable-packaging`
Policy: recoverable move only; T24 never deletes files.

## Review gate

This manifest was reviewed and approved by the user before the filesystem move in T24 Step 4. The
source path no longer exists in `dist/`; the complete item is now under the target path below. No
`.tmp/`, `.cache/`, `.logs/`, source, test, build-input, runtime-data, or
acceptance-evidence path is included because those paths remain regenerable-but-unreviewed,
ambiguous, live, or protected.

## Proposed move set

| # | Original path | Proposed quarantine path | Classification | Contents at review time | Evidence / reason |
|---:|---|---|---|---:|---|
| 1 | `dist/post-t22-editing-final/` | `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` | `SUPERSEDED` | 814 files; 933,569,500 bytes | historical editing-correction folder/ZIP; later consolidated `dist/post-t22-refresh-save-final/` is the accepted package and contains the later accepted follow-ups |

Move result: **completed 2026-09-01**. The source path is absent, the target path exists, and a
post-move count reports 814 files and 933,569,500 bytes. The current accepted release
`dist/post-t22-refresh-save-final/` remains present. The target contains the original folder and ZIP
without deletion or overwrite.

The proposed move preserves the complete original directory as one recoverable unit, including:

- `STAAD_Model_Preprocessor_0.1.0_win64_portable/` (the historical portable folder); and
- `STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` (the historical ZIP).

## Why this item is eligible

- It is not the current accepted release. The accepted release remains
  `dist/post-t22-refresh-save-final/`.
- The current source, tests, build scripts, runtime paths, and package assembly do not use this
  historical release directory as an input.
- Current documentation references it for historical traceability only. After approval and the
  move, those historical references must point to the quarantine path or be explicitly labeled as
  archived, so no live documentation link remains broken.
- The earlier UX-only package is described in documentation as already archived, but its physical
  archive is absent from this worktree and is **not** included in this manifest.

## Restore instruction

From the active worktree, restore the item with:

```powershell
New-Item -ItemType Directory -Force -Path 'dist' | Out-Null
Move-Item -LiteralPath 'DEL/t24-quarantine-20260901/dist/post-t22-editing-final' -Destination 'dist/post-t22-editing-final'
```

If the destination already exists, stop and compare it before restoring; do not overwrite either
copy. The source and target are both project-local.

## Post-move obligations

After an approved move, T24 Step 4 was followed by:

1. historical documentation links were updated from the old path to the quarantine path;
2. the reference scan found no live source/test/script/config path pointing to the moved original;
3. verify the current accepted package remains present and unchanged;
4. affected documentation/reference checks and `git diff --check` were run; and
5. this manifest was updated with the observed post-move counts and verification result.

## Explicit exclusions

The following are not proposed for this move:

- `dist/post-t22-refresh-save-final/` — current accepted release;
- `build/windows/final/` and `build/sketchup/` — current build and RBZ evidence/input;
- `src/`, `tests/`, `scripts/`, `native/`, `extensions/`, `packaging/`, `vendor/`, `.venv/` —
  protected development/build boundaries;
- `artifacts/` — development inbox/project data and acceptance evidence pending child-level review;
- `.tmp/`, `.cache/`, `.logs/` — large or potentially active regenerable output requiring separate
  exact review;
- `DEL/` itself — quarantine root and restore metadata.

## Approval state

**User approved the exact move set. T24 Steps 4–5 are complete.** No files were deleted. The
post-move scan found no live reference to the old package path. T24 Step 6 targeted verification is
also complete: the current accepted package suite passed 7/7, `git diff --check` passed, and the
quarantine/current-release counts remained intact. Full source lint/type/build reruns were not
required because the move set changed only generated historical package location and documentation;
no source, test, or build input was modified. T24 Step 7 final documentation synchronization is
complete and the checkpoint commit records this manifest.
