# Project Storage Audit Manifest

Status: **T28/T29 STORAGE AUDITS — VERIFIED SUPERSEDED/UNUSED OUTPUTS MOVED; NO DELETION**
Original manifest prepared: 2026-09-01; updated: 2026-09-13
Worktree: `task/22-portable-packaging`
Policy: move-only, recoverable quarantine; final deletion remains user-controlled.

Current candidate: `dist/STAAD_Model_Preprocessor_0.2.0_win64_portable/` and its ZIP. Package gates
pass 9/9; the owner has not yet reported manual acceptance of this exact compiled build. The active
candidate, build evidence, source, tests, current project data, and required runtime/vendor files are
not in the quarantine.

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

These are recoverable historical artifacts and were not deleted. At the T27 checkpoint, the
then-current release was `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/` and the then-current
RBZ was `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz`. The T28 section below records the 0.2.0
candidate and later move.

## T28 post-compile storage audit and GitHub preparation

On 2026-09-13, after the owner authorized the compile/cleanup sequence and the 0.2.0 package gates
passed, the following superseded packages and clearly regenerable outputs were moved into the dated
quarantine. All moves stayed within the active project/worktree storage on the same volume. No files
were deleted. Package files below are summarized by folder inventory plus their package manifest;
standalone files (ZIP/RBZ) have direct SHA-256 values.

| Original relative path/group | Quarantine path under `DEL/post-compile-cleanup-20260913/` | Classification and verification at move |
|---|---|---|
| `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/` | `old-release/dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/` | Superseded package; 812 files / 708,474,179 bytes; manifest's 811 managed files matched |
| `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` | `old-release/dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` | Superseded archive; 225,277,088 bytes; SHA-256 `7A163315FD01E42A98D63F6728AB7DCFCA0FF6C05549B91ECBE2396C789A4E11` |
| `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz` | `old-release/build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz` | Superseded RBZ; 4,008 bytes; SHA-256 `C67349CBE3CB0315926FB69606287835AF981245344DDD48ED5B3FB9D4306701` |
| Pre-documentation-sync `dist/STAAD_Model_Preprocessor_0.2.0_win64_portable/` | `pre-doc-sync-package/dist/STAAD_Model_Preprocessor_0.2.0_win64_portable/` | Superseded candidate with stale portable README; 813 files / 709,570,973 bytes |
| Pre-documentation-sync `dist/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip` | `pre-doc-sync-package/dist/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip` | Superseded candidate archive; 226,243,451 bytes; SHA-256 `A18729D4FE92D34800FC0294D3B13A969B112E2E2CE0E23F871FB36BF14D9D15` |
| `build/windows/icon-checkpoint-20260912/` | `old-build-evidence/build/windows/icon-checkpoint-20260912/` | Intermediate icon-conversion checkpoint superseded by the final 0.2.0 build; 1 file / 79,047 bytes |
| Generated pytest/test copies from canonical and active worktree `.tmp/`, including the fresh final package-gate run | `generated-tests/` | Regenerable test output; 15,855 files / 12,781,504,680 bytes |
| Generated `.cache/` trees from canonical and active worktree | `generated-cache/` | Regenerable pytest/mypy/Nuitka/Ruff cache data; 5,520 files / 460,492,001 bytes |
| Eight historical T22 build logs | `old-build-logs/active-worktree/.logs/` | Superseded logs; 8 files / 53,625 bytes |
| Six one-off documentation helper scripts from the canonical checkout `.tmp/` | `temporary-helpers/canonical-checkout/tmp/` | Regenerable temporary helpers; 6 files / 35,683 bytes |

T28 quarantine payload total: **23,018 files / 15,111,734,735 bytes**. The manifest file is outside
that payload under `DEL/`. Moving to `DEL/` on the same volume does not reduce disk usage; the owner
may delete the quarantine separately after review.

### Retained current paths and reference check

| Path/group | Current snapshot | Disposition |
|---|---:|---|
| `build/` | 5,527 files / 2,272,332,867 bytes | KEEP — current 0.2.0 Nuitka/RBZ and reproducibility evidence |
| `dist/` | 814 files / 935,814,890 bytes | KEEP — 0.2.0 candidate folder (813 files / 709,571,303 bytes) and ZIP (226,243,587 bytes) |
| `artifacts/` | 6 files / 156,182 bytes | KEEP — active user project/import data and reports |
| Active worktree `.tmp/` | `.gitkeep` plus `nuitka/` and `pytest/` directories; recursive access to `pytest/` was denied | KEEP — configured test/temp root; unreadable paths were left untouched |
| Active worktree `.cache/` | 4 files / 1,527 bytes | KEEP — small active checkout cache; not worth moving |
| Separate canonical `master` checkout `.cache/` | 1,235 files / 33,560,418 bytes; `.cache/pytest/` access denied | KEEP — separate checkout cache left untouched |
| `.logs/` | empty at snapshot | KEEP — configured project-local log root |
| `.worktrees/` | active `task-22-portable-packaging` worktree | KEEP — active Git worktree |
| `src/`, `tests/`, `scripts/`, `extensions/`, `native/`, `assets/`, `packaging/`, `vendor/`, `.venv/` | source, tests, current packaging/runtime inputs | KEEP — required for development, reproduction, or project scope |

The pre-move search found no live source/test/script/config dependency on the old 0.1.0 release
paths or the pre-documentation-sync candidate path. Dated tracked documentation may reference those
paths as historical evidence. Post-move checks confirm the obsolete source paths are absent, the
quarantine destinations exist, and the 0.2.0 active candidate remains present. A post-move
no-Python/different-CWD package launch passed **1/1**. The earlier 0.1.0 and pre-doc-sync 0.2.0
package copies are deliberately not edited; they remain recoverable snapshots.

### Current 0.2.0 candidate checksums

| Artifact | SHA-256 |
|---|---|
| executable | `A616C8286DD63C718D821132B37C4C24F82AA2FB75E15BB46A4FC60E004174A2` |
| RBZ | `655238B3EA983C2A3C76A66BA8C9D44FE030F68BE49A9D8B950CC5CD70234D06` |
| portable ZIP | `635AF835CE71C211E6FE184EBE05656187E0C4C36D2FA8BC542679802C7B15A7` |

The local, ignored detailed inventory is `artifacts/cleanup/post-compile-storage-audit.md`. T28 was
local-only; T29's full project recheck is recorded below.

## T29 whole-project recheck — 2026-09-13

The owner requested a fresh audit across the canonical checkout and active T22 worktree before
publishing. The canonical `master` checkout has no standalone/build files in its `build/` or `dist/`
folders; its `tools/` and `vendor/` folders are empty, and its `artifacts/sketchup_bridge/inbox/`
is a configured runtime location that was kept. The active worktree's source/tests and current 0.2.0
build/package remain in place.

Three unselected logo draft images in the owner-supplied root `LOGO/` folder had no live source,
test, script, or documentation references. The selected image `06_17_26 PM.png` was retained because
it is the approved source asset; its SHA-256 matches the tracked
`assets/branding/staad-model-preprocessor.png` byte-for-byte. The unused alternatives were moved
recoverably (not deleted):

| Original path | Quarantine path | Classification | Size / SHA-256 |
|---|---|---|---|
| `LOGO/ChatGPT Image Sep 12, 2026, 05_44_55 PM.png` | `DEL/project-wide-audit-20260913/owner-logo-alternatives/LOGO/ChatGPT Image Sep 12, 2026, 05_44_55 PM.png` | Superseded logo draft; no live references | 1,531,613 bytes / `B4A15E4B96FF52C7475443788758A7A987B2B108D2DDAB9AD1FC4E628EC69A35` |
| `LOGO/ChatGPT Image Sep 12, 2026, 06_12_39 PM.png` | `DEL/project-wide-audit-20260913/owner-logo-alternatives/LOGO/ChatGPT Image Sep 12, 2026, 06_12_39 PM.png` | Superseded logo draft; no live references | 690,290 bytes / `EF8C6B43E37B87E3D84D0A0CCBE18BA4B59DFAB1D327F9C6B9DCFF683E9D5322` |
| `LOGO/ChatGPT Image Sep 12, 2026, 06_15_26 PM.png` | `DEL/project-wide-audit-20260913/owner-logo-alternatives/LOGO/ChatGPT Image Sep 12, 2026, 06_15_26 PM.png` | Superseded logo draft; no live references | 1,157,979 bytes / `CB0050D648ACE315F9252A9506E0493379607DCB737239E1273E7E65C39E5313` |
| `.tmp/project-wide-audit-tests-20260913/` | `DEL/project-wide-audit-20260913/generated-tests/active-worktree/tmp/project-wide-audit-tests-20260913/` | Generated temporary output from focused 5-test package/RBZ verification | 29 files / 55,453 bytes |

Post-move verification: all three logo sources are absent; all logo and test-temp destinations exist
with the recorded lengths/hashes. The selected `06_17_26 PM.png` remains in `LOGO/`, and its hash
equals the tracked active branding asset. The focused package/RBZ suite passed **5/5**; its temp
output was archived after the test. T29 added **32 files / 3,435,335 bytes**. Combined `DEL/`
payload excluding this tracked manifest is **23,050 files / 15,115,170,070 bytes**. These are
same-volume moves, so no storage is released until the owner deletes the quarantine.

The unreadable active `.tmp/pytest/` and canonical `.cache/pytest/` paths, plus the canonical
checkout's 33,560,418-byte cache, remain untouched: Windows returned access denied and Python
processes were present. No process was terminated, no ACL changed, and no uncertain cache/temp path
was moved. The detailed full-root inventory is in the ignored local report
`artifacts/cleanup/project-wide-storage-audit-20260913.md`.
