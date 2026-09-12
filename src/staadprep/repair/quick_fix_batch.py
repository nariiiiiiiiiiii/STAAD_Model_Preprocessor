"""Plan conflict-checked, atomic batches of validation quick fixes."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from staadprep.editing.manual_ops import build_split_selected_intersection
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import DeleteMember, DeleteNode, MergeNodes, RepairCommand
from staadprep.repair.composite import CompositeRepair
from staadprep.validation.issues import Issue, IssueType
from staadprep.validation.validators import validate_model

type EntityRef = tuple[str, UUID]

_MERGE_ISSUES = {
    IssueType.DUPLICATE_NODE,
    IssueType.NEAR_NODE,
    IssueType.UNCONNECTED_GAP,
}
_DELETE_MEMBER_ISSUES = {
    IssueType.ZERO_LENGTH_MEMBER,
    IssueType.SHORT_MEMBER,
}


class QuickFixBatchError(ValueError):
    """Raised when selected issues cannot safely be planned as one batch."""


def build_quick_fix_batch(
    model: ProjectModel,
    issues: Sequence[Issue],
    *,
    validated_issues: Sequence[Issue] | None = None,
) -> CompositeRepair:
    """Plan independent fixes against one unchanged model snapshot.

    Unsupported, stale, duplicate, malformed, or overlapping selections are
    rejected before returning a command, so callers can fail closed without
    mutating the model. UI selection preflight may supply its current validation
    snapshot to avoid rerunning geometry validation for every selected row;
    the Apply path calls without that snapshot for a fresh check.
    """
    selected = tuple(issues)
    if not selected:
        raise QuickFixBatchError("Select at least one issue to repair.")

    seen_ids: set[str] = set()
    current_issues = validate_model(model) if validated_issues is None else validated_issues
    current_by_id = {issue.id: issue for issue in current_issues}
    planned: list[tuple[Issue, RepairCommand, frozenset[EntityRef]]] = []

    for issue in selected:
        if issue.id in seen_ids:
            raise QuickFixBatchError(
                f"Duplicate selected issue {issue.type.value} [{issue.id}]."
            )
        seen_ids.add(issue.id)

        if current_by_id.get(issue.id) != issue:
            raise QuickFixBatchError(
                f"Selected issue {issue.type.value} [{issue.id}] is stale; "
                "refresh validation and select it again."
            )

        command = _command_for_issue(model, issue)
        footprint = _mutation_footprint(model, issue, command)
        for previous_issue, _previous_command, previous_footprint in planned:
            overlap = footprint & previous_footprint
            if overlap:
                entities = ", ".join(
                    f"{kind} {key}"
                    for kind, key in sorted(
                        overlap,
                        key=lambda item: (item[0], item[1].int),
                    )
                )
                raise QuickFixBatchError(
                    "Selected fixes overlap and cannot be applied together: "
                    f"{previous_issue.type.value} [{previous_issue.id}] and "
                    f"{issue.type.value} [{issue.id}] share {entities}."
                )
        planned.append((issue, command, footprint))

    return CompositeRepair(
        tuple(command for _issue, command, _footprint in planned),
        label="apply selected quick fixes",
    )


def _command_for_issue(model: ProjectModel, issue: Issue) -> RepairCommand:
    node_keys = tuple(key for key in issue.entity_keys if key in model.nodes)
    member_keys = tuple(key for key in issue.entity_keys if key in model.members)
    if len(node_keys) + len(member_keys) != len(issue.entity_keys):
        raise QuickFixBatchError(
            f"Issue {issue.type.value} [{issue.id}] references missing or ambiguous entities."
        )

    if issue.type in _MERGE_ISSUES and len(node_keys) == 2 and not member_keys:
        return MergeNodes(node_keys[0], node_keys[1])
    if issue.type is IssueType.ORPHAN_NODE and len(node_keys) == 1 and not member_keys:
        return DeleteNode(node_keys[0])
    if issue.type in _DELETE_MEMBER_ISSUES and len(member_keys) == 1 and not node_keys:
        return DeleteMember(member_keys[0])
    if issue.type is IssueType.DUPLICATE_MEMBER and len(member_keys) == 2 and not node_keys:
        return DeleteMember(member_keys[-1])
    if issue.type is IssueType.CROSSING_WITHOUT_NODE and len(member_keys) == 2 and not node_keys:
        try:
            return build_split_selected_intersection(model, member_keys[0], member_keys[1])
        except ValueError as exc:
            raise QuickFixBatchError(
                f"Cannot plan intersection fix for issue {issue.id}: {exc}"
            ) from exc

    raise QuickFixBatchError(
        f"No predefined quick fix for {issue.type.value} issue [{issue.id}]."
    )


def _mutation_footprint(
    model: ProjectModel,
    issue: Issue,
    command: RepairCommand,
) -> frozenset[EntityRef]:
    footprint: set[EntityRef] = set()

    def include_node(node_key: UUID) -> None:
        footprint.add(("node", node_key))

    def include_member(member_key: UUID) -> None:
        member = model.members[member_key]
        footprint.add(("member", member_key))
        include_node(member.start)
        include_node(member.end)

    for key in issue.entity_keys:
        if key in model.nodes:
            include_node(key)
        elif key in model.members:
            include_member(key)

    if isinstance(command, MergeNodes):
        include_node(command.keep)
        include_node(command.remove)
        for member in model.members.values():
            if member.start == command.remove or member.end == command.remove:
                include_member(member.key)
    elif isinstance(command, DeleteNode):
        include_node(command.node_key)
        for member in model.members.values():
            if member.start == command.node_key or member.end == command.node_key:
                include_member(member.key)
    elif isinstance(command, DeleteMember):
        include_member(command.member_key)

    return frozenset(footprint)
