# STAAD Model Preprocessor — Design

Date: 2026-08-28
Status: Written design awaiting user review.

## Purpose

Build a fast-to-develop Windows desktop preprocessor that removes the repetitive analytical-geometry cleanup normally performed after importing SketchUp/DXF geometry into STAAD.Pro.

The application prepares geometry; STAAD.Pro remains the analysis/design system.

## Product boundary

V1 performs:
- import,
- unit/scale/reference-length verification,
- canonical node/member topology creation,
- geometry/connectivity validation,
- user-driven repair,
- structure detection,
- member incidence normalization,
- deterministic renumbering,
- final validation,
- `.STD` export.

V1 does not perform structural analysis, section design, load generation, code checks, BIM, cloud, or AI design.

## Recommended architecture

A layered desktop application:

1. PySide6 UI.
2. PyVista/VTK 3D viewer.
3. Format-independent canonical structural model.
4. Import adapters:
   - DXF via ezdxf,
   - SKP via isolated C++ SketchUp C API helper.
5. Validator producing issue objects without mutation.
6. Command-based repair engine with audit/undo.
7. Deterministic normalization/numbering.
8. STAAD `.STD` export adapter.

All geometry semantics flow through the canonical model so import formats and UI can change without rewriting structural logic.

## Why this approach

Compared with building a mini CAD modeler, it directly attacks the user pain point and reuses SketchUp for modeling.

Compared with a DXF-only cleaner, native SKP input can preserve richer SketchUp hierarchy/metadata and removes one conversion step, while DXF remains a practical fallback and useful early implementation slice.

Compared with writing the entire app in C++, Python/PySide6 gives substantially faster iteration for UI, validation, repair, testing, and future patches. C++ is isolated to the native SKP SDK boundary.

## UI

The approved V1 UI is locked to the dark engineering desktop baseline documented in:
- `docs/UI_BASELINE.md`
- `docs/ui/main_dashboard.svg`
- `docs/ui/unit_check.svg`
- `docs/ui/issue_repair.svg`

The UI is issue-first: select an issue, zoom/highlight it, inspect context, apply a valid repair action, and immediately revalidate affected model state.

## Data flow

```text
SKP/DXF
 -> importer
 -> canonical Y-Up/metre model
 -> validators
 -> Issue list
 -> repair command(s)
 -> affected revalidation
 -> normalize
 -> renumber
 -> final validation
 -> STAAD `.STD`
```

Importers and exporters must not silently repair geometry.

## Error handling

- ERROR: blocks normal export.
- WARNING: requires inspection/review.
- INFO: audit/context.

Repairs affecting geometry/topology are explicit and logged.

The UI must expose selected IDs, coordinates, distances/lengths, and predicted repair impact where practical.

## Testing strategy

Risk-based:
- FAST: cosmetic UI/docs.
- STANDARD: ordinary UI/viewer/project plumbing/import orchestration.
- STRICT / Full TDD after explicit user approval for unit/axis transformations, topology mutation/repair, `.STD` semantics, and atomic renumber/reference rewriting.

Golden dirty-model fixtures are part of the V1 acceptance strategy.

## File boundary

Canonical root:

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

All project files, logs, cache, temp, build output, generated artifacts, and project-controlled dependency staging must stay inside this root. See `AGENTS.md` and `docs/PROJECT_RULES.md`.

## Delivery strategy

Optimize for earliest real-world usage rather than feature breadth.

Implement the pipeline vertically and add later functionality as patches after V1 is used on actual projects.

Canonical detailed documents:
- `docs/PROJECT_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/WORKFLOW.md`
- `docs/CHECKLIST.md`
- `docs/RISK_GATES.md`
- `docs/HANDOFF.md`
