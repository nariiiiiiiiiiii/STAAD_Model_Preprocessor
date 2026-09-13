"""Portable standalone runtime path policy.

The packaged application owns only paths below its extracted release root.  The
portable root is detected from Nuitka's compiled containing directory and never
from the process current working directory.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _compiled_containing_dir() -> Path | None:
    """Return the executable directory for a compiled build, else ``None``."""
    compiled: Any = globals().get("__compiled__")
    if compiled is None or not sys.executable:
        return None
    return Path(sys.executable).expanduser().resolve().parent


@dataclass(frozen=True, slots=True)
class PortablePaths:
    """Immutable layout for a writable portable application release."""

    root: Path
    data: Path
    config: Path
    projects: Path
    sketchup_inbox: Path
    exports: Path
    reports: Path
    logs: Path
    cache: Path
    temp: Path
    backups: Path

    @classmethod
    def from_root(cls, root: Path) -> PortablePaths:
        """Derive the portable layout from *root* without touching the filesystem."""
        resolved_root = root.expanduser().resolve()
        data = resolved_root / "Data"
        return cls(
            root=resolved_root,
            data=data,
            config=data / "Config",
            projects=data / "Projects",
            sketchup_inbox=data / "Inbox" / "SketchUp",
            exports=data / "Exports",
            reports=data / "Reports",
            logs=data / "Logs",
            cache=data / "Cache",
            temp=data / "Temp",
            backups=data / "Backups",
        )

    @classmethod
    def detect(cls) -> PortablePaths | None:
        """Detect a compiled portable root without consulting the process CWD."""
        root = _compiled_containing_dir()
        if root is None:
            return None
        return cls.from_root(root)

    @property
    def writable_dirs(self) -> tuple[Path, ...]:
        """Directories that the portable application may create implicitly."""
        return (
            self.data,
            self.config,
            self.projects,
            self.sketchup_inbox,
            self.exports,
            self.reports,
            self.logs,
            self.cache,
            self.temp,
            self.backups,
        )

    def assert_inside_root(self, path: Path) -> Path:
        """Resolve *path* and reject traversal outside the extracted release root."""
        candidate = path.expanduser()
        if not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve()
        if not resolved.is_relative_to(self.root):
            raise ValueError(f"Path escapes portable root: {path}")
        return resolved

    def ensure_layout(self) -> None:
        """Create the portable writable hierarchy below ``Data/`` only."""
        for path in self.writable_dirs:
            self.assert_inside_root(path).mkdir(parents=True, exist_ok=True)

    def assert_writable(self) -> None:
        """Fail explicitly when package-local writable state cannot be used."""
        if not self.data.is_dir() or not os.access(self.data, os.W_OK):
            raise PermissionError(f"Portable Data directory is not writable: {self.data}")

    def apply_environment(self) -> None:
        """Route process/app-managed caches, logs and temp state below ``Data/``."""
        assignments = {
            "TEMP": self.temp,
            "TMP": self.temp,
            "PYTHONPYCACHEPREFIX": self.cache / "pycache",
            "STAADPREP_CACHE_DIR": self.cache,
            "STAADPREP_LOG_DIR": self.logs,
            "STAADPREP_PROJECT_ROOT": self.data,
            "STAADPREP_SKETCHUP_INBOX": self.sketchup_inbox,
        }
        for name, path in assignments.items():
            os.environ[name] = str(self.assert_inside_root(path))
