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
- [ ] Verify exported `.STD` in target STAAD.Pro environment (T23).

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

### T22 live progress checkpoint — 2026-08-30
- [x] Portable `Data/` runtime path policy implemented and source-tested.
- [x] Version contract `0.1.0` synchronized across app/package/RBZ tooling.
- [x] SketchUp `.rbz` builder and portable inbox path support implemented.
- [x] Portable assembler, manual-update contract, package manifest, and SHA-256 logic implemented.
- [x] Source-level packaged T21 workflow smoke implemented.
- [x] Source regression at checkpoint: **303/303 PASS** excluding final-package tests requiring the real `.exe`.
- [x] T22-local strict mypy: **0 issues**; relevant Ruff checks passed.
- [ ] Nuitka standalone `.exe` emitted and launched with real PySide6/VTK.
- [ ] Final portable folder and ZIP assembled from the verified `.exe`.
- [ ] No-Python PATH, different-CWD, relocation, spaces/Unicode, and `Data/` containment gates passed.
- [ ] Packaged T21 READY -> `.STD` -> validation-report workflow passed.
- [ ] Final T22 docs/checkpoint commit complete; T23 remains not started.

The detailed live status is maintained in [`docs/INDEX.md`](INDEX.md) and [`docs/HANDOFF.md`](HANDOFF.md). The remaining unchecked M14 items below are product/acceptance gates and are not silently marked complete by source-level T22 tests.

- [ ] Save/open project workflow completed as required by final product.
- [ ] Crash-safe audit/logging.
- [x] Complete golden dirty-model fixtures.
- [x] Full SketchUp-Ruby and Direct-DXF -> repair/manual edit -> normalize -> numbering -> READY -> STD pipeline.
- [x] READY gate report JSON.
- [ ] Large-model smoke test.
- [ ] Package Windows executable.
- [ ] Real-project acceptance test.
- [ ] Open final `.STD` in target STAAD.Pro.
- [ ] Update final HANDOFF.


## M15 — Post-acceptance cleanup / DEL quarantine (T24)
- [ ] Inventory tracked/untracked/generated project files after T23 acceptance.
- [ ] Build reference map for source imports, tests, docs, scripts, packaging config, fixtures, and runtime paths.
- [ ] Classify each candidate as KEEP / REGENERABLE / SUPERSEDED / UNUSED with evidence.
- [ ] Do not move `.git`, active `.worktrees`, current runtime `.venv`, required `vendor` SDK, acceptance evidence, or any referenced file.
- [ ] Move only verified-unused/superseded candidates to project-local `DEL/`; do not delete.
- [ ] Write `DEL/UNUSED_FILES_MANIFEST.md` with original path, reason, evidence, and restore path.
- [ ] Run regression/lint/type/build/package smoke appropriate to the moved files.
- [ ] Confirm Git/reference scan contains no live path pointing to quarantined files.
- [ ] Update README/HANDOFF/TASK_BOARD/CHECKLIST with final lean workspace state.
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
- [ ] `.STD` opens in STAAD.Pro with intended geometry/incidence/numbering.
- [ ] Manual STAAD geometry cleanup is materially reduced.
