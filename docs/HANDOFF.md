Status: **T15 complete on `task/15-sketchup-ruby`; T16 is next and not started.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source/temp/cache/log/build/test/generated/exported/quarantine files remain inside this root.

## Completed baseline

- T01-T13: canonical model, validation/repair, local-X normalization, numbering, and deterministic `.STD` geometry export.
- T14: preserved optional native direct-SKP bridge contract (`fb95771`); official C SDK is not a V1 dependency.
- V1 import architecture planning: `520dc57 docs: switch V1 SketchUp import to Ruby bridge`.
- T15: lightweight SketchUp Ruby Bridge + Direct DXF canonical integration.
- T24 remains post-acceptance move-only quarantine to project-local `DEL/`; no automatic deletion.

Canonical continuation documents:
- `docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`
- `docs/superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`
- `docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md`
- `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md`

## T15 — SketchUp Ruby Extension + Neutral Import Integration

Branch/worktree:
- branch: `task/15-sketchup-ruby`
- worktree: `.worktrees/task-15-sketchup-ruby`
- base: `520dc57`
- commit subject: `feat: bridge SketchUp Ruby geometry into canonical import`

### V1 import routes

1. SketchUp open model -> lightweight Ruby Extension `Send to STAAD Prep` -> Neutral JSON v1 -> `artifacts/sketchup_bridge/inbox/` -> `NeutralReader` -> shared T06 unit/axis transform -> T07 topology.
2. Direct DXF -> `DxfReader` -> shared T06 unit/axis transform -> T07 topology.
3. T14 C++/C-SDK direct `.skp` reader remains future optional and does not block V1.

### Lightweight SketchUp extension decision

Confirmed 2026-08-29:
- one primary toolbar/menu action: `Send to STAAD Prep`;
- first use selects/configures the project-local inbox;
- later sends are one-click;
- success/failure notification only;
- no dashboard, preview panel, progress UI, advanced settings UI, or styling work in T15/V1;
- visual polish and richer UX are deferred without changing Neutral JSON or canonical import architecture.

### Implemented files

Created:
- `extensions/sketchup_staadprep/staadprep_loader.rb`
- `extensions/sketchup_staadprep/staadprep/exporter.rb`
- `src/staadprep/importers/neutral_reader.py`
- `src/staadprep/importers/pipeline.py`
- `tests/unit/test_neutral_reader.py`
- `tests/unit/test_import_pipeline.py`
- `tests/unit/test_sketchup_ruby_contract.py`
- `tests/integration/test_sketchup_ruby_pipeline.py`
- `tests/ui/test_import_routes.py`
- `tests/golden_models/11_sketchup_ruby_simple_frame/expected.json`

Modified:
- `src/staadprep/importers/dxf_reader.py` — declares DXF source axis `Z-UP` for the shared T06 gate.
- `src/staadprep/ui/main_window.py` — independent SketchUp Bridge JSON and Direct DXF canonical import actions.
- relevant DXF/UI regression tests and status docs.

### Coordinate authority

Ruby emits SketchUp API internal coordinate values explicitly as inches with `source_axis=Z-UP`.
It does not perform STAAD conversion.

T06 remains the single authority:

`STAAD(x,y,z) = (SKP.x, SKP.z, -SKP.y)` after unit conversion to metres.

T07 remains the single topology authority; the bridge does not merge/repair/split/renumber geometry.

### Runtime verification

Verified against installed SketchUp 2026 `26.1.256`:
- loader registered `STAAD Prep Bridge` successfully;
- real Ruby exporter produced Neutral JSON from a root edge + translated Group + nested rotated Component fixture;
- exported metadata preserved `FrameGroup` and `NestedBeamInstance` paths;
- real Neutral JSON reported 3 segments, `source_unit=in`, `source_axis=Z-UP`;
- Python `NeutralReader -> T06 -> T07` produced exactly 4 nodes / 3 members;
- hand-checked 120 in span mapped to exactly 3.048 m in canonical space.

### Verification evidence

Fresh final gate must remain green before commit:
- unit suite;
- all UI tests including Qt/VTK smoke;
- integration suite including Direct DXF and SketchUp-neutral pipeline;
- Ruff;
- targeted mypy for new/changed T15 Python modules;
- `git diff --check`;
- runtime SketchUp evidence above.

Known non-T15 typing debt: including `dxf_reader.py` in strict mypy exposes pre-existing ezdxf typing errors (`readfile`, `DXFGraphic.is_3d_polyline`, `vertices`, untyped helper). T15 changes only the one-line `source_axis="Z-UP"` behavior there; targeted T15 modules are type-clean.

## Next Task

**T16 — SketchUp-style Navigation + Selection Foundation**

Risk: STANDARD.

Do not start T16 until the user explicitly continues after the T15 commit/checkpoint.

## T24 cleanup boundary

T24 runs only after T23 acceptance. It moves only verified-unused/superseded files into project-local `DEL/`, writes `DEL/UNUSED_FILES_MANIFEST.md`, and never deletes files. Final deletion is user-controlled.
