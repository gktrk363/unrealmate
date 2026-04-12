# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Git Setup Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshots for git init/lfs stabilization."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.git.git_setup_adapter import (
    GitProcessAdapter,
    GitSetupAdapter,
    GitTemplateAdapter,
)
from unrealmate.contracts.git_setup import GitExternalCommandResult, GitInitRequest, GitLfsRequest


class _TemplateAdapter(GitTemplateAdapter):
    def __init__(self, templates_root: Path) -> None:
        self._templates_root = templates_root

    def templates_root(self) -> Path:
        return self._templates_root


class _ProcessAdapter(GitProcessAdapter):
    def __init__(self, responses: dict[tuple[str, ...], GitExternalCommandResult]) -> None:
        self._responses = responses

    def run(
        self,
        command: tuple[str, ...],
        cwd: Path,
        timeout_seconds: float = 10.0,
        max_retries: int = 0,
        retry_backoff_seconds: float = 0.25,
    ) -> GitExternalCommandResult:
        return self._responses[command]


def _write_template(templates_root: Path, name: str, content: str) -> Path:
    templates_root.mkdir(parents=True, exist_ok=True)
    template_path = templates_root / name
    template_path.write_text(content, encoding="utf-8")
    return template_path


def test_git_init_preview_payload_snapshot(tmp_path: Path) -> None:
    project = tmp_path / "GitInitPreviewSnapshot"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    template_content = "*.sln\nSaved/\n"
    template_path = _write_template(templates_root, "gitignore.template", template_content)

    adapter = GitSetupAdapter(
        template_adapter=_TemplateAdapter(templates_root),
        process_adapter=_ProcessAdapter({}),
    )
    result = adapter.initialize_gitignore(
        GitInitRequest.from_cli(path=str(project), preview_only=True),
    )

    assert result.to_payload() == {
        "project_path": str(project.resolve()),
        "target_path": str((project / ".gitignore").resolve()),
        "template_path": str(template_path.resolve()),
        "file_status": "would_create",
        "preview_only": True,
        "bytes_written": len(template_content),
        "warnings": [
            {
                "code": "preview_only",
                "message": "Preview mode enabled; no files were written.",
                "source": str((project / ".gitignore").resolve()),
                "details": "action=preview; preexisting=False",
            }
        ],
        "errors": [],
    }


def test_git_lfs_missing_payload_snapshot(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsMissingSnapshot"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    template_path = _write_template(
        templates_root,
        "gitattributes.template",
        "*.uasset filter=lfs diff=lfs merge=lfs -text\n",
    )
    version_missing = GitExternalCommandResult(
        command=("git", "lfs", "version"),
        cwd=project.resolve(),
        status="missing",
        return_code=None,
        stdout="",
        stderr="FileNotFoundError: git-lfs",
        attempts=1,
        timeout_seconds=10.0,
        timed_out=False,
    )
    adapter = GitSetupAdapter(
        template_adapter=_TemplateAdapter(templates_root),
        process_adapter=_ProcessAdapter({("git", "lfs", "version"): version_missing}),
    )
    result = adapter.initialize_git_lfs(GitLfsRequest.from_cli(path=str(project), force=True))

    assert result.to_payload() == {
        "project_path": str(project.resolve()),
        "target_path": str((project / ".gitattributes").resolve()),
        "template_path": str(template_path.resolve()),
        "file_status": "dependency_missing",
        "preview_only": False,
        "dependency_status": "missing",
        "bytes_written": 0,
        "pattern_count": 0,
        "version_command": {
            "command": ["git", "lfs", "version"],
            "cwd": str(project.resolve()),
            "status": "missing",
            "return_code": None,
            "stdout": "",
            "stderr": "FileNotFoundError: git-lfs",
            "attempts": 1,
            "timeout_seconds": 10.0,
            "timed_out": False,
        },
        "install_command": None,
        "warnings": [],
        "errors": [
            {
                "code": "git_lfs_missing",
                "message": "Git LFS is not installed on your system.",
                "source": str(project.resolve()),
                "details": (
                    "status=missing; return_code=None; timed_out=False; attempts=1; "
                    "timeout_seconds=10.0; stderr=FileNotFoundError: git-lfs"
                ),
            }
        ],
    }


def test_git_lfs_preview_payload_snapshot(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsPreviewSnapshot"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    template_content = "*.uasset filter=lfs diff=lfs merge=lfs -text\n"
    template_path = _write_template(templates_root, "gitattributes.template", template_content)
    version_success = GitExternalCommandResult(
        command=("git", "lfs", "version"),
        cwd=project.resolve(),
        status="success",
        return_code=0,
        stdout="git-lfs/3.5.1",
        stderr="",
        attempts=1,
        timeout_seconds=5.0,
        timed_out=False,
    )
    adapter = GitSetupAdapter(
        template_adapter=_TemplateAdapter(templates_root),
        process_adapter=_ProcessAdapter({("git", "lfs", "version"): version_success}),
    )
    result = adapter.initialize_git_lfs(
        GitLfsRequest.from_cli(path=str(project), force=True, preview_only=True),
    )

    assert result.to_payload() == {
        "project_path": str(project.resolve()),
        "target_path": str((project / ".gitattributes").resolve()),
        "template_path": str(template_path.resolve()),
        "file_status": "would_create",
        "preview_only": True,
        "dependency_status": "available",
        "bytes_written": len(template_content),
        "pattern_count": template_content.count("\n"),
        "version_command": {
            "command": ["git", "lfs", "version"],
            "cwd": str(project.resolve()),
            "status": "success",
            "return_code": 0,
            "stdout": "git-lfs/3.5.1",
            "stderr": "",
            "attempts": 1,
            "timeout_seconds": 5.0,
            "timed_out": False,
        },
        "install_command": None,
        "warnings": [
            {
                "code": "preview_only",
                "message": "Preview mode enabled; no files were written and no install command was run.",
                "source": str((project / ".gitattributes").resolve()),
                "details": "action=preview; preexisting=False; skipped_command=git lfs install",
            }
        ],
        "errors": [],
    }
