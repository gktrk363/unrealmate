# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Ci Gate Workflow Regression
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Regression checks for release-critical CI gate expectations."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "tests.yml"
RELEASE_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release.yml"


def _job_block(job_name: str) -> str:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    match = re.search(
        rf"^  {re.escape(job_name)}:\n(?P<body>(?:^(?:    |\s*$).*\n?)*)",
        workflow,
        flags=re.MULTILINE,
    )
    assert match is not None, f"Job '{job_name}' was not found in tests.yml"
    return match.group("body")


def _step_block(job_name: str, step_name: str) -> str:
    job_block = _job_block(job_name)
    match = re.search(
        rf"^      - name: {re.escape(step_name)}\n(?P<body>(?:^(?:        |\s*$).*\n?)*)",
        job_block,
        flags=re.MULTILINE,
    )
    assert match is not None, f"Step '{step_name}' was not found in job '{job_name}'"
    return match.group("body")


def test_dedicated_lint_job_ruff_check_is_blocking() -> None:
    step = _step_block("lint", "Check linting with Ruff")

    assert "ruff check unrealmate/ tests/" in step
    assert "continue-on-error: true" not in step


def test_test_matrix_no_longer_runs_redundant_non_blocking_ruff_step() -> None:
    job = _job_block("test")

    assert "Run linting with Ruff" not in job


def test_registry_truth_job_checks_generated_artifact_sync() -> None:
    step = _step_block("registry-truth", "Verify generated command registry artifact is up to date")

    assert "python scripts/generate_command_registry_artifact.py --check" in step
    assert "continue-on-error: true" not in step


def test_release_workflow_publishes_only_from_release_published() -> None:
    workflow = RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "types: [published]" in workflow
    assert "types: [published, created]" not in workflow


def test_release_publish_job_waits_for_release_verification() -> None:
    workflow = RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^  pypi-publish:\n(?P<body>(?:^(?:    |\s*$).*\n?)*)",
        workflow,
        flags=re.MULTILINE,
    )
    assert match is not None, "Job 'pypi-publish' was not found in release.yml"

    assert "needs: release-verification" in match.group("body")


def test_release_verification_job_checks_smoke_registry_and_generated_truth() -> None:
    workflow = RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^  release-verification:\n(?P<body>(?:^(?:    |\s*$).*\n?)*)",
        workflow,
        flags=re.MULTILINE,
    )
    assert match is not None, "Job 'release-verification' was not found in release.yml"
    job = match.group("body")

    assert "python -m pytest -q tests/smoke tests/registry" in job
    assert "python scripts/sync_docs_from_registry.py --check" in job
    assert "python scripts/generate_command_registry_artifact.py --check" in job
    assert "python -m ruff check unrealmate tests" in job
    assert "continue-on-error: true" not in job
