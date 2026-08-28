# WORKFLOW

## A. User workflow — V1

```text
1. Open project
2. Import SKP (primary) or DXF (fallback)
3. Confirm unit + model extents
4. Verify one known/reference length
5. Inspect validation summary
6. Resolve geometry/topology issues
7. Confirm expected structure count
8. Normalize member incidence/local-X direction
9. Renumber nodes/members
10. Run final validation
11. Export .STD
12. Open in STAAD.Pro and start section/load/design work
```

## B. Import workflow

```text
Source file
  -> adapter read
  -> source metadata/unit
  -> coordinate transform to Y-Up
  -> canonical nodes/members
  -> initial validation
  -> render
```

Importer must not silently merge, split, or delete structural geometry.

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
Issue Console row
 -> click issue
 -> zoom/highlight
 -> show properties/context
 -> recommended actions
 -> user chooses action
 -> execute RepairCommand
 -> record audit
 -> revalidate affected scope
 -> refresh issue/status
```

Examples:

### Near nodes
`Inspect -> Measure gap -> Merge / Snap / Ignore`

### Orphan node
`Inspect -> Delete / Connect / Ignore`

### Detached structure
`Isolate -> show closest candidate connection -> Merge/Connect where appropriate -> recompute structures`

### Crossing without node
`Inspect -> Split at intersection -> recompute topology`

### Short member
`Inspect length -> Delete / Keep`

### Wrong member direction
`Show local-X arrow -> Reverse -> revalidate`

## F. Structure-count workflow

1. Calculate connected components.
2. Display total structures.
3. Display nodes/members per structure.
4. Select/isolate any structure.
5. For detached structures, calculate nearby candidate connection points without auto-connecting them.
6. User decides repair.
7. Recalculate component count.

## G. Normalize workflow

Normalization happens after topology cleanup.

```text
Topology clean
 -> classify member orientation
 -> preview direction changes
 -> reverse incidence where required
 -> show local-X arrows
 -> validate direction consistency
```

## H. Renumber workflow

Renumber happens after cleanup and normalization.

```text
Clean topology
 -> deterministic node sort
 -> assign node IDs
 -> deterministic member classification/sort
 -> assign member IDs
 -> update references atomically
 -> audit mapping old -> new
```

## I. Final export workflow

Normal export requires critical validation PASS.

Pre-export summary:
- source file,
- canonical unit,
- reference-length status,
- model extents,
- nodes/members,
- structure count,
- critical issues = 0,
- normalization status,
- numbering status.

Then:

`Canonical Model -> STAAD exporter -> .STD -> export report`

Exporter must not modify or repair the model.

## J. Real-project feedback loop

After V1 begins real use:

`Real project -> observed pain point -> small patch -> targeted regression fixture -> release`

Do not redesign the entire application for each new case. Add patches around stable canonical interfaces.
