from __future__ import annotations

from uuid import UUID

import pytest
from PySide6.QtWidgets import QWidget

from staadprep.exporters.staad_std import StaadExportError
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.ui.main_window import MainWindow


def _key(value: int) -> UUID:
    return UUID(int=value)


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model: ProjectModel | None = None
        self.fit_calls = 0

    def set_model(self, model: ProjectModel) -> None:
        self.model = model

    def fit_model(self) -> None:
        self.fit_calls += 1


def _clean_model() -> ProjectModel:
    a = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1)
    b = Node(_key(2), Vec3(6.0, 0.0, 0.0), number=2)
    member = Member(_key(101), a.key, b.key, number=1)
    return ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
        metadata=ModelMetadata(source_format="test", source_unit="m", source_axis="Y-UP"),
        revision=5,
    )


def test_ready_gate_is_authoritative_for_status_and_export_action(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)

    window.set_canonical_model(_clean_model())

    assert window.current_ready_status is not None
    assert window.current_ready_status.ready
    assert window.model_status.text() == "MODEL STATUS: READY FOR STAAD"
    assert window.export_std_action.isEnabled()


def test_disconnected_warning_is_not_ready_under_default_policy(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    model = _clean_model()
    c = Node(_key(3), Vec3(10.0, 0.0, 0.0), number=3)
    d = Node(_key(4), Vec3(12.0, 0.0, 0.0), number=4)
    detached = Member(_key(102), c.key, d.key, number=2)
    model.nodes.update({c.key: c, d.key: d})
    model.members[detached.key] = detached

    window.set_canonical_model(model)

    assert window.current_ready_status is not None
    assert not window.current_ready_status.ready
    assert "disconnected-structure" in window.current_ready_status.blockers
    assert window.model_status.text().startswith("MODEL STATUS: NOT READY")
    assert not window.export_std_action.isEnabled()
    with pytest.raises(StaadExportError, match="not READY FOR STAAD"):
        window.export_current_std(window._project_paths.artifacts / "blocked.std")


def test_unverified_source_unit_blocks_ready_even_without_validation_errors(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    model = _clean_model()
    model.metadata.source_unit = None

    window.set_canonical_model(model)

    assert window.current_issues == []
    assert window.current_ready_status is not None
    assert not window.current_ready_status.ready
    assert "unit-unverified" in window.current_ready_status.blockers
    assert not window.export_std_action.isEnabled()


def test_select_and_fit_navigation_do_not_change_revision_or_readiness(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    model = _clean_model()
    window.set_canonical_model(model)
    before_revision = model.revision
    before_status = window.current_ready_status

    window.select_mode_action.trigger()
    window.fit_model_action.trigger()

    assert model.revision == before_revision
    assert window.current_ready_status == before_status
    assert window.model_status.text() == "MODEL STATUS: READY FOR STAAD"
