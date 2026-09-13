# Project Storage Audit and Safe Cleanup Plan
> Historical plan record: task-date checkboxes and status are preserved as recorded; for current status see [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

> **For agentic workers:** Use this plan task-by-task with a fresh inventory and a user review gate before any move or deletion.

**Goal:** Re-audit the complete project worktree, identify unused/superseded storage without guessing, and isolate approved old archives/packages so the user can reclaim disk space safely.

**Architecture:** Treat source, tests, active build inputs, the accepted portable package, runtime data, evidence, caches, and historical releases as separate ownership classes. First produce a fresh inventory and reference map; then move only exact approved old generated items into a project-local quarantine. Moving does not free disk space, so final deletion remains a separate user-controlled action after the quarantine review.

**Tech Stack:** PowerShell inventory, Git tracked-file inspection, rg reference scans, existing package/RBZ manifests, Markdown evidence, and project-local `DEL/` quarantine.

**Spec:** `AGENTS.md`, `docs/PROJECT_RULES.md`, `docs/WORKTREE_MINDMAP.md`, and T24 cleanup rules.

## Global Constraints

- Canonical root: the repository clone root containing `.git` and the active `.worktrees/` directory.
- Active worktree: `.worktrees/task-22-portable-packaging`.
- All generated, staged, moved, and audit files remain inside the canonical project root.
- Never move or delete `.git`, active `.worktrees`, `.venv`, source, tests, native code, extensions, packaging instructions, required vendor SDK, current build inputs, current accepted package, or acceptance evidence without explicit separate approval.
- Move-only quarantine is recoverable; no deletion is performed by the audit.
- The accepted release is `dist/post-t22-refresh-save-final/`.
- Current RBZ build input is `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz`.
- No compile, package rebuild, or application behavior change is part of this cleanup.

## Planned execution

### Task 1: Freeze and inventory the current worktree — COMPLETE

- [x] Confirm the user-deleted `DEL/UNUSED_FILES_MANIFEST.md` state without restoring or overwriting user files.
- [x] Record branch, HEAD, worktree, tracked/untracked status, and exact top-level project directories.
- [x] Enumerate archive files and standalone package roots under `dist/`, `build/`, `artifacts/`, and any existing quarantine.
- [x] Measure candidate file counts and byte sizes without recursively scanning protected cache trees unless needed.

### Task 2: Classify every candidate — COMPLETE

- [x] KEEP: current source, tests, docs, scripts, current package, current RBZ, build inputs, and acceptance evidence.
- [x] REGENERABLE: stale build output, test caches, temporary reports, and duplicate generated evidence only when no live reference or recovery value remains.
- [x] SUPERSEDED: older standalone folders/ZIPs whose accepted successor is verified and whose references are historical only.
- [x] QUARANTINED: items moved under `DEL/t25-storage-audit-20260901/`.
- [x] REVIEW REQUIRED: high-volume `.tmp/` and `.cache/` remain explicitly outside this move.

### Task 3: Reference and integrity recheck — COMPLETE

- [x] Search source, tests, scripts, configs, and current docs for every candidate path.
- [x] Distinguish historical documentation links from live build/runtime inputs.
- [x] Confirm the current package manifest, executable, RBZ, and ZIP remain internally consistent.
- [x] Confirm no candidate is the only copy of a user model, validation report, or restoration evidence.
- [x] Write `artifacts/cleanup/storage-audit-20260901.md` with evidence, classification, and proposed action.

### Task 4: User review gate — COMPLETE

- [x] Present the exact candidate list, sizes, reasons, references, and proposed quarantine destinations.
- [x] Receive user approval for the exact six-item move set; no deletion was requested for caches/data.
- [x] Do not infer approval for `.tmp/`, `.cache/`, `.logs/`, `artifacts/projects/`, or user data from a request about old standalone packages.

### Task 5: Recoverable move only — COMPLETE

- [x] Recreate/update `DEL/UNUSED_FILES_MANIFEST.md` with the new audit date and restore paths.
- [x] Move only the exact approved superseded generated folders/files under a dated `DEL/t25-storage-audit-20260901/` directory.
- [x] Preserve relative structure and never overwrite an existing destination.
- [x] Re-scan references and verify current release/RBZ/package integrity after the move.

### Task 6: Final space-reduction decision

- [ ] Report that quarantine alone does not reduce used disk space.
- [ ] Leave final deletion to the user after they inspect the manifest and quarantine.
- [ ] If the user explicitly authorizes deletion later, resolve exact paths first and use a separate confirmation/checkpoint.

### Task 7: Documentation checkpoint

- [x] Update `README.md`, `docs/INDEX.md`, `docs/HANDOFF.md`, `docs/TASK_BOARD.md`, `docs/CHECKLIST.md`, and `docs/WORKTREE_MINDMAP.md` with the new audit result.
- [ ] Run `git diff --check`, verify required paths, and confirm no source/test/build behavior changed.
- [ ] Commit the audit and any approved move as a separate maintenance checkpoint, then stop for user review.

## Definition of done

The worktree has a fresh, evidence-backed classification of project storage; current runtime and
release inputs are protected; old packages are either explicitly quarantined with restore paths or
flagged for review; and no file is deleted or silently moved.
