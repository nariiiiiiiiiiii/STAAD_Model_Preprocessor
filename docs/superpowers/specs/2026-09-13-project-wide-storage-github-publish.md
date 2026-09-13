# Project-Wide Storage Audit and GitHub Publish — Behavior Specification

## User request

Recheck the entire STAAD Model Preprocessor project carefully; move only verified-unused or
superseded project files into `DEL/` (never delete); prepare a GitHub push for the supplied repository;
publish only the zipped application as a downloadable artifact, not the extracted portable folder;
finish all local checks before any remote write.

Repository supplied by the owner:
`https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor.git`

## Required behavior

- Inventory the canonical checkout, active worktree, tracked source, ignored build/package output,
  local project data, existing `DEL/`, and remote GitHub state relevant to the requested branch and
  downloadable ZIP.
- Protect tracked source/tests, active package/build evidence, `.venv`, `.git`, active worktrees,
  user project/import data, the owner-supplied `LOGO/`, and the user's pre-existing working-tree
  change. Keep inaccessible or uncertain paths in place and record why.
- Move confirmed obsolete/superseded/regenerable files into a dated child of `DEL/`, record original
  and destination paths plus counts/bytes/hashes where meaningful, and verify moves. Never delete.
- Keep the extracted portable folder local and ignored. Do not add it or other build binaries to Git.
  Keep only the versioned portable ZIP as the intended download asset; prefer a GitHub Release asset
  over a ZIP stored in normal Git history.
- Complete tests, documentation, ignore/secret/large-file/link checks, and review the exact commit
  set locally before publishing. The owner instructed commit/push after local completion; do not
  publish before these gates pass.
- For the T29 publication task, preserve the remote `main`'s then-current LICENSE. This scope
  decision was superseded by the separate T30 owner request; the migration is committed/pushed on
  `task/22-portable-packaging`, and PR #1 is open. `main` remains unchanged pending review/merge.

## Completion gates

1. Storage scan finished; only positively classified items moved; protected/ambiguous items remain.
2. Current package and user data remain intact; applicable package/source checks pass.
3. Repository remote is confirmed to match the supplied URL; branch/commit set and release/tag
   strategy are reviewed before any remote write.
4. Normal Git history contains source/docs only, not the extracted standalone folder or ZIP. The
   ZIP is made available through the agreed download mechanism.
5. The user is told what was moved, what could not be inspected, tests performed, branch/commit,
   whether anything was pushed, and any remaining manual acceptance or push-approval decision.

## Safety boundaries

- Work locally in the active project/worktree first. User instruction gates any remote commit/push;
  stop and ask if remote branch history or release/tag state makes the requested operation ambiguous.
- Move-only cleanup under project-local `DEL/`; no deletion, reset, force push, branch merge, or
  overwrite of remote history.
- The 0.2.0 standalone is an automated-verified candidate; the owner has not reported manual testing
  of that exact compiled executable. Do not label it owner-accepted/stable unless the owner reports
  that test.
- Preserve the local uncommitted `tests/ui/test_manual_edit_mouse.py` line-ending-only change; do not
  stage it.
