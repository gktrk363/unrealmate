# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Git Setup Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter tests for git init/lfs extraction slice."""

from __future__ import annotations

import subprocess
from pathlib import Path

import unrealmate.adapters.git.git_setup_adapter as git_setup_adapter_module
from unrealmate.adapters.git.git_setup_adapter import (
    GitProcessAdapter,
    GitSetupAdapter,
    GitTemplateAdapter,
)
from unrealmate.contracts.git_setup import (
    GitExternalCommandResult,
    GitInitRequest,
    GitLfsRequest,
    GitProcessPolicy,
)


class _TestTemplateAdapter(GitTemplateAdapter):
    def __init__(self, templates_root: Path) -> None:
        self._templates_root = templates_root

    def templates_root(self) -> Path:
        return self._templates_root


class _StubProcessAdapter(GitProcessAdapter):
    def __init__(self, responses: dict[tuple[str, ...], GitExternalCommandResult]) -> None:
        self._responses = responses
        self.calls: list[tuple[tuple[str, ...], Path]] = []

    def run(
        self,
        command: tuple[str, ...],
        cwd: Path,
        timeout_seconds: float = 10.0,
        max_retries: int = 0,
        retry_backoff_seconds: float = 0.25,
    ) -> GitExternalCommandResult:
        resolved_cwd = cwd.resolve()
        self.calls.append((command, resolved_cwd))
        return self._responses.get(
            command,
            GitExternalCommandResult(
                command=command,
                cwd=resolved_cwd,
                status="missing",
                return_code=None,
                stdout="",
                stderr="missing stub response",
            ),
        )


def _write_template(templates_root: Path, name: str, content: str) -> Path:
    templates_root.mkdir(parents=True, exist_ok=True)
    template_path = templates_root / name
    template_path.write_text(content, encoding="utf-8")
    return template_path


def test_gitignore_adapter_create_skip_and_force_overwrite(tmp_path: Path) -> None:
    project = tmp_path / "GitInitProject"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    initial_template = "*.sln\nSaved/\n"
    _write_template(templates_root, "gitignore.template", initial_template)

    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=_StubProcessAdapter({}),
    )

    created_result = adapter.initialize_gitignore(
        GitInitRequest.from_cli(path=str(project), force=False),
    )
    assert created_result.file_status == "created"
    assert created_result.errors == []
    assert (project / ".gitignore").read_text(encoding="utf-8") == initial_template
    assert created_result.to_payload() == {
        "project_path": str(project.resolve()),
        "target_path": str((project / ".gitignore").resolve()),
        "template_path": str((templates_root / "gitignore.template").resolve()),
        "file_status": "created",
        "preview_only": False,
        "bytes_written": len(initial_template),
        "warnings": [],
        "errors": [],
    }

    skipped_result = adapter.initialize_gitignore(
        GitInitRequest.from_cli(path=str(project), force=False),
    )
    assert skipped_result.file_status == "skipped"
    assert skipped_result.errors == []
    assert skipped_result.warnings[0].code == "target_exists"

    updated_template = "*.sln\nIntermediate/\n"
    _write_template(templates_root, "gitignore.template", updated_template)
    updated_result = adapter.initialize_gitignore(
        GitInitRequest.from_cli(path=str(project), force=True),
    )
    assert updated_result.file_status == "updated"
    assert updated_result.errors == []
    assert (project / ".gitignore").read_text(encoding="utf-8") == updated_template
    assert updated_result.bytes_written == len(updated_template)


def test_gitignore_adapter_preview_reports_would_create_and_does_not_write(tmp_path: Path) -> None:
    project = tmp_path / "GitInitPreviewProject"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    template_content = "*.sln\nSaved/\n"
    _write_template(templates_root, "gitignore.template", template_content)

    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=_StubProcessAdapter({}),
    )

    result = adapter.initialize_gitignore(
        GitInitRequest.from_cli(path=str(project), force=False, preview_only=True),
    )

    assert result.file_status == "would_create"
    assert result.preview_only is True
    assert result.warnings[0].code == "preview_only"
    assert not (project / ".gitignore").exists()
    assert result.bytes_written == len(template_content)


def test_git_lfs_adapter_missing_dependency_is_structured(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsMissingProject"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    _write_template(templates_root, "gitattributes.template", "*.uasset filter=lfs diff=lfs merge=lfs -text\n")

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
    process_adapter = _StubProcessAdapter({("git", "lfs", "version"): version_missing})
    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=process_adapter,
    )

    result = adapter.initialize_git_lfs(GitLfsRequest.from_cli(path=str(project), force=True))

    assert result.file_status == "dependency_missing"
    assert result.dependency_status == "missing"
    assert result.errors[0].code == "git_lfs_missing"
    assert result.version_command is not None
    assert result.version_command.status == "missing"
    assert not (project / ".gitattributes").exists()
    assert result.to_payload()["errors"][0]["details"] == (
        "status=missing; return_code=None; timed_out=False; attempts=1; "
        "timeout_seconds=10.0; stderr=FileNotFoundError: git-lfs"
    )


def test_git_lfs_adapter_success_writes_template_and_runs_install(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsSuccessProject"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    template_content = (
        "*.uasset filter=lfs diff=lfs merge=lfs -text\n"
        "*.umap filter=lfs diff=lfs merge=lfs -text\n"
    )
    _write_template(templates_root, "gitattributes.template", template_content)

    responses = {
        ("git", "lfs", "version"): GitExternalCommandResult(
            command=("git", "lfs", "version"),
            cwd=project.resolve(),
            status="success",
            return_code=0,
            stdout="git-lfs/3.5.1",
            stderr="",
        ),
        ("git", "lfs", "install"): GitExternalCommandResult(
            command=("git", "lfs", "install"),
            cwd=project.resolve(),
            status="success",
            return_code=0,
            stdout="Git LFS initialized.",
            stderr="",
        ),
    }
    process_adapter = _StubProcessAdapter(responses)
    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=process_adapter,
    )

    result = adapter.initialize_git_lfs(GitLfsRequest.from_cli(path=str(project), force=True))

    assert result.file_status == "created"
    assert result.dependency_status == "available"
    assert result.errors == []
    assert result.pattern_count == template_content.count("\n")
    assert (project / ".gitattributes").read_text(encoding="utf-8") == template_content
    assert [call[0] for call in process_adapter.calls] == [
        ("git", "lfs", "version"),
        ("git", "lfs", "install"),
    ]


def test_git_lfs_adapter_preview_reports_would_update_and_skips_install(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsPreviewProject"
    project.mkdir(parents=True, exist_ok=True)
    (project / ".gitattributes").write_text("existing", encoding="utf-8")
    templates_root = tmp_path / "templates"
    template_content = "*.uasset filter=lfs diff=lfs merge=lfs -text\n"
    _write_template(templates_root, "gitattributes.template", template_content)

    responses = {
        ("git", "lfs", "version"): GitExternalCommandResult(
            command=("git", "lfs", "version"),
            cwd=project.resolve(),
            status="success",
            return_code=0,
            stdout="git-lfs/3.5.1",
            stderr="",
        ),
    }
    process_adapter = _StubProcessAdapter(responses)
    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=process_adapter,
    )

    result = adapter.initialize_git_lfs(
        GitLfsRequest.from_cli(path=str(project), force=True, preview_only=True),
    )

    assert result.file_status == "would_update"
    assert result.preview_only is True
    assert result.install_command is None
    assert result.errors == []
    assert result.warnings[0].code == "preview_only"
    assert (project / ".gitattributes").read_text(encoding="utf-8") == "existing"
    assert [call[0] for call in process_adapter.calls] == [("git", "lfs", "version")]


def test_git_lfs_adapter_install_failure_is_structured(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsFailureProject"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    _write_template(templates_root, "gitattributes.template", "*.uasset filter=lfs diff=lfs merge=lfs -text\n")

    responses = {
        ("git", "lfs", "version"): GitExternalCommandResult(
            command=("git", "lfs", "version"),
            cwd=project.resolve(),
            status="success",
            return_code=0,
            stdout="git-lfs/3.5.1",
            stderr="",
        ),
        ("git", "lfs", "install"): GitExternalCommandResult(
            command=("git", "lfs", "install"),
            cwd=project.resolve(),
            status="failed",
            return_code=1,
            stdout="",
            stderr="fatal: failed to initialize",
        ),
    }
    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=_StubProcessAdapter(responses),
    )

    result = adapter.initialize_git_lfs(GitLfsRequest.from_cli(path=str(project), force=True))

    assert result.file_status == "created"
    assert result.dependency_status == "failed"
    assert result.errors[0].code == "external_command_failed"
    assert result.install_command is not None
    assert result.install_command.return_code == 1
    assert "status=failed" in (result.errors[0].details or "")
    assert "return_code=1" in (result.errors[0].details or "")


def test_git_lfs_adapter_version_timeout_is_structured_failure(tmp_path: Path) -> None:
    project = tmp_path / "GitLfsTimeoutProject"
    project.mkdir(parents=True, exist_ok=True)
    templates_root = tmp_path / "templates"
    _write_template(templates_root, "gitattributes.template", "*.uasset filter=lfs diff=lfs merge=lfs -text\n")

    version_timeout = GitExternalCommandResult(
        command=("git", "lfs", "version"),
        cwd=project.resolve(),
        status="timeout",
        return_code=None,
        stdout="",
        stderr="TimeoutExpired: command timed out",
        attempts=2,
        timeout_seconds=0.2,
        timed_out=True,
    )
    process_adapter = _StubProcessAdapter({("git", "lfs", "version"): version_timeout})
    adapter = GitSetupAdapter(
        template_adapter=_TestTemplateAdapter(templates_root),
        process_adapter=process_adapter,
    )

    request = GitLfsRequest.from_cli(
        path=str(project),
        force=True,
        process_policy=GitProcessPolicy(timeout_seconds=0.2, max_retries=1, retry_backoff_seconds=0.0),
    )
    result = adapter.initialize_git_lfs(request)

    assert result.file_status == "failed"
    assert result.dependency_status == "failed"
    assert result.errors[0].code == "external_command_failed"
    assert "timed_out=True" in (result.errors[0].details or "")
    assert "attempts=2" in (result.errors[0].details or "")


def test_git_process_adapter_retries_then_succeeds(monkeypatch, tmp_path: Path) -> None:
    call_count = {"count": 0}

    def _run(*args, **kwargs):  # type: ignore[no-untyped-def]
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="ok\n",
            stderr="",
        )

    monkeypatch.setattr(git_setup_adapter_module.subprocess, "run", _run)
    monkeypatch.setattr(git_setup_adapter_module.time, "sleep", lambda *a, **k: None)

    adapter = GitProcessAdapter()
    result = adapter.run(
        ("git", "lfs", "version"),
        cwd=tmp_path,
        timeout_seconds=0.1,
        max_retries=1,
        retry_backoff_seconds=0.0,
    )

    assert result.status == "success"
    assert result.return_code == 0
    assert result.attempts == 2
    assert result.timeout_seconds == 0.1


def test_git_process_adapter_returns_timeout_after_retries(monkeypatch, tmp_path: Path) -> None:
    def _always_timeout(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(git_setup_adapter_module.subprocess, "run", _always_timeout)
    monkeypatch.setattr(git_setup_adapter_module.time, "sleep", lambda *a, **k: None)

    adapter = GitProcessAdapter()
    result = adapter.run(
        ("git", "lfs", "install"),
        cwd=tmp_path,
        timeout_seconds=0.1,
        max_retries=1,
        retry_backoff_seconds=0.0,
    )

    assert result.status == "timeout"
    assert result.timed_out is True
    assert result.attempts == 2
