# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Build Domain Stabilization
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Build-domain stabilization tests for details normalization and ordering."""

from __future__ import annotations

import json
from pathlib import Path

from unrealmate.contracts.build_ci_init import BuildCiInitRequest
from unrealmate.contracts.build_info import BuildInfoRequest
from unrealmate.core.application.use_cases.get_build_info import GetBuildInfoUseCase
from unrealmate.core.application.use_cases.initialize_build_ci import (
    InitializeBuildCiUseCase,
)


def _create_project(tmp_path: Path, name: str = "StabilizeGame") -> tuple[Path, Path]:
    project = tmp_path / "BuildDomainStabilizeProject"
    project.mkdir(parents=True, exist_ok=True)
    project_file = project / f"{name}.uproject"
    project_file.write_text(
        json.dumps(
            {
                "FileVersion": 3,
                "EngineAssociation": "5.4",
                "Plugins": {"unexpected": True},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return project, project_file


def test_build_domain_details_share_project_key_prefixes(tmp_path: Path) -> None:
    project, project_file = _create_project(tmp_path)

    info_result = GetBuildInfoUseCase().execute(BuildInfoRequest.from_cli(str(project)))
    ci_result = InitializeBuildCiUseCase().execute(
        BuildCiInitRequest.from_cli(path=str(project), platform="github")
    )

    info_details = info_result.warnings[0].details or ""
    ci_details = ci_result.generated_files[0].details or ""
    shared_expected_parts = (
        f"project_path={project.resolve()}",
        f"project_file={project_file.resolve()}",
        "project_name=StabilizeGame",
    )
    for part in shared_expected_parts:
        assert part in info_details
        assert part in ci_details


def test_build_ci_result_payload_ordering_is_deterministic(tmp_path: Path) -> None:
    project, _ = _create_project(tmp_path, name="BGame")
    (project / "AGame.uproject").write_text(
        json.dumps({"FileVersion": 3, "EngineAssociation": "5.4"}, indent=2),
        encoding="utf-8",
    )
    use_case = InitializeBuildCiUseCase()
    result = use_case.execute(BuildCiInitRequest.from_cli(path=str(project), platform="gitlab"))
    payload = result.to_payload()

    assert payload["selected_project_name"] == "AGame"
    assert payload["selection_strategy"] == "alphabetical_first"
    warning_codes = [item["code"] for item in payload["warnings"]]
    assert warning_codes == sorted(warning_codes)

