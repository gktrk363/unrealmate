# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Ci İnit Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshots for build ci-init extraction slice."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.build_ci_init import BuildCiInitRequest
from unrealmate.core.application.use_cases.initialize_build_ci import (
    InitializeBuildCiUseCase,
)


def _create_project(tmp_path: Path) -> Path:
    project = tmp_path / "BuildCiSnapshotProject"
    project.mkdir(parents=True, exist_ok=True)
    (project / "BuildCiSnapshotProject.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    return project


def test_build_ci_init_payload_snapshot_for_normal_generation(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="gitlab")

    result = use_case.execute(request)
    payload = result.to_payload()

    expected_path = str((project / ".gitlab-ci.yml").resolve())
    assert payload == {
        "project_path": str(project.resolve()),
        "platform": "gitlab",
        "selected_project_file": str((project / "BuildCiSnapshotProject.uproject").resolve()),
        "selected_project_name": "BuildCiSnapshotProject",
        "selection_strategy": "alphabetical_first",
        "preview_only": False,
        "generated_files": [
            {
                "path": expected_path,
                "status": "created",
                "bytes_written": result.generated_files[0].bytes_written,
                "provider": "gitlab",
                "details": (
                    f"project_path={project.resolve()}; "
                    f"project_file={(project / 'BuildCiSnapshotProject.uproject').resolve()}; "
                    "project_name=BuildCiSnapshotProject; platform=gitlab; "
                    "selection_strategy=alphabetical_first; status=created"
                ),
            }
        ],
        "artifacts": [
            {
                "name": "GitLab CI",
                "path": expected_path,
                "provider": "gitlab",
            }
        ],
        "warnings": [],
        "errors": [],
    }


def test_build_ci_init_payload_snapshot_for_skip_and_warning(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    use_case = InitializeBuildCiUseCase()
    request = BuildCiInitRequest.from_cli(path=str(project), platform="jenkins")

    first = use_case.execute(request)
    assert first.generated_files[0].status == "created"

    second = use_case.execute(request)
    payload = second.to_payload()
    expected_path = str((project / "Jenkinsfile").resolve())

    assert payload["project_path"] == str(project.resolve())
    assert payload["platform"] == "jenkins"
    assert payload["selected_project_file"] == str((project / "BuildCiSnapshotProject.uproject").resolve())
    assert payload["selected_project_name"] == "BuildCiSnapshotProject"
    assert payload["selection_strategy"] == "alphabetical_first"
    assert payload["generated_files"] == [
        {
            "path": expected_path,
            "status": "skipped",
            "bytes_written": 0,
            "provider": "jenkins",
            "details": (
                f"project_path={project.resolve()}; "
                f"project_file={(project / 'BuildCiSnapshotProject.uproject').resolve()}; "
                "project_name=BuildCiSnapshotProject; platform=jenkins; "
                "selection_strategy=alphabetical_first; status=skipped; reason=up_to_date"
            ),
        }
    ]
    assert payload["artifacts"] == [
        {"name": "Jenkins", "path": expected_path, "provider": "jenkins"}
    ]
    assert payload["errors"] == []
    assert payload["warnings"] == [
        {
            "code": "build_ci_already_exists",
            "message": "CI configuration already exists and is up-to-date.",
            "source": expected_path,
            "details": (
                f"project_path={project.resolve()}; "
                f"project_file={(project / 'BuildCiSnapshotProject.uproject').resolve()}; "
                "project_name=BuildCiSnapshotProject; platform=jenkins; "
                "selection_strategy=alphabetical_first; status=skipped; reason=content_unchanged"
            ),
        }
    ]


def test_build_ci_init_payload_snapshot_for_preview_modes(tmp_path: Path) -> None:
    project = _create_project(tmp_path)
    use_case = InitializeBuildCiUseCase()

    preview_create = use_case.execute(
        BuildCiInitRequest.from_cli(path=str(project), platform="github", preview_only=True)
    )
    payload_create = preview_create.to_payload()
    expected_path = str((project / ".github" / "workflows" / "unreal-build.yml").resolve())
    expected_project_file = str((project / "BuildCiSnapshotProject.uproject").resolve())

    assert payload_create["preview_only"] is True
    assert payload_create["generated_files"] == [
        {
            "path": expected_path,
            "status": "would_create",
            "bytes_written": preview_create.generated_files[0].bytes_written,
            "provider": "github",
            "details": (
                f"project_path={project.resolve()}; "
                f"project_file={expected_project_file}; "
                "project_name=BuildCiSnapshotProject; platform=github; "
                "selection_strategy=alphabetical_first; status=would_create; mode=preview"
            ),
        }
    ]

    created = use_case.execute(
        BuildCiInitRequest.from_cli(path=str(project), platform="github", preview_only=False)
    )
    assert created.generated_files[0].status == "created"
    (project / ".github" / "workflows" / "unreal-build.yml").write_text(
        "# stale\n",
        encoding="utf-8",
    )

    preview_update = use_case.execute(
        BuildCiInitRequest.from_cli(path=str(project), platform="github", preview_only=True)
    )
    payload_update = preview_update.to_payload()
    assert payload_update["generated_files"][0]["status"] == "would_update"
