# Post-Compile Cleanup and GitHub Readiness Plan

> **For agentic workers:** Compile and recoverable storage moves are complete. Finish the local GitHub-readiness preflight, then stop before push/release. The owner must manually accept the exact 0.2.0 executable before it is described as a released/accepted build.

**Goal:** After an explicitly authorized and verified standalone build, quarantine verified obsolete outputs, synchronize all tracked Markdown, and locally prepare the repository for the owner to push to GitHub.

**Architecture:** Verify the explicitly authorized package first; then inventory/move recoverable obsolete outputs, synchronize tracked documentation and README, and run a no-push repository preflight.

**Tech Stack:** PowerShell, Git, Python 3.12, existing Nuitka/portable package scripts and package verification tests.

**Spec:** `docs/superpowers/specs/2026-09-13-post-compile-cleanup-github-readiness.md`

## Global Constraints

- Run Nuitka only after an explicit owner instruction. The owner authorized this post-compile sequence on 2026-09-13; the build is complete.
- Quarantine verified superseded outputs only after package gates pass and the owner requests the recoverable move. Manual testing of the exact executable remains a separate pre-release acceptance step.
- Move only verified-obsolete files under the canonical root to `DEL/`; never delete files.
- Moving to `DEL/` does not reclaim disk space; deletion remains a separate owner action.
- For this T28/T29 readiness sequence, license selection was outside scope. That boundary was later
  superseded by the separate T30 owner request; its local changes await review before commit/push.
- Preserve source, tests, current package/build evidence, required vendor files, and unrelated owner changes.
- Audit every tracked Markdown file; retain historical measurements and label them historical rather than rewriting history.

## Current gate (2026-09-13)

The owner authorized the sequence with “เริ่มทำได้” after requesting compile, old-output quarantine,
Markdown synchronization, and GitHub preparation. On `task/22-portable-packaging`, version `0.2.0`
was built in Nuitka standalone mode (`completion=yes`), the matching RBZ and portable folder/ZIP were
assembled, and package gates passed **9/9**. The owner has not yet reported manual launch/acceptance
of this exact compiled candidate. It is verified as a build candidate, not an accepted public
release. Superseded items were moved to `DEL/post-compile-cleanup-20260913/` after the package gates;
none were deleted.

### Task 1: Verify and identify the new standalone release

**Files / evidence:**
- Review: `src/staadprep/version.py`, `scripts/build_windows.ps1`, `scripts/assemble_portable.py`
- Review after build: `build/windows/final/nuitka-report.xml`, the new `dist/` folder, its
  `package-manifest.json`, and `docs/HANDOFF.md`
- Test: `tests/integration/test_packaged_paths.py` plus the existing package-only gates recorded by
  the build handoff

- [x] Confirm the build was separately authorized; verify Nuitka reports standalone completion and
  the output version matches the source and manifest.
- [x] Run manifest/hash verification, no-Python/different-CWD launch, relocation/reopen, and the
  package smoke required by the existing release plan. Record folder/ZIP sizes and SHA-256 values.
- [x] Keep the previous release recoverable until package gates passed, then move it to the
  owner-requested `DEL/` quarantine. Manual acceptance of the new candidate remains pending before
  public release; if the owner finds a defect, restore the archived build as needed.

### Task 2: Re-audit storage and quarantine verified obsolete outputs

**Files / evidence:**
- Review: project-root `build/`, `dist/`, `.tmp/`, `.cache/`, `artifacts/`, `vendor/`, `.worktrees/`,
  existing `DEL/`, and all references in tracked source/tests/scripts/docs
- Create/update: `artifacts/cleanup/post-compile-storage-audit.md`
- Update: `DEL/UNUSED_FILES_MANIFEST.md`

- [x] Produce a read-only size inventory with file count, bytes, version/hash where relevant, and
  KEEP / REGENERABLE / SUPERSEDED / UNUSED classification.
- [x] Search tracked source, tests, scripts, build configuration, manifests, and Markdown for every
  proposed move target. Keep anything referenced, required to reproduce the accepted build, or
  uncertain; report ambiguous candidates rather than moving them.
- [x] Move only confirmed old standalone folders/ZIPs and clearly obsolete generated attempts into a
  dated child of `DEL/`; leave the new accepted standalone and all current source/build evidence in
  their active paths. Preserve relative structure and record original/destination paths, sizes, and
  hashes in the manifest.
- [x] Verify moved release/archive items at the destination, source absence, new package presence,
  reference scan, and no-Python launch. Record that same-volume DEL movement is archival and does not
  free disk space.

### Task 3: Synchronize all Markdown and make README GitHub-facing

**Files:**
- Inventory: every `.md` under the canonical checkout and active T22 worktree, classifying tracked,
  untracked, historical `DEL/`, and generated/package-copy documents; exclude `.git/`, `.venv/`,
  dependency caches, build outputs, and extracted portable packages from the source-doc update set.
- Modify: every current-status and tracked Markdown file found by that inventory, including
  `README.md`, `docs/HANDOFF.md`, `docs/INDEX.md`, `docs/TASK_BOARD.md`, `docs/CHECKLIST.md`,
  `docs/WORKFLOW.md`, `docs/RISK_GATES.md`, `docs/ARCHITECTURE.md`, `docs/WORKTREE_MINDMAP.md`,
  `DEL/UNUSED_FILES_MANIFEST.md`, and applicable plan/spec documents

- [x] Inventory all **46 tracked Markdown** files in the active source worktree and classify current
  guides/status, durable specs/plans, historical evidence, and generated/archive copies. Update stale
  current claims and links; retain historical test/build facts with explicit historical context.
  Generated package/archive copies are intentionally not edited.
- [x] Rewrite the root README as a GitHub entry point: project purpose and non-analysis scope;
  features; supported source/portable workflows; prerequisites and source launch; verification
  commands; current release/version; limitations; and where to find deeper docs. Do not publish
  local absolute paths or claim a package is current unless Task 1 verified it.
- [x] Check current Markdown links and cross-document status; remove machine-specific checkout paths
  from tracked docs without rewriting dated build/test evidence. The final automated link, secret,
  binary, and ignore preflight is recorded in Task 4.

### Task 4: Run local GitHub-readiness preflight; stop before push

**Files / evidence:**
- Review: `.gitignore`, `git ls-files`, `git status`, branch/history, Markdown inventory, and large
  tracked files
- Do not push or create remote objects.

- [x] Verify generated `build/`, `dist/`, `.tmp/`, `.cache/`, `.worktrees/`, and DEL contents follow
  the existing ignore rules; keep only the intended DEL manifest tracked.
- [x] Audit for secrets, personal machine paths in public-facing content, broken links, unexpected
  large binaries, untracked artifacts, and uncommitted unrelated owner changes. Do not delete or
  stage unrelated files to force a clean tree.
- [x] At that checkpoint, treat any license selection as an owner decision; the later T30 request
  supplied that decision and is documented separately.
- [x] Run relevant source/package tests, Ruff, strict mypy where applicable, Markdown/link checks,
  and `git diff --check`. Verify the exact intended commit set and branch name; do not merge or push.
- [x] Commit the cleanup manifest/docs and README in reviewed checkpoints. Hand off the branch and
  exact push-ready status to the owner; the owner performs the GitHub push.

## Model recommendation

Recommended model for any later multi-file implementation fix: **Luna Max with Max reasoning**.
The build authorization checkpoint for this plan is already satisfied; the remaining owner gates are
manual testing of the exact candidate and review/approval before the separate T30 license changes are
committed or pushed.
