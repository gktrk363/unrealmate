# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Ci İnit Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for build ci-init extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.adapters.build.build_ci_adapter import BuildCiAdapter
from unrealmate.contracts.build_ci_init import BuildCiInitRequest


def _create_project(tmp_path: Path) -> Path:
    project = tmp_path / "BuildCiAdapterProject"
    project.mkdir(parents=True, exist_ok=True)
    (project / "BuildCiAdapterProject.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    return project


def test_adapter_generates_github_file_and_tracks_artifacts(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = BuildCiAdapter()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")

    result = adapter.initialize(request)

    assert result.is_success is True
    assert len(result.generated_files) == 1
    assert result.generated_files[0].status == "created"
    assert result.generated_files[0].provider == "github"
    assert result.generated_files[0].path == (project / ".github" / "workflows" / "unreal-build.yml").resolve()
    assert result.selected_project_name == "BuildCiAdapterProject"
    assert result.selected_project_file == (project / "BuildCiAdapterProject.uproject").resolve()
    assert result.generated_files[0].path.exists()
    assert len(result.artifacts) == 1
    assert result.artifacts[0].name == "GitHub Actions"


def test_adapter_skip_when_content_unchanged(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = BuildCiAdapter()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")

    first = adapter.initialize(request)
    second = adapter.initialize(request)

    assert first.generated_files[0].status == "created"
    assert second.generated_files[0].status == "skipped"
    warning_codes = [warning.code for warning in second.warnings]
    assert "build_ci_already_exists" in warning_codes


def test_adapter_update_when_content_changes(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = BuildCiAdapter()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")

    created = adapter.initialize(request)
    assert created.generated_files[0].status == "created"

    target = created.generated_files[0].path
    target.write_text("# modified\n", encoding="utf-8")

    updated = adapter.initialize(request)
    assert updated.generated_files[0].status == "updated"
    assert "Unreal Engine Build" in target.read_text(encoding="utf-8")


def test_adapter_template_missing_returns_structured_error(tmp_path: Path) -> None:
    class _BrokenGenerator:
        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root

    project = _create_project(tmp_path)
    adapter = BuildCiAdapter(generator_factory=_BrokenGenerator)
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")

    result = adapter.initialize(request)

    assert result.is_success is False
    assert result.errors[0].code == "build_ci_template_missing"


def test_adapter_partial_generation_warning_for_unreadable_existing_file(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    target = project / ".github" / "workflows" / "unreal-build.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\xff\xfe\xfd")

    adapter = BuildCiAdapter()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="github")
    result = adapter.initialize(request)

    assert result.is_success is True
    assert result.generated_files[0].status == "updated"
    warning_codes = [warning.code for warning in result.warnings]
    assert "build_ci_partial_generation" in warning_codes


def test_adapter_preview_status_would_create_and_would_update(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = BuildCiAdapter()

    preview_create = adapter.initialize(
        BuildCiInitRequest.from_cli(path=str(project), platform="github", preview_only=True)
    )
    assert preview_create.generated_files[0].status == "would_create"
    assert not (project / ".github" / "workflows" / "unreal-build.yml").exists()

    target = project / ".github" / "workflows" / "unreal-build.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# existing\n", encoding="utf-8")

    preview_update = adapter.initialize(
        BuildCiInitRequest.from_cli(path=str(project), platform="github", preview_only=True)
    )
    assert preview_update.generated_files[0].status == "would_update"


def test_adapter_details_use_normalized_build_shape(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    adapter = BuildCiAdapter()
    result = adapter.initialize(
        BuildCiInitRequest.from_cli(path=str(project), platform="jenkins")
    )

    details = result.generated_files[0].details
    assert isinstance(details, str)
    assert details is not None
    assert f"project_path={project.resolve()}" in details
    assert f"project_file={(project / 'BuildCiAdapterProject.uproject').resolve()}" in details
    assert "project_name=BuildCiAdapterProject" in details
    assert "platform=jenkins" in details
