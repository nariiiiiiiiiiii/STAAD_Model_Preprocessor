# Worktree Mindmap and File-Relationship Map Implementation Plan

> **For agentic workers:** This is a post-T24 documentation deliverable. Do not execute it until T24 cleanup, reference verification, regression checks, and the T24 commit are complete.

**Goal:** Create one canonical Markdown mindmap that explains the complete project worktree, every current file or protected generated area, and the relationships needed for future development and patches.

**Architecture:** Generate the map from the final post-T24 worktree state rather than relying only on manually remembered files. The deliverable will combine a Mermaid relationship map, a complete file/folder catalog, source-import relationships, test coverage links, documentation/plan links, runtime-data flow, build/package flow, worktree/branch state, and lifecycle status (`KEEP`, `REGENERABLE`, `SUPERSEDED`, `QUARANTINED`). The SketchUp `.rbz` will be inspected as an archive with its internal files, entrypoints, callbacks, UI assets, version contract, and JSON handoff mapped explicitly. Ambiguous relationships will be marked for review instead of guessed.

**Tech Stack:** Git file inventory, `rg` reference scans, Python AST/import inspection, Markdown, Mermaid, existing project path/build/package conventions.

**Output:** `docs/WORKTREE_MINDMAP.md`
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
- The complete mindmap does **not** exist yet; it is intentionally gated until after T24.

## Planned file structure

**Files:**

- Create: `docs/WORKTREE_MINDMAP.md` — canonical human-readable map and file catalog.
- Optional create: `scripts/generate_worktree_mindmap.py` — deterministic regeneration helper if the final implementation benefits from repeat updates.
- Modify: `docs/INDEX.md` — link the canonical mindmap and record its coverage/date.
- Modify: `docs/HANDOFF.md` — record generation evidence, coverage counts, known ambiguities, and resume instructions.
- Modify: `docs/TASK_BOARD.md` and `docs/CHECKLIST.md` — mark the deliverable complete only after its self-check passes.

## Planned execution

### Task 1: Freeze the post-T24 source state

- [ ] Confirm T24 move set, manifest, post-move reference scan, regression checks, and commit are complete.
- [ ] Record the exact commit, branch, worktree path, and date at the top of the mindmap.

### Task 2: Build the complete inventory

- [ ] Enumerate every tracked file with `git ls-files`.
- [ ] Enumerate relevant ignored/generated/protected directories: `build/`, `dist/`, `artifacts/`, `.tmp/`, `.cache/`, `.logs/`, `DEL/`, `.venv/`, `vendor/`, and active `.worktrees/`.
- [ ] Assign each entry a stable category, owner/role, lifecycle status, and protection reason.
- [ ] Include quarantined files from `DEL/UNUSED_FILES_MANIFEST.md` without presenting them as current source.

### Task 3: Derive source and test relationships

- [ ] Parse Python imports for `src/` and identify package/module boundaries.
- [ ] Link each test file to the source modules, fixtures, scripts, or runtime paths it exercises.
- [ ] Link smoke/build/package scripts to the executable, RBZ, manifest, ZIP, and runtime `Data/` outputs.
- [ ] Record high-risk boundaries: coordinate/unit conversion, topology/repair commands, `.STD` export, and acceptance gates.

### Task 4: Reverse-map the SketchUp RBZ contract

- [ ] Enumerate the RBZ archive members and map each member to its source file under `extensions/` or to an intentionally generated packaging entry.
- [ ] Identify the RBZ loader/registration entrypoint, extension metadata, HtmlDialog/UI assets, callback names, and Ruby modules/classes.
- [ ] Map the callback flow from user action to geometry traversal, JSON serialization, atomic write, output filename, and inbox destination.
- [ ] Record source units/axis, JSON schema/protocol version, compact filename convention, portable inbox path, legacy development inbox path, and version-matching rules.
- [ ] Link RBZ tests, builder script, package manifest entry, installation documentation, and future patch points.

### Task 5: Derive documentation and workflow relationships

- [ ] Scan Markdown/code/config references with `rg` and link specs to plans, plans to source/tests, and handoff/checklist/index to evidence.
- [ ] Map the operational workflow: SketchUp/DXF input → Neutral JSON → model/repair/edit → validation/READY → `.STD`/report → portable package → T23 acceptance → T24 quarantine.
- [ ] Map runtime writable paths and the CWD/compiled-root boundary, including `Data/Inbox/SketchUp`, `Data/Projects`, and development `artifacts/` paths.

### Task 6: Write the canonical mindmap

- [ ] Add a Mermaid graph showing worktree/branch, application layers, data flow, verification, packaging, acceptance, and quarantine relationships.
- [ ] Add a dedicated Mermaid RBZ subgraph showing extension source, archive members, SketchUp callbacks/UI, JSON output, inbox, and application import.
- [ ] Add a complete catalog table with path, type, role, status, inbound relationships, outbound relationships, and evidence link.
- [ ] Add an RBZ archive table with member path, source mapping, runtime role, build source, version/schema contract, and future patch notes.
- [ ] Add separate sections for `DONE`, `CURRENT`, `REGENERABLE`, `SUPERSEDED`, `QUARANTINED`, `PROTECTED`, and `NEXT PATCH ENTRY POINTS`.
- [ ] Mark each known feature/task as implemented, user accepted, package verified, deferred, or blocked, without silently promoting historical evidence.

### Task 7: Self-check and synchronize

- [ ] Verify every tracked file is represented exactly once or explicitly covered by a documented group rule.
- [ ] Verify every linked current path exists and every quarantined path resolves through the manifest/restore map.
- [ ] Scan for broken or stale references and resolve or flag each ambiguity.
- [ ] Validate Mermaid blocks and Markdown links as far as the available local tooling permits.
- [ ] Verify the RBZ member list matches the builder output and that every documented callback/path/schema claim has source or test evidence.
- [ ] Update `docs/INDEX.md`, `docs/HANDOFF.md`, `docs/TASK_BOARD.md`, and `docs/CHECKLIST.md` with counts, commit, and verification results.
- [ ] Commit the mindmap and synchronized documentation as a separate maintenance checkpoint.

## Definition of done

The project has one navigable `docs/WORKTREE_MINDMAP.md` that a future maintainer can use to locate
any source, test, script, document, fixture, runtime path, build artifact, package artifact, or
quarantined file, understand what depends on it, and know whether it is already implemented,
accepted, regenerable, superseded, protected, or safe to consider for a later patch.
