# STAAD Model Preprocessor — Project Index

Last synchronized: **2026-09-13** · Active branch: `task/22-portable-packaging` · Current source/package version: **0.2.0** · Tracked Markdown after T29 additions: **49**

This index is the navigation point for current project status. Dated plans/specs and older sections
in the handoff, task board, checklist, and mindmap are historical records; their “pending” notes
describe the state at that checkpoint. Use the current status below and the top of
[`HANDOFF.md`](HANDOFF.md) for present truth.

## Current status

| Area | Status on 2026-09-13 | Authority |
|---|---|---|
| T01–T21 | Complete | [`TASK_BOARD.md`](TASK_BOARD.md) |
| T22 portable Windows packaging | Complete; package is folder-based standalone + ZIP, not one-file EXE | [`HANDOFF.md`](HANDOFF.md) |
| T23 owner acceptance | Pass by owner report (2026-09-01); see note in handoff for acceptance scope | [`HANDOFF.md`](HANDOFF.md) |
| T24–T27 | Historical task checkpoints complete; earlier quarantine contents were later removed by owner | [`DEL/UNUSED_FILES_MANIFEST.md`](../DEL/UNUSED_FILES_MANIFEST.md) |
| 0.2.0 source follow-ups | Source-verified; owner reported the requested UI and Save behavior working | [`HANDOFF.md`](HANDOFF.md) |
| 0.2.0 package candidate | Nuitka standalone + RBZ + portable folder/ZIP built; package gates **9/9 PASS**; post-cleanup launch smoke **1/1 PASS** | [`HANDOFF.md`](HANDOFF.md), `dist/` (local ignored output) |
| Manual acceptance of exact 0.2.0 standalone | **Not yet reported by owner**; keep candidate status until tested | [`HANDOFF.md`](HANDOFF.md) |
| T28/T29 storage audit | T28 superseded packages/generated outputs and T29 three unreferenced logo drafts plus focused-test output moved to `DEL/`; no deletion; inaccessible caches retained | [`DEL/UNUSED_FILES_MANIFEST.md`](../DEL/UNUSED_FILES_MANIFEST.md), ignored local audit reports under `artifacts/cleanup/` |
| GitHub preparation | `task/22-portable-packaging` pushed; private repo `main` left unchanged; `v0.2.0` pre-release published with only the portable ZIP asset. Exact EXE manual acceptance remains pending. | [`README.md`](../README.md), [`HANDOFF.md`](HANDOFF.md), [download ZIP](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/download/v0.2.0/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip) |

## Current 0.2.0 build evidence

| Artifact | Path | SHA-256 / size |
|---|---|---|
| Windows x64 executable | `build/windows/final/app.dist/STAAD Model Preprocessor.exe` | `A616C8286DD63C718D821132B37C4C24F82AA2FB75E15BB46A4FC60E004174A2` |
| SketchUp extension | `build/sketchup/STAAD_Prep_Bridge_0.2.0.rbz` | `655238B3EA983C2A3C76A66BA8C9D44FE030F68BE49A9D8B950CC5CD70234D06` |
| Portable ZIP | `dist/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip` | `635AF835CE71C211E6FE184EBE05656187E0C4C36D2FA8BC542679802C7B15A7` |

All build/package paths above are generated and ignored by Git; they are present in the local active
worktree, not committed release assets. See the handoff for sizes, package-manifest verification,
automated test counts, caveats, and the exact user action still needed.

## Core documentation

- [`PROJECT_SPEC.md`](PROJECT_SPEC.md) — approved V1 scope and product constraints.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — module boundaries and data flow.
- [`WORKFLOW.md`](WORKFLOW.md) — user-facing import, edit, save, validate, and export workflow.
- [`CHECKLIST.md`](CHECKLIST.md) — implementation and delivery checkpoints.
- [`RISK_GATES.md`](RISK_GATES.md) — risk levels and explicit approval requirements.
- [`UI_BASELINE.md`](UI_BASELINE.md) — approved dark engineering UI baseline.
- [`PROJECT_RULES.md`](PROJECT_RULES.md) and [`AGENTS.md`](../AGENTS.md) — project boundary and development rules.
- [`WORKTREE_MINDMAP.md`](WORKTREE_MINDMAP.md) — source, test, package, and SketchUp RBZ relationships.
- [`TASK_BOARD.md`](TASK_BOARD.md) — completed work and current next action.
- [`RELEASE_NOTES_0.2.0.md`](RELEASE_NOTES_0.2.0.md) — candidate binary download and verification notes.

## Plans and specifications

The dated files under [`superpowers/plans/`](superpowers/plans/) and
[`superpowers/specs/`](superpowers/specs/) preserve the decisions, approvals, and verification
evidence for individual increments. They are not a live task queue. The current project-wide audit
is tracked in [`2026-09-13-project-wide-storage-github-publish.md`](superpowers/plans/2026-09-13-project-wide-storage-github-publish.md)
and [`2026-09-13-project-wide-storage-github-publish.md`](superpowers/specs/2026-09-13-project-wide-storage-github-publish.md).
For current state, use this index and the handoff first.

## Storage and GitHub notes

- Obsolete and generated material was **moved, not deleted**, into `DEL/post-compile-cleanup-20260913/`.
- Moving files to `DEL/` on the same drive does not free storage. The owner decides whether to delete
  that quarantine later.
- `.gitignore` excludes `build/`, `dist/`, user data, caches, logs, temporary test output, and all
  `DEL/` content except the tracked move manifest.
- Current license: PolyForm Noncommercial 1.0.0. The official terms and required notice are in
  [`../LICENSE`](../LICENSE); package metadata uses SPDX identifier
  `PolyForm-Noncommercial-1.0.0`.
- The supplied private repo's `main` began with an unrelated starter history. T30 joined that
  history on `task/22-portable-packaging`; [PR #1](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/pull/1)
  is open against `main`. `main` remains unchanged until the PR is reviewed and merged.
- A version-matched `v0.2.0` pre-release is published with the ZIP as its only application asset;
  the extracted folder and EXE were not added to Git history.
- The license commit `7bc1dcc` and history-bridge merge `f6aa64f` are pushed on
  `task/22-portable-packaging`; PR #1 is open and has not been merged.
