# STAAD Model Preprocessor — Project Index

Last synchronized: **2026-09-12**

This file is the navigation and synchronization index for the project. It records which checkout contains the live task, where the authoritative handoff is, which artifacts exist, and which Markdown files must be updated at task checkpoints.

## Current status

| Task | Status | Authoritative location |
|---|---|---|
| T01–T21 | Complete | `master` / historical task checkpoints |
| T22 | **COMPLETE** | branch `task/22-portable-packaging`, worktree `.worktrees/task-22-portable-packaging` |
| T23 | **COMPLETE / PASS** | User-tested target STAAD.Pro acceptance (2026-09-01) |
| T24 | **COMPLETE** | Project-local `DEL/` quarantine only; final deletion remains user-controlled |
| T25 | **HISTORICAL MOVE VERIFIED** | Approved old package/build attempts were moved and later removed by the user; standalone smoke 1/1 PASS |
| T26 | **MOVE + SMOKE VERIFIED** | Generated temp/cache output and 22 old clean worktrees moved to `DEL/t26-storage-cleanup-20260901/`; post-move standalone smoke 1/1 PASS; user deletion remains pending |
| T27 | **SOURCE + PACKAGE COMPLETE** | User-selected SketchUp paths and STD export destinations; source 24/24, unit+integration 336/336, package gates 9/9 |

Post-package user testing on 2026-08-30 produced a nine-item usability patch request. It is split into a SketchUp bridge checkpoint (requirements 1-2) and a desktop interaction checkpoint (requirements 3-9); no structural calculation, topology, repair, or `.STD` semantic change is included.

SketchUp bridge checkpoint status: **USER ACCEPTED** — the new HtmlDialog opened and was usable in real SketchUp and compact `SP_YYYYMMDD_HHMMSS.json` naming is packaged.

Desktop requirements 3-9 status: **VERIFIED HISTORICAL CHECKPOINT / SUPERSEDED FOR ACCEPTANCE** — Node/Member picking and highlights, context actions, Reset View, tool ordering, and active-mode styling remain implemented. Its **311/311 unit+integration**, **100/100 UI**, and package evidence are preserved, but current acceptance is consolidated under the ten-item editing-final package.

Superseded standalone artifacts are recoverably archived under `DEL/standalone-archive-20260831/` by explicit user request; the exact move/restore map is in [`DEL/UNUSED_FILES_MANIFEST.md`](../DEL/UNUSED_FILES_MANIFEST.md). This targeted archive is not the full T24 cleanup.

Ten-item editing correction status: **VERIFIED HISTORICAL PACKAGE CHECKPOINT / SUPERSEDED FOR
CURRENT ACCEPTANCE**. Reset/Crop, selection Properties, unified Delete, Merge Members, orphan
removal, Member Repeat, distinct Create Node actions, and usable Draw/Move/Delete modes are
implemented. Preserved evidence is **325/325
unit+integration PASS**, **111/111 UI PASS**, three real Windows smokes, Ruff clean, strict mypy
clean for 7 affected source files, package gates **4/4**, manifest **811/811**, and extracted-ZIP
launch exit 0. `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` is historical and lacks later accepted source
follow-ups; the earlier UX package is also superseded.

Next follow-up status: **ALL AGREED SOURCE FEATURES USER ACCEPTED / FULL SOURCE VERIFIED**. This
includes Apply/OK refresh, repeated-Orphan handling, Project Explorer selection, UUID-free
engineering Properties, Member Repeat preview, Member Local Axes, Save/Open Project JSON, and
corrected Exit confirmation. Task 7 source evidence is **332/332 source unit+integration** and
**140/140 UI**, with six real Windows source smokes, focused Save/Open **5/5**, Ruff, strict mypy,
and diff checks passing. The user authorized compile step 1 and Nuitka completed a fresh standalone
build. Portable assembly/ZIP creation are complete under `dist/post-t22-refresh-save-final/`; the
package-only verification is **7/7 PASS** and real package acceptance is **PASS** (2026-08-31).
T23 acceptance is **PASS** (user-tested 2026-09-01). T24 inventory and reference/evidence mapping
are complete; the approved pre-move manifest has been executed and no files were deleted. Evidence is recorded in
`artifacts/cleanup/t24-inventory-20260901.md` and
`artifacts/cleanup/t24-reference-map-20260901.md`; the move record is in
`DEL/UNUSED_FILES_MANIFEST.md`. The post-move reference scan and targeted affected verification are
complete; final documentation synchronization and commit are next.

The active T22 handoff is [`task-22-portable-packaging/docs/HANDOFF.md`](D:/Dizayn59/CLICodex/gpt_mcp_workshop/STAAD_Model_Preprocessor/.worktrees/task-22-portable-packaging/docs/HANDOFF.md). The root `master` checkout contains T21 plus the T22 plan; the active T22 implementation is isolated in the dedicated worktree.

Next usability follow-up: **SOURCE VERIFIED; TASKBAR LOGO OWNER-CONFIRMED; VIEWPORT MANUAL ACCEPTANCE PASS; SAVE SOURCE IMPLEMENTED / OWNER SAVE ACCEPTANCE PENDING; PACKAGE ACCEPTANCE PENDING**. CP1–CP5 implement source version `0.2.0`, owner-confirmed SketchUp JSON naming, the selected Qt/executable icon, unrestricted Project JSON Open with Save-back, and STRICT multi-issue Quick Fix/intersection routing. Evidence: **345 unit+integration PASS**, **1 RBZ archive test skipped**, **3 portable-executable gates deselected**, **26/26 affected UI PASS**, Ruff PASS, strict mypy **0 issues** for four source files, and diff check PASS. On 2026-09-12 the owner reported that the app-window and source-run taskbar icons now show the selected logo, and Quick Fix/Undo/Redo work. The source taskbar change has **10/10 focused checks PASS**. The owner reports Crop to Select / Zoom in Select work on 2026-09-13. The approved Save fix now permits external Project JSON First Save and Save As through the existing user-path resolver and atomic serializer; **58/58 relevant tests PASS**, Ruff PASS, strict mypy **0 issues**. Import dialogs and Export STD accept chosen external paths; the STD validation report stays beside the selected `.STD`. Owner manual Save acceptance remains pending. The compiled executable is still `0.1.0.0` from 2026-09-06; no `0.2.0` executable/RBZ/ZIP has been built or accepted.

Additional 2026-09-12 request, owner recheck and Save implementation on 2026-09-13: **Crop to Select / Zoom in Select is manually accepted; external Project JSON First Save/Save As source fix is implemented under STRICT approval.** The **13 non-renderer viewport tests PASS**, and **58/58 relevant Save/import/export/path UI/unit tests PASS**; Ruff and strict mypy pass. Automated real-VTK smoke remains unverified because offscreen startup reported `vtkWin32OpenGLRenderWindow: failed to get valid pixel format`, followed by a Python Application Error. The Save guard is removed only from user-selected project saves; runtime project-local guards remain. The owner reports Save works in the app on 2026-09-13; no compile/package build was run.

**Owner Save test update (2026-09-13):** The owner reports the Save flow now works in the uncompiled
app. This supersedes the “acceptance pending” wording in the earlier status snapshots above. No
compile/package authorization has been given.

## T22 final checkpoint

### Completed

- Portable runtime root and `Data/` path policy; packaged paths do not use launch CWD.
- Application/package/SketchUp version contract at this accepted T22 package checkpoint: `0.1.0` (the current source follow-up has since approved `0.2.0`; see status above).
- Deterministic SketchUp `.rbz` builder and portable SketchUp inbox support.
- Portable assembler, manual-update contract, ZIP/manifest/hash logic.
- Source-level T21 workflow smoke: import → repair/manual path → renumber → READY → `.STD` + validation report.
- Final evidence reported in the active handoff: **307/307 unit+integration PASS**, **3/3 affected UI PASS**, **6/6 final-package gates PASS**, T22-local strict mypy **0 issues**, and Ruff passed.
- Nuitka standalone build emitted `build/windows/final/app.dist/STAAD Model Preprocessor.exe`; report completion is `yes`.
- Current folder/ZIP exist under `dist/post-t22-refresh-save-final/`; package-only verification is **7/7 PASS**.
- Current ZIP SHA-256 is `0EF7933499179284B7FC01B011876BF196F7471D4F8CA5B7B12F46E36059E314`; current
  packaged executable SHA-256 is `1C7BB68D12BEFA8A1DBDC5A8A18B031A1E19AEFCFB91C7567441E79DB88F4470`.
- `Update/package-manifest.json` independently verifies **811/811 managed files**; no forbidden installer/updater/one-file artifact exists. Real package acceptance is **PASS** (2026-08-31).

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
| `e7ce6ad` | User-accepted SketchUp bridge interface and compact JSON export names |

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
- Original T22 folder/ZIP: archived under `DEL/standalone-archive-20260831/dist-root/`; baseline ZIP SHA-256 `D31A70005D7F0B2C09B467D6A5591892868E9E56AC35874434BA38CFC4687115`.
- Post-T22 desktop rebuild folder/ZIP: archived under `DEL/standalone-archive-20260831/post-t22-ux-final/`; UX ZIP SHA-256 `E1633876C102E5B77E6FD87D9B384235D25844EA6D324F01E9119963E9201AD2`.
- Editing-correction folder: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/` (812 files; 708,288,929 bytes).
- Editing-correction ZIP: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip` (225,217,293 bytes; SHA-256 `5B261CCEC2DD75D88F6DB3456548F15D714190365F5348ADD77481D3CA48E52B`).
- Editing-correction executable: 160,055,296 bytes; SHA-256 `8AE21D68F21FFDDCC7A6DEE91D41E7303ECEC090D511760D9973A082928D1D9E`.

## Documentation catalog

### Required status and navigation documents

- [`README.md`](../README.md) — user-facing product status and workflow.
- [`HANDOFF.md`](HANDOFF.md) — exact resume point, evidence, blocker, and next actions.
- [`TASK_BOARD.md`](TASK_BOARD.md) — task state and task-gating rules.
- [`CHECKLIST.md`](CHECKLIST.md) — acceptance and verification checklist.
- [`INDEX.md`](INDEX.md) — this synchronization map.

Markdown synchronization audit (2026-08-31): all **28** source Markdown files plus `DEL/UNUSED_FILES_MANIFEST.md` were inventoried. Status-bearing documents and active/superseded plan checkpoints were synchronized; immutable policy, approved baseline, historical evidence, and generic packaging manuals were reviewed and left substantively unchanged where no current-state field exists.

### Product and architecture documents

- [`PROJECT_SPEC.md`](PROJECT_SPEC.md) — approved V1 scope, behavior, and definition of done.
- [`PROJECT_RULES.md`](PROJECT_RULES.md) — project-local boundary and cleanup rules.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system architecture and mutation boundaries.
- [`WORKFLOW.md`](WORKFLOW.md) — user workflow, export, and post-acceptance flow.
- [`RISK_GATES.md`](RISK_GATES.md) — STANDARD/STRICT risk classification and approval gates.
- [`UI_BASELINE.md`](UI_BASELINE.md) — locked V1 UI baseline.
- [`../AGENTS.md`](../AGENTS.md) — repository execution and verification policy.
- [`../DEL/UNUSED_FILES_MANIFEST.md`](../DEL/UNUSED_FILES_MANIFEST.md) — recoverable archive map for user-authorized superseded standalone moves.

### Plans and specifications

- [`superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`](superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md) — master task plan T01–T24.
- [`superpowers/plans/2026-08-28-manual-model-editing-v1.md`](superpowers/plans/2026-08-28-manual-model-editing-v1.md) — T16–T20 implementation plan.
- [`superpowers/plans/2026-08-29-t22-portable-standalone-packaging.md`](superpowers/plans/2026-08-29-t22-portable-standalone-packaging.md) — detailed T22 plan and final checkpoint.
- [`superpowers/plans/2026-08-30-sketchup-bridge-usability.md`](superpowers/plans/2026-08-30-sketchup-bridge-usability.md) — post-smoke RBZ interface and compact export-name patch.
- [`superpowers/plans/2026-08-30-desktop-interaction-usability.md`](superpowers/plans/2026-08-30-desktop-interaction-usability.md) — post-smoke selection, context-menu, toolbar, active-mode, and Reset View patch.
- [`superpowers/plans/2026-08-30-post-t22-editing-corrections.md`](superpowers/plans/2026-08-30-post-t22-editing-corrections.md) — ten-item post-package editing correction implementation and verification.
- [`superpowers/plans/2026-08-31-post-t22-refresh-properties-save.md`](superpowers/plans/2026-08-31-post-t22-refresh-properties-save.md) — accepted Apply/OK refresh, Properties, Save/Open, exit, package verification, and user-acceptance checkpoint.
- [`superpowers/plans/2026-08-31-project-explorer-entity-selection.md`](superpowers/plans/2026-08-31-project-explorer-entity-selection.md) — accepted Project Explorer entity inventory and selection wiring, included in the accepted portable package.
- [`superpowers/plans/2026-09-01-worktree-mindmap.md`](superpowers/plans/2026-09-01-worktree-mindmap.md) — plan and completion record for the post-T24 map.
- [`superpowers/plans/2026-09-06-free-user-selected-paths.md`](superpowers/plans/2026-09-06-free-user-selected-paths.md) — source/package plan for unrestricted explicit SketchUp and STD destinations.
- [`superpowers/plans/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md`](superpowers/plans/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md) — CP1–CP5 source-verified; owner decisions, STRICT evidence, test gates, and pre-compile handoff recorded.
- [`superpowers/plans/2026-09-12-marquee-selection.md`](superpowers/plans/2026-09-12-marquee-selection.md) — Crop to Select marquee / Zoom in Select; owner manual acceptance pass, automated VTK smoke pending.
- [`superpowers/plans/2026-09-12-user-selected-save-destinations.md`](superpowers/plans/2026-09-12-user-selected-save-destinations.md) — STRICT-approved First Save/Save As implementation, 58-test evidence, and owner reports Save works; no compile authorization.
- [`superpowers/plans/2026-09-13-post-compile-cleanup-github-readiness.md`](superpowers/plans/2026-09-13-post-compile-cleanup-github-readiness.md) — after separately authorized compile: package verification, move-only DEL audit, all-Markdown/README sync, and local GitHub preflight; no push.
- [`WORKTREE_MINDMAP.md`](WORKTREE_MINDMAP.md) — current complete worktree, source/test/build/package, and deep RBZ relationship map.
- [`superpowers/specs/2026-08-30-post-t22-editing-corrections-design.md`](superpowers/specs/2026-08-30-post-t22-editing-corrections-design.md) — approved correction behavior and STRICT graph contracts.
- [`superpowers/specs/2026-08-31-post-t22-refresh-properties-save-design.md`](superpowers/specs/2026-08-31-post-t22-refresh-properties-save-design.md) — binding follow-up design and new HR-2 approval gate.
- [`superpowers/specs/2026-09-06-free-user-selected-paths-spec.md`](superpowers/specs/2026-09-06-free-user-selected-paths-spec.md) — explicit user-selected path boundary and preserved runtime path contracts.
- [`superpowers/specs/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md`](superpowers/specs/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md) — approved version/name/icon/Open-Save/batch contracts and remaining user/package acceptance boundaries.
- [`superpowers/specs/2026-09-12-marquee-selection.md`](superpowers/specs/2026-09-12-marquee-selection.md) — filtered rectangle selection, Ctrl-additive behavior, and the view-only Zoom in Select contract.
- [`superpowers/specs/2026-09-12-user-selected-save-destinations.md`](superpowers/specs/2026-09-12-user-selected-save-destinations.md) — First Save root cause and implemented unrestricted explicit save scope, atomic-write safety, and acceptance status.
- [`superpowers/specs/2026-09-13-post-compile-cleanup-github-readiness.md`](superpowers/specs/2026-09-13-post-compile-cleanup-github-readiness.md) — post-build package, quarantine, Markdown/README, and owner-push boundaries.
- [`superpowers/specs/2026-08-31-project-explorer-entity-selection-design.md`](superpowers/specs/2026-08-31-project-explorer-entity-selection-design.md) — Node/Member row ordering, select-one/select-all, and no-mutation contract.
- [`superpowers/specs/2026-08-28-staad-model-preprocessor-design.md`](superpowers/specs/2026-08-28-staad-model-preprocessor-design.md) — approved V1 design.
- [`superpowers/specs/2026-08-28-manual-model-editing-design.md`](superpowers/specs/2026-08-28-manual-model-editing-design.md) — approved manual-editing design.
- [`superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`](superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md) — approved SketchUp Ruby bridge design.
- [`superpowers/specs/2026-08-30-post-t22-usability-design.md`](superpowers/specs/2026-08-30-post-t22-usability-design.md) — binding design for the nine post-package usability corrections.

### Packaging manuals

- [`../packaging/README_PORTABLE.md`](../packaging/README_PORTABLE.md) — portable extraction/runtime contract.
- [`../packaging/INSTALL_RBZ.md`](../packaging/INSTALL_RBZ.md) — bundled SketchUp extension installation.
- [`../packaging/UPDATE_MANUAL.md`](../packaging/UPDATE_MANUAL.md) — manual patch/update process preserving `Data/`.

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

T22 is complete because the real `.exe`, final portable folder/ZIP, relocation/no-Python gates, manifest hashes, packaged T21 workflow, regression, lint/type checks, and documentation checkpoint are evidenced. T23 acceptance is recorded as PASS; do not start T24 automatically.


## 2026-08-31 source handoff checkpoint

- User-accepted source behavior before handoff: Member Translational Repeat preview, engineering Properties, Project Explorer entity selection, Member Local Axes XYZ, three-row toolbar with visible View controls, Save/Open Project JSON, import-derived save filename, `SAVED` / `NOT SAVED` title state, Ctrl+S save confirmation, readable Node/Member/Coordinate labels, Global Axis X/Y/Z labels, and Exit confirmation UI.
- Latest real-user defect was clicking window `X` and choosing `Yes` without closing the application.
- Latest source fix: exit dialog now compares the native Qt button result with equality (`==`) and the accepted close path delegates to `QMainWindow.closeEvent()`.
- Exit regression evidence after fix: `tests/ui/test_exit_confirmation.py` **4/4 PASS**; Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Status of latest close fix: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**.
- Full source verification is **COMPLETE**: **332/332 source unit+integration PASS**, **102/102
  lightweight UI PASS**, **38/38 isolated VTK UI PASS**, six real source smokes exit 0, focused
  Save/Open **5/5 PASS**, Ruff PASS, strict mypy 0 issues, and diff check PASS.
- The package-only verification suite was run against the new package after explicit authorization:
  **7/7 PASS**. Nuitka compilation, portable assembly, and ZIP creation completed successfully
  under `dist/post-t22-refresh-save-final/`; real package acceptance is **PASS** (2026-08-31).
  T23 target acceptance is also **PASS** by user report (2026-09-01); T24 reference/evidence mapping
  is complete and the approved move is recorded in `DEL/UNUSED_FILES_MANIFEST.md`; the post-move
  reference scan and targeted affected verification are complete; final documentation synchronization
  and commit are complete. Final audit evidence is recorded in
  `artifacts/cleanup/t24-final-verification-20260901.md`; the next planned deliverable is the
  post-T24 worktree mindmap.
