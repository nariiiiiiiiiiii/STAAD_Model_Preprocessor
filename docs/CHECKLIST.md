# DEVELOPMENT CHECKLIST

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
- [x] Toolbar: Import Model / Unit Check / Repair / Normalize Axis / Renumber / Validate / Export STD.
- [x] Project Explorer.
- [x] 3D viewport placeholder.
- [x] Replace placeholder with real viewer (T04).
- [x] Properties panel.
- [x] Validation panel.
- [x] Quick Fix panel.
- [x] Issue Console.
- [x] Model summary/status.

## M2 — Canonical model
- [x] Define ProjectModel/Node/Member contracts.
- [x] Define model serialization version.
- [x] Define coordinate/unit metadata container (no conversion semantics yet).
- [x] Define stable UUID identities and source mapping.

## M3 — Import vertical slice
- [x] DXF line import.
- [x] Render imported members.
- [x] Display node/member count.
- [x] Source metadata.
- [ ] SKP importer contract.
- [ ] SKP native helper after core pipeline is stable enough.

## M4 — Unit / dimension
- [x] Source unit metadata + verified LengthUnit conversion engine.
- [x] Canonical metre conversion engine.
- [x] Overall extents engine.
- [x] Point-to-point measure engine.
- [x] Reference-length ratio workflow engine.
- [x] Suspicious scale-factor warning engine (never auto-rescales).
- [x] SketchUp Z-Up -> STAAD Y-Up right-handed transform engine.
- [ ] Wire Unit Check / dimension UI to the verified engine.

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

## M6 — Repair
- [x] Command interface.
- [x] Undo/redo stack.
- [x] Merge nodes.
- [x] Snap nodes.
- [x] Delete node/member.
- [x] Connect nodes.
- [x] Split at intersection.
- [x] Reverse member.
- [x] Scale model.
- [x] Audit log.

### Repair / issue UI (T10)
- [x] Issue Console binds rows to exact issue IDs.
- [x] Severity filter and ERROR/WARNING/INFO counts.
- [x] Select issue -> highlight + camera focus.
- [x] Disconnected structure isolate/restore in viewport.
- [x] Predefined Quick Fix dispatch through `RepairHistory`.
- [x] Destructive delete confirmation.
- [x] Undo/Redo UI with automatic re-render and re-validation.
- [x] Combined dirty fixture real Qt/VTK smoke flow.

## M7 — Normalize / renumber
- [x] Preview member directions.
- [x] Direction arrows in viewer.
- [x] Normalize incidence.
- [ ] Deterministic node renumber.
- [ ] Deterministic member renumber.
- [ ] Old->new mapping report.

## M8 — STAAD export
- [ ] Define supported `.STD` subset.
- [ ] Generate UNIT command / joint coordinates.
- [ ] Generate member incidences.
- [ ] Syntax validation.
- [ ] Golden expected files.
- [ ] Verify with target STAAD.Pro environment.

## M9 — Production readiness
- [ ] Save/open project.
- [ ] Crash-safe audit/logging.
- [ ] Large-model smoke test.
- [ ] Package Windows executable.
- [ ] Real-project acceptance test.
- [ ] Update HANDOFF.

# Golden fixtures

Create at minimum:
- [ ] 01_clean_frame
- [ ] 02_orphan_node
- [ ] 03_near_nodes
- [ ] 04_duplicate_member
- [ ] 05_short_member
- [ ] 06_disconnected_structures
- [ ] 07_wrong_scale
- [ ] 08_wrong_axis
- [ ] 09_crossing_without_node
- [ ] 10_combined_dirty_frame

# V1 acceptance
- [ ] Real SketchUp/DXF model imports.
- [ ] Units/reference dimension can be verified.
- [ ] Dirty topology is visible and actionable.
- [ ] Common errors can be repaired in-app.
- [ ] Structure count reaches expected value.
- [ ] Model normalizes/renumbers deterministically.
- [ ] Critical validation passes.
- [ ] `.STD` opens in STAAD.Pro with intended geometry.
- [ ] Manual STAAD geometry cleanup is materially reduced.
