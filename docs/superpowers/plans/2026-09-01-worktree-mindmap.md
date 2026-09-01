# Worktree Mindmap and File-Relationship Map Implementation Plan

> **For agentic workers:** This is a post-T24 documentation deliverable. Do not execute it until T24 cleanup, reference verification, regression checks, and the T24 commit are complete.

**Goal:** Create one canonical Markdown mindmap that explains the complete project worktree, every current file or protected generated area, and the relationships needed for future development and patches.

**Architecture:** Generate the map from the final post-T24 worktree state rather than relying only on manually remembered files. The deliverable will combine a Mermaid relationship map, a complete file/folder catalog, source-import relationships, test coverage links, documentation/plan links, runtime-data flow, build/package flow, worktree/branch state, and lifecycle status (`KEEP`, `REGENERABLE`, `SUPERSEDED`, `QUARANTINED`). The SketchUp `.rbz` will be inspected as an archive with its internal files, entrypoints, callbacks, UI assets, version contract, and JSON handoff mapped explicitly. Ambiguous relationships will be marked for review instead of guessed.

**Tech Stack:** Git file inventory, `rg` reference scans, Python AST/import inspection, Markdown, Mermaid, existing project path/build/package conventions.

**Output:** `docs/WORKTREE_MINDMAP.md` — created and synchronized in the active worktree.
**Prerequisite:** T24 complete, including the final `DEL/UNUSED_FILES_MANIFEST.md`, post-move reference scan, verification, and commit.

## Global Constraints

- Do not start before T24 is complete and its move set is committed.
- Protect `.git/`, active `.worktrees/`, `.venv/`, required `vendor/` SDK contents, acceptance evidence, and all live source/runtime paths.
- Include tracked files and relevant project-local generated/protected directories; do not silently omit ignored files that affect development or release behavior.
- Treat `extensions/` source and the generated `.rbz` as separate but related nodes; document the archive member list and source-to-member mapping.
- Map the RBZ runtime contract end-to-end: SketchUp UI/dialog → Ruby callbacks → geometry traversal/export → compact JSON → `Data/Inbox/SketchUp` → application import.
- Record RBZ version/schema/filename contracts, build script inputs/outputs, install-facing entrypoints, and safe future extension points without changing them during mindmap generation.
- Do not infer a relationship from filename similarity alone; record the actual import, path, build, test, or documentation evidence.
- Preserve historical/superseded records and distinguish them from the current accepted release.
- The mindmap is documentation and navigation only; it must not alter application behavior or structural-model logic.

## Current preparation already completed

- `docs/INDEX.md` exists as a project navigation index.
- `docs/ARCHITECTURE.md` documents the major source/runtime boundaries.
- `docs/HANDOFF.md` records task state, acceptance, artifacts, and resume points.
- `docs/TASK_BOARD.md` and the master plan record T01–T24 status.
- T24 Step 1 inventory is recorded in `artifacts/cleanup/t24-inventory-20260901.md`.
- T24 is complete and the complete mindmap now exists; the original gate is satisfied.

## Planned file structure

**Files:**

- Create: `docs/WORKTREE_MINDMAP.md` — canonical human-readable map and file catalog.
- Optional create: `scripts/generate_worktree_mindmap.py` — deterministic regeneration helper if the final implementation benefits from repeat updates.
- Modify: `docs/INDEX.md` — link the canonical mindmap and record its coverage/date.
- Modify: `docs/HANDOFF.md` — record generation evidence, coverage counts, known ambiguities, and resume instructions.
- Modify: `docs/TASK_BOARD.md` and `docs/CHECKLIST.md` — mark the deliverable complete only after its self-check passes.

## Planned execution

### Task 1: Freeze the post-T24 source state — COMPLETE

- [x] Confirm T24 move set, manifest, post-move reference scan, regression checks, and commit are complete.
- [x] Record the exact commit, branch, worktree path, and date at the top of the mindmap.

### Task 2: Build the complete inventory — COMPLETE

- [x] Enumerate every tracked file with `git ls-files`.
- [x] Enumerate relevant ignored/generated/protected directories: `build/`, `dist/`, `artifacts/`, `.tmp/`, `.cache/`, `.logs/`, `DEL/`, `.venv/`, `vendor/`, and active `.worktrees/`.
- [x] Assign each entry a stable category, owner/role, lifecycle status, and protection reason.
- [x] Include quarantined files from `DEL/UNUSED_FILES_MANIFEST.md` without presenting them as current source.

### Task 3: Derive source and test relationships — COMPLETE

- [x] Parse Python imports for `src/` and identify package/module boundaries.
- [x] Link each test file to the source modules, fixtures, scripts, or runtime paths it exercises.
- [x] Link smoke/build/package scripts to the executable, RBZ, manifest, ZIP, and runtime `Data/` outputs.
- [x] Record high-risk boundaries: coordinate/unit conversion, topology/repair commands, `.STD` export, and acceptance gates.

### Task 4: Reverse-map the SketchUp RBZ contract — COMPLETE

- [x] Enumerate the RBZ archive members and map each member to its source file under `extensions/` or to an intentionally generated packaging entry.
- [x] Identify the RBZ loader/registration entrypoint, extension metadata, HtmlDialog/UI assets, callback names, and Ruby modules/classes.
- [x] Map the callback flow from user action to geometry traversal, JSON serialization, atomic write, output filename, and inbox destination.
- [x] Record source units/axis, JSON schema/protocol version, compact filename convention, portable inbox path, legacy development inbox path, and version-matching rules.
- [x] Link RBZ tests, builder script, package manifest entry, installation documentation, and future patch points.

### Task 5: Derive documentation and workflow relationships — COMPLETE

- [x] Scan Markdown/code/config references with `rg` and link specs to plans, plans to source/tests, and handoff/checklist/index to evidence.
- [x] Map the operational workflow: SketchUp/DXF input → Neutral JSON → model/repair/edit → validation/READY → `.STD`/report → portable package → T23 acceptance → T24 quarantine.
- [x] Map runtime writable paths and the CWD/compiled-root boundary, including `Data/Inbox/SketchUp`, `Data/Projects`, and development `artifacts/` paths.

### Task 6: Write the canonical mindmap — COMPLETE

- [x] Add a Mermaid graph showing worktree/branch, application layers, data flow, verification, packaging, acceptance, and quarantine relationships.
- [x] Add a dedicated Mermaid RBZ subgraph showing extension source, archive members, SketchUp callbacks/UI, JSON output, inbox, and application import.
- [x] Add a complete tracked-file catalog and generated/protected group map with role and lifecycle status.
- [x] Add an RBZ archive table with member path, source mapping, runtime role, build source, version/schema contract, and future patch notes.
- [x] Add sections for completed/current/protected/quarantined material and future patch entry points.
- [x] Mark known feature/task status without silently promoting historical evidence.

### Task 7: Self-check and synchronize — COMPLETE

- [x] Verify every tracked file is represented exactly once or explicitly covered by a documented group rule.
- [x] Verify every linked current path exists and every quarantined path resolves through the manifest/restore map.
- [x] Scan for broken or stale references and resolve or flag each ambiguity.
- [x] Validate Mermaid blocks and Markdown links as far as the available local tooling permits.
- [x] Verify the RBZ member list matches the builder output and that every documented callback/path/schema claim has source or test evidence.
- [x] Update `docs/INDEX.md`, `docs/HANDOFF.md`, `docs/TASK_BOARD.md`, and `docs/CHECKLIST.md` with counts, commit, and verification results.
- [x] Commit the mindmap and synchronized documentation as a separate maintenance checkpoint.

Implementation note: Tasks 1–7 content, self-check work, and the separate documentation checkpoint
are complete. No compile or new implementation task is part of this plan.

## Definition of done

The project has one navigable `docs/WORKTREE_MINDMAP.md` that a future maintainer can use to locate
any source, test, script, document, fixture, runtime path, build artifact, package artifact, or
quarantined file, understand what depends on it, and know whether it is already implemented,
accepted, regenerable, superseded, protected, or safe to consider for a later patch.
