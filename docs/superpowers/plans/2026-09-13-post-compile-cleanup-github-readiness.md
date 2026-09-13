# Post-Compile Cleanup and GitHub Readiness Plan

> **For agentic workers:** Execute inline task-by-task. Stop at the compile authorization, ambiguous-move, and owner-push gates.

**Goal:** After an explicitly authorized and verified standalone build, quarantine verified obsolete outputs, synchronize all tracked Markdown, and locally prepare the repository for the owner to push to GitHub.

**Architecture:** Treat package creation as an external prerequisite, not an authorization in this plan. Verify the new release first; then inventory/move recoverable obsolete outputs, synchronize tracked documentation and README, and run a no-push repository preflight.

**Tech Stack:** PowerShell, Git, Python 3.12, existing Nuitka/portable package scripts and package verification tests.

**Spec:** `docs/superpowers/specs/2026-09-13-post-compile-cleanup-github-readiness.md`

## Global Constraints

- Do not run Nuitka until the owner separately authorizes compile/package creation.
- Do not move or quarantine anything until the new package passes the current package gates and the owner accepts it.
- Move only verified-obsolete files under the canonical root to `DEL/`; never delete files.
- Moving to `DEL/` does not reclaim disk space; deletion remains a separate owner action.
- Do not push, create a GitHub release, merge branches, or invent/choose a software license.
- Preserve source, tests, current package/build evidence, required vendor files, and unrelated owner changes.
- Audit every tracked Markdown file; retain historical measurements and label them historical rather than rewriting history.

## Current gate (2026-09-13)

The owner reports the Project JSON Save fix works in the uncompiled source app. Source checkpoint
`ef28cc0` and owner-acceptance documentation checkpoint `a8415d1` are present in
`task/22-portable-packaging`. The accepted executable/package has not been rebuilt. The user's
“after compile” instruction is recorded as a post-build sequence, not compile authorization. Begin
Task 1 only after a separate explicit compile instruction and successful build.

### Task 1: Verify and identify the new standalone release

**Files / evidence:**
- Review: `src/staadprep/version.py`, `scripts/build_windows.ps1`, `scripts/assemble_portable.py`
- Review after build: `build/windows/final/nuitka-report.xml`, the new `dist/` folder, its
  `package-manifest.json`, and `docs/HANDOFF.md`
- Test: `tests/integration/test_packaged_paths.py` plus the existing package-only gates recorded by
  the build handoff

- [ ] Confirm the build was separately authorized; verify Nuitka reports standalone completion and
  the output version matches the source and manifest.
- [ ] Run manifest/hash verification, no-Python/different-CWD launch, relocation/reopen, and the
  package smoke required by the existing release plan. Record folder/ZIP sizes and SHA-256 values.
- [ ] Keep the previous accepted package untouched until the new output passes and the owner accepts
  it. If any package gate fails, stop cleanup and preserve every old artifact.

### Task 2: Re-audit storage and quarantine verified obsolete outputs

**Files / evidence:**
- Review: project-root `build/`, `dist/`, `.tmp/`, `.cache/`, `artifacts/`, `vendor/`, `.worktrees/`,
  existing `DEL/`, and all references in tracked source/tests/scripts/docs
- Create/update: `artifacts/cleanup/post-compile-storage-audit.md`
- Update: `DEL/UNUSED_FILES_MANIFEST.md`

- [ ] Produce a read-only size inventory with file count, bytes, version/hash where relevant, and
  KEEP / REGENERABLE / SUPERSEDED / UNUSED classification.
- [ ] Search tracked source, tests, scripts, build configuration, manifests, and Markdown for every
  proposed move target. Keep anything referenced, required to reproduce the accepted build, or
  uncertain; report ambiguous candidates rather than moving them.
- [ ] Move only confirmed old standalone folders/ZIPs and clearly obsolete generated attempts into a
  dated child of `DEL/`; leave the new accepted standalone and all current source/build evidence in
  their active paths. Preserve relative structure and record original/destination paths, sizes, and
  hashes in the manifest.
- [ ] Verify every moved file is present at the destination with matching hash/size, the new package
  remains in its active location, no live reference points into quarantine, and the new standalone
  still launches. Explicitly state that DEL movement is archival and does not free disk space.

### Task 3: Synchronize all Markdown and make README GitHub-facing

**Files:**
- Inventory: every `.md` under the canonical checkout and active T22 worktree, classifying tracked,
  untracked, historical `DEL/`, and generated/package-copy documents; exclude `.git/`, `.venv/`,
  dependency caches, build outputs, and extracted portable packages from the source-doc update set.
- Modify: every current-status and tracked Markdown file found by that inventory, including
  `README.md`, `docs/HANDOFF.md`, `docs/INDEX.md`, `docs/TASK_BOARD.md`, `docs/CHECKLIST.md`,
  `docs/WORKFLOW.md`, `docs/RISK_GATES.md`, `docs/ARCHITECTURE.md`, `docs/WORKTREE_MINDMAP.md`,
  `DEL/UNUSED_FILES_MANIFEST.md`, and applicable plan/spec documents

- [ ] Inventory all Markdown in the active source surfaces and classify each file as current
  guide/status, durable spec/plan, historical evidence, or generated/archive copy. Update stale
  current claims, version/package paths, hashes, test counts, approval gates, and links; keep
  historical build/test facts unchanged and label them historical. Report archived/generated copies
  that are intentionally not edited.
- [ ] Rewrite the root README as a concise GitHub entry point: project purpose and non-analysis scope;
  features; supported source/portable workflows; prerequisites and source launch; verification
  commands; current release/version; limitations; and where to find deeper docs. Do not publish
  local absolute paths or claim a package is current unless Task 1 verified it.
- [ ] Check relative Markdown links, image references, filenames, and cross-document status. Search
  for user-specific paths (`D:\Dizayn59`, `C:\Users\MSI`), secrets/credentials, generated logs, and
  accidentally tracked build binaries; sanitize public-facing references without rewriting required
  internal historical evidence.

### Task 4: Run local GitHub-readiness preflight; stop before push

**Files / evidence:**
- Review: `.gitignore`, `git ls-files`, `git status`, branch/history, Markdown inventory, and large
  tracked files
- Do not push or create remote objects.

- [ ] Verify generated `build/`, `dist/`, `.tmp/`, `.cache/`, `.worktrees/`, and DEL contents follow
  the existing ignore rules; keep only the intended DEL manifest tracked.
- [ ] Audit for secrets, personal machine paths in public-facing content, broken links, unexpected
  large binaries, untracked artifacts, and uncommitted unrelated owner changes. Do not delete or
  stage unrelated files to force a clean tree.
- [ ] If no LICENSE exists, report that GitHub license selection is an owner decision; do not create
  one without instruction.
- [ ] Run relevant source/package tests, Ruff, strict mypy where applicable, Markdown/link checks,
  and `git diff --check`. Verify the exact intended commit set and branch name; do not merge or push.
- [ ] Commit the cleanup manifest/docs and README in reviewed checkpoints. Hand off the branch and
  exact push-ready status to the owner; the owner performs the GitHub push.

## Model recommendation

Use **Luna Max with Max reasoning** for the post-build artifact audit, broad Markdown reconciliation,
and GitHub-readiness review. Keep compile authorization as an explicit separate checkpoint.
