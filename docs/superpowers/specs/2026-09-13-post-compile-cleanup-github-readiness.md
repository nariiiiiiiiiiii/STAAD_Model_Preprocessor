# Post-Compile Cleanup and GitHub Readiness — Behavior Specification

## User request

After a separately authorized compile, inspect the project for unused data and superseded standalone
folders/ZIPs, move only verified-unused items to `DEL/`, update all Markdown files, and prepare the
repository—including the root `README.md`—for the owner to push to their GitHub repository.

## Current gate and preconditions

- The owner authorized the post-compile sequence with “เริ่มทำได้” on 2026-09-13; the 0.2.0
  standalone build and portable assembly have completed.
- The new folder/ZIP passed the existing package verification (**9/9**) and the post-cleanup
  no-Python/different-CWD launch smoke (**1/1**).
- The owner has not reported manually launching/accepting this exact compiled 0.2.0 candidate. Keep
  it identified as a verified candidate, not an owner-accepted public release, until that test.
- Superseded outputs were moved to `DEL/` recoverably after package gates; no data was deleted.

## Expected results

- A dated storage audit classifies retained and obsolete outputs with sizes, versions, hashes, and
  reference checks.
- Superseded standalone folders/ZIPs and other clearly unused generated outputs are moved—not
  deleted—into a project-local `DEL/` quarantine. Ambiguous candidates stay in place for owner review.
- Tracked Markdown is inventoried; all current-status and navigation documents agree with the
  post-compile state. Historical evidence remains labeled as historical rather than rewritten as
  current behavior.
- The root README is a GitHub-facing landing page with accurate purpose, features, prerequisites,
  source setup, standalone usage, testing, limitations, and current release status.
- Local GitHub-readiness checks find no unintended binaries, secrets, personal machine paths in
  public-facing docs, broken relative links, or unreviewed changes. The owner performs the push.

## Safety boundaries

- All audit reports and moves stay inside the canonical project root.
- Never delete files. Moving to `DEL/` is recoverable but does not free disk space on the same volume;
  the owner decides separately whether to delete quarantined data.
- Do not move the newly accepted standalone, active source, tests, required SDK/vendor files, or
  current build evidence needed to reproduce the package.
- This T28/T29 task did not push or merge branches. Its no-license-change scope was superseded by the
  separate T30 owner request; T30 is committed/pushed on the feature branch, PR #1 was created, and
  the owner later authorized merging the PR.
- Preserve the existing project-local runtime path policy and exclude generated `build/`, `dist/`,
  `.tmp/`, `.cache/`, `.worktrees/`, and quarantined `DEL/` contents from Git unless an owner-approved
  release policy explicitly requires otherwise.
