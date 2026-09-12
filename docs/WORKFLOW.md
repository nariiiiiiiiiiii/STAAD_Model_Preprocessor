## A. User workflow — V1

Accepted package checkpoint (historical, 2026-09-01): agreed source behavior was user accepted and full source
verification is complete. The user explicitly authorized compile step 1 and Nuitka produced a fresh
standalone build. `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` remains historical; portable assembly and ZIP
creation are complete under `dist/post-t22-refresh-save-final/`. Package-only verification is
**7/7 PASS**; real package acceptance is **PASS** (2026-08-31), and T23 acceptance is **PASS by user report** (2026-09-01). T24 inventory, reference/evidence mapping, manifest review, the approved Step 4 move, post-move reference scan, targeted verification, and final documentation synchronization are complete. T25 storage audit approved moves are complete; the post-T24/T25 map is `docs/WORKTREE_MINDMAP.md` and storage evidence is `artifacts/cleanup/storage-audit-20260901.md`.
T26 then moved regenerable `.tmp`/`.cache` contents and 22 historical clean worktrees into
`DEL/t26-storage-cleanup-20260901/`; deletion remains user-controlled.
T27 allows explicit user-selected SketchUp input/output locations and STD export destinations outside
the project; implicit runtime paths remain project-local. Project JSON may now be opened from any folder and saved back to that path; first Save for a new model remains in the default Projects area. The accepted package is
assembled under `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/`.

### Active source follow-up — 2026-09-12

The approved source version is `0.2.0`; source checkpoints cover SKP-stem/date JSON names, the
selected application icon, free Project JSON Open with Save-back, and multi-issue Quick Fix with
existing intersection splitting. STRICT / Full TDD was approved and completed for the topology
batch. Current source evidence is **345 unit+integration passed**, **1 skipped**, **3 package gates
deselected**, and **26/26 affected UI passed**, with Ruff and strict mypy clean. The accepted
portable package remains `0.1.0`; no new RBZ or Windows executable is retained. User testing and
separate compile/package authorization remain pending.

A legacy integration test briefly generated a transient `0.2.0` RBZ; the file was removed. It also
refreshed pre-existing ignored `build/sketchup/stage/` copies, which remain in place. The RBZ/package
fixtures have since been changed so ordinary full-suite runs do not write build artifacts.

Post-CP5 viewport feedback added Crop to Select marquee mode and renamed the previous camera action
to Zoom in Select. The non-renderer tests are **13/13 PASS**; the owner manually reports the viewport
flow works (2026-09-13), while the automated real-VTK smoke remains unverified after a Win32 OpenGL /
Python Application Error. The owner reproduced Save Blocked for an external Project JSON destination;
after explicit refreshed-plan approval, First Save/Save As now use user-selected paths with atomic
serialization. The focused Save/import/export/path regression is **58/58 PASS**, Ruff PASS, and strict
mypy reports **0 issues**. Manual external Save acceptance is pending; no compile has started.


```text
1. Open project
2. Bring geometry in through SketchUp `Send to STAAD Prep` or Direct DXF Import
3. Confirm unit + model extents
4. Verify one known/reference length
5. Inspect validation summary
6. Resolve geometry/topology issues with Quick Fix and/or Manual Edit
7. Confirm expected structure count
8. Normalize/control member incidence/local-X direction
9. Renumber nodes/members
10. Run final READY validation
11. Export .STD
12. Open in STAAD.Pro and start section/load/design work
```

### Development iteration and pre-compile approval gate

For post-T22 corrections, develop and test from source before rebuilding the Windows executable:

```text
Choose one user-visible correction
 -> implement in source
 -> run focused tests/static checks
 -> launch the development application from the project virtual environment
 -> report the exact behavior ready for user testing
 -> wait for the user to test, comment, and explicitly instruct the next step
 -> repeat for the next correction
 -> run the agreed source-level regression
 -> STOP and request explicit user approval to compile
 -> only after approval: build Nuitka standalone, assemble folder/ZIP, and run package gates
```

Rules:

- Do not rebuild Nuitka or create a replacement standalone folder/ZIP during ordinary UI iteration.
- Work through corrections incrementally; do not silently advance to the next correction while the
  user is testing the current one.
- Source-level acceptance is a separate checkpoint from package acceptance.
- Even after every source test passes, stop and wait before compilation. A message such as
  `compile`, `build the EXE`, or an equally explicit instruction is required.
- After compilation, verify executable-only concerns: bundled Qt/VTK dependencies, portable paths,
  relocation, no-Python launch, manifest/hash, and extracted-ZIP launch.
- If a defect can only be reproduced in the compiled executable, explain that constraint and still
  obtain approval before rebuilding.
- This gate does not replace the mandatory STRICT / Full TDD approval gate for high-risk topology,
  coordinate, automatic-repair, or `.STD`-semantics changes.

## B. Import workflow

```text
Route A — SketchUp
Active SketchUp model
  -> Ruby Extension `Send to STAAD Prep`
  -> Neutral JSON v1 in project-local inbox
  -> neutral reader -> ImportBatch

Route B — Direct DXF
DXF file
  -> DxfReader -> ImportBatch

Both routes
  -> source metadata/unit
  -> T06 coordinate/unit transform to metre/Y-Up
  -> T07 canonical topology
  -> initial validation
  -> render
```

Importer/exporter bridge stages must not silently merge, split, delete, or repair structural geometry. Direct DXF remains usable when SketchUp/extension is unavailable. Direct `.skp` C-SDK import is future optional.

## C. Unit / dimension workflow

1. Show detected/source unit and canonical unit.
2. Show overall model extents.
3. User activates Reference Length.
4. Select two nodes/points.
5. App shows measured length.
6. User enters known physical length.
7. App reports PASS or likely scale mismatch.
8. If scale correction is requested, preview the factor before applying.
9. Apply through a repair command and record it.

## D. Validation workflow

```text
Validate
 -> Unit/scale sanity
 -> Coordinate sanity
 -> Node quality
 -> Member quality
 -> Intersection/gap checks
 -> Connected components
 -> Direction/numbering readiness
 -> Issue list
```

Severity:
- ERROR: blocks normal export.
- WARNING: requires review but may not block export depending on rule.
- INFO: audit/context only.

## E. Issue repair workflow

```text
Issue Console row(s)
 -> select one issue or several issue rows
 -> highlight the selected entities; show one issue or a multi-issue summary
 -> preflight current issues and typed mutation footprints
 -> fail closed before mutation if any selected fix is unsupported, stale, or overlapping
 -> user chooses Quick Fix or Manual Edit
 -> one Apply/OK dialog executes one CompositeRepair for an accepted batch
 -> one audit/history operation; one Undo restores the complete pre-batch graph
 -> revalidate and refresh the issue/status/viewport
```

Examples:

### Near nodes
`Inspect -> Measure gap -> Merge / Snap / Manual Move-Snap / Ignore`

### Orphan node
`Inspect -> Delete / Draw Member / Move-Snap / Ignore`

### Detached structure
`Isolate -> show closest candidate connection -> user chooses connection -> recompute structures`

### Crossing without node
`Inspect -> Split at intersection -> recompute topology`

### Short member
`Inspect length -> Delete / Keep`

### Duplicate overlapping member
`Cycle exact member under cursor -> select unwanted member -> Delete -> revalidate`

### Wrong member direction
`Show local-X arrow -> Auto Fix / Flip / Set Start (i) -> revalidate`

## F. SketchUp-style navigation workflow

Navigation is always available, including while an edit tool is active:

```text
Middle Mouse drag         -> Orbit
Shift + Middle Mouse drag -> Pan
Mouse Wheel               -> Zoom
Shift + Z                 -> Fit / Zoom Extents
```

Navigation temporarily overrides the edit gesture but does not cancel it. Releasing Middle Mouse returns to the active edit preview.

Select mode never moves structural geometry.

## G. Selection / identity workflow

1. Default mode = `SELECT`.
2. Selection filter chooses `Node`, `Member`, or both.
3. Left click selects exact entity.
4. Ctrl+click toggles additive selection.
5. If entities overlap, cycle/choose exact candidate.
6. Double-click focuses/zooms selected entity.
7. Optional labels show Node Number, Member Number, Local-X, Coordinates.
8. Context menu shows only valid operations for the selected entity.

## H. Manual geometry editing workflow

All manual geometry edits use explicit modes and ghost previews.

### Draw missing Member

```text
DRAW MEMBER
 -> click Start Node
 -> ghost member follows inference target
 -> click existing End Node OR valid new-node position
 -> build command/composite
 -> commit through RepairHistory
 -> revalidate + rerender
```

If a new endpoint is created, node+member creation commits atomically. Failure leaves no orphan new node.

### Move / Snap Node

```text
MOVE / SNAP NODE
 -> left-drag selected Node
 -> ghost preview only
 -> release in valid free space = MoveNode
 -> release on existing Node = Merge/Snap semantics
 -> commit
 -> revalidate + rerender
```

`Esc` cancels without changing canonical coordinates.

### Delete selected Node/Member

```text
Select exact entity/entities
 -> Delete toolbar / keyboard Delete / right-click Delete Selected
 -> destructive confirmation
 -> one Delete command or atomic delete-selection composite
 -> revalidate + rerender
```

Deleting one of multiple overlapping members affects only the selected UUID.
An orphan Node can be deleted either from its Issue Console Quick Fix or the same selection-delete
path. A Node with any unselected incident Member is rejected instead of silently changing topology.

### Split Member

Selected Member can create a canonical split:
- midpoint,
- percentage,
- exact distance from Start,
- detected intersection.

The split is atomic and undoable.

### Merge Members

Select exactly two collinear Members sharing one degree-2 Node, then choose `Merge Members`.
The lower deterministic Member UUID is retained with its number/source/group, the other Member and
shared Node are removed, duplicate incidence is rejected, and one Undo restores the exact graph.

## I. Snap / inference workflow

Manual draw/move/create uses canonical-space inference:
- Existing Node,
- Member endpoint,
- Member midpoint,
- Member intersection,
- X axis,
- STAAD Y axis (Vertical),
- Z axis,
- active working plane/grid.

Axis locks:

```text
X -> constrain to canonical X
Y -> constrain to canonical Y (Vertical)
Z -> constrain to canonical Z
Esc -> cancel edit/lock
```

If a valid 3D position cannot be inferred, the app shows preview as non-committable rather than guessing depth.

## J. Create Node workflow

### Click / Snap

`CREATE NODE -> valid inference point -> ghost preview -> Create`

- existing Node hit: use existing; no duplicate Node;
- Member hit: split Member correctly;
- Intersection hit: create/split affected topology atomically;
- free-space hit: requires active working plane/inference.

### Exact XYZ

Dialog uses canonical metre coordinates:
- STAAD X
- STAAD Y (Vertical)
- STAAD Z

Preview appears before commit.

### Relative to selected Node

Example:

```text
Reference Node: 21
X [ + ] [ 1.000 ] m
Y [ - ] [ 0.000 ] m
Z [ + ] [ 0.000 ] m

[ ] Create Member
```

The dialog shows reference and result XYZ. If `Create Member` is checked, `Reference Node -> New Node` is created atomically with the new node.

If result matches an existing Node within tolerance, the app reports that Node and asks whether to use it or cancel; it never silently creates a duplicate.

### Translational Repeat

```text
Reference Node
 + ΔX/ΔY/ΔZ per step
 + Repeat Count (new positions only)
 + optional Create Member
 + Connection Mode
 -> Preview all ghost Nodes/Members
 -> resolve existing-node collisions
 -> one atomic commit
```

Connection modes:
- `Connect Consecutive Nodes` — default;
- `Connect From Reference Node`.

One Undo reverts the entire repeat.

For selected Members, use the same command with no selected Nodes. The dialog reports selected
Members, source/new Node counts, new Member count, and collisions. Shared targets between repeat
steps reuse one generated Node; existing-model collisions require `Use Existing Node` or cancel.

### View and selection recovery

- `Reset View` restores the canonical STAAD Y-up isometric camera and fits the model.
- `Crop to Selection` frames selected Nodes/Members without hiding or mutating model data.
- right-click empty space selects Node/Member/both mode or invokes Fit/Reset.
- the active edit/filter action stays checked; Properties follows the current selection.
- expand `Nodes (N)` or `Members (N)` in Project Explorer to browse STAAD-numbered entities;
  click one row to highlight one entity, or click the group row to highlight all of that type.
- a single-entity Properties view shows engineering numbers and coordinates in metres; Member
  Properties also show endpoint coordinates, length, and Group / Layer. UUID/source fields stay hidden.

## K. Structure-count workflow

1. Calculate connected components.
2. Display total structures.
3. Display nodes/members per structure.
4. Select/isolate any structure.
5. For detached structures, calculate nearby candidate connection points without auto-connecting them.
6. User decides repair.
7. Recalculate component count.

## L. Member direction workflow

Normalization happens after topology cleanup, but the user can also correct selected members explicitly.

```text
Topology clean
 -> show Local-X arrows
 -> Auto Fix All / Auto Fix Selected
 OR Flip Selected
 OR Set Direction: click endpoint that shall be Start (i)
 -> incidence/local-X changes only
 -> validate direction consistency
```

No coordinate movement occurs during Set Direction.

## M. Numbering workflow

Renumber happens after cleanup/direction review.

```text
Clean canonical model
 -> Auto Node Number / Auto Member Number / Auto Number All
 -> preview UUID: Old -> New mapping
 -> apply deterministic numbering
 -> preserve UUID keys and member endpoint UUID references
 -> audit mapping
```

Numbering changes only STAAD-facing `.number` attributes.

## N. Final export workflow

Normal export requires critical validation PASS / READY gate.

Pre-export summary:
- source file,
- canonical unit,
- reference-length status,
- model extents,
- nodes/members,
- structure count,
- critical issues = 0,
- direction status,
- numbering status.

Then:

`Canonical Model -> STAAD exporter -> .STD -> export report`

Exporter must not modify, renumber, or repair the model.

## O. Real-project feedback loop

After V1 begins real use:

`Real project -> observed pain point -> narrowly scoped patch -> targeted regression fixture -> release`

Do not turn later feedback into a full CAD rewrite. Add patches around stable canonical/editing interfaces.

## K. Post-acceptance cleanup workflow (T24)

After T23 succeeds:

```text
Accepted V1 workspace
 -> inventory files
 -> reference/import/config scan
 -> classify KEEP / REGENERABLE / SUPERSEDED / UNUSED
 -> preview quarantine manifest
 -> move verified-unused items to project-local DEL/
 -> regression/lint/type/build/package verification
 -> final manifest + HANDOFF
 -> user reviews DEL/ and deletes separately if desired
```

No file is deleted by T24. A candidate with uncertain ownership/reference remains in place.


## 2026-08-31 source handoff checkpoint

- User-accepted source behavior before handoff: Member Translational Repeat preview, engineering Properties, Project Explorer entity selection, Member Local Axes XYZ, three-row toolbar with visible View controls, Save/Open Project JSON, import-derived save filename, `SAVED` / `NOT SAVED` title state, Ctrl+S save confirmation, readable Node/Member/Coordinate labels, Global Axis X/Y/Z labels, and Exit confirmation UI.
- Latest real-user defect: clicking window `X` and choosing `Yes` did not close the application.
- Latest source fix: exit dialog now compares the native Qt button result with equality (`==`) and the accepted close path delegates to `QMainWindow.closeEvent()`.
- Exit regression evidence after fix: `tests/ui/test_exit_confirmation.py` **4/4 PASS**; Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Status of latest close fix: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**.
- Full source verification is **COMPLETE**: **332/332 source unit+integration PASS**, **102/102
  lightweight UI PASS**, **38/38 isolated VTK UI PASS**, six real Windows source smokes exit 0,
  focused Save/Open **5/5 PASS**, Ruff PASS, strict mypy 0 issues, and diff check PASS.
- The package-only verification suite was run after the user authorized step 3: **7/7 PASS**.
  Nuitka compilation, portable assembly, and ZIP creation completed under
  `dist/post-t22-refresh-save-final/`; real package acceptance is **PASS** (2026-08-31).

## P. Project JSON Open/Save workflow

```text
Open Project JSON
 -> start in the default Projects directory
 -> user may navigate to and select any valid JSON file
 -> parse and validate the project schema
 -> retain the selected path
 -> Save writes back to that selected file through a sibling atomic temp file
```

First Save for a new or imported model remains in the default Projects directory (`Data/Projects/`
in the portable app; the project-local Projects directory in development). External Open/Save
behavior is source-verified; package acceptance awaits a separately authorized build.
