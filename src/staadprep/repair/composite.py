"""Atomic composition of reversible structural repair commands."""

from __future__ import annotations

from uuid import UUID

from staadprep.model.project import ProjectModel
from staadprep.repair.commands import (
    RepairCommand,
    RepairResult,
    assert_graph_integrity,
)
from staadprep.validation.validators import validate_model


class CompositeRepair:
    """Apply multiple reversible commands as one history/audit operation."""

    def __init__(self, commands: tuple[RepairCommand, ...], *, label: str) -> None:
        if not commands:
            raise ValueError("CompositeRepair requires at least one child command")
        if not label.strip():
            raise ValueError("CompositeRepair label must not be empty")
        self.commands = tuple(commands)
        self.label = label.strip()
        self._applied = False
        self._before_revision: int | None = None
        self._affected_keys: tuple[UUID, ...] = ()

    def apply(self, model: ProjectModel) -> RepairResult:
        if self._applied:
            raise RuntimeError("CompositeRepair is already applied")
        assert_graph_integrity(model)
        before_revision = model.revision
        before_nodes = dict(model.nodes)
        before_members = dict(model.members)
        applied: list[RepairCommand] = []
        affected: set[UUID] = set()

        try:
            for command in self.commands:
                result = command.apply(model)
                applied.append(command)
                affected.update(result.affected_keys)
        except Exception:
            for command in reversed(applied):
                try:
                    command.revert(model)
                except Exception:
                    pass
            model.nodes.clear()
            model.nodes.update(before_nodes)
            model.members.clear()
            model.members.update(before_members)
            model.revision = before_revision
            raise

        self._applied = True
        self._before_revision = before_revision
        self._affected_keys = tuple(sorted(affected, key=lambda key: key.int))
        assert_graph_integrity(model)
        return RepairResult(
            command_type=type(self).__name__,
            before_revision=before_revision,
            after_revision=model.revision,
            affected_keys=self._affected_keys,
            issues=tuple(validate_model(model)),
        )

    def revert(self, model: ProjectModel) -> RepairResult:
        if not self._applied or self._before_revision is None:
            raise RuntimeError("CompositeRepair is not currently applied")
        before_revert = model.revision
        for command in reversed(self.commands):
            command.revert(model)
        assert model.revision == self._before_revision
        self._applied = False
        assert_graph_integrity(model)
        return RepairResult(
            command_type=f"UNDO:{type(self).__name__}",
            before_revision=before_revert,
            after_revision=model.revision,
            affected_keys=self._affected_keys,
            issues=tuple(validate_model(model)),
        )

    def audit_parameters(self) -> dict[str, object]:
        return {
            "label": self.label,
            "children": [
                {
                    "command_type": type(command).__name__,
                    "parameters": command.audit_parameters(),
                }
                for command in self.commands
            ],
        }
