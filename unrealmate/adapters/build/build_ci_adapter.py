# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Build Ci Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrapper that maps CI generation to structured contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from unrealmate.contracts.build_domain_common import format_build_details
from unrealmate.contracts.build_ci_init import (
    BuildArtifactEntry,
    BuildCiInitError,
    BuildCiInitRequest,
    BuildCiInitResult,
    BuildCiInitWarning,
    GeneratedFileEntry,
    SUPPORTED_BUILD_CI_PROVIDERS,
)
from unrealmate.core.automation.ci_generator import CIGenerator


class BuildCiAdapter:
    """Filesystem-backed CI generation adapter with deterministic output."""

    def __init__(
        self,
        generator_factory: Callable[[Path], object] | None = None,
    ) -> None:
        self._generator_factory = generator_factory or CIGenerator

    def initialize(self, request: BuildCiInitRequest) -> BuildCiInitResult:
        platform = request.platform
        target_map = {
            "github": (".github/workflows/unreal-build.yml", "generate_github_actions", "GitHub Actions"),
            "gitlab": (".gitlab-ci.yml", "generate_gitlab_ci", "GitLab CI"),
            "jenkins": ("Jenkinsfile", "generate_jenkins", "Jenkins"),
        }

        mapping = target_map.get(platform)
        if mapping is None:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_provider_unsupported",
                        message=f"Unknown platform: {platform}",
                        source=platform,
                        details=f"supported={','.join(SUPPORTED_BUILD_CI_PROVIDERS)}",
                    )
                ],
            )

        relative_target, renderer_name, artifact_name = mapping
        target_path = (request.project_path / relative_target).resolve()

        selection = self._resolve_project_selection(request)
        if selection is None:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                preview_only=request.preview_only,
                selection_strategy=request.selection_strategy,
                errors=[
                    BuildCiInitError(
                        code="build_ci_project_missing",
                        message="No .uproject file found!",
                        source=str(request.project_path.resolve()),
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                        ),
                    )
                ],
            )

        selected_project_file, selected_project_name, candidate_projects = selection
        generator = self._generator_factory(request.project_path)
        if hasattr(generator, "project_name"):
            setattr(generator, "project_name", selected_project_name)
        renderer = getattr(generator, renderer_name, None)
        if not callable(renderer):
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                selected_project_file=selected_project_file,
                selected_project_name=selected_project_name,
                selection_strategy=request.selection_strategy,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_template_missing",
                        message="CI template renderer is not available for selected platform.",
                        source=platform,
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            renderer=renderer_name,
                        ),
                    )
                ],
            )

        try:
            rendered_content = str(renderer())
        except Exception as exc:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                preview_only=request.preview_only,
                errors=[
                    BuildCiInitError(
                        code="build_ci_template_missing",
                        message="Failed to render CI configuration template.",
                        source=str(target_path),
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            stage="render",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
                selected_project_file=selected_project_file,
                selected_project_name=selected_project_name,
                selection_strategy=request.selection_strategy,
            )

        warnings: list[BuildCiInitWarning] = []
        if len(candidate_projects) > 1:
            warnings.append(
                BuildCiInitWarning(
                    code="build_ci_project_selection",
                    message="Multiple .uproject files found; using the first file alphabetically.",
                    source=str(request.project_path.resolve()),
                    details=format_build_details(
                        project_path=str(request.project_path.resolve()),
                        project_file=str(selected_project_file),
                        project_name=selected_project_name,
                        platform=platform,
                        selection_strategy=request.selection_strategy,
                        selected_project_file=selected_project_file.name,
                        selected_project_name=selected_project_name,
                        candidate_projects=",".join(project.name for project in candidate_projects),
                    ),
                )
            )

        existing_content: str | None = None
        target_exists = target_path.exists()
        if target_exists:
            try:
                existing_content = target_path.read_text(encoding="utf-8")
            except Exception as exc:
                warnings.append(
                    BuildCiInitWarning(
                        code="build_ci_partial_generation",
                        message="Existing CI file could not be read for comparison; file will be replaced.",
                        source=str(target_path),
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            stage="read_existing",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                )

        if existing_content is not None and existing_content == rendered_content:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                selected_project_file=selected_project_file,
                selected_project_name=selected_project_name,
                selection_strategy=request.selection_strategy,
                preview_only=request.preview_only,
                generated_files=[
                    GeneratedFileEntry(
                        path=target_path,
                        status="skipped",
                        bytes_written=0,
                        provider=platform,
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            status="skipped",
                            reason="up_to_date",
                        ),
                    )
                ],
                artifacts=[
                    BuildArtifactEntry(
                        name=artifact_name,
                        path=target_path,
                        provider=platform,
                    )
                ],
                warnings=self._sort_signals(
                    warnings
                    + [
                        BuildCiInitWarning(
                            code="build_ci_already_exists",
                            message="CI configuration already exists and is up-to-date.",
                            source=str(target_path),
                            details=format_build_details(
                                project_path=str(request.project_path.resolve()),
                                project_file=str(selected_project_file),
                                project_name=selected_project_name,
                                platform=platform,
                                selection_strategy=request.selection_strategy,
                                status="skipped",
                                reason="content_unchanged",
                            ),
                        )
                    ]
                ),
                errors=[],
            )

        status = "updated" if target_exists else "created"
        if request.preview_only:
            preview_status = "would_update" if target_exists else "would_create"
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                selected_project_file=selected_project_file,
                selected_project_name=selected_project_name,
                selection_strategy=request.selection_strategy,
                preview_only=True,
                generated_files=[
                    GeneratedFileEntry(
                        path=target_path,
                        status=preview_status,
                        bytes_written=len(rendered_content),
                        provider=platform,
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            mode="preview",
                            status=preview_status,
                        ),
                    )
                ],
                artifacts=[
                    BuildArtifactEntry(
                        name=artifact_name,
                        path=target_path,
                        provider=platform,
                    )
                ],
                warnings=self._sort_signals(warnings),
                errors=[],
            )

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(rendered_content, encoding="utf-8")
        except Exception as exc:
            return BuildCiInitResult(
                project_path=request.project_path,
                platform=platform,
                selected_project_file=selected_project_file,
                selected_project_name=selected_project_name,
                selection_strategy=request.selection_strategy,
                preview_only=request.preview_only,
                generated_files=[
                    GeneratedFileEntry(
                        path=target_path,
                        status="failed",
                        bytes_written=0,
                        provider=platform,
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            stage="write",
                            status="failed",
                        ),
                    )
                ],
                warnings=self._sort_signals(warnings),
                errors=[
                    BuildCiInitError(
                        code="build_ci_write_failed",
                        message="Failed to write CI configuration file.",
                        source=str(target_path),
                        details=format_build_details(
                            project_path=str(request.project_path.resolve()),
                            project_file=str(selected_project_file),
                            project_name=selected_project_name,
                            platform=platform,
                            selection_strategy=request.selection_strategy,
                            stage="write",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        return BuildCiInitResult(
            project_path=request.project_path,
            platform=platform,
            selected_project_file=selected_project_file,
            selected_project_name=selected_project_name,
            selection_strategy=request.selection_strategy,
            preview_only=request.preview_only,
            generated_files=[
                GeneratedFileEntry(
                    path=target_path,
                    status=status,
                    bytes_written=len(rendered_content),
                    provider=platform,
                    details=format_build_details(
                        project_path=str(request.project_path.resolve()),
                        project_file=str(selected_project_file),
                        project_name=selected_project_name,
                        platform=platform,
                        selection_strategy=request.selection_strategy,
                        status=status,
                    ),
                )
            ],
            artifacts=[
                BuildArtifactEntry(
                    name=artifact_name,
                    path=target_path,
                    provider=platform,
                )
            ],
            warnings=self._sort_signals(warnings),
            errors=[],
        )

    def _resolve_project_selection(
        self,
        request: BuildCiInitRequest,
    ) -> tuple[Path, str, list[Path]] | None:
        if request.selected_project_file is not None:
            selected_file = request.selected_project_file.resolve()
            selected_name = request.selected_project_name or selected_file.stem
            candidate_files = sorted(
                [path.resolve() for path in request.project_path.glob("*.uproject") if path.is_file()],
                key=lambda path: path.name.lower(),
            )
            if selected_file not in candidate_files:
                candidate_files.append(selected_file)
                candidate_files = sorted(candidate_files, key=lambda path: path.name.lower())
            return selected_file, selected_name, candidate_files

        candidate_files = sorted(
            [path.resolve() for path in request.project_path.glob("*.uproject") if path.is_file()],
            key=lambda path: path.name.lower(),
        )
        if not candidate_files:
            return None
        selected_file = candidate_files[0]
        return selected_file, selected_file.stem, candidate_files

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
