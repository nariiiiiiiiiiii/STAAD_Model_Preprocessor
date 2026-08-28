# SketchUp Ruby Bridge + Direct DXF Import Design

Status: APPROVED FOR V1 on 2026-08-28.

## Goal

Keep two independent first-class V1 import routes into the same canonical analytical model:

1. **SketchUp Ruby Extension -> Neutral JSON v1 -> STAAD Model Preprocessor**
2. **Direct DXF Import -> STAAD Model Preprocessor**

Direct `.skp` reading through the SketchUp C SDK is no longer a V1 dependency. The T14 C++/C-SDK bridge remains preserved as a future optional backend if official SDK access becomes available.

## V1 import architecture

```text
SketchUp open model
   -> STAAD Prep Ruby Extension
   -> Neutral JSON v1
   -> project-local SketchUp inbox
   -> NeutralImportReader
   -> T06 unit/Z-Up -> metre/Y-Up
   -> T07 canonical topology
   -> canonical ProjectModel

DXF file
   -> DxfReader
   -> raw ImportBatch
   -> T06 unit/axis gate
   -> T07 canonical topology
   -> canonical ProjectModel
```

Both routes converge before validation/repair/manual editing. No downstream subsystem may depend on whether geometry came from SketchUp or DXF.

## SketchUp extension scope

The extension runs inside SketchUp and provides a command/toolbar action named approximately:

`Send to STAAD Prep`

V1 exporter responsibilities:
- inspect the active SketchUp model through the public SketchUp Ruby API;
- recursively walk supported edges inside model entities, groups, and component instances;
- compose nested instance transforms into source/world coordinates;
- preserve useful group/component/tag metadata;
- report source unit metadata;
- declare source axis as SketchUp Z-Up;
- emit Neutral JSON protocol version `1`;
- ignore faces/solids except insofar as their explicit edges are already present;
- never infer analytical centerlines from solid members.

## Handoff transport

V1 uses a **file-based project-local inbox**, not a local HTTP server.

Canonical inbox inside the application project root:

`artifacts/sketchup_bridge/inbox/`

The SketchUp extension stores/configures this inbox path once. `Send to STAAD Prep` writes a new neutral JSON file there using an atomic temporary-write -> rename pattern. The app imports a selected/new neutral envelope from that inbox.

Reasons for file-based transport in V1:
- deterministic and inspectable;
- easy to audit/replay in tests;
- no port/firewall/server lifecycle;
- compatible with the project-local generated-file rule;
- neutral JSON can be retained as acceptance evidence.

The extension source and `.rbz` package are developed/built under the project root. Installing the packaged extension into SketchUp's normal Plugins location is a user/product installation action, not project working data.

## Neutral JSON v1

Reuse the protocol boundary established in T14. Required top-level fields:
- `protocol_version`
- `source_file`
- `source_unit`
- `source_axis`
- `points`
- `segments`
- `groups`
- `tags`
- `warnings`

Each segment contains source-space/world-space start/end coordinates, stable source reference, tag/layer name where available, and group/component path metadata where available.

Protocol mismatch or malformed JSON fails closed.

## Direct DXF route

Direct DXF Import remains independent of SketchUp and the Ruby extension.

V1 supported raw DXF entities remain:
- `LINE`
- 3D `POLYLINE`
- `POINT`

DXF `$INSUNITS`, layer and source metadata are retained. Direct DXF must continue to work even when SketchUp is not installed or the Ruby extension is unavailable.

## Coordinate correctness

The Ruby extension must not implement STAAD coordinate conversion. It emits SketchUp source/world coordinates and metadata only.

Canonical conversion stays centralized in T06:

`STAAD(x,y,z) = (SKP.x, SKP.z, -SKP.y)`

Canonical unit remains metre and canonical axis remains Y-Up.

This preserves one tested coordinate authority for both future direct-SKP and current Ruby bridge paths.

## Safety / audit rules

- SketchUp exporter reports geometry; it does not repair topology.
- Importers do not silently merge/delete/split members.
- Neutral JSON is input evidence, not canonical truth.
- T07 topology builder remains the authority for endpoint merging/connectivity.
- All project-generated bridge files stay inside the canonical project root.
- The extension must not make network downloads or require the private C SDK.

## Future optional direct SKP backend

T14 native `skp_reader` and `SkpBridge` are retained but removed from the V1 critical path.

If official SketchUp C SDK access is granted later:

```text
.skp -> native skp_reader -> Neutral JSON v1 -> same NeutralImportReader
```

No canonical model, validator, repair, viewer, numbering or exporter redesign should be required.

## Acceptance for T15

T15 is complete when:
1. a hand-authored transform fixture proves nested source transforms exactly;
2. Ruby exporter contract emits protocol-v1 geometry/metadata in tests/static fixtures;
3. neutral JSON imports to `ImportBatch` and passes through T06/T07 to exact expected metre/Y-Up coordinates/topology;
4. direct DXF import regression remains green;
5. no C SDK is required for the V1 path;
6. project-local inbox boundary is enforced;
7. actual SketchUp runtime verification is performed when a local SketchUp environment is available, otherwise that runtime verification is explicitly deferred to real-project acceptance rather than falsely claimed.
