# Project Storage Audit Manifest

Status: **T25/T26 STORAGE AUDIT — APPROVED MOVES COMPLETE; NO DELETION**
Prepared: 2026-09-01
Worktree: `task/22-portable-packaging`
Policy: move-only, recoverable quarantine; final deletion remains user-controlled.

## Scope

The previous T24 manifest and quarantine contents were deleted by the user before this audit. This
manifest is the recreated record for the six exact paths approved for the T25 storage audit. The
T25 quarantine contents were subsequently removed by the user; the T25 paths below are historical
move evidence and are not currently present on disk.

## Move result

At the time of the T25 operation, all six approved sources existed, all six destinations were absent,
and all six moves completed with no overwrite on 2026-09-01. The user later removed that T25
quarantine; no T25 archive content is currently present.

| # | Original path | Quarantine path | Classification | Contents at move time |
|---:|---|---|---|---:|
| 1 | `artifacts/t22/pre-path-guidance-release/` | `DEL/t25-storage-audit-20260901/artifacts/t22/pre-path-guidance-release/` | SUPERSEDED package | 813 files; 933,164,365 bytes |
| 2 | `build/windows/pre-portable-root-fix/` | `DEL/t25-storage-audit-20260901/build/windows/pre-portable-root-fix/` | SUPERSEDED build attempt | 5,509 files; 2,263,902,708 bytes |
| 3 | `build/windows/failed-final-before-current/` | `DEL/t25-storage-audit-20260901/build/windows/failed-final-before-current/` | FAILED build attempt | 2 files; 2,911,558 bytes |
| 4 | `build/windows/failed-network-download/` | `DEL/t25-storage-audit-20260901/build/windows/failed-network-download/` | FAILED build attempt | 2 files; 2,912,277 bytes |
| 5 | `build/windows/retry1/` | `DEL/t25-storage-audit-20260901/build/windows/retry1/` | RETRY build attempt | 2 files; 2,911,257 bytes |
| 6 | `build/windows/failed-interactive-prompt/` | `DEL/t25-storage-audit-20260901/build/windows/failed-interactive-prompt/` | FAILED build attempt | 1 file; 1 byte |

## Protected current paths

- `dist/post-t22-refresh-save-final/` — current accepted portable package; retained.
- `build/windows/final/` — current Nuitka build input/evidence; retained.
- `build/sketchup/` — current RBZ source/stage/archive; retained.
- `src/`, `tests/`, `scripts/`, `extensions/`, `native/`, `packaging/`, `vendor/` — retained.
- `.venv/`, `.worktrees/`, `.git/` — retained.
- `.tmp/`, `.cache/`, `.logs/`, `artifacts/projects/`, `artifacts/sketchup_bridge/` — generated or
  evidence paths; T26 moved their generated contents to the T26 quarantine, while `.tmp/.gitkeep`
  and empty pytest skeletons remain.

## Verification and restore

Post-move checks confirmed each original path is absent, each quarantine path exists, the current
release remains present, and no live source/test/script/config reference points to an original path.

Current-release integrity after the move:

| Artifact | SHA-256 |
|---|---|
| current portable ZIP | `0EF7933499179284B7FC01B011876BF196F7471D4F8CA5B7B12F46E36059E314` |
| current executable | `1C7BB68D12BEFA8A1DBDC5A8A18B031A1E19AEFCFB91C7567441E79DB88F4470` |
| current RBZ build input | `ECC8CB4A7E0434A6B937473A5E1D0D1DAB8F129BDF285959CC483B752CD1EE91` |

Restore one item only after checking that its original destination does not exist and comparing the
quarantined contents:

```powershell
Move-Item -LiteralPath 'DEL/t25-storage-audit-20260901/artifacts/t22/pre-path-guidance-release' -Destination 'artifacts/t22/pre-path-guidance-release'
Move-Item -LiteralPath 'DEL/t25-storage-audit-20260901/build/windows/pre-portable-root-fix' -Destination 'build/windows/pre-portable-root-fix'
Move-Item -LiteralPath 'DEL/t25-storage-audit-20260901/build/windows/failed-final-before-current' -Destination 'build/windows/failed-final-before-current'
Move-Item -LiteralPath 'DEL/t25-storage-audit-20260901/build/windows/failed-network-download' -Destination 'build/windows/failed-network-download'
Move-Item -LiteralPath 'DEL/t25-storage-audit-20260901/build/windows/retry1' -Destination 'build/windows/retry1'
Move-Item -LiteralPath 'DEL/t25-storage-audit-20260901/build/windows/failed-interactive-prompt' -Destination 'build/windows/failed-interactive-prompt'
```

Moving to `DEL/` does not reduce used disk space on the same drive. The user may delete the
quarantined paths separately after review. This agent does not delete them as part of this audit.

## T26 space-cleanup move

On 2026-09-01 the user approved moving regenerable output and historical worktrees into a
project-local quarantine instead of deleting them. Nothing was deleted:

| Group | Quarantine path | Contents moved |
|---|---|---:|
| Generated temporary output | `DEL/t26-storage-cleanup-20260901/generated-tmp/` | 68,900 files; 58,120,618,730 bytes |
| Generated cache output | `DEL/t26-storage-cleanup-20260901/generated-cache/` | 10,211 files; 506,361,099 bytes |
| Old Git worktrees | `DEL/t26-storage-cleanup-20260901/old-worktrees/` | 22 clean worktrees; 67,375 files; 5,706,009,647 bytes |

The only active worktree remaining is `task-22-portable-packaging`. Git worktree metadata was updated
for all moved historical worktrees; their branch refs remain available. The source `.tmp/` retains
`.gitkeep` plus an empty `pytest/` directory, and source `.cache/` retains an empty `pytest/` directory.
The current portable package, current RBZ, source, tests, build final, and documentation were not moved.

Post-cleanup standalone verification: `tests/integration/test_packaged_paths.py::test_final_package_launches_without_python_from_different_cwd`
passed **1/1 in 6.54 seconds** after the T26 moves. The test used the current portable package, a
different temporary CWD, and a sanitized PATH without Python. Its generated basetemp and pytest
cache were moved into `DEL/t26-storage-cleanup-20260901/post-move-standalone-test/` afterward.

## T27 old-release archive

On 2026-09-06 the previous accepted release/build inputs were moved before the new path-selection
package was created:

| Old item | Quarantine path |
|---|---|
| Previous accepted portable folder/ZIP | `DEL/t27-free-path-selection-20260906/old-release/dist/post-t22-refresh-save-final/` |
| Previous Nuitka final build/evidence | `DEL/t27-free-path-selection-20260906/old-release/build/windows/final/` |
| Previous SketchUp RBZ build/stage | `DEL/t27-free-path-selection-20260906/old-release/build/sketchup/` |
| First T27 assembly before documentation sync | `DEL/t27-free-path-selection-20260906/pre-doc-sync-package/` |
| T27 source/package test output | `DEL/t27-free-path-selection-20260906/test-output/` |

These are recoverable historical artifacts and were not deleted. The current release is under
`dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/`; the current RBZ is under
`build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz`.
