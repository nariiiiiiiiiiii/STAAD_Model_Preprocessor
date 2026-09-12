## M0 — Foundation
- [x] Create isolated project folder.
- [x] Initialize project-local Git repository.
- [x] Add mandatory project-boundary rules.
- [x] Add product specification.
- [x] Add architecture/workflow docs.
- [x] Add implementation plan after written-spec approval.
- [x] Create Python package skeleton.
- [x] Add project-local path service.
- [x] Add development environment configuration.
- [x] Add smoke-launch script.

## M1 — UI shell
- [x] Reproduce approved dark engineering layout.
- [x] Initial toolbar: Import / Unit Check / Repair / Normalize / Renumber / Validate / Export.
- [x] Project Explorer.
- [x] Real 3D viewport.
- [x] Properties panel.
- [x] Validation panel.
- [x] Quick Fix panel.
- [x] Issue Console.
- [x] Model summary/status.

## M2 — Canonical model
- [x] Define ProjectModel/Node/Member contracts.
- [x] Define model serialization version.
- [x] Define coordinate/unit metadata container.
- [x] Define stable UUID identities and source mapping.

## M3 — Import vertical slice
- [x] DXF line import.
- [x] Render imported members.
- [x] Display node/member count.
- [x] Source metadata.
- [x] SKP bridge contract + protocol/capability probe (T14).
- [x] SketchUp Ruby Extension exports supported edges/groups/components/tags/units to Neutral JSON v1.
- [x] Project-local SketchUp inbox handoff works without C SDK.
- [x] SketchUp Neutral JSON -> T06/T07 -> canonical metre/Y-Up integration.
- [x] Direct DXF -> T06/T07 -> canonical metre/Y-Up integration remains green.

## M4 — Unit / dimension
- [x] Source unit metadata + verified LengthUnit conversion engine.
- [x] Canonical metre conversion engine.
- [x] Overall extents engine.
- [x] Point-to-point measure engine.
- [x] Reference-length ratio workflow engine.
- [x] Suspicious scale-factor warning engine.
- [x] SketchUp Z-Up -> STAAD Y-Up right-handed transform engine.
- [ ] Wire full Unit Check / dimension UI to the verified engine.

## M5 — Validation
- [x] Invalid coordinate.
- [x] Duplicate node.
- [x] Near node.
- [x] Orphan node.
- [x] Zero-length member.
- [x] Short member.
- [x] Duplicate member.
- [x] Unconnected gap.
- [x] Crossing without node.
- [x] Connected-component count.

## M6 — Repair engine
- [x] Command interface.
- [x] Undo/redo stack.
- [x] Merge nodes.
- [x] Snap node.
- [x] Delete node/member.
- [x] Connect nodes.
- [x] Split at intersection core command.
- [x] Reverse member.
- [x] Scale/transform model commands.
- [x] Audit log.

### Repair / issue UI
- [x] Issue Console binds rows to exact issue IDs.
- [x] Severity filter and ERROR/WARNING/INFO counts.
- [x] Select issue -> highlight + camera focus.
- [x] Disconnected structure isolate/restore in viewport.
- [x] Predefined Quick Fix dispatch through RepairHistory.
- [x] Destructive delete confirmation.
- [x] Undo/Redo UI with automatic re-render and re-validation.
- [x] Combined dirty fixture real Qt/VTK smoke flow.

## M7 — Normalize / renumber core
- [x] Preview member directions.
- [x] Direction arrows in viewer.
- [x] Normalize incidence/local-X.
- [x] Deterministic node renumber.
- [x] Deterministic member renumber.
- [x] UUID -> STAAD-facing number mapping report.

## M8 — STAAD export
- [x] Define supported `.STD` subset.
- [x] Generate UNIT / JOINT COORDINATES.
- [x] Generate MEMBER INCIDENCES.
- [x] Deterministic syntax/format validation.
- [x] Golden expected `.STD`.
- [x] Verify exported `.STD` in target STAAD.Pro environment (T23) — user reported PASS on 2026-09-01.

## M9 — SketchUp-style navigation / selection (T16)
- [x] Explicit EditMode state; default SELECT.
- [x] SELECT drag cannot mutate model.
- [x] Middle Mouse Orbit.
- [x] Shift + Middle Mouse Pan.
- [x] Mouse Wheel Zoom.
- [x] Shift+Z Fit Model.
- [x] Navigation override preserves active edit preview.
- [x] Node/Member selection filter.
- [x] Overlap entity cycling/chooser.
- [x] Ctrl additive selection.
- [x] Double-click Focus/Zoom Selected.
- [x] Node Number / Member Number / Local-X / Coordinates toggles.
- [x] Context menu valid operations by entity type.

## M10 — Snap / inference / axis lock (T17)
- [x] Existing Node inference.
- [x] Member endpoint inference.
- [x] Member midpoint inference.
- [x] Member intersection inference.
- [x] Canonical X/Y/Z axis inference.
- [x] Working plane/grid inference.
- [x] X/Y/Z keyboard axis locks.
- [x] Y explicitly labeled Vertical.
- [x] No arbitrary depth guess when inference is unresolved.
- [x] Deterministic tie-break between equal candidates.

## M11 — Manual analytical editing (T18)
- [x] CreateNode reversible command.
- [x] MoveNode reversible command.
- [x] Atomic CompositeRepair / one Undo for multi-step operation.
- [x] DRAW MEMBER existing Node -> existing Node.
- [x] DRAW MEMBER existing Node -> new Node atomically.
- [x] MOVE/SNAP NODE with ghost preview only until release.
- [x] Snap/Merge onto existing Node without co-located duplicates.
- [x] Delete exact selected overlapping Member.
- [x] Delete selected structurally valid Node.
- [x] Split Member at midpoint.
- [x] Split Member at percentage/distance.
- [x] Split affected Member(s) at intersection atomically.
- [x] Esc cancels edit preview with no model mutation.
- [x] Middle Mouse navigation during editing does not cancel edit.
- [x] Real Qt/VTK manual-edit smoke flow.

## M12 — Precision Create Node + Translational Repeat (T19)
- [x] Create Node by click/snap.
- [x] Create Node by exact STAAD XYZ.
- [x] Create Node relative to selected reference Node.
- [x] Relative dialog shows reference/result coordinates.
- [x] Relative dialog uses X/Y(Vertical)/Z direction + distance.
- [x] Optional Create Member checkbox.
- [x] Node+Member creation atomic and one Undo.
- [x] Existing-node collision shown before commit.
- [x] Translational Repeat ΔX/ΔY/ΔZ.
- [x] Repeat count excludes reference Node.
- [x] Connect Consecutive Nodes mode.
- [x] Connect From Reference Node mode.
- [x] Ghost preview all repeated Nodes/Members.
- [x] Existing-node resolution: Use Existing / Skip / Cancel.
- [x] Entire repeat is one atomic history item / one Undo.

## M13 — Numbering + member-direction controls (T20)

Status: **COMPLETE — implementation, strict verification, documentation, and task commit complete.**

- [x] Auto Node Number.
- [x] Auto Member Number.
- [x] Auto Number All.
- [x] Old -> New mapping preview before Apply.
- [x] Numbering commands reversible as history items.
- [x] Auto Fix Axis All.
- [x] Auto Fix Axis Selected.
- [x] Flip Selected Member(s).
- [x] Set Direction by clicking desired Start `(i)` endpoint.
- [x] Local-X preview before direction Apply.
- [x] Numbering changes numbers only; UUID references unchanged.
- [x] Direction controls change incidence only; geometry unchanged.
- [x] T20-local strict static typing gate clean; inherited `dxf_reader.py` typing debt remains outside T20.
- [x] T20 task commit + post-commit clean/doc gate complete.

## M14 — End-to-End READY / production readiness (T21-T23)

### T22 final checkpoint — 2026-08-30
- [x] Portable `Data/` runtime path policy implemented and source-tested.
- [x] Version contract `0.1.0` synchronized across app/package/RBZ tooling.
- [x] SketchUp `.rbz` builder and portable inbox path support implemented.
- [x] Portable assembler, manual-update contract, package manifest, and SHA-256 logic implemented.
- [x] Source-level packaged T21 workflow smoke implemented.
- [x] Final source regression: **307/307 unit+integration PASS**.
- [x] T22-local strict mypy: **0 issues**; relevant Ruff checks passed.
- [x] Nuitka standalone `.exe` emitted; report records successful standalone completion.
- [x] Emitted `.exe` launched with real PySide6/VTK.
- [x] Final portable folder and ZIP assembled from the verified `.exe`.
- [x] No-Python PATH, different-CWD, relocation, spaces/Unicode, existing-`Data`, and `Data/` containment gates passed.
- [x] Manifest hashes verified: **811/811 managed files**; bundled `.rbz` and entrypoint present.
- [x] Packaged T21 READY -> `.STD` -> validation-report workflow passed.
- [x] Relevant affected UI regression: **3/3 PASS**; Ruff and T22-local strict mypy passed.
- [x] Final T22 docs/checkpoint complete; T23 acceptance subsequently reported PASS on 2026-09-01.

The final T22 evidence is maintained in [`docs/INDEX.md`](INDEX.md) and [`docs/HANDOFF.md`](HANDOFF.md). T23 acceptance is recorded as user-reported PASS on 2026-09-01; remaining unchecked M14 items are not silently marked complete without direct evidence.

### Post-T22 usability checkpoint — SketchUp Bridge

- [x] RBZ opens a dedicated interface explaining the geometry handoff.
- [x] Interface provides Export Geometry, Choose Inbox, and Close actions.
- [x] Export names use compact `SP_YYYYMMDD_HHMMSS.json` format with collision suffixes.
- [x] RBZ source/package contract verification: **3/3 PASS**; Ruff and `git diff --check` passed.
- [x] User accepted the rebuilt RBZ in real SketchUp; the window opened and was usable.
- [x] Desktop requirements 3-9 implemented in source: scaled Node/Member picking, visible highlights, functional entity/empty-space context menu, Reset View, usage-order toolbar rows, and active-mode styling.
- [x] Desktop source verification: **311/311 unit+integration PASS**, **100/100 UI PASS**, real viewport smoke `selection=pass reset_view=pass`.
- [x] Rebuilt standalone report `completion="yes"`; exact package manifest **811/811**, package gates **3/3**, and freshly extracted ZIP launch passed.
- [x] Separate `post-t22-ux-final` acceptance checkpoint superseded by the consolidated ten-item editing-correction package; its evidence remains historical.

### Post-T22 editing corrections — 2026-08-31

- [x] Reset View uses canonical STAAD Y-up isometric camera.
- [x] selected/create/orphan Nodes and selected Members delete through one confirmed, undoable path.
- [x] keyboard `Delete`, toolbar Delete, and context Delete Selected are wired.
- [x] Crop to Selection frames selected geometry without model mutation.
- [x] Properties shows selected Node/Member identity, coordinates/incidence, length, and metadata.
- [x] Merge Members restores two split collinear Members and is exactly undoable.
- [x] orphan Issue Quick Fix and viewport selection deletion both remain available.
- [x] selected-Member Translational Repeat preserves shared topology and rejects duplicate incidence.
- [x] Create Node actions are distinguished as `(Click)` and `(XYZ)`.
- [x] Draw/Move/Delete modes force compatible filters, focus the viewport, show next-click guidance,
  and remain visibly checked while active.
- [x] STRICT graph tests include exact undo, incidence, collision, metadata, and invalid-case checks.
- [x] Verification: **299/299 unit**, **26/26 integration**, **77/77 lightweight UI**, and
  **34/34 isolated VTK UI**; Ruff and strict mypy for 7 affected source files pass.
- [x] Rebuilt standalone folder/ZIP under the now-quarantined `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/`; exact package gates **4/4**, manifest **811/811**, and extracted-ZIP launch passed.
- [x] User-authorized targeted archive moved superseded baseline and `post-t22-ux-final` releases into `DEL/standalone-archive-20260831/`; current editing-final release and latest build input remain in place.
- [x] Historical ten-item package evidence is preserved at
  `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/`; consolidated user acceptance and
  commit are recorded under `dist/post-t22-refresh-save-final/`.

### Planned follow-up — repair refresh, Properties, Save/Open, exit confirmation

- [x] Read-only diagnosis and binding design recorded on 2026-08-31.
- [x] Detailed implementation/verification plan recorded; implementation intentionally not started during usage-limit pause.
- [x] Record the user-mandated source-first, one-correction-at-a-time workflow and explicit pre-compile stop gate.
- [x] Obtain explicit STRICT / Full TDD approval for Apply-before-OK Delete/Merge/Quick-Fix/Auto-Fix orchestration when execution resumes.
- [x] Implement and source-verify Apply→OK exact-once command execution and automatic refresh without requiring Undo.
- [x] User accepted the Apply→OK interaction in the development app.
- [x] Add STRICT multi-Orphan regression and clear stale Issue Console row/current selection after each validation rebuild.
- [x] Obtain user retest acceptance for repeated Orphan Quick Fix before starting Properties.
- [x] Add expandable, STAAD-number-sorted Node/Member rows to Project Explorer.
- [x] Route individual/group Explorer clicks to exact/select-all viewport highlighting and matching selection filters.
- [x] Source verification for Explorer selection: **16/16 affected UI PASS** and Ruff clean.
- [x] Obtain user development-app acceptance for Project Explorer entity lists and highlighting.
- [x] Replace visible UUID/source fields with requested Node/Member engineering Properties in source.
- [x] Verify exact Node/Member Properties contracts: affected regression **15/15 PASS**, Ruff clean, strict mypy **0 issues**.
- [x] Obtain user development-app acceptance for UUID-free engineering Properties.
- [x] Add atomic canonical Project JSON Save/Open under project-local `Projects`.
- [x] Add confirmed application exit with explicit packaged-smoke bypass.
- [x] Obtain user acceptance of the corrected `X -> No` / `X -> Yes` close behavior.
- [x] Present each completed source correction for user testing and wait for an explicit instruction before continuing to the next correction.
- [x] Run agreed source regression: **332/332 source unit+integration**, **140/140 UI**, six real
  source smokes, focused Save/Open **5/5**, Ruff, strict mypy, and diff checks pass; stopped at the
  mandatory pre-compile gate.
- [x] Obtain explicit user approval and complete the fresh Nuitka standalone compile.
- [x] Obtain the next explicit user instruction before portable-folder assembly or ZIP creation.
- [x] After compile approval, rebuild/package and create the isolated portable folder/ZIP under
  `dist/post-t22-refresh-save-final/`.
- [x] Run executable-only/package-path gates against the new package: **7/7 PASS**.
- [x] Obtain real package acceptance: **PASS** (user-tested 2026-08-31).

- [x] Save/open project workflow completed as required by the accepted source checkpoint.
- [ ] Crash-safe audit/logging.
- [x] Complete golden dirty-model fixtures.
- [x] Full SketchUp-Ruby and Direct-DXF -> repair/manual edit -> normalize -> numbering -> READY -> STD pipeline.
- [x] READY gate report JSON.
- [ ] Large-model smoke test.
- [x] Package Windows executable.
- [ ] Real-project acceptance test.
- [ ] Open final `.STD` in target STAAD.Pro.
- [x] Update final HANDOFF for the post-T22 editing-correction package checkpoint.


## M15 — Post-acceptance cleanup / DEL quarantine (T24)
- [x] Inventory tracked/untracked/generated project files after T23 acceptance; see
  `artifacts/cleanup/t24-inventory-20260901.md`.
- [x] Build reference map for source imports, tests, docs, scripts, packaging config, fixtures, and runtime paths; see
  `artifacts/cleanup/t24-reference-map-20260901.md`.
- [x] Classify each candidate as KEEP / REGENERABLE / SUPERSEDED / UNUSED with evidence; see the
  inventory and reference map.
- [x] Keep `.git`, active `.worktrees`, current runtime `.venv`, required `vendor` SDK, acceptance
  evidence, and all referenced files in place.
- [x] Move only the verified superseded candidate to project-local `DEL/`; do not delete.
- [x] Write `DEL/UNUSED_FILES_MANIFEST.md` with original path, reason, evidence, and restore path.
- [x] Run affected verification appropriate to the moved files: current package suite **7/7 PASS**
  and `git diff --check` PASS; no source/lint/type/build rerun was required because source and build
  inputs were untouched.
- [x] Confirm Git/reference scan contains no live source/test/script/config path pointing to the
  quarantined package; historical documentation links point to its `DEL/` path.
- [x] Update README/HANDOFF/TASK_BOARD/CHECKLIST and synchronized status documents with final lean
  workspace state; see `artifacts/cleanup/t24-final-verification-20260901.md`.
- [ ] User performs final deletion from `DEL/` separately after review.

# Golden fixtures

Create/complete at minimum:
- [x] 01_clean_frame
- [x] 02_orphan_node
- [x] 03_near_nodes
- [x] 04_duplicate_member
- [x] 05_short_member
- [x] 06_disconnected_structures
- [x] 07_wrong_scale
- [x] 08_wrong_axis
- [x] 09_crossing_without_node
- [x] 10_combined_dirty_frame
- [x] 11_sketchup_ruby_simple_frame
- [x] manual-edit clean/dirty expected canonical fixtures for T18-T21

# V1 acceptance
- [ ] Real SketchUp model can hand off through Ruby bridge and real DXF can import directly.
- [x] Units/reference dimension can be verified.
- [x] Dirty topology is visible and actionable.
- [x] Common errors can be repaired through Quick Fix/manual repair commands.
- [x] Missing member can be drawn directly in viewport.
- [x] Floating/misplaced Node can be moved/snapped directly in viewport.
- [x] Overlapping duplicate Member can be selected exactly and deleted.
- [x] New Node can be created by exact/relative coordinate.
- [x] Translational Repeat can generate repeated Nodes and optional Members atomically.
- [x] SketchUp-style orbit/pan/zoom works without accidental geometry mutation.
- [x] Node/member labels and filters identify entities unambiguously.
- [x] Auto Node / Member / All numbering works with preview/undo.
- [x] Auto Fix / Flip / Set Direction controls work with local-X preview.
- [x] Structure count reaches expected value.
- [x] Critical validation passes and READY gate is authoritative.
- [x] `.STD` opens in STAAD.Pro with intended geometry/incidence/numbering — user reported PASS on 2026-09-01.
- [x] Manual STAAD geometry cleanup is materially reduced — user reported T23 PASS on 2026-09-01.


## 2026-08-31 source handoff checkpoint

- User-accepted source behavior before handoff: Member Translational Repeat preview, engineering Properties, Project Explorer entity selection, Member Local Axes XYZ, three-row toolbar with visible View controls, Save/Open Project JSON, import-derived save filename, `SAVED` / `NOT SAVED` title state, Ctrl+S save confirmation, readable Node/Member/Coordinate labels, Global Axis X/Y/Z labels, and Exit confirmation UI.
- Latest real-user defect was clicking window `X` and choosing `Yes` without closing the application.
- Latest source fix: exit dialog now compares the native Qt button result with equality (`==`) and the accepted close path delegates to `QMainWindow.closeEvent()`.
- Exit regression evidence after fix: `tests/ui/test_exit_confirmation.py` **4/4 PASS**; Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Status of latest close fix: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**.
- Full source verification is **COMPLETE**: **332/332 source unit+integration PASS**, **102/102
  lightweight UI PASS**, **38/38 isolated VTK UI PASS**, six real source smokes exit 0, focused
  Save/Open **5/5 PASS**, Ruff PASS, strict mypy 0 issues, and diff check PASS.
- The package-only verification suite was run after the user authorized step 3: **7/7 PASS**.
  Nuitka compilation, portable assembly, and ZIP creation are complete under
  `dist/post-t22-refresh-save-final/`; real package acceptance is **PASS** (2026-08-31).

## M16 — Post-T24 worktree/RBZ mindmap

- [x] Canonical `docs/WORKTREE_MINDMAP.md` created in the active T22 worktree.
- [x] Tracked source, tests, docs, plans/specs, scripts, native boundary, and fixtures cataloged.
- [x] Build/package/runtime, portable `Data/`, accepted package, hashes, and T24 quarantine mapped.
- [x] RBZ archive members, Ruby source, loader, callbacks, HtmlDialog actions, JSON schema, inbox,
  and Python handoff mapped.
- [x] Current status and future safe patch entry points recorded.
- [x] Separate documentation checkpoint commit contains the mindmap and synchronized status docs.

## M17 — T25 full storage audit and approved quarantine

- [x] Recheck project storage and classify current/protected/generated/superseded material.
- [x] Preserve current accepted package, current RBZ, final build, source, tests, and evidence.
- [x] Move the approved old package and five old build attempts into `DEL/t25-storage-audit-20260901/`.
- [x] Verify originals are absent, quarantine targets exist, and live references to old names are 0.
- [x] Recreate `DEL/UNUSED_FILES_MANIFEST.md` after the user had deleted the previous manifest.
- [ ] User reviews and separately deletes quarantined files if actual disk-space recovery is desired.
- [ ] Separate explicit decision for clearing `.tmp/` and `.cache/` regenerable output.

## M18 — T26 space-cleanup move

- [x] Move generated `.tmp/` contents to the project-local T26 quarantine, preserving `.tmp/.gitkeep`.
- [x] Move generated `.cache/` contents to the project-local T26 quarantine.
- [x] Move all 22 historical clean worktrees (maintenance plus T01–T21) with Git metadata repaired;
  retain only the active T22 worktree under `.worktrees/`.
- [x] Verify current package, ZIP/RBZ, source, tests, final build, and hashes remain intact.
- [x] Re-run focused standalone smoke after the move: **1/1 PASS** with no Python and a different CWD;
  quarantine the test output afterward.
- [ ] User reviews and deletes T26 quarantine when disk-space reclamation is desired.

## M19 — T27 free user-selected paths

- [x] Allow selected SketchUp Bridge JSON import from any file location while retaining the default inbox.
- [x] Allow RBZ output folder selection from any existing directory.
- [x] Allow selected STD export destinations outside the project and write the sibling validation report.
- [x] Preserve project-local Project JSON and application-managed runtime path contracts.
- [x] Run source regressions, Ruff, strict mypy, and package gates before release assembly.
- [x] Compile/package the updated standalone and archive the previous accepted package/build/RBZ in DEL.

## 2026-09-12 source follow-up — CP1–CP5

- [x] Sync approved source version `0.2.0` across canonical Python, package metadata/export, and SketchUp loader.
- [x] Name SketchUp JSON from safe SKP stem plus local `DDMMYYYY`; preserve source metadata and collision suffixes.
- [x] Copy the selected logo byte-identically; verify Qt app icon and Windows build-contract wiring; generate 7-size ICO.
- [x] Open Project JSON from any selected folder; Save back to the opened path; keep first Save in the default Projects folder.
- [x] Obtain explicit STRICT / Full TDD approval for multi-issue Quick Fix/intersection.
- [x] Add conflict-checked batch planning, extended selection, existing intersection splitter route, CompositeRepair audit/history, and exact Undo/Redo coverage.
- [x] Verify **345 unit+integration PASS**, **1 skipped** (RBZ archive acceptance requires an explicit RBZ build), **3 deselected** (portable-executable gates require an explicit `0.2.0` package), and **26/26 affected UI PASS**; Ruff and strict mypy pass.
- [x] Record owner-reported partial development smoke (2026-09-12): app-window icon changed; Quick Fix and Undo/Redo work.
- [x] Add stable Windows AppUserModelID before QApplication creation and explicitly set the selected app icon on the main window; focused regression **10/10 PASS**, Ruff PASS, strict mypy **0 issues**.
- [x] Owner confirms the selected logo appears on the source-run app taskbar (2026-09-12); this does not verify the old compiled executable.
- [x] Update the RBZ/portable fixture tests so ordinary integration testing does not build an RBZ or release package in `build/` or `dist/`.
- [ ] User manually accepts the uncompiled development app and SketchUp handoff after an authorized RBZ build.
- [ ] User separately authorizes Nuitka/RBZ/portable package build and then package acceptance.

Incident record: an earlier full-suite run invoked the legacy RBZ builder test and created a transient
`0.2.0` RBZ. That single file was removed; the existing `0.1.0` RBZ/package was retained. The builder
also refreshed pre-existing ignored `build/sketchup/stage/` copies; those files were left in place.
