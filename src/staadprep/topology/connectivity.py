"""Connected-component analysis for canonical structural topology."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from uuid import UUID

from staadprep.model.project import ProjectModel


@dataclass(frozen=True, slots=True)
class StructureComponent:
    node_keys: tuple[UUID, ...]
    member_keys: tuple[UUID, ...]


def _node_sort_key(model: ProjectModel, key: UUID) -> tuple[float, float, float, str]:
    point = model.nodes[key].position
    return (point.x, point.y, point.z, str(key))


def connected_components(model: ProjectModel) -> list[StructureComponent]:
    """Return all graph components, including isolated zero-member nodes."""
    adjacency: dict[UUID, set[UUID]] = {key: set() for key in model.nodes}
    members_by_node: dict[UUID, list[UUID]] = {key: [] for key in model.nodes}

    for member_key, member in model.members.items():
        if member.start not in model.nodes:
            raise ValueError(f"Member {member_key} references missing node {member.start}")
        if member.end not in model.nodes:
            raise ValueError(f"Member {member_key} references missing node {member.end}")
        adjacency[member.start].add(member.end)
        adjacency[member.end].add(member.start)
        members_by_node[member.start].append(member_key)
        if member.end != member.start:
            members_by_node[member.end].append(member_key)

    visited: set[UUID] = set()
    components: list[StructureComponent] = []
    ordered_nodes = sorted(model.nodes, key=lambda key: _node_sort_key(model, key))

    for seed in ordered_nodes:
        if seed in visited:
            continue
        queue: deque[UUID] = deque([seed])
        visited.add(seed)
        component_nodes: list[UUID] = []
        component_members: set[UUID] = set()

        while queue:
            current = queue.popleft()
            component_nodes.append(current)
            component_members.update(members_by_node[current])
            for neighbor in sorted(adjacency[current], key=lambda key: _node_sort_key(model, key)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        component_nodes.sort(key=lambda key: _node_sort_key(model, key))
        ordered_member_keys = tuple(key for key in model.members if key in component_members)
        components.append(
            StructureComponent(
                node_keys=tuple(component_nodes),
                member_keys=ordered_member_keys,
            )
        )

    def component_sort_key(
        component: StructureComponent,
    ) -> tuple[int, int, float, float, float, str]:
        first_key = component.node_keys[0]
        point = model.nodes[first_key].position
        return (
            -len(component.member_keys),
            -len(component.node_keys),
            point.x,
            point.y,
            point.z,
            str(first_key),
        )

    components.sort(key=component_sort_key)
    return components
