# DEVELOPMENT CHECKLIST

## M0 — Foundation
- [x] Create isolated project folder.
- [x] Initialize project-local Git repository.
- [x] Add mandatory project-boundary rules.
- [x] Add product specification.
- [x] Add architecture/workflow docs.
- [x] Add implementation plan after written-spec approval.
- [ ] Create Python package skeleton.
- [ ] Add project-local path service.
- [ ] Add development environment configuration.
- [ ] Add smoke-launch script.

## M1 — UI shell
- [ ] Reproduce approved dark engineering layout.
- [ ] Toolbar: Import Model / Unit Check / Repair / Normalize Axis / Renumber / Validate / Export STD.
- [ ] Project Explorer.
- [ ] 3D viewport placeholder -> real viewer.
- [ ] Properties panel.
- [ ] Validation panel.
- [ ] Quick Fix panel.
- [ ] Issue Console.
- [ ] Model summary/status.

## M2 — Canonical model
- [ ] Define ProjectModel/Node/Member/Issue contracts.
- [ ] Define model serialization version.
- [ ] Define coordinate/unit metadata.
- [ ] Define deterministic IDs and source mapping.

## M3 — Import vertical slice
- [ ] DXF line import.
- [ ] Render imported members.
- [ ] Display node/member count.
- [ ] Source metadata.
- [ ] SKP importer contract.
- [ ] SKP native helper after core pipeline is stable enough.

## M4 — Unit / dimension
- [ ] Source unit display.
- [ ] Canonical metre display.
- [ ] Overall extents.
- [ ] Measure tool.
- [ ] Reference-length workflow.
- [ ] Suspicious scale-factor warning.

## M5 — Validation
- [ ] Invalid coordinate.
- [ ] Duplicate node.
- [ ] Near node.
- [ ] Orphan node.
- [ ] Zero-length member.
- [ ] Short member.
- [ ] Duplicate member.
- [ ] Unconnected gap.
- [ ] Crossing without node.
- [ ] Connected-component count.

## M6 — Repair
- [ ] Command interface.
- [ ] Undo/redo stack.
- [ ] Merge nodes.
- [ ] Snap nodes.
- [ ] Delete node/member.
- [ ] Connect nodes.
- [ ] Split at intersection.
- [ ] Reverse member.
- [ ] Scale model.
- [ ] Audit log.

## M7 — Normalize / renumber
- [ ] Preview member directions.
- [ ] Direction arrows in viewer.
- [ ] Normalize incidence.
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
