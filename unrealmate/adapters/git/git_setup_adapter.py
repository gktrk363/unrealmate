# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Git Setup Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Adapter wrappers for git init / git lfs setup flows."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from unrealmate.contracts.git_setup import (
    GitExternalCommandResult,
    GitInitRequest,
    GitInitResult,
    GitLfsRequest,
    GitLfsResult,
    GitSetupError,
    GitSetupWarning,
)


class GitTemplateAdapter:
    """Template filesystem adapter for packaged git templates."""

    def templates_root(self) -> Path:
        return Path(__file__).resolve().parents[2] / "templates"

    def resolve_template_path(self, template_filename: str) -> Path:
        return self.templates_root() / template_filename

    def read_template(self, template_path: Path) -> str:
        return template_path.read_text(encoding="utf-8")

    def write_target(self, target_path: Path, content: str) -> None:
        target_path.write_text(content, encoding="utf-8")


class GitProcessAdapter:
    """Subprocess adapter for git command execution."""

    def run(
        self,
        command: tuple[str, ...],
        cwd: Path,
        timeout_seconds: float = 10.0,
        max_retries: int = 0,
        retry_backoff_seconds: float = 0.25,
    ) -> GitExternalCommandResult:
        attempts_total = max(1, int(max_retries) + 1)
        timeout = max(0.1, float(timeout_seconds))
        backoff = max(0.0, float(retry_backoff_seconds))

        attempt = 0
        while attempt < attempts_total:
            attempt += 1
            try:
                completed = subprocess.run(
                    list(command),
                    capture_output=True,
                    text=True,
                    cwd=str(cwd),
                    timeout=timeout,
                )
                status = "success" if completed.returncode == 0 else "failed"
                result = GitExternalCommandResult(
                    command=command,
                    cwd=cwd.resolve(),
                    status=status,
                    return_code=completed.returncode,
                    stdout=(completed.stdout or "").strip(),
                    stderr=(completed.stderr or "").strip(),
                    attempts=attempt,
                    timeout_seconds=timeout,
                    timed_out=False,
                )
                if status == "success" or attempt >= attempts_total:
                    return result
            except FileNotFoundError as exc:
                return GitExternalCommandResult(
                    command=command,
                    cwd=cwd.resolve(),
                    status="missing",
                    return_code=None,
                    stdout="",
                    stderr=f"{type(exc).__name__}: {exc}",
                    attempts=attempt,
                    timeout_seconds=timeout,
                    timed_out=False,
                )
            except subprocess.TimeoutExpired as exc:
                stderr = ""
                if isinstance(exc.stderr, bytes):
                    stderr = exc.stderr.decode("utf-8", errors="replace").strip()
                elif isinstance(exc.stderr, str):
                    stderr = exc.stderr.strip()
                timeout_result = GitExternalCommandResult(
                    command=command,
                    cwd=cwd.resolve(),
                    status="timeout",
                    return_code=None,
                    stdout="",
                    stderr=stderr or f"{type(exc).__name__}: command timed out",
                    attempts=attempt,
                    timeout_seconds=timeout,
                    timed_out=True,
                )
                if attempt >= attempts_total:
                    return timeout_result
            except Exception as exc:
                failed_result = GitExternalCommandResult(
                    command=command,
                    cwd=cwd.resolve(),
                    status="failed",
                    return_code=None,
                    stdout="",
                    stderr=f"{type(exc).__name__}: {exc}",
                    attempts=attempt,
                    timeout_seconds=timeout,
                    timed_out=False,
                )
                if attempt >= attempts_total:
                    return failed_result

            if backoff > 0 and attempt < attempts_total:
                time.sleep(backoff * attempt)

        return GitExternalCommandResult(
            command=command,
            cwd=cwd.resolve(),
            status="failed",
            return_code=None,
            stdout="",
            stderr="unexpected process adapter state",
            attempts=attempts_total,
            timeout_seconds=timeout,
            timed_out=False,
        )


class GitSetupAdapter:
    """High-level adapter for gitignore and git lfs initialization."""

    def __init__(
        self,
        template_adapter: GitTemplateAdapter | None = None,
        process_adapter: GitProcessAdapter | None = None,
    ) -> None:
        self._templates = template_adapter or GitTemplateAdapter()
        self._process = process_adapter or GitProcessAdapter()

    def initialize_gitignore(self, request: GitInitRequest) -> GitInitResult:
        target_path = request.project_path / request.target_filename
        template_path = self._templates.resolve_template_path(request.template_filename)

        if target_path.exists() and not request.force:
            return GitInitResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="skipped",
                preview_only=request.preview_only,
                warnings=[
                    GitSetupWarning(
                        code="target_exists",
                        message=f"{request.target_filename} already exists in this directory.",
                        source=str(target_path),
                        details=self._format_details(
                            force=False,
                            preview_only=request.preview_only,
                            target_exists=True,
                        ),
                    )
                ],
            )

        if not template_path.exists():
            return GitInitResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="failed",
                preview_only=request.preview_only,
                errors=[
                    GitSetupError(
                        code="template_missing",
                        message="Could not find the gitignore template file.",
                        source=str(template_path),
                    )
                ],
            )

        try:
            template_content = self._templates.read_template(template_path)
            preexisted = target_path.exists()
            if request.preview_only:
                return GitInitResult(
                    project_path=request.project_path,
                    target_path=target_path,
                    template_path=template_path,
                    file_status="would_update" if preexisted else "would_create",
                    preview_only=True,
                    bytes_written=len(template_content),
                    warnings=[
                        GitSetupWarning(
                            code="preview_only",
                            message="Preview mode enabled; no files were written.",
                            source=str(target_path),
                            details=self._format_details(
                                action="preview",
                                preexisting=preexisted,
                            ),
                        )
                    ],
                )
            self._templates.write_target(target_path, template_content)
        except Exception as exc:
            return GitInitResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="failed",
                preview_only=request.preview_only,
                errors=[
                    GitSetupError(
                        code="write_failed",
                        message="Failed to write gitignore configuration.",
                        source=str(target_path.resolve()),
                        details=self._format_details(
                            operation="write_target",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        return GitInitResult(
            project_path=request.project_path,
            target_path=target_path,
            template_path=template_path,
            file_status="updated" if preexisted else "created",
            preview_only=request.preview_only,
            bytes_written=len(template_content),
        )

    def initialize_git_lfs(self, request: GitLfsRequest) -> GitLfsResult:
        target_path = request.project_path / request.target_filename
        template_path = self._templates.resolve_template_path(request.template_filename)

        version_command = self._process.run(
            ("git", "lfs", "version"),
            cwd=request.project_path,
            timeout_seconds=request.process_policy.timeout_seconds,
            max_retries=request.process_policy.max_retries,
            retry_backoff_seconds=request.process_policy.retry_backoff_seconds,
        )
        if version_command.status == "missing":
            return GitLfsResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="dependency_missing",
                preview_only=request.preview_only,
                dependency_status="missing",
                version_command=version_command,
                errors=[
                    GitSetupError(
                        code="git_lfs_missing",
                        message="Git LFS is not installed on your system.",
                        source=str(request.project_path),
                        details=self._command_failure_details(version_command),
                    )
                ],
            )
        if version_command.status != "success" or version_command.return_code != 0:
            return GitLfsResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="failed",
                preview_only=request.preview_only,
                dependency_status="failed",
                version_command=version_command,
                errors=[
                    GitSetupError(
                        code="external_command_failed",
                        message="Git LFS version command failed.",
                        source=str(request.project_path),
                        details=self._command_failure_details(version_command),
                    )
                ],
            )

        if target_path.exists() and not request.force:
            return GitLfsResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="skipped",
                preview_only=request.preview_only,
                dependency_status="available",
                version_command=version_command,
                warnings=[
                    GitSetupWarning(
                        code="target_exists",
                        message=f"{request.target_filename} already exists.",
                        source=str(target_path),
                        details=self._format_details(
                            force=False,
                            preview_only=request.preview_only,
                            target_exists=True,
                        ),
                    )
                ],
            )

        if not template_path.exists():
            return GitLfsResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="failed",
                preview_only=request.preview_only,
                dependency_status="available",
                version_command=version_command,
                errors=[
                    GitSetupError(
                        code="template_missing",
                        message="Could not find gitattributes template.",
                        source=str(template_path),
                    )
                ],
            )

        try:
            template_content = self._templates.read_template(template_path)
            preexisted = target_path.exists()
            if request.preview_only:
                return GitLfsResult(
                    project_path=request.project_path,
                    target_path=target_path,
                    template_path=template_path,
                    file_status="would_update" if preexisted else "would_create",
                    preview_only=True,
                    dependency_status="available",
                    bytes_written=len(template_content),
                    pattern_count=template_content.count("\n"),
                    version_command=version_command,
                    warnings=[
                        GitSetupWarning(
                            code="preview_only",
                            message="Preview mode enabled; no files were written and no install command was run.",
                            source=str(target_path),
                            details=self._format_details(
                                action="preview",
                                preexisting=preexisted,
                                skipped_command="git lfs install",
                            ),
                        )
                    ],
                )
            self._templates.write_target(target_path, template_content)
        except Exception as exc:
            return GitLfsResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="failed",
                preview_only=request.preview_only,
                dependency_status="available",
                version_command=version_command,
                errors=[
                    GitSetupError(
                        code="write_failed",
                        message="Failed to write gitattributes configuration.",
                        source=str(target_path.resolve()),
                        details=self._format_details(
                            operation="write_target",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        install_command = self._process.run(
            ("git", "lfs", "install"),
            cwd=request.project_path,
            timeout_seconds=request.process_policy.timeout_seconds,
            max_retries=request.process_policy.max_retries,
            retry_backoff_seconds=request.process_policy.retry_backoff_seconds,
        )
        if install_command.status != "success" or install_command.return_code != 0:
            dependency_status = "missing" if install_command.status == "missing" else "failed"
            error_code = "git_lfs_missing" if install_command.status == "missing" else "external_command_failed"
            error_message = (
                "Git LFS install command is unavailable."
                if install_command.status == "missing"
                else "Git LFS install command failed."
            )
            return GitLfsResult(
                project_path=request.project_path,
                target_path=target_path,
                template_path=template_path,
                file_status="updated" if preexisted else "created",
                preview_only=request.preview_only,
                dependency_status=dependency_status,
                bytes_written=len(template_content),
                pattern_count=template_content.count("\n"),
                version_command=version_command,
                install_command=install_command,
                errors=[
                    GitSetupError(
                        code=error_code,
                        message=error_message,
                        source=str(request.project_path),
                        details=self._command_failure_details(install_command),
                    )
                ],
            )

        return GitLfsResult(
            project_path=request.project_path,
            target_path=target_path,
            template_path=template_path,
            file_status="updated" if preexisted else "created",
            preview_only=request.preview_only,
            dependency_status="available",
            bytes_written=len(template_content),
            pattern_count=template_content.count("\n"),
            version_command=version_command,
            install_command=install_command,
        )

    def _command_failure_details(self, result: GitExternalCommandResult) -> str:
        return self._format_details(
            status=result.status,
            return_code=result.return_code,
            timed_out=result.timed_out,
            attempts=result.attempts,
            timeout_seconds=result.timeout_seconds,
            stderr=result.stderr,
        )

    def _format_details(self, **fields: object) -> str:
        ordered_keys = (
            "operation",
            "action",
            "status",
            "return_code",
            "timed_out",
            "attempts",
            "timeout_seconds",
            "force",
            "preview_only",
            "target_exists",
            "preexisting",
            "skipped_command",
            "error_type",
            "error",
            "stderr",
        )
        keys = [key for key in ordered_keys if key in fields]
        keys.extend(sorted(key for key in fields if key not in ordered_keys))
        return "; ".join(f"{key}={fields[key]}" for key in keys)
