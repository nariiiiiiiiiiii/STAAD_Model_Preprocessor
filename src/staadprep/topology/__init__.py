"""Canonical topology construction and connectivity analysis."""

from .builder import TopologyPolicy, build_project
from .connectivity import StructureComponent, connected_components

__all__ = [
    "StructureComponent",
    "TopologyPolicy",
    "build_project",
    "connected_components",
]
