# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Build İnfo Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper that maps build metadata discovery to structured contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from unrealmate.contracts.build_domain_common import format_build_details
from unrealmate.contracts.build_info import (
    BuildEnvironmentInfo,
    BuildInfoError,
    BuildInfoRequest,
    BuildInfoResult,
    BuildInfoWarning,
    BuildMetadata,
)


class BuildInfoAdapter:
    """Filesystem-backed build info adapter with deterministic output."""

    def collect(self, request: BuildInfoRequest) -> BuildInfoResult:
        environment = self._detect_environment(request.project_path)
        uproject_files = self._discover_uproject_files(request.project_path)
        if not uproject_files:
            return BuildInfoResult(
                project_path=request.project_path,
                environment=environment,
                errors=[
                    BuildInfoError(
                        code="build_info_project_missing",
                        message="No .uproject file found!",
                        source=str(request.project_path.resolve()),
                    )
                ],
            )

        warnings: list[BuildInfoWarning] = []
        selected_file = uproject_files[0]
        if len(uproject_files) > 1:
            warnings.append(
                BuildInfoWarning(
                    code="build_info_partial_metadata",
                    message="Multiple .uproject files found; using the first file alphabetically.",
                    source=str(request.project_path.resolve()),
                    details=format_build_details(
                        project_path=str(request.project_path.resolve()),
                        project_file=str(selected_file.resolve()),
                        project_name=selected_file.stem,
                        selection_strategy="alphabetical_first",
                        selected_project_file=selected_file.name,
                        selected_project_name=selected_file.stem,
                        candidate_projects=",".join(project.name for project in uproject_files),
                    ),
                )
            )

        try:
            payload = json.loads(selected_file.read_text(encoding="utf-8"))
        except Exception as exc:
            return BuildInfoResult(
                project_path=request.project_path,
                environment=environment,
                warnings=self._sort_signals(warnings),
                errors=[
                    BuildInfoError(
                        code="build_info_parse_failed",
                        message=f"Error reading project file: {exc}",
                        source=str(selected_file.resolve()),
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_file.resolve()),
                            project_name=selected_file.stem,
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        if not isinstance(payload, dict):
            return BuildInfoResult(
                project_path=request.project_path,
                environment=environment,
                warnings=self._sort_signals(warnings),
                errors=[
                    BuildInfoError(
                        code="build_info_parse_failed",
                        message="Error reading project file: invalid project metadata format.",
                        source=str(selected_file.resolve()),
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_file.resolve()),
                            project_name=selected_file.stem,
                            expected_type="dict",
                            actual_type=type(payload).__name__,
                        ),
                    )
                ],
            )

        metadata, metadata_warning = self._extract_metadata(
            project_path=request.project_path,
            project_file=selected_file,
            payload=payload,
        )
        if metadata_warning is not None:
            warnings.append(metadata_warning)

        return BuildInfoResult(
            project_path=request.project_path,
            metadata=metadata,
            environment=environment,
            warnings=self._sort_signals(warnings),
            errors=[],
        )

    def _discover_uproject_files(self, project_path: Path) -> list[Path]:
        return sorted(
            [path.resolve() for path in project_path.glob("*.uproject") if path.is_file()],
            key=lambda path: path.name.lower(),
        )

    def _extract_metadata(
        self,
        project_path: Path,
        project_file: Path,
        payload: dict[str, Any],
    ) -> tuple[BuildMetadata, BuildInfoWarning | None]:
        missing_fields: list[str] = []

        engine_value = payload.get("EngineAssociation")
        category_value = payload.get("Category")
        description_value = payload.get("Description")

        if not self._has_text(engine_value):
            missing_fields.append("EngineAssociation")
        if not self._has_text(category_value):
            missing_fields.append("Category")
        if not self._has_text(description_value):
            missing_fields.append("Description")

        plugins_value = payload.get("Plugins", [])
        plugin_count = 0
        plugin_shape_issue: tuple[str, str] | None = None
        if isinstance(plugins_value, list):
            plugin_count = len(plugins_value)
        elif plugins_value is None:
            plugin_count = 0
            missing_fields.append("Plugins")
        else:
            plugin_shape_issue = ("list", type(plugins_value).__name__)

        metadata = BuildMetadata(
            project_name=project_file.stem,
            project_file=project_file.resolve(),
            engine_version=self._normalize_text(engine_value, fallback="Unknown"),
            category=self._normalize_text(category_value, fallback="N/A"),
            description=self._normalize_text(description_value, fallback="N/A"),
            plugin_count=plugin_count,
        )

        if not missing_fields and plugin_shape_issue is None:
            return metadata, None

        details_fields: dict[str, str] = {}
        if missing_fields:
            details_fields["missing_fields"] = ",".join(sorted(set(missing_fields)))
        if plugin_shape_issue is not None:
            expected_type, actual_type = plugin_shape_issue
            details_fields["invalid_field"] = "Plugins"
            details_fields["expected_type"] = expected_type
            details_fields["actual_type"] = actual_type

        return (
            metadata,
            BuildInfoWarning(
                code="build_info_partial_metadata",
                message="Some project metadata fields are missing or invalid; defaults were applied.",
                source=str(project_file.resolve()),
                details=format_build_details(
                    project_path=str(project_path.resolve()),
                    project_file=str(project_file.resolve()),
                    project_name=project_file.stem,
                    **details_fields,
                ),
            ),
        )

    def _detect_environment(self, project_path: Path) -> BuildEnvironmentInfo:
        ci_markers: tuple[tuple[str, Path], ...] = (
            ("github", project_path / ".github" / "workflows"),
            ("gitlab", project_path / ".gitlab-ci.yml"),
            ("jenkins", project_path / "Jenkinsfile"),
            ("azure", project_path / "azure-pipelines.yml"),
            ("circleci", project_path / ".circleci" / "config.yml"),
        )

        ci_providers: list[str] = []
        ci_files: list[str] = []
        for provider, marker_path in ci_markers:
            if marker_path.exists():
                ci_providers.append(provider)
                ci_files.append(marker_path.relative_to(project_path).as_posix())

        return BuildEnvironmentInfo(
            has_git_repository=(project_path / ".git").exists(),
            has_plugins_directory=(project_path / "Plugins").exists(),
            ci_providers=tuple(ci_providers),
            detected_ci_files=tuple(ci_files),
        )

    def _normalize_text(self, value: object, fallback: str) -> str:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
        return fallback

    def _has_text(self, value: object) -> bool:
        return isinstance(value, str) and bool(value.strip())

    def _sort_signals(self, items):
        return sorted(
            items,
            key=lambda item: (
                item.code,
                item.source or "",
                item.message,
                item.details or "",
            ),
        )
