# Project-Wide Storage Audit and GitHub Publish Plan

> **For agentic workers:** Execute locally first. Move only verified items to `DEL/`. The owner has
> requested commit/push after local completion; stop if remote branch or release state is ambiguous.
> Never delete, force-push, or add the extracted app folder to Git history.

**Goal:** Re-audit the full project/worktree, quarantine only confirmed unused outputs, verify the
current package and source repository, then prepare the ZIP-only download and owner-requested GitHub
push without disturbing user data.

**Architecture:** Inventory and classify first; reference-scan each move candidate; move confirmed
items to a dated `DEL/` child; rerun focused package and repository checks; inspect remote state
read-only; then publish only after local state and the exact target operation are verified.

**Tech Stack:** PowerShell, Git, existing Python package tests/Ruff/mypy, GitHub CLI/API read-only
inspection, GitHub Release asset upload if repository conventions support it.

**Spec:** `docs/superpowers/specs/2026-09-13-project-wide-storage-github-publish.md`

## Global constraints

- All files and temporary output remain inside the project clone/worktrees.
- Move verified-unused items only into `DEL/`; preserve source, tests, active package/build, user
  project data, the selected owner logo source, `.venv`, `.git`, active worktrees, and the existing
  unstaged test-file change. Only the three explicitly audited obsolete logo variants were moved.
- Do not commit the extracted portable folder or binary ZIP into normal Git history. The ZIP is the
  only application artifact intended for a GitHub download; keep the extracted folder local.
- Complete local audit and verification before any remote write. No delete, force push, merge, or
  remote-history overwrite.
- Current 0.2.0 compiled package is a verified candidate; manual owner acceptance remains pending.
- Do not invent, revise, or replace a LICENSE. The supplied remote `main` already has an Unlicense;
  preserve that exact owner-supplied file in this branch. Do not stage the known change in
  `tests/ui/test_manual_edit_mouse.py`.

## Task 1: Inventory the complete local project

**Files/evidence:** both checkout roots, `.worktrees/`, `git ls-files`, `git status`, `.gitignore`,
`build/`, `dist/`, `artifacts/`, `.tmp/`, `.cache/`, `.logs/`, `vendor/`, `DEL/`, and the GitHub
repository's read-only metadata.

- [x] Confirm canonical and active worktree roots, branches, status, remote configuration, and registered
  worktrees. Record the pre-existing user-owned changes.
- [x] Inventory tracked/untracked/ignored file groups and sizes; inspect exact contents only for
  candidate obsolete paths. Exclude OS/global paths and never recurse blindly into `.git`/`.venv`.
- [x] Reference-scan candidates against source, tests, scripts, build manifests, docs, and package
  entrypoints. Classify KEEP / REGENERABLE / SUPERSEDED / UNCERTAIN; keep UNCERTAIN or inaccessible.

## Task 2: Quarantine confirmed obsolete material

**Create/update:** `DEL/UNUSED_FILES_MANIFEST.md`; local ignored detail at
`artifacts/cleanup/project-wide-storage-audit-20260913.md`.

- [x] Create a dated `DEL/` target under the active project after inventory review.
- [x] Move confirmed candidates with exact `Move-Item -LiteralPath` source/destination; preserve
  relative paths and do not overwrite existing targets.
- [x] Verify source absence, destination presence, file counts/bytes and hashes for discrete
  artifacts; verify current 0.2.0 ZIP/folder/EXE/RBZ and user project data remain unchanged.
- [x] Report inaccessible caches/temp paths without terminating processes or changing ACLs.

## Task 3: Local repository and package readiness

- [x] Keep only the source/docs commit set in Git; check `.gitignore`, secrets, machine-specific
  paths, tracked binary extensions, files over 50 MiB, Markdown links, and license status.
- [x] Re-run relevant focused tests (**5/5 package/RBZ PASS**), Ruff, strict mypy (**0 issues**),
  local Markdown links (**51 files resolve**), and `git diff --check`; current package hashes remain
  unchanged. Archive newly generated test output under `DEL/` if large.
- [x] Verify the packaged README against the versioned template; verify the portable ZIP checksum.
- [x] Confirm the intended release download is the ZIP only; do not include the extracted folder in
  Git. Preserve the candidate label until owner manual acceptance.

## Task 4: Inspect and publish to the supplied GitHub repository

- [x] Read-only verify remote URL, default branch, existing branch, tags, and releases. The repo is
  private; `main` has an initial README/Unlicense only, the local/remote histories are unrelated,
  and no feature branch, tag, or release exists. Safest route: push the existing
  `task/22-portable-packaging` branch as a new branch, leave `main` untouched, and create a
  version-matched pre-release `v0.2.0` because the owner has not manually accepted the EXE.
- [ ] Review the exact commit diff locally; commit only intentional source/docs/manifest changes,
  release notes, and the exact owner-supplied LICENSE. Leave `main` unchanged; exclude the existing
  test line-ending change plus all build, cache, user-data, and `DEL` payloads.
- [ ] Push `task/22-portable-packaging` only after all local gates are complete. Create the
  `v0.2.0` pre-release and attach only the portable ZIP; do not upload the extracted folder or
  overwrite `main`.
- [ ] Report the exact branch, commit, release/tag/asset URL, and remaining owner actions. If blocked,
  stop without any remote mutation.

## Recommended model

For the broad storage/reference audit and repository publishing checks: **Luna Max with Max
reasoning**. No source-code feature change is planned.
