"""Canonical release version for application and packaging tooling."""

from __future__ import annotations


def validate_release_version(value: str) -> str:
    """Return a safe non-empty release version or raise ``ValueError``."""
    normalized = value.strip()
    if not normalized or "/" in normalized or "\\" in normalized:
        raise ValueError(f"Invalid release version: {value!r}")
    return normalized


__version__ = validate_release_version("0.2.0")
