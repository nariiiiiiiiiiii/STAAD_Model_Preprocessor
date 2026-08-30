# STAAD Model Preprocessor — Project Index

Last synchronized: **2026-08-30**

This file is the navigation and synchronization index for the project. It records which checkout contains the live task, where the authoritative handoff is, which artifacts exist, and which Markdown files must be updated at task checkpoints.

## Current status

| Task | Status | Authoritative location |
|---|---|---|
| T01–T21 | Complete | `master` / historical task checkpoints |
| T22 | **COMPLETE** | branch `task/22-portable-packaging`, worktree `.worktrees/task-22-portable-packaging` |
| T23 | Ready; not started | Target STAAD.Pro acceptance |
| T24 | Blocked by T23; not started | Project-local `DEL/` quarantine only |

The active T22 handoff is [`task-22-portable-packaging/docs/HANDOFF.md`](D:/Dizayn59/CLICodex/gpt_mcp_workshop/STAAD_Model_Preprocessor/.worktrees/task-22-portable-packaging/docs/HANDOFF.md). The root `master` checkout contains T21 plus the T22 plan; the active T22 implementation is isolated in the dedicated worktree.

## T22 final checkpoint

### Completed

- Portable runtime root and `Data/` path policy; packaged paths do not use launch CWD.
- Application/package/SketchUp version contract: `0.1.0`.
- Deterministic SketchUp `.rbz` builder and portable SketchUp inbox support.
- Portable assembler, manual-update contract, ZIP/manifest/hash logic.
- Source-level T21 workflow smoke: import → repair/manual path → renumber → READY → `.STD` + validation report.
- Final evidence reported in the active handoff: **307/307 unit+integration PASS**, **3/3 affected UI PASS**, **6/6 final-package gates PASS**, T22-local strict mypy **0 issues**, and Ruff passed.
- Nuitka standalone build emitted `build/windows/final/app.dist/STAAD Model Preprocessor.exe`; report completion is `yes`.
- Final folder/ZIP exist under `dist/`; sanitized-PATH/no-Python, different-CWD, spaces/Unicode relocation, existing-`Data`, freshly extracted ZIP, and packaged T21 READY/STD/report gates passed.
- `Update/package-manifest.json` independently verifies **811/811 managed files**; no forbidden installer/updater/one-file artifact exists.

### T22 commit map

| Commit | Purpose |
|---|---|
| `7d0ee2b` | Portable runtime path boundary |
| `ec04b46` | Version contract |
| `6afaea9` | SketchUp `.rbz` builder |
| `22510bc` | Portable assembler, ZIP, manifest, hashes, manual update |
| `056d906` | Portable SketchUp inbox support |
| `034456a` | T22 documentation checkpoint |
| `dcc2d6e` | Final Windows standalone package implementation and verification |

## Checkout alignment

| Checkout | Expected role | Current truth |
|---|---|---|
| `master` | Stable integrated baseline | T21 complete; T22 plan present; T22 implementation not merged here |
| `.worktrees/task-22-portable-packaging` | T22 final source/release | T22 complete; final portable folder and ZIP are generated under this worktree's `dist/` |

Do not report T22 as “not started” merely because the current shell is at `master`. Always inspect the active worktree and its handoff first.

## Project structure

```text
STAAD_Model_Preprocessor/
├─ src/staadprep/                 Application and canonical model code
├─ scripts/                       Smoke, build, bridge, and packaging tooling
├─ extensions/sketchup_staadprep/ SketchUp Ruby bridge source
├─ tests/                         Unit, integration, UI, golden, and smoke tests
├─ docs/                          Project specifications, plans, status, and this index
├─ build/                         Project-local intermediate build/RBZ/Nuitka output
├─ dist/                          Final T22 portable folder and ZIP
├─ artifacts/                     Project-local evidence and generated reports
├─ .tmp/                          Project-local temporary test files
├─ .cache/                        Project-local caches
├─ .logs/                         Project-local logs
└─ .worktrees/                    Isolated task worktrees; active T22 is below here
```

### T22 files and artifacts

Expected/implemented source files in the active T22 worktree include:

- `src/staadprep/portable_paths.py`
- `src/staadprep/version.py`
- `src/staadprep/packaged_smoke.py`
- `scripts/build_windows.ps1`
- `scripts/build_sketchup_rbz.py`
- `scripts/assemble_portable.py`
- `packaging/README_PORTABLE.md`
- `packaging/INSTALL_RBZ.md`
- `packaging/UPDATE_MANUAL.md`
- `tests/unit/test_portable_paths.py`
- `tests/unit/test_version_contract.py`
- `tests/unit/test_windows_build_contract.py`
- `tests/integration/test_rbz_package.py`
- `tests/integration/test_package_manifest.py`
- `tests/integration/test_packaged_paths.py`
- `tests/integration/test_packaged_workflow_smoke.py`

Current evidence/artifacts:

- `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz` exists.
- `build/windows/final/nuitka-report.xml` records successful standalone completion.
- `build/windows/final/app.dist/STAAD Model Preprocessor.exe` exists (159,788,032 bytes; SHA-256 `2401E9C0689CE6ACFDA0E7E7BBE6859F6848780CD79792322CCCADAC2ADB1A57`).
- `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/` exists (812 files; 708,028,512 bytes).
- `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` exists (225,136,191 bytes; SHA-256 `D31A70005D7F0B2C09B467D6A5591892868E9E56AC35874434BA38CFC4687115`).

## Documentation catalog

### Required status and navigation documents

- [`README.md`](../README.md) — user-facing product status and workflow.
- [`HANDOFF.md`](HANDOFF.md) — exact resume point, evidence, blocker, and next actions.
- [`TASK_BOARD.md`](TASK_BOARD.md) — task state and task-gating rules.
- [`CHECKLIST.md`](CHECKLIST.md) — acceptance and verification checklist.
- [`INDEX.md`](INDEX.md) — this synchronization map.

### Product and architecture documents

- [`PROJECT_SPEC.md`](PROJECT_SPEC.md) — approved V1 scope, behavior, and definition of done.
- [`PROJECT_RULES.md`](PROJECT_RULES.md) — project-local boundary and cleanup rules.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system architecture and mutation boundaries.
- [`WORKFLOW.md`](WORKFLOW.md) — user workflow, export, and post-acceptance flow.
- [`RISK_GATES.md`](RISK_GATES.md) — STANDARD/STRICT risk classification and approval gates.
- [`UI_BASELINE.md`](UI_BASELINE.md) — locked V1 UI baseline.
- [`../AGENTS.md`](../AGENTS.md) — repository execution and verification policy.

### Plans and specifications

- [`superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`](superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md) — master task plan T01–T24.
- [`superpowers/plans/2026-08-28-manual-model-editing-v1.md`](superpowers/plans/2026-08-28-manual-model-editing-v1.md) — T16–T20 implementation plan.
- [`superpowers/plans/2026-08-29-t22-portable-standalone-packaging.md`](superpowers/plans/2026-08-29-t22-portable-standalone-packaging.md) — detailed T22 plan and final checkpoint.
- [`superpowers/specs/2026-08-28-staad-model-preprocessor-design.md`](superpowers/specs/2026-08-28-staad-model-preprocessor-design.md) — approved V1 design.
- [`superpowers/specs/2026-08-28-manual-model-editing-design.md`](superpowers/specs/2026-08-28-manual-model-editing-design.md) — approved manual-editing design.
- [`superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`](superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md) — approved SketchUp Ruby bridge design.

## Source-of-truth order

When documents disagree, use this order:

1. Active worktree `docs/HANDOFF.md` for the exact current implementation state.
2. Active worktree `docs/TASK_BOARD.md` for task status and whether the next task is blocked.
3. Active worktree `docs/CHECKLIST.md` for verified acceptance evidence.
4. The detailed task plan for scope and required gates.
5. `README.md` for user-facing summary.
6. `master` documents as the integrated baseline only; they may intentionally lag an active task worktree until merge.

## Checkpoint update protocol

At every task checkpoint, update these together:

1. Active worktree `docs/HANDOFF.md`: status, branch/worktree, commits, evidence, blocker, and exact resume sequence.
2. Active worktree `docs/TASK_BOARD.md`: task row and current-task section.
3. Active worktree `docs/CHECKLIST.md`: only mark evidence that was actually verified.
4. Active task plan: add/update a dated live checkpoint and keep scope boundaries explicit.
5. `README.md`: update only user-visible behavior and tested packaging instructions.
6. `docs/INDEX.md`: synchronize cross-tree location, artifacts, commit map, and document catalog.

T22 is complete because the real `.exe`, final portable folder/ZIP, relocation/no-Python gates, manifest hashes, packaged T21 workflow, regression, lint/type checks, and documentation checkpoint are evidenced. Do not start T23 automatically.
