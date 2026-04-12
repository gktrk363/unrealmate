# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Git Setup Use Case
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Contract and use-case tests for git init/lfs extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.git_setup import GitInitRequest, GitLfsRequest
from unrealmate.core.application.use_cases.initialize_git_setup import (
    InitializeGitIgnoreUseCase,
    InitializeGitLfsUseCase,
)


def test_git_setup_requests_normalize_relative_cli_path(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "GitProject"
    project.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(project)

    init_request = GitInitRequest.from_cli(".", force=True, preview_only=True)
    lfs_request = GitLfsRequest.from_cli(".", force=False, preview_only=False)

    assert init_request.project_path == project.resolve()
    assert init_request.project_path.is_absolute()
    assert init_request.force is True
    assert init_request.preview_only is True
    assert init_request.path_strategy == "cwd_fallback"
    assert init_request.target_filename == ".gitignore"
    assert init_request.template_filename == "gitignore.template"

    assert lfs_request.project_path == project.resolve()
    assert lfs_request.project_path.is_absolute()
    assert lfs_request.force is False
    assert lfs_request.preview_only is False
    assert lfs_request.path_strategy == "cwd_fallback"
    assert lfs_request.process_policy.timeout_seconds > 0
    assert lfs_request.target_filename == ".gitattributes"
    assert lfs_request.template_filename == "gitattributes.template"


def test_git_setup_requests_support_explicit_path_strategy(tmp_path: Path) -> None:
    project = tmp_path / "GitExplicitPathProject"
    project.mkdir(parents=True, exist_ok=True)

    init_request = GitInitRequest.from_cli(str(project), force=False)
    lfs_request = GitLfsRequest.from_cli(str(project), force=True)

    assert init_request.path_strategy == "explicit"
    assert lfs_request.path_strategy == "explicit"
    assert init_request.project_path == project.resolve()
    assert lfs_request.project_path == project.resolve()


def test_git_init_use_case_invalid_project_path_returns_structured_error(tmp_path: Path) -> None:
    missing_project = tmp_path / "MissingProject"
    request = GitInitRequest.from_cli(str(missing_project))
    use_case = InitializeGitIgnoreUseCase()

    result = use_case.execute(request)

    assert result.is_success is False
    assert result.file_status == "failed"
    assert result.errors[0].code == "project_path_not_found"
    assert result.errors[0].source == str(missing_project.resolve())


def test_git_lfs_use_case_file_path_returns_structured_error(tmp_path: Path) -> None:
    file_path = tmp_path / "project.txt"
    file_path.write_text("not-a-directory", encoding="utf-8")

    request = GitLfsRequest.from_cli(str(file_path))
    use_case = InitializeGitLfsUseCase()
    result = use_case.execute(request)

    assert result.is_success is False
    assert result.file_status == "failed"
    assert result.dependency_status == "unknown"
    assert result.errors[0].code == "project_path_not_directory"
    assert result.errors[0].source == str(file_path.resolve())
