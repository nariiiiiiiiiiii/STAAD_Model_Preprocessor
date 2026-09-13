"""Undo/redo orchestration for reversible structural repair commands."""

from __future__ import annotations

from staadprep.model.project import ProjectModel
from staadprep.repair.audit import AuditLog
from staadprep.repair.commands import RepairCommand, RepairResult


class RepairHistory:
    def __init__(self, model: ProjectModel, *, audit: AuditLog | None = None) -> None:
        self.model = model
        self.audit = audit or AuditLog()
        self._undo_stack: list[RepairCommand] = []
        self._redo_stack: list[RepairCommand] = []

    @property
    def undo_stack(self) -> tuple[RepairCommand, ...]:
        return tuple(self._undo_stack)

    @property
    def redo_stack(self) -> tuple[RepairCommand, ...]:
        return tuple(self._redo_stack)

    def execute(self, command: RepairCommand) -> RepairResult:
        result = command.apply(self.model)
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self.audit.append(
            command_type=result.command_type,
            before_revision=result.before_revision,
            after_revision=result.after_revision,
            affected_keys=result.affected_keys,
            parameters=command.audit_parameters(),
        )
        return result

    def undo(self) -> RepairResult:
        if not self._undo_stack:
            raise IndexError("Nothing to undo")
        command = self._undo_stack[-1]
        result = command.revert(self.model)
        self._undo_stack.pop()
        self._redo_stack.append(command)
        self.audit.append(
            command_type=result.command_type,
            before_revision=result.before_revision,
            after_revision=result.after_revision,
            affected_keys=result.affected_keys,
            parameters=command.audit_parameters(),
        )
        return result

    def redo(self) -> RepairResult:
        if not self._redo_stack:
            raise IndexError("Nothing to redo")
        command = self._redo_stack[-1]
        result = command.apply(self.model)
        self._redo_stack.pop()
        self._undo_stack.append(command)
        self.audit.append(
            command_type=f"REDO:{type(command).__name__}",
            before_revision=result.before_revision,
            after_revision=result.after_revision,
            affected_keys=result.affected_keys,
            parameters=command.audit_parameters(),
        )
        return result
