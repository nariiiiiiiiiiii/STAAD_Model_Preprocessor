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
- [ ] SKP bridge contract.
- [ ] Native SKP edge extraction.
- [ ] Native -> neutral -> canonical metre/Y-Up integration.

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
- [ ] Explicit EditMode state; default SELECT.
- [ ] SELECT drag cannot mutate model.
- [ ] Middle Mouse Orbit.
- [ ] Shift + Middle Mouse Pan.
- [ ] Mouse Wheel Zoom.
- [ ] Shift+Z Fit Model.
- [ ] Navigation override preserves active edit preview.
- [ ] Node/Member selection filter.
- [ ] Overlap entity cycling/chooser.
- [ ] Ctrl additive selection.
- [ ] Double-click Focus/Zoom Selected.
- [ ] Node Number / Member Number / Local-X / Coordinates toggles.
- [ ] Context menu valid operations by entity type.

## M10 — Snap / inference / axis lock (T17)
- [ ] Existing Node inference.
- [ ] Member endpoint inference.
- [ ] Member midpoint inference.
- [ ] Member intersection inference.
- [ ] Canonical X/Y/Z axis inference.
- [ ] Working plane/grid inference.
- [ ] X/Y/Z keyboard axis locks.
- [ ] Y explicitly labeled Vertical.
- [ ] No arbitrary depth guess when inference is unresolved.
- [ ] Deterministic tie-break between equal candidates.

## M11 — Manual analytical editing (T18)
- [ ] CreateNode reversible command.
- [ ] MoveNode reversible command.
- [ ] Atomic CompositeRepair / one Undo for multi-step operation.
- [ ] DRAW MEMBER existing Node -> existing Node.
- [ ] DRAW MEMBER existing Node -> new Node atomically.
- [ ] MOVE/SNAP NODE with ghost preview only until release.
- [ ] Snap/Merge onto existing Node without co-located duplicates.
- [ ] Delete exact selected overlapping Member.
- [ ] Delete selected structurally valid Node.
- [ ] Split Member at midpoint.
- [ ] Split Member at percentage/distance.
- [ ] Split affected Member(s) at intersection atomically.
- [ ] Esc cancels edit preview with no model mutation.
- [ ] Middle Mouse navigation during editing does not cancel edit.
- [ ] Real Qt/VTK manual-edit smoke flow.

## M12 — Precision Create Node + Translational Repeat (T19)
- [ ] Create Node by click/snap.
- [ ] Create Node by exact STAAD XYZ.
- [ ] Create Node relative to selected reference Node.
- [ ] Relative dialog shows reference/result coordinates.
- [ ] Relative dialog uses X/Y(Vertical)/Z direction + distance.
- [ ] Optional Create Member checkbox.
- [ ] Node+Member creation atomic and one Undo.
- [ ] Existing-node collision shown before commit.
- [ ] Translational Repeat ΔX/ΔY/ΔZ.
- [ ] Repeat count excludes reference Node.
- [ ] Connect Consecutive Nodes mode.
- [ ] Connect From Reference Node mode.
- [ ] Ghost preview all repeated Nodes/Members.
- [ ] Existing-node resolution: Use Existing / Skip / Cancel.
- [ ] Entire repeat is one atomic history item / one Undo.

## M13 — Numbering + member-direction controls (T20)
- [ ] Auto Node Number.
- [ ] Auto Member Number.
- [ ] Auto Number All.
- [ ] Old -> New mapping preview before Apply.
- [ ] Numbering commands reversible as history items.
- [ ] Auto Fix Axis All.
- [ ] Auto Fix Axis Selected.
- [ ] Flip Selected Member(s).
- [ ] Set Direction by clicking desired Start `(i)` endpoint.
- [ ] Local-X preview before direction Apply.
- [ ] Numbering changes numbers only; UUID references unchanged.
- [ ] Direction controls change incidence only; geometry unchanged.

## M14 — End-to-End READY / production readiness (T21-T23)
- [ ] Save/open project workflow completed as required by final product.
- [ ] Crash-safe audit/logging.
- [ ] Complete golden dirty-model fixtures.
- [ ] Full SKP/DXF -> repair/manual edit -> normalize -> numbering -> READY -> STD pipeline.
- [ ] READY gate report JSON.
- [ ] Large-model smoke test.
- [ ] Package Windows executable.
- [ ] Real-project acceptance test.
- [ ] Open final `.STD` in target STAAD.Pro.
- [ ] Update final HANDOFF.

# Golden fixtures

Create/complete at minimum:
- [x] 01_clean_frame
- [ ] 02_orphan_node
- [ ] 03_near_nodes
- [ ] 04_duplicate_member
- [ ] 05_short_member
- [ ] 06_disconnected_structures
- [ ] 07_wrong_scale
- [ ] 08_wrong_axis
- [ ] 09_crossing_without_node
- [ ] 10_combined_dirty_frame
- [ ] 11_skp_simple_frame
- [ ] manual-edit clean/dirty expected canonical fixtures for T18-T21

# V1 acceptance
- [ ] Real SketchUp/DXF model imports.
- [ ] Units/reference dimension can be verified.
- [ ] Dirty topology is visible and actionable.
- [ ] Common errors can be repaired through Quick Fix.
- [ ] Missing member can be drawn directly in viewport.
- [ ] Floating/misplaced Node can be moved/snapped directly in viewport.
- [ ] Overlapping duplicate Member can be selected exactly and deleted.
- [ ] New Node can be created by exact/relative coordinate.
- [ ] Translational Repeat can generate repeated Nodes and optional Members atomically.
- [ ] SketchUp-style orbit/pan/zoom works without accidental geometry mutation.
- [ ] Node/member labels and filters identify entities unambiguously.
- [ ] Auto Node / Member / All numbering works with preview/undo.
- [ ] Auto Fix / Flip / Set Direction controls work with local-X preview.
- [ ] Structure count reaches expected value.
- [ ] Critical validation passes and READY gate is authoritative.
- [ ] `.STD` opens in STAAD.Pro with intended geometry/incidence/numbering.
- [ ] Manual STAAD geometry cleanup is materially reduced.
