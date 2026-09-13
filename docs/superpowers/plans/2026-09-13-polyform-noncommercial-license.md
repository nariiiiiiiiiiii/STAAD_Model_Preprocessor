# PolyForm Noncommercial License Migration Implementation Plan

> **For agentic workers:** Execute inline in the existing `task/22-portable-packaging` worktree. Do not commit or push without user approval.

**Goal:** Replace the repository license with official PolyForm Noncommercial 1.0.0 text and align README/package metadata.

**Architecture:** Keep the official license body word-for-word as published by PolyForm, placing the repository-specific Required Notice outside the body. Express package metadata with the SPDX identifier and explicitly include `LICENSE` in built distributions.

**Tech Stack:** Markdown, TOML, Python packaging metadata (PEP 639 / setuptools).

**Spec:** `docs/superpowers/specs/2026-09-13-polyform-noncommercial-license.md`

## Global Constraints

- No application source-code or behavior changes.
- The official license wording must remain unchanged; line wrapping may follow the official plain-text file.
- The owner approved branch commit/push, PR creation, and PR #1 integration on 2026-09-13; do not push directly to `main` outside that PR.
- Preserve unrelated existing working-tree changes.

---

### Task 1: Replace the repository license

**Files:**
- Modify: `LICENSE`

- [x] Replace the old license text with the official PolyForm Noncommercial License 1.0.0 plain-text content.
- [x] Add the exact required notice as a separate line outside the license body.
- [x] Preserve the official text's title, URL, sections, examples, and wording.

### Task 2: Align README and package metadata

**Files:**
- Modify: `README.md`
- Modify: `pyproject.toml`

- [x] State the human-readable license name and required noncommercial-use summary in README.
- [x] Set the SPDX identifier and list `LICENSE` in `project.license-files`.
- [x] Require setuptools 77.0.3 or newer for PEP 639 metadata support.

### Task 3: Reconcile existing documentation

**Files:**
- Modify only documentation that describes the superseded license state.

- [x] Remove obsolete current-state instructions and make historical references explicitly historical without claiming the old license remains current.
- [x] Keep all changes within licensing/documentation scope.

### Task 4: Verify before handoff

- [x] Compare the license body with the official PolyForm source; confirm the only addition is the separate Required Notice.
- [x] Search active repository files for obsolete license names and contradictory project-license claims.
- [x] Surface the official funded-organization permission in README and PR #1; the owner authorized PR #1 integration after the caveat was included.
- [x] Parse `pyproject.toml`, check README/metadata consistency, run `git diff --check`, and inspect the final diff/status.
- [x] Confirm no source-code or behavior files changed in the license patch; commit `7bc1dcc` and merge bridge `f6aa64f` are pushed, and PR #1 records the integration.
