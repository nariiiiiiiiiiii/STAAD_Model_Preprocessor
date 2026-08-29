Status: **T16 complete on `task/16-navigation-selection`; T17 is next.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source/temp/cache/log/build/test/generated/exported/quarantine files remain inside this root.

## Completed baseline

- T01-T13: canonical model, validation/repair, local-X normalization, numbering, deterministic `.STD` geometry export.
- T14: future-optional native direct-SKP bridge contract; C SDK is not a V1 dependency.
- T15: lightweight SketchUp Ruby Bridge + Direct DXF -> shared T06/T07 canonical import.
- T16: safe SketchUp-style navigation + selection/filter/label foundation.
- T24 remains post-acceptance move-only quarantine to project-local `DEL/`; never auto-delete.

Canonical continuation docs:
- `docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`
- `docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md`
- `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md`
- `docs/superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`

## T16 — SketchUp-Style Navigation + Selection Foundation

Branch/worktree:
- branch: `task/16-navigation-selection`
- worktree: `.worktrees/task-16-navigation-selection`
- base: `f4118e1` (T15 merged to master before T16)
- task commit subject: `feat: add safe SketchUp-style viewport controls`

### Implemented interaction contract

- `EditMode` enum: `SELECT`, `CREATE_NODE`, `DRAW_MEMBER`, `MOVE_SNAP_NODE`, `DELETE`, `MEASURE`, `SET_DIRECTION`.
- Default mode is `SELECT`.
- `InteractionState.allows_geometry_drag` is true only for `MOVE_SNAP_NODE`.
- Navigation override never changes active edit mode.
- `SelectionFilter(nodes=True, members=True)` can independently block Node/Member picking.
- `LabelVisibility` controls Node No., Member No., Local-X and Coordinates; all default off.
- Local-X validation count remains visible in the Validation panel, but arrows are user-controlled and no longer forced on.

### Viewport controls

- Middle Mouse drag: Orbit.
- Shift + Middle Mouse drag: Pan.
- Mouse wheel: zoom; uses picked world position as cursor anchor when available.
- Shift+Z: Fit Model.
- Orbit prefers selected entity center as camera focal pivot.
- Double-click: Focus Selected.
- Left drag in SELECT is intercepted as non-editing selection behavior; it cannot mutate canonical geometry.
- Ctrl+selection provides additive/toggle behavior.
- Node and Member selection supported with deterministic overlap cycling by entity type then stable UUID.
- Right-click context exposes non-mutating, selection-valid Focus / Fit / Clear Selection actions.

### UI surface

Second toolbar `View & Selection` exposes:
`Select | Nodes | Members | Node No. | Member No. | Local-X | Coordinates | Fit`.

This is intentionally a lightweight engineering control surface; no geometry-edit tools are activated in T16.

### Main implementation files

Created:
- `src/staadprep/viewer/interaction.py`
- `tests/unit/test_interaction_state.py`
- `tests/unit/test_selection_cycle.py`
- `tests/ui/test_viewport_navigation.py`

Modified:
- `src/staadprep/viewer/selection.py`
- `src/staadprep/viewer/widget.py`
- `src/staadprep/ui/main_window.py`
- `scripts/smoke_viewport.py`
- `scripts/smoke_orientation.py`
- orientation/viewport UI regression tests.

`src/staadprep/ui/panels.py` did not require modification; the approved toggles fit cleanly in the toolbar without introducing another panel.

### Verification evidence

Fresh pre-commit verification:
- unit: 172 passed;
- UI: 28 passed (split because long combined Qt/VTK runs can cause connector 502 despite subprocess success);
- integration: 5 passed;
- total: 205 tests passed;
- real Windows Qt/VTK viewport smoke: `navigation=pass selection=pass labels=pass revision=stable`;
- orientation Qt/VTK smoke updated for Local-X default-off + explicit view toggle;
- Ruff: passed;
- targeted mypy (`interaction.py`, `selection.py`, `widget.py`, `main_window.py` with third-party imports skipped): passed;
- scope scan: no new repair/geometry mutation command added to the viewport path.

## Next Task

**T17 — Snap / Inference + Axis Lock Engine**

Risk: **STRICT HR-1 / HR-2**, already covered by the user's approved high-risk envelope.

T17 must implement deterministic canonical-space Node/endpoint/midpoint/intersection inference, X/Y/Z constraints, working-plane behavior and keyboard axis locks. It may not guess unresolved 3D depth. T16 navigation/select behavior and non-mutation invariants must remain green.

Do not start T17 until the user explicitly continues after the T16 commit/checkpoint.

## T24 cleanup boundary

T24 runs only after T23 acceptance. It moves only verified-unused/superseded files into project-local `DEL/`, writes `DEL/UNUSED_FILES_MANIFEST.md`, and never deletes files. Final deletion remains user-controlled.
