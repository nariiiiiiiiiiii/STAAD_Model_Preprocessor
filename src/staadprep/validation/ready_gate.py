"""Authoritative READY gate for validated STAAD geometry export."""

from __future__ import annotations

from dataclasses import dataclass

from staadprep.model.project import ProjectModel
from staadprep.units.transforms import LengthUnit
from staadprep.validation.issues import Issue, IssueSeverity, IssueType


@dataclass(frozen=True, slots=True)
class ReadyPolicy:
    require_verified_source_unit: bool = True
    require_reference_dimension: bool = False
    block_disconnected_structure: bool = True


@dataclass(frozen=True, slots=True)
class ReadyStatus:
    ready: bool
    blockers: tuple[str, ...]
    error_issue_ids: tuple[str, ...]
    warning_issue_ids: tuple[str, ...]
    numbering_complete: bool
    unit_verified: bool
    reference_dimension_verified: bool


def _valid_number_sequence(numbers: list[int | None]) -> bool:
    if not numbers:
        return True
    if any(type(number) is not int or number <= 0 for number in numbers):
        return False
    return len(set(numbers)) == len(numbers)


class ReadyGate:
    def __init__(
        self,
        policy: ReadyPolicy | None = None,
        *,
        reference_dimension_verified: bool = False,
    ) -> None:
        self.policy = policy or ReadyPolicy()
        self.reference_dimension_verified = reference_dimension_verified

    def evaluate(self, model: ProjectModel, issues: list[Issue]) -> ReadyStatus:
        error_ids = tuple(issue.id for issue in issues if issue.severity is IssueSeverity.ERROR)
        warning_ids = tuple(issue.id for issue in issues if issue.severity is IssueSeverity.WARNING)
        node_numbers = [node.number for node in model.nodes.values()]
        member_numbers = [member.number for member in model.members.values()]
        numbering_complete = bool(model.nodes) and _valid_number_sequence(
            node_numbers
        ) and _valid_number_sequence(member_numbers)
        supported_units = {unit.value for unit in LengthUnit}
        unit_verified = model.metadata.source_unit in supported_units

        blockers: list[str] = []
        if error_ids:
            blockers.append("validation-errors")
        if self.policy.block_disconnected_structure and any(
            issue.type is IssueType.DISCONNECTED_STRUCTURE for issue in issues
        ):
            blockers.append("disconnected-structure")
        if not numbering_complete:
            blockers.append("numbering-incomplete")
        if self.policy.require_verified_source_unit and not unit_verified:
            blockers.append("unit-unverified")
        if self.policy.require_reference_dimension and not self.reference_dimension_verified:
            blockers.append("reference-dimension-unverified")

        return ReadyStatus(
            ready=not blockers,
            blockers=tuple(blockers),
            error_issue_ids=error_ids,
            warning_issue_ids=warning_ids,
            numbering_complete=numbering_complete,
            unit_verified=unit_verified,
            reference_dimension_verified=self.reference_dimension_verified,
        )
