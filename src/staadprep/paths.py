"""Project-local path management.

All runtime-generated files must remain below the canonical project root.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    """Canonical project-local runtime directories."""

    root: Path
    tmp: Path
    cache: Path
    logs: Path
    artifacts: Path
    build: Path
    dist: Path
    vendor: Path
    development_layout: bool = True

    @classmethod
    def from_root(cls, root: Path) -> ProjectPaths:
        """Create a path layout rooted at *root* without touching the filesystem."""
        resolved_root = root.expanduser().resolve()
        return cls(
            root=resolved_root,
            tmp=resolved_root / ".tmp",
            cache=resolved_root / ".cache",
            logs=resolved_root / ".logs",
            artifacts=resolved_root / "artifacts",
            build=resolved_root / "build",
            dist=resolved_root / "dist",
            vendor=resolved_root / "vendor",
        )

    @classmethod
    def from_runtime_root(cls, root: Path) -> ProjectPaths:
        """Create runtime paths below a portable ``Data`` root without build outputs."""
        resolved_root = root.expanduser().resolve()
        return cls(
            root=resolved_root,
            tmp=resolved_root / "Temp",
            cache=resolved_root / "Cache",
            logs=resolved_root / "Logs",
            artifacts=resolved_root,
            build=resolved_root / "build",
            dist=resolved_root / "dist",
            vendor=resolved_root / "vendor",
            development_layout=False,
        )

    @property
    def generated_dirs(self) -> tuple[Path, ...]:
        """Directories allowed to contain generated/runtime artifacts."""
        runtime_dirs = (
            self.tmp,
            self.cache,
            self.logs,
            self.artifacts,
        )
        if not self.development_layout:
            return runtime_dirs
        return (*runtime_dirs, self.build, self.dist, self.vendor)

    def ensure_layout(self) -> None:
        """Create all project-local generated directories."""
        for path in self.generated_dirs:
            self.assert_inside_project(path).mkdir(parents=True, exist_ok=True)

    def assert_inside_project(self, path: Path) -> Path:
        """Resolve *path* and reject any path that escapes the project root."""
        candidate = path.expanduser()
        if not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve()
        if not resolved.is_relative_to(self.root):
            raise ValueError(f"Path escapes project root: {path}")
        return resolved
