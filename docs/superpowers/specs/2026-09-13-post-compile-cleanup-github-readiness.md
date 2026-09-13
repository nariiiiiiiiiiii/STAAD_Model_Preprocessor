# Post-Compile Cleanup and GitHub Readiness — Behavior Specification

## User request

After a separately authorized compile, inspect the project for unused data and superseded standalone
folders/ZIPs, move only verified-unused items to `DEL/`, update all Markdown files, and prepare the
repository—including the root `README.md`—for the owner to push to their GitHub repository.

## Preconditions

- Compilation/package creation is a separate approval gate. This request describes work to do after
  that compile; it does not itself authorize running Nuitka or replacing the accepted package.
- The new standalone folder/ZIP must first pass the existing package verification and owner acceptance
  applicable to the build.
- The current accepted package and source remain protected until the new package is identified and
  verified by version, manifest, and hashes.

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
- Do not push, create a remote release, change branches/merge into `master`, or invent a LICENSE
  without a separate owner instruction.
- Preserve the existing project-local runtime path policy and exclude generated `build/`, `dist/`,
  `.tmp/`, `.cache/`, `.worktrees/`, and quarantined `DEL/` contents from Git unless an owner-approved
  release policy explicitly requires otherwise.
