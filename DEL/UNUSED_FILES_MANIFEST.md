# Project Storage Audit Manifest

Status: **T25 STORAGE AUDIT — APPROVED MOVES COMPLETE; NO DELETION**
Prepared: 2026-09-01
Worktree: `task/22-portable-packaging`
Policy: move-only, recoverable quarantine; final deletion remains user-controlled.

## Scope

The previous T24 manifest and quarantine contents were deleted by the user before this audit. This
manifest is the recreated current record for the six exact paths approved for the T25 storage audit.
No source, test, current package, current RBZ, `.tmp/`, `.cache/`, or `.venv/` path was moved.

## Move result

All six approved sources existed, all six destinations were absent, and all six moves completed with
no overwrite on 2026-09-01.

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
- `.tmp/`, `.cache/`, `.logs/`, `artifacts/projects/`, `artifacts/sketchup_bridge/` — not part of
  this move; separately review before any space-reclamation deletion.

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
