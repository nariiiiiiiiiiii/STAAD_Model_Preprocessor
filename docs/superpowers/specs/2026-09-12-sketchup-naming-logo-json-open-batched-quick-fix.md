# Version, SketchUp Naming, App Icon, Open JSON, and Batched Quick Fix
> Historical design record: accepted behavior and tests are preserved as recorded; current status is in [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

**Date:** 2026-09-12

**Status:** Source checkpoints 1–5 are verified; uncompiled user acceptance and release builds remain pending

**Implementation plan:** [`../plans/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md`](../plans/2026-09-12-sketchup-naming-logo-json-open-batched-quick-fix.md)

## Proposed version contract

The previous accepted app/package/SketchUp extension release is `0.1.0`. The owner approved **`0.2.0`** on 2026-09-12 as the next additive usability feature release, without asserting final V1 acceptance. The source contract is now synchronized: canonical Python version, package `__version__` export, and Ruby extension metadata all resolve to `0.2.0`. The version-contract test passes **6/6**, Ruff passes, and strict mypy reports **0 issues** for the affected Python files. No `0.2.0` release RBZ/executable/package is retained; a transient RBZ from a legacy test was removed. Historical `0.1.0` records remain immutable evidence.

## Requirements

1. **SketchUp export naming (owner-confirmed):** JSON basename derives from the source `.skp` file and appends the local export date as `DDMMYYYY`: `<safe-source-stem>_<DDMMYYYY>.json`. Same-stem/day collisions append `_02`, `_03`, etc. For an unsaved model use its title, falling back to `Untitled`. Keep the `source_file` payload value unchanged. Source-contract test passes; Ruby/SketchUp runtime acceptance is still pending.
2. **Application/executable icon:** use exactly `LOGO/ChatGPT Image Sep 12, 2026, 06_17_26 PM.png` (1254×1254; black background, white structural mark, blue STAAD wordmark). Preserve the original. A byte-identical tracked copy now drives the Qt application/window icon and a validated multi-resolution Windows `.ico` generated under project-local build output. Source verification is **12/12 PASS** with Ruff and strict mypy passing; no Windows executable was rebuilt, so packaged runtime acceptance remains pending.
3. **Project JSON Open/Save (owner-confirmed):** allow opening a JSON file from any folder while retaining schema validation. Save writes back to that explicitly opened file. First Save for a newly imported/created project remains inside `Data/Projects/`. Stage atomic-save temporary files beside the destination so replacement stays on the same volume; remove the temporary sibling on success or failure.
4. **Multi-issue Quick Fix (STRICT approved/source-verified):** allow selecting several issues and applying supported non-conflicting fixes as one atomic, audited, undoable batch. Unsupported/stale/conflicting selections fail closed with a visible explanation; the batch is never silently filtered or partially applied.
5. **Intersection Quick Fix (source-verified):** expose existing `CROSSING_WITHOUT_NODE` repair in Quick Fix by routing to the current `build_split_selected_intersection()` command. Do not add or alter intersection-detection geometry/math.

## Atomicity and history contract

- A valid batch uses one `CompositeRepair`, one confirmation, one audit/history entry, and one refresh.
- One Undo restores the exact graph/revision from before the batch; Redo reapplies the batch.
- Plan all selected commands against the same unchanged starting model. Reject overlapping entity footprints (including incident members affected by a merge) before mutation.
- On any child-command failure, restore the complete pre-batch graph/revision and produce no success audit record.

## Constraints and boundaries

- No changes to coordinate conversion, validation thresholds/meaning, ReadyGate, `.STD` serialization, or geometry detection.
- Keep source changes in `.worktrees/task-22-portable-packaging`; preserve historical releases and the original logo.
- Implement and verify source behavior first. Stop for user testing before any Nuitka/RBZ/portable/ZIP build; a separate explicit compile/package instruction is required.
- Follow `AGENTS.md`: the batch Quick Fix/intersection topology work is HIGH-RISK and requires explicit STRICT / Full TDD approval before any tests or implementation for that scope.

## Acceptance evidence categories

- **Source evidence:** focused tests, lint/type checks, and diff review for each approved checkpoint.
- **User acceptance:** development app checks and real SketchUp behavior where source contracts alone cannot prove runtime behavior.
- **Package evidence:** only after separate compile/package authorization; do not call source verification a package pass.
