"""Geometry primitives for the canonical analytical model."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class Vec3:
    """Finite 3D coordinate in canonical model space."""

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        values = (self.x, self.y, self.z)
        if not all(isfinite(value) for value in values):
            raise ValueError("Vec3 coordinates must be finite")

    def as_tuple(self) -> tuple[float, float, float]:
        """Return coordinates in X, Y, Z order."""
        return (self.x, self.y, self.z)
