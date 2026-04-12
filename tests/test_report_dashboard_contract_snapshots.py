# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Dashboard Contract Snapshots
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Structured payload snapshots for report dashboard extraction slice."""

from __future__ import annotations

from pathlib import Path

from unrealmate.contracts.report_dashboard import (
    DashboardDataSnapshot,
    DashboardError,
    DashboardStartResult,
    DashboardStatus,
    DashboardWarning,
)


def test_dashboard_start_result_payload_snapshot_for_success(tmp_path: Path) -> None:
    project = (tmp_path / "DashboardSnapshotProject").resolve()
    result = DashboardStartResult(
        project_path=project,
        startup_status="started",
        url="http://127.0.0.1:8080",
        status=DashboardStatus(
            state="running",
            host="127.0.0.1",
            port=8080,
            startup_status="started",
            url="http://127.0.0.1:8080",
            browser_opened=True,
            thread_name="report-dashboard-8080",
            started_at_iso="2026-04-03T12:00:00",
        ),
        snapshot=DashboardDataSnapshot(
            project_name="DashboardSnapshotGame",
            project_path=project,
            generated_at_iso="2026-04-03T11:59:00",
            stats={
                "uproject_files": 1,
                "cpp_source_files": 2,
                "blueprint_assets": 3,
                "scene_maps": 4,
            },
            config_snapshot={"ui": {"theme": "default"}},
        ),
        warnings=[
            DashboardWarning(
                code="report_dashboard_browser_open_failed",
                message="Browser open failed.",
                source="http://127.0.0.1:8080",
                details="operation=browser_open",
            )
        ],
    )

    assert result.to_payload() == {
        "project_path": str(project),
        "startup_status": "started",
        "url": "http://127.0.0.1:8080",
        "status": {
            "state": "running",
            "host": "127.0.0.1",
            "port": 8080,
            "startup_status": "started",
            "url": "http://127.0.0.1:8080",
            "shutdown_status": None,
            "thread_name": "report-dashboard-8080",
            "browser_opened": True,
            "started_at_iso": "2026-04-03T12:00:00",
        },
        "snapshot": {
            "project_name": "DashboardSnapshotGame",
            "project_path": str(project),
            "generated_at_iso": "2026-04-03T11:59:00",
            "stats": {
                "blueprint_assets": 3,
                "cpp_source_files": 2,
                "scene_maps": 4,
                "uproject_files": 1,
            },
            "config_snapshot": {"ui": {"theme": "default"}},
        },
        "warnings": [
            {
                "code": "report_dashboard_browser_open_failed",
                "message": "Browser open failed.",
                "source": "http://127.0.0.1:8080",
                "details": "operation=browser_open",
            }
        ],
        "errors": [],
    }


def test_dashboard_start_result_payload_snapshot_for_failure_sorted_errors(tmp_path: Path) -> None:
    project = (tmp_path / "DashboardSnapshotFailure").resolve()
    result = DashboardStartResult(
        project_path=project,
        startup_status="port_in_use",
        url="http://127.0.0.1:8080",
        status=DashboardStatus(
            state="failed",
            host="127.0.0.1",
            port=8080,
            startup_status="port_in_use",
            url="http://127.0.0.1:8080",
        ),
        errors=[
            DashboardError(
                code="report_dashboard_startup_failed",
                message="Unexpected startup issue.",
                source="127.0.0.1:8080",
            ),
            DashboardError(
                code="report_dashboard_port_in_use",
                message="Port is in use.",
                source="127.0.0.1:8080",
            ),
        ],
    )

    payload = result.to_payload()
    assert payload["errors"] == [
        {
            "code": "report_dashboard_port_in_use",
            "message": "Port is in use.",
            "source": "127.0.0.1:8080",
            "details": None,
        },
        {
            "code": "report_dashboard_startup_failed",
            "message": "Unexpected startup issue.",
            "source": "127.0.0.1:8080",
            "details": None,
        },
    ]
